-- check_missing_event_metadata.sql
-- Check whether all event records have matching metadata.

select
    i.canonical_event_id,
    count(*) as rows_without_metadata
from stg_identity_records i
left join stg_events e
    on i.canonical_event_id = e.canonical_event_id
where i.is_auxiliary_source = false
  and e.canonical_event_id is null
group by i.canonical_event_id
order by rows_without_metadata desc;
