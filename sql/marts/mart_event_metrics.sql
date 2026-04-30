-- mart_event_metrics.sql
-- Event-level product metrics.

with events as (
    select *
    from stg_events
),

identity_records as (
    select *
    from stg_identity_records
    where is_auxiliary_source = false
),

participations as (
    select *
    from stg_event_participations
),

full_metrics as (
    select
        canonical_event_id,
        count(*) as raw_rows,
        count(distinct participant_hash_private) as full_unique_participants,
        sum(case when has_any_identifier then 1 else 0 end) as rows_with_any_identifier,
        sum(case when has_strong_identifier then 1 else 0 end) as rows_with_strong_identifier
    from identity_records
    group by canonical_event_id
),

clean_metrics as (
    select
        canonical_event_id,
        count(distinct participant_hash_private) as clean_unique_participants
    from participations
    where is_clean_identity = true
    group by canonical_event_id
),

final as (
    select
        e.canonical_event_id,
        e.event_name,
        e.event_family,
        e.event_year,
        e.event_season,
        e.event_type,
        e.strategic_role,

        coalesce(f.raw_rows, 0) as raw_rows,
        coalesce(f.full_unique_participants, 0) as full_unique_participants,
        coalesce(f.rows_with_any_identifier, 0) as rows_with_any_identifier,
        coalesce(f.rows_with_strong_identifier, 0) as rows_with_strong_identifier,
        coalesce(c.clean_unique_participants, 0) as clean_unique_participants,

        case
            when coalesce(f.raw_rows, 0) > 0
            then 1.0 * f.rows_with_strong_identifier / f.raw_rows
            else null
        end as strong_identifier_share,

        case
            when coalesce(f.full_unique_participants, 0) > 0
            then 1.0 * c.clean_unique_participants / f.full_unique_participants
            else null
        end as clean_coverage_share

    from events e
    left join full_metrics f
        on e.canonical_event_id = f.canonical_event_id
    left join clean_metrics c
        on e.canonical_event_id = c.canonical_event_id
)

select *
from final;
