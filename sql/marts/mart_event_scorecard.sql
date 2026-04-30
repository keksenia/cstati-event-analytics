-- mart_event_scorecard.sql
-- Product scorecard for event comparison.
-- This is a SQL reference version of the Python scorecard.

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
        e.event_year,
        e.strategic_role,

        coalesce(r.clean_participants, 0) as clean_participants,
        coalesce(r.new_participants, 0) as new_participants,
        coalesce(r.repeat_participants, 0) as repeat_participants,
        coalesce(r.new_share, 0) as new_share,
        coalesce(r.repeat_share, 0) as repeat_share,

        coalesce(e.strong_identifier_share, 0) as strong_identifier_share,
        coalesce(e.clean_coverage_share, 0) as clean_coverage_share

    from event_metrics e
    left join retention r
        on e.canonical_event_id = r.canonical_event_id
),

ranked as (
    select
        *,

        percent_rank() over (order by new_participants) as new_participants_rank,
        percent_rank() over (order by new_share) as new_share_rank,

        percent_rank() over (order by repeat_participants) as repeat_participants_rank,
        percent_rank() over (order by repeat_share) as repeat_share_rank,

        percent_rank() over (order by strong_identifier_share) as strong_id_rank,
        percent_rank() over (order by clean_coverage_share) as clean_coverage_rank

    from joined
),

scored as (
    select
        *,

        0.5 * new_participants_rank
        + 0.5 * new_share_rank as acquisition_score,

        0.5 * repeat_participants_rank
        + 0.5 * repeat_share_rank as retention_score,

        0.5 * strong_id_rank
        + 0.5 * clean_coverage_rank as data_quality_score

    from ranked
),

final as (
    select
        *,

        0.4 * acquisition_score
        + 0.4 * retention_score
        + 0.2 * data_quality_score as portfolio_score

    from scored
)

select *
from final
order by portfolio_score desc;
