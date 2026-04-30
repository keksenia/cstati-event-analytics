-- mart_family_metrics.sql
-- Family-level aggregation of event portfolio metrics.

with event_metrics as (
    select *
    from mart_event_metrics
),

retention as (
    select *
    from mart_retention
),

joined as (
    select
        e.canonical_event_id,
        e.event_name,
        e.event_family,

        e.raw_rows,
        e.full_unique_participants,
        e.clean_unique_participants,
        e.strong_identifier_share,
        e.clean_coverage_share,

        coalesce(r.clean_participants, 0) as clean_participants,
        coalesce(r.new_participants, 0) as new_participants,
        coalesce(r.repeat_participants, 0) as repeat_participants

    from event_metrics e
    left join retention r
        on e.canonical_event_id = r.canonical_event_id
),

family_metrics as (
    select
        event_family,

        count(distinct canonical_event_id) as events,
        sum(raw_rows) as raw_rows,
        sum(full_unique_participants) as full_unique_participants,
        sum(clean_unique_participants) as clean_unique_participants,
        sum(clean_participants) as clean_participants,
        sum(new_participants) as new_participants,
        sum(repeat_participants) as repeat_participants,

        avg(strong_identifier_share) as avg_strong_identifier_share,
        avg(clean_coverage_share) as avg_clean_coverage_share

    from joined
    group by event_family
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

    from family_metrics
)

select *
from final
order by clean_participants desc;
