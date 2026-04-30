import numpy as np
import pandas as pd


def build_event_participation_layer(identity_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build deduplicated event-participant layer.
    """
    return (
        identity_df[
            identity_df["participant_hash_private"].notna()
        ]
        .drop_duplicates(["canonical_event_id", "participant_hash_private"])
        .copy()
    )


def build_clean_identity_layer(identity_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build strict clean identity layer for sensitive product metrics.
    """
    return identity_df[
        (identity_df["is_auxiliary_source"] == False)
        & (identity_df["identity_conflict_flag"] == False)
        & (identity_df["identity_confidence"].isin(["high", "medium"]))
        & (identity_df["participant_hash_private"].notna())
    ].copy()


def build_event_metrics(
    event_identity_df: pd.DataFrame,
    event_participation_clean: pd.DataFrame,
    event_metadata: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate event-level metrics.
    """
    event_full_metrics = (
        event_identity_df
        .groupby("canonical_event_id", dropna=False)
        .agg(
            raw_rows=("source_row_number", "count"),
            full_unique_participants=("participant_hash_private", "nunique"),
            rows_with_any_identifier=("has_any_identifier", "sum"),
            rows_with_strong_identifier=("has_strong_identifier", "sum"),
        )
        .reset_index()
    )

    event_clean_metrics = (
        event_participation_clean
        .groupby("canonical_event_id", dropna=False)
        .agg(
            clean_unique_participants=("participant_hash_private", "nunique"),
        )
        .reset_index()
    )

    metadata = event_metadata.rename(columns={"event_id": "canonical_event_id"})

    event_metrics = (
        metadata
        .merge(event_full_metrics, on="canonical_event_id", how="left")
        .merge(event_clean_metrics, on="canonical_event_id", how="left")
    )

    numeric_cols = [
        "raw_rows",
        "full_unique_participants",
        "rows_with_any_identifier",
        "rows_with_strong_identifier",
        "clean_unique_participants",
    ]

    for col in numeric_cols:
        event_metrics[col] = event_metrics[col].fillna(0).astype(int)

    event_metrics["strong_identifier_share"] = np.where(
        event_metrics["raw_rows"] > 0,
        event_metrics["rows_with_strong_identifier"] / event_metrics["raw_rows"],
        np.nan,
    )

    event_metrics["clean_coverage_share"] = np.where(
        event_metrics["full_unique_participants"] > 0,
        event_metrics["clean_unique_participants"] / event_metrics["full_unique_participants"],
        np.nan,
    )

    return event_metrics


def add_new_repeat_metrics(
    event_metrics: pd.DataFrame,
    clean_sequence: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add new vs repeat participant metrics to event-level table.
    """
    new_repeat_metrics = (
        clean_sequence
        .groupby("canonical_event_id", dropna=False)
        .agg(
            clean_participants=("participant_hash_private", "nunique"),
            new_participants=("is_first_event", "sum"),
            repeat_participants=("prior_events_cnt", lambda s: (s > 0).sum()),
            avg_prior_events=("prior_events_cnt", "mean"),
        )
        .reset_index()
    )

    new_repeat_metrics["new_share"] = (
        new_repeat_metrics["new_participants"]
        / new_repeat_metrics["clean_participants"]
    ).round(3)

    new_repeat_metrics["repeat_share"] = (
        new_repeat_metrics["repeat_participants"]
        / new_repeat_metrics["clean_participants"]
    ).round(3)

    result = event_metrics.merge(
        new_repeat_metrics,
        on="canonical_event_id",
        how="left",
    )

    for col in ["clean_participants", "new_participants", "repeat_participants"]:
        result[col] = result[col].fillna(0).astype(int)

    for col in ["new_share", "repeat_share", "avg_prior_events"]:
        result[col] = result[col].fillna(0)

    return result


def build_clean_sequence(event_participation_clean: pd.DataFrame) -> pd.DataFrame:
    """
    Build participant-level event sequence.
    """
    required_cols = [
        "participant_hash_private",
        "canonical_event_id",
        "event_name",
        "event_family",
        "event_year",
        "event_order",
    ]

    sequence = event_participation_clean[
        required_cols
    ].dropna(
        subset=["participant_hash_private", "canonical_event_id", "event_order"]
    ).copy()

    sequence = sequence.sort_values(
        ["participant_hash_private", "event_order", "canonical_event_id"]
    )

    sequence["participant_event_rank"] = (
        sequence
        .groupby("participant_hash_private")
        .cumcount()
        + 1
    )

    sequence["is_first_event"] = sequence["participant_event_rank"] == 1
    sequence["prior_events_cnt"] = sequence["participant_event_rank"] - 1

    return sequence


def build_family_metrics(event_metrics: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate event family-level metrics.
    """
    family_metrics = (
        event_metrics
        .groupby("event_family", dropna=False)
        .agg(
            events=("canonical_event_id", "nunique"),
            raw_rows=("raw_rows", "sum"),
            full_unique_participants=("full_unique_participants", "sum"),
            clean_unique_participants=("clean_unique_participants", "sum"),
            clean_participants=("clean_participants", "sum"),
            new_participants=("new_participants", "sum"),
            repeat_participants=("repeat_participants", "sum"),
            avg_strong_identifier_share=("strong_identifier_share", "mean"),
            avg_clean_coverage_share=("clean_coverage_share", "mean"),
        )
        .reset_index()
    )

    family_metrics["new_share"] = np.where(
        family_metrics["clean_participants"] > 0,
        family_metrics["new_participants"] / family_metrics["clean_participants"],
        np.nan,
    ).round(3)

    family_metrics["repeat_share"] = np.where(
        family_metrics["clean_participants"] > 0,
        family_metrics["repeat_participants"] / family_metrics["clean_participants"],
        np.nan,
    ).round(3)

    return family_metrics.sort_values("clean_participants", ascending=False)


def build_depth_distribution(clean_sequence: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate distribution of event depth per participant.
    """
    participant_depth = (
        clean_sequence
        .groupby("participant_hash_private")
        .agg(
            events_cnt=("canonical_event_id", "nunique"),
            first_event=("event_name", "first"),
            first_event_family=("event_family", "first"),
        )
        .reset_index()
    )

    depth_distribution = (
        participant_depth
        .groupby("events_cnt")
        .agg(participants=("participant_hash_private", "nunique"))
        .reset_index()
    )

    depth_distribution["participant_share"] = (
        depth_distribution["participants"]
        / depth_distribution["participants"].sum()
    ).round(3)

    return depth_distribution


def build_event_transitions(clean_sequence: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculate event-to-event and family-to-family transitions.
    """
    journey_df = clean_sequence.sort_values(
        ["participant_hash_private", "event_order"]
    ).copy()

    journey_df["next_event_name"] = (
        journey_df
        .groupby("participant_hash_private")["event_name"]
        .shift(-1)
    )

    journey_df["next_event_family"] = (
        journey_df
        .groupby("participant_hash_private")["event_family"]
        .shift(-1)
    )

    event_transitions = (
        journey_df[journey_df["next_event_name"].notna()]
        .groupby(["event_name", "next_event_name"], dropna=False)
        .agg(participants=("participant_hash_private", "nunique"))
        .reset_index()
        .sort_values("participants", ascending=False)
    )

    family_transitions = (
        journey_df[journey_df["next_event_family"].notna()]
        .groupby(["event_family", "next_event_family"], dropna=False)
        .agg(participants=("participant_hash_private", "nunique"))
        .reset_index()
        .sort_values("participants", ascending=False)
    )

    return event_transitions, family_transitions

