-- check_clean_layer_coverage.sql
-- Check how much of the event-level data survives into the clean identity layer.

with event_level as (
    select
        canonical_event_id,
        count(*) as event_level_rows,
        count(distinct participant_hash_private) as event_level_unique_participants
    from stg_identity_records
    where is_auxiliary_source = false
    group by canonical_event_id
),

clean_layer as (
    select
        canonical_event_id,
        count(*) as clean_rows,
        count(distinct participant_hash_private) as clean_unique_participants
    from stg_event_participations
    where is_clean_identity = true
    group by canonical_event_id
)

select
    e.canonical_event_id,
    e.event_level_rows,
    coalesce(c.clean_rows, 0) as clean_rows,

    e.event_level_unique_participants,
    coalesce(c.clean_unique_participants, 0) as clean_unique_participants,

    case
        when e.event_level_rows > 0
        then 1.0 * coalesce(c.clean_rows, 0) / e.event_level_rows
        else null
    end as clean_row_coverage,

    case
        when e.event_level_unique_participants > 0
        then 1.0 * coalesce(c.clean_unique_participants, 0) / e.event_level_unique_participants
        else null
    end as clean_participant_coverage

from event_level e
left join clean_layer c
    on e.canonical_event_id = c.canonical_event_id
order by clean_participant_coverage asc;
