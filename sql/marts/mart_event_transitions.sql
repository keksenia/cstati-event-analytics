-- mart_event_transitions.sql
-- Event-to-event and family-to-family transitions.

with clean_participations as (
    select
        p.participant_hash_private,
        p.canonical_event_id,
        e.event_name,
        e.event_family,
        e.event_year * 100 + e.event_season_order as event_order

    from stg_event_participations p
    left join stg_events e
        on p.canonical_event_id = e.canonical_event_id
    where p.is_clean_identity = true
),

sequenced as (
    select
        *,

        lead(event_name) over (
            partition by participant_hash_private
            order by event_order, canonical_event_id
        ) as next_event_name,

        lead(event_family) over (
            partition by participant_hash_private
            order by event_order, canonical_event_id
        ) as next_event_family

    from clean_participations
),

event_transitions as (
    select
        event_name,
        next_event_name,
        count(distinct participant_hash_private) as participants
    from sequenced
    where next_event_name is not null
    group by
        event_name,
        next_event_name
),

family_transitions as (
    select
        event_family,
        next_event_family,
        count(distinct participant_hash_private) as participants
    from sequenced
    where next_event_family is not null
    group by
        event_family,
        next_event_family
)

select
    'event_transition' as transition_level,
    event_name as from_entity,
    next_event_name as to_entity,
    participants
from event_transitions

union all

select
    'family_transition' as transition_level,
    event_family as from_entity,
    next_event_family as to_entity,
    participants
from family_transitions;
