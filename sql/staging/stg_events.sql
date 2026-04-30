-- stg_events.sql
-- Canonical event dictionary based on manual/event_metadata.csv.
-- One row = one canonical event.

with source as (
    select
        event_id,
        event_name,
        event_family,
        cast(event_year as integer) as event_year,
        event_date,
        event_season,
        event_type,
        is_paid,
        approx_capacity,
        target_audience,
        format,
        strategic_role,
        notes
    from raw_event_metadata
),

season_ordered as (
    select
        *,
        case
            when lower(event_season) = 'winter' then 1
            when lower(event_season) = 'spring' then 2
            when lower(event_season) = 'summer' then 3
            when lower(event_season) in ('autumn', 'fall') then 4
            else 9
        end as event_season_order
    from source
),

final as (
    select
        event_id as canonical_event_id,
        event_name,
        event_family,
        event_year,
        event_date,
        event_season,
        event_season_order,
        event_type,
        is_paid,
        approx_capacity,
        target_audience,
        format,
        strategic_role,
        notes
    from season_ordered
)

select *
from final;
