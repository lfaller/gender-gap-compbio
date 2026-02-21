"""
Visualization utilities for publication-ready figures.

Generates figures matching the style of the original Bonham & Stefan (2017) paper.
"""

from typing import Dict, List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px


# Set default plotting style
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams["figure.dpi"] = 100
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.size"] = 12


def plot_pfemale_by_position(
    df: pd.DataFrame,
    group_col: str = "dataset",
    output_path: str = None,
    figsize: tuple = (10, 6)
):
    """
    Bar plot of P_female by author position.

    Args:
        df: DataFrame with columns: position, mean, ci_lower, ci_upper, dataset
        group_col: Column to group by (e.g., 'dataset' for Biology vs. Comp Bio)
        output_path: Path to save figure (optional)
        figsize: Figure size (width, height)
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Get unique positions in order
    position_order = ["first", "second", "other", "penultimate", "last"]
    positions = [p for p in position_order if p in df["position"].unique()]

    # Get unique groups
    groups = df[group_col].unique()
    x_pos = np.arange(len(positions))
    width = 0.35

    # Plot bars for each group
    for i, group in enumerate(groups):
        group_df = df[df[group_col] == group].set_index("position")
        means = [group_df.loc[p, "mean"] if p in group_df.index else None for p in positions]
        ci_lower = [group_df.loc[p, "ci_lower"] if p in group_df.index else None for p in positions]
        ci_upper = [group_df.loc[p, "ci_upper"] if p in group_df.index else None for p in positions]

        # Calculate error bars
        errors = [
            [m - l if m and l else 0 for m, l in zip(means, ci_lower)],
            [u - m if u and m else 0 for u, m in zip(ci_upper, means)]
        ]

        ax.bar(
            x_pos + i * width,
            means,
            width,
            label=group,
            yerr=errors,
            capsize=5,
            error_kw={"elinewidth": 1}
        )

    ax.set_xlabel("Author Position", fontsize=12, fontweight="bold")
    ax.set_ylabel("P(Female)", fontsize=12, fontweight="bold")
    ax.set_ylim([0, 1])
    ax.set_xticks(x_pos + width / 2)
    ax.set_xticklabels(positions)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"Saved figure to {output_path}")

    return fig, ax


def plot_pfemale_over_time(
    df: pd.DataFrame,
    group_col: str = "dataset",
    output_path: str = None,
    figsize: tuple = (12, 6)
):
    """
    Line plot of P_female over time.

    Args:
        df: DataFrame with columns: year, mean, ci_lower, ci_upper, dataset
        group_col: Column to group by (e.g., 'dataset' for Biology vs. Comp Bio)
        output_path: Path to save figure (optional)
        figsize: Figure size (width, height)
    """
    fig, ax = plt.subplots(figsize=figsize)

    for group in df[group_col].unique():
        group_df = df[df[group_col] == group].sort_values("year")

        ax.plot(
            group_df["year"],
            group_df["mean"],
            marker="o",
            label=group,
            linewidth=2,
            markersize=6
        )

        # Shade confidence interval
        ax.fill_between(
            group_df["year"],
            group_df["ci_lower"],
            group_df["ci_upper"],
            alpha=0.2
        )

    ax.set_xlabel("Year", fontsize=12, fontweight="bold")
    ax.set_ylabel("P(Female)", fontsize=12, fontweight="bold")
    ax.set_ylim([0, 1])
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"Saved figure to {output_path}")

    return fig, ax


def plot_female_pi_effect(
    df: pd.DataFrame,
    output_path: str = None,
    figsize: tuple = (10, 6)
):
    """
    Bar plot comparing P_female by position for male vs. female last authors.

    Args:
        df: DataFrame with columns: position, mean, ci_lower, ci_upper, last_author_gender
        output_path: Path to save figure (optional)
        figsize: Figure size (width, height)
    """
    fig, ax = plt.subplots(figsize=figsize)

    position_order = ["first", "second", "other", "penultimate", "last"]
    positions = [p for p in position_order if p in df["position"].unique()]

    x_pos = np.arange(len(positions))
    width = 0.35

    for i, gender in enumerate(["Male", "Female"]):
        gender_df = df[df["last_author_gender"] == gender].set_index("position")
        means = [gender_df.loc[p, "mean"] if p in gender_df.index else None for p in positions]
        ci_lower = [gender_df.loc[p, "ci_lower"] if p in gender_df.index else None for p in positions]
        ci_upper = [gender_df.loc[p, "ci_upper"] if p in gender_df.index else None for p in positions]

        errors = [
            [m - l if m and l else 0 for m, l in zip(means, ci_lower)],
            [u - m if u and m else 0 for u, m in zip(ci_upper, means)]
        ]

        ax.bar(
            x_pos + i * width,
            means,
            width,
            label=f"{gender} Last Author",
            yerr=errors,
            capsize=5,
            error_kw={"elinewidth": 1}
        )

    ax.set_xlabel("Author Position", fontsize=12, fontweight="bold")
    ax.set_ylabel("P(Female)", fontsize=12, fontweight="bold")
    ax.set_ylim([0, 1])
    ax.set_xticks(x_pos + width / 2)
    ax.set_xticklabels(positions)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"Saved figure to {output_path}")

    return fig, ax


def plot_interactive_temporal_trend(
    df: pd.DataFrame,
    group_col: str = "dataset",
    output_path: str = None
) -> go.Figure:
    """
    Interactive Plotly line plot of P_female over time.

    Args:
        df: DataFrame with columns: year, mean, ci_lower, ci_upper, dataset
        group_col: Column to group by
        output_path: Path to save HTML (optional)

    Returns:
        Plotly Figure object
    """
    fig = px.line(
        df,
        x="year",
        y="mean",
        color=group_col,
        markers=True,
        title="Female Representation in Authorship Over Time",
        labels={"year": "Year", "mean": "P(Female)", group_col: "Dataset"}
    )

    fig.update_yaxes(range=[0, 1])
    fig.update_layout(hovermode="x unified")

    if output_path:
        fig.write_html(output_path)
        print(f"Saved interactive figure to {output_path}")

    return fig


def plot_pfemale_by_journal_quartile(
    df: pd.DataFrame,
    output_path: str = None,
    figsize: tuple = (12, 6)
):
    """
    Bar plot of P_female by author position, grouped by journal quartile.

    Args:
        df: DataFrame with columns: quartile, position, mean, ci_lower, ci_upper
        output_path: Path to save figure (optional)
        figsize: Figure size (width, height)
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Define order for quartiles (Q1 = highest impact)
    quartile_order = ["Q1", "Q2", "Q3", "Q4"]
    position_order = ["first", "second", "other", "penultimate", "last"]

    # Filter to rows with valid positions
    positions = [p for p in position_order if p in df["position"].unique()]

    # Set up x-axis positions
    x_pos = np.arange(len(positions))
    width = 0.2  # Width for each bar

    # Plot bars for each quartile
    for i, quartile in enumerate(quartile_order):
        quartile_df = df[df["quartile"] == quartile].set_index("position")
        means = [quartile_df.loc[p, "mean"] if p in quartile_df.index else None for p in positions]
        ci_lower = [quartile_df.loc[p, "ci_lower"] if p in quartile_df.index else None for p in positions]
        ci_upper = [quartile_df.loc[p, "ci_upper"] if p in quartile_df.index else None for p in positions]

        # Calculate error bars
        errors = [
            [m - l if m and l else 0 for m, l in zip(means, ci_lower)],
            [u - m if u and m else 0 for u, m in zip(ci_upper, means)]
        ]

        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
        ax.bar(
            x_pos + i * width,
            means,
            width,
            label=quartile,
            yerr=errors,
            capsize=5,
            color=colors[i],
            alpha=0.8,
            error_kw={"elinewidth": 1}
        )

        # Add value labels on top of bars
        for j, (x, mean) in enumerate(zip(x_pos + i * width, means)):
            if mean is not None:
                label_text = f"{mean*100:.1f}%"
                ax.text(
                    x, mean + 0.02,
                    label_text,
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    fontweight="bold"
                )

    # Add reference line at 50% parity
    ax.axhline(y=0.5, color="red", linestyle="--", linewidth=1.5, alpha=0.7, label="50% parity")

    ax.set_xlabel("Author Position", fontsize=12, fontweight="bold")
    ax.set_ylabel("P(Female)", fontsize=12, fontweight="bold")
    ax.set_title("Female Representation by Journal Impact Quartile", fontsize=13, fontweight="bold")
    ax.set_ylim([0, 1])
    ax.set_xticks(x_pos + width * 1.5)
    ax.set_xticklabels(positions)
    ax.legend(title="Journal\nQuartile", loc="upper left")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"Saved figure to {output_path}")

    return fig, ax


def plot_journal_quartile_distribution(
    df: pd.DataFrame,
    position: str = "first",
    output_path: str = None,
    figsize: tuple = (10, 6)
):
    """
    Stacked bar chart showing distribution of journal quartiles by author gender.

    Args:
        df: DataFrame with columns: position, gender, quartile
        position: Author position to analyze (default: 'first')
        output_path: Path to save figure (optional)
        figsize: Figure size (width, height)
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Filter to specified position
    position_df = df[df["position"] == position].copy()

    # Get counts by gender and quartile
    quartile_order = ["Q1", "Q2", "Q3", "Q4"]
    genders = ["female", "male"]

    # Calculate distribution
    distributions = {}
    totals = {}

    for gender in genders:
        gender_df = position_df[position_df["gender"] == gender]
        totals[gender] = len(gender_df)

        counts = {}
        for q in quartile_order:
            counts[q] = len(gender_df[gender_df["quartile"] == q])

        # Convert to percentages
        distributions[gender] = {q: (counts[q] / totals[gender] * 100) if totals[gender] > 0 else 0
                                 for q in quartile_order}

    # Create stacked bar chart
    x_pos = np.arange(len(genders))
    width = 0.5
    bottom = np.zeros(len(genders))

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    for i, q in enumerate(quartile_order):
        values = [distributions[g][q] for g in genders]
        ax.bar(x_pos, values, width, label=q, bottom=bottom, color=colors[i], alpha=0.8)

        # Add value labels in the center of each stacked segment
        for j, (x, val, b) in enumerate(zip(x_pos, values, bottom)):
            if val > 3:  # Only show label if segment is large enough
                ax.text(
                    x, b + val / 2,
                    f"{val:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=9,
                    fontweight="bold",
                    color="white"
                )

        bottom += np.array(values)

    # Customize plot
    ax.set_ylabel("Percentage of Papers (%)", fontsize=12, fontweight="bold")
    ax.set_title(f"Journal Impact Distribution by Author Gender ({position.capitalize()} Author Position)",
                 fontsize=13, fontweight="bold")
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f"{g.capitalize()}\n(n={totals[g]})" for g in genders])
    ax.legend(title="Journal\nQuartile", loc="upper right")
    ax.set_ylim([0, 100])
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"Saved figure to {output_path}")

    return fig, ax
