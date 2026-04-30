from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def plot_clean_participants_by_event(
    event_metrics: pd.DataFrame,
    output_path: Path | None = None,
):
    """
    Plot clean participants by event.
    """
    plot_df = event_metrics.sort_values("clean_unique_participants", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(plot_df["event_name"], plot_df["clean_unique_participants"])

    ax.set_title("Clean participants by event")
    ax.set_xlabel("Clean unique participants")
    ax.set_ylabel("Event")

    plt.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=200, bbox_inches="tight")

    return fig, ax


def plot_new_vs_repeat_by_event(
    event_metrics: pd.DataFrame,
    output_path: Path | None = None,
):
    """
    Plot stacked new vs repeat participants by event.
    """
    plot_df = event_metrics.sort_values("event_order").copy()

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(
        plot_df["event_name"],
        plot_df["new_participants"],
        label="New participants",
    )

    ax.bar(
        plot_df["event_name"],
        plot_df["repeat_participants"],
        bottom=plot_df["new_participants"],
        label="Repeat participants",
    )

    ax.set_title("New vs repeat participants by event")
    ax.set_xlabel("Event")
    ax.set_ylabel("Participants")
    ax.tick_params(axis="x", rotation=75)
    ax.legend()

    plt.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=200, bbox_inches="tight")

    return fig, ax


def plot_portfolio_health_matrix(
    event_metrics: pd.DataFrame,
    output_path: Path | None = None,
):
    """
    Scatter plot: new_share vs repeat_share.
    Bubble size represents clean participants.
    """
    plot_df = event_metrics[
        event_metrics["clean_participants"] > 0
    ].copy()

    fig, ax = plt.subplots(figsize=(9, 6))

    sizes = plot_df["clean_participants"].clip(lower=10) * 2

    ax.scatter(
        plot_df["new_share"],
        plot_df["repeat_share"],
        s=sizes,
        alpha=0.7,
    )

    for _, row in plot_df.iterrows():
        ax.annotate(
            row["event_name"],
            (row["new_share"], row["repeat_share"]),
            fontsize=8,
            alpha=0.8,
        )

    ax.set_title("Portfolio health matrix")
    ax.set_xlabel("New participants share")
    ax.set_ylabel("Repeat participants share")

    plt.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=200, bbox_inches="tight")

    return fig, ax


def plot_repeat_depth_distribution(
    depth_distribution: pd.DataFrame,
    output_path: Path | None = None,
):
    """
    Plot distribution of event depth per participant.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(
        depth_distribution["events_cnt"],
        depth_distribution["participants"],
    )

    ax.set_title("Distribution of event depth per participant")
    ax.set_xlabel("Number of events per participant")
    ax.set_ylabel("Participants")

    plt.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=200, bbox_inches="tight")

    return fig, ax

