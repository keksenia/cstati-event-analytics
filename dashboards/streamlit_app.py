from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="cstati Event Analytics",
    page_icon="📊",
    layout="wide",
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed_public"


def load_table(name: str) -> pd.DataFrame:
    parquet_path = DATA_DIR / f"{name}.parquet"
    csv_path = DATA_DIR / f"{name}.csv"

    if parquet_path.exists():
        return pd.read_parquet(parquet_path)

    if csv_path.exists():
        return pd.read_csv(csv_path)

    raise FileNotFoundError(f"Could not find {name}.parquet or {name}.csv")


@st.cache_data
def load_data():
    event_metrics = load_table("metrics_event_level")
    family_metrics = load_table("metrics_family_level")
    event_scorecard = load_table("event_scorecard")

    return event_metrics, family_metrics, event_scorecard


st.title("cstati Event Analytics")
st.caption("Product analytics dashboard for cstati event portfolio")

try:
    event_metrics, family_metrics, event_scorecard = load_data()
except FileNotFoundError as error:
    st.error(str(error))
    st.stop()


st.sidebar.header("Filters")

families = sorted(event_metrics["event_family"].dropna().unique())
selected_families = st.sidebar.multiselect(
    "Event family",
    options=families,
    default=families,
)

filtered_events = event_metrics[
    event_metrics["event_family"].isin(selected_families)
].copy()


st.header("Portfolio overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Events", filtered_events["event_name"].nunique())
col2.metric(
    "Clean participants",
    int(filtered_events["clean_participants"].sum())
    if "clean_participants" in filtered_events.columns
    else int(filtered_events["clean_unique_participants"].sum())
)
col3.metric(
    "New participants",
    int(filtered_events["new_participants"].sum())
    if "new_participants" in filtered_events.columns
    else 0
)
col4.metric(
    "Repeat participants",
    int(filtered_events["repeat_participants"].sum())
    if "repeat_participants" in filtered_events.columns
    else 0
)


st.subheader("Event metrics")

display_cols = [
    "event_name",
    "event_family",
    "event_year",
    "clean_participants",
    "new_participants",
    "repeat_participants",
    "new_share",
    "repeat_share",
    "clean_coverage_share",
]

existing_cols = [col for col in display_cols if col in filtered_events.columns]

st.dataframe(
    filtered_events[existing_cols].sort_values(
        "clean_participants",
        ascending=False,
    ),
    use_container_width=True,
)


st.subheader("Clean participants by event")

chart_df = (
    filtered_events[["event_name", "clean_participants"]]
    .dropna()
    .sort_values("clean_participants", ascending=False)
    .set_index("event_name")
)

st.bar_chart(chart_df)


st.subheader("Family metrics")

st.dataframe(
    family_metrics.sort_values("clean_participants", ascending=False),
    use_container_width=True,
)


st.subheader("Event scorecard")

scorecard_cols = [
    "event_name",
    "event_family",
    "strategic_role",
    "clean_participants",
    "new_share",
    "repeat_share",
    "portfolio_score",
]

existing_scorecard_cols = [
    col for col in scorecard_cols
    if col in event_scorecard.columns
]

st.dataframe(
    event_scorecard[existing_scorecard_cols].sort_values(
        "portfolio_score",
        ascending=False,
    ),
    use_container_width=True,
)


st.markdown(
    """
    ### Notes

    This dashboard uses only aggregated public outputs from `data/processed_public/`.
    Raw personal data and private identity tables are not used here.
    """
)
