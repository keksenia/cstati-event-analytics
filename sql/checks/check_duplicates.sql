-- check_duplicates.sql
-- Check duplicate event-participant records.

select
    canonical_event_id,
    participant_hash_private,
    count(*) as rows_count
from stg_identity_records
where is_auxiliary_source = false
  and participant_hash_private is not null
group by
    canonical_event_id,
    participant_hash_private
having count(*) > 1
order by rows_count desc;
