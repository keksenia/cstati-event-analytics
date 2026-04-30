-- stg_event_participations.sql
-- Deduplicated event × participant layer.

with identity_records as (
    select *
    from stg_identity_records
),

event_level as (
    select
        canonical_event_id,
        canonical_event_name,
        participant_hash_private,
        identity_confidence,
        identity_conflict_flag,
        has_any_identifier,
        has_strong_identifier
    from identity_records
    where is_auxiliary_source = false
      and participant_hash_private is not null
),

deduplicated as (
    select distinct
        canonical_event_id,
        canonical_event_name,
        participant_hash_private,
        identity_confidence,
        identity_conflict_flag,
        has_any_identifier,
        has_strong_identifier
    from event_level
),

clean_layer as (
    select
        *,
        case
            when identity_conflict_flag = false
             and identity_confidence in ('high', 'medium')
            then true
            else false
        end as is_clean_identity
    from deduplicated
)

select *
from clean_layer;

