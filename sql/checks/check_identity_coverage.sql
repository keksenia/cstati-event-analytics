-- check_identity_coverage.sql
-- Check identity coverage by event.

select
    canonical_event_id,

    count(*) as rows_total,

    sum(case when has_any_identifier then 1 else 0 end) as rows_with_any_identifier,

    sum(case when has_strong_identifier then 1 else 0 end) as rows_with_strong_identifier,

    sum(case when identity_confidence = 'high' then 1 else 0 end) as high_confidence_rows,

    sum(case when identity_confidence = 'medium' then 1 else 0 end) as medium_confidence_rows,

    sum(case when identity_confidence = 'low' then 1 else 0 end) as low_confidence_rows,

    sum(case when identity_confidence = 'missing' then 1 else 0 end) as missing_identity_rows,

    1.0 * sum(case when has_any_identifier then 1 else 0 end) / count(*) as any_identifier_share,

    1.0 * sum(case when has_strong_identifier then 1 else 0 end) / count(*) as strong_identifier_share

from stg_identity_records
where is_auxiliary_source = false
group by canonical_event_id
order by strong_identifier_share asc;
