-- mart_retention.sql
-- New vs repeat participation and retention proxy.

with clean_participations as (
    select
        p.canonical_event_id,
        e.event_name,
        e.event_family,
        e.event_year,
        e.event_season_order,
        p.participant_hash_private,

        -- Proxy event ordering.
        -- Exact event_date should replace this once available.
        e.event_year * 100 + e.event_season_order as event_order

    from stg_event_participations p
    left join stg_events e
        on p.canonical_event_id = e.canonical_event_id
    where p.is_clean_identity = true
),

sequenced as (
    select
        *,
        row_number() over (
            partition by participant_hash_private
            order by event_order, canonical_event_id
        ) as participant_event_rank
    from clean_participations
),

with_flags as (
    select
        *,
        case
            when participant_event_rank = 1 then true
            else false
        end as is_first_event,

        participant_event_rank - 1 as prior_events_cnt
    from sequenced
),

event_retention as (
    select
        canonical_event_id,
        event_name,
        event_family,

        count(distinct participant_hash_private) as clean_participants,

        sum(case when is_first_event then 1 else 0 end) as new_participants,

        sum(case when prior_events_cnt > 0 then 1 else 0 end) as repeat_participants,

        avg(prior_events_cnt) as avg_prior_events

    from with_flags
    group by
        canonical_event_id,
        event_name,
        event_family
),

final as (
    select
        *,
        case
            when clean_participants > 0
            then 1.0 * new_participants / clean_participants
            else null
        end as new_share,

        case
            when clean_participants > 0
            then 1.0 * repeat_participants / clean_participants
            else null
        end as repeat_share

    from event_retention
)

select *
from final;
