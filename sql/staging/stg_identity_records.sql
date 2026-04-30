-- stg_identity_records.sql
-- Private identity-resolution output.
-- In the real project this table is created locally and must not expose raw PII publicly.

with source as (
    select
        source_file,
        source_row_number,
        inferred_event_name,
        canonical_event_id,
        canonical_event_name,
        cast(is_auxiliary_source as boolean) as is_auxiliary_source,

        identity_confidence,
        cast(identity_conflict_flag as boolean) as identity_conflict_flag,

        cast(has_any_identifier as boolean) as has_any_identifier,
        cast(has_strong_identifier as boolean) as has_strong_identifier,

        participant_hash_private

    from identity_records_private
),

final as (
    select
        *
    from source
    where canonical_event_id is not null
)

select *
from final;
