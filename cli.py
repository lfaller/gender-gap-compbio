#!/usr/bin/env python3
"""
Gender Gap in Computational Biology: CLI Tool

A flexible command-line interface for the analysis pipeline with support for
custom date ranges and step-by-step execution.

Usage:
    # Run full pipeline (2015-2025)
    python cli.py run

    # Fetch only 2025 data and append to existing
    python cli.py fetch --start-year 2025 --end-year 2025 --append

    # Run gender inference
    python cli.py infer

    # Run analysis and figures
    python cli.py analyze
    python cli.py figures

    # Chain multiple steps
    python cli.py fetch infer analyze figures --start-year 2025

    # Get help on any command
    python cli.py fetch --help
"""

import os
import sys
import click
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Import pipeline modules
from src.pubmed_fetcher import PubMedFetcher
from src.gender_utils import assign_positions
from src.db_utils import GenderDatabase
from src.bootstrap import bootstrap_by_multiple_groups, bootstrap_pfemale
from src.plotting import (
    plot_pfemale_by_position,
    plot_pfemale_over_time,
    plot_interactive_temporal_trend,
)
import matplotlib.pyplot as plt

load_dotenv()


def add_author_positions(papers):
    """Add author position information to papers."""
    for paper in papers:
        authors = paper.get("authors", [])
        paper["positions"] = assign_positions(authors)
    return papers


@click.group()
def cli():
    """Gender Gap in Computational Biology: Analysis Pipeline CLI"""
    pass


@cli.command()
@click.option(
    "--start-year",
    default=2015,
    type=int,
    help="Start year for PubMed data fetch (default: 2015)",
)
@click.option(
    "--end-year",
    default=2025,
    type=int,
    help="End year for PubMed data fetch (default: 2025)",
)
@click.option(
    "--append",
    is_flag=True,
    help="Append to existing CSV files instead of overwriting",
)
def fetch(start_year, end_year, append):
    """Fetch PubMed data for Biology and Computational Biology."""
    print("=" * 70)
    print(f"FETCHING PUBMED DATA ({start_year}-{end_year})")
    print("=" * 70)

    # Setup
    Path("data/processed").mkdir(parents=True, exist_ok=True)

    email = os.getenv("NCBI_EMAIL")
    if not email:
        raise click.ClickException("NCBI_EMAIL not set in .env file")

    fetcher = PubMedFetcher(email=email)
    print(f"\nEmail: {email}")
    print(f"API key: {'✓ Yes' if fetcher.api_key else '⚠ No (limited to 3 req/sec)'}\n")

    # Fetch Biology papers
    print("=" * 70)
    print(f"Fetching Biology papers ({start_year}-{end_year})...")
    print("=" * 70)
    bio_pmids = fetcher.search_biology(start_year=start_year, end_year=end_year)
    print(f"Fetched {len(bio_pmids)} Biology PMIDs\n")

    print("Fetching Biology paper details...")
    bio_papers = fetcher.fetch_paper_details(bio_pmids, batch_size=500)
    bio_papers = add_author_positions(bio_papers)
    bio_df = pd.DataFrame(bio_papers)
    bio_df["dataset"] = "Biology"

    # Handle append mode
    bio_file = "data/processed/pubmed_biology_2015_2025.csv"
    if append and Path(bio_file).exists():
        print(f"Loading existing Biology data...")
        existing_bio = pd.read_csv(bio_file)
        print(f"  Existing: {len(existing_bio)} papers")
        print(f"  New: {len(bio_df)} papers")
        bio_df = pd.concat([existing_bio, bio_df], ignore_index=True)
        print(f"  Combined: {len(bio_df)} papers")

    bio_df.to_csv(bio_file, index=False)
    print(f"✓ Saved {len(bio_df)} Biology papers\n")

    # Fetch Computational Biology papers
    print("=" * 70)
    print(f"Fetching Computational Biology papers ({start_year}-{end_year})...")
    print("=" * 70)
    comp_pmids = fetcher.search_computational_biology(start_year=start_year, end_year=end_year)
    print(f"Fetched {len(comp_pmids)} Computational Biology PMIDs\n")

    print("Fetching Computational Biology paper details...")
    comp_papers = fetcher.fetch_paper_details(comp_pmids, batch_size=500)
    comp_papers = add_author_positions(comp_papers)
    comp_df = pd.DataFrame(comp_papers)
    comp_df["dataset"] = "Computational Biology"

    # Handle append mode
    comp_file = "data/processed/pubmed_compbio_2015_2025.csv"
    if append and Path(comp_file).exists():
        print(f"Loading existing Computational Biology data...")
        existing_comp = pd.read_csv(comp_file)
        print(f"  Existing: {len(existing_comp)} papers")
        print(f"  New: {len(comp_df)} papers")
        comp_df = pd.concat([existing_comp, comp_df], ignore_index=True)
        print(f"  Combined: {len(comp_df)} papers")

    comp_df.to_csv(comp_file, index=False)
    print(f"✓ Saved {len(comp_df)} Computational Biology papers\n")

    print("=" * 70)
    print("✓ FETCH COMPLETE!")
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  Biology:               {len(bio_df):,} papers")
    print(f"  Computational Biology: {len(comp_df):,} papers")
    print(f"  Total:                 {len(bio_df) + len(comp_df):,} papers")


@cli.command()
def infer():
    """Run gender inference on PubMed data (populates SQLite database)."""
    print("=" * 70)
    print("GENDER INFERENCE WITH SQLITE DATABASE")
    print("=" * 70)
    print("\nTo run gender inference, execute:")
    print("  python run_gender_inference_db.py")
    print("\nThis will:")
    print("  1. Load paper data from CSV files")
    print("  2. Identify unique authors")
    print("  3. Infer gender for each author")
    print("  4. Populate SQLite database at data/gender_data.db")


@cli.command()
def analyze():
    """Run statistical analysis on gender-inferred data."""
    print("=" * 70)
    print("STATISTICAL ANALYSIS")
    print("=" * 70)

    # Load data from SQLite database
    db_path = Path("data/gender_data.db")
    if not db_path.exists():
        raise click.ClickException(
            "Database not found at data/gender_data.db\n"
            "Please run: python run_gender_inference_db.py"
        )

    db = GenderDatabase(db_path="data/gender_data.db")
    pubmed_df = db.get_author_data_as_dataframe()
    db.close()

    # Filter PubMed data (2015-2025)
    pubmed_2015_2025 = pubmed_df[
        (pubmed_df["year"] >= 2015) & (pubmed_df["year"] <= 2025)
    ]

    # Analysis 1: Position breakdown
    print("\nAnalysis 1: P_female by Author Position...")
    position_results = bootstrap_by_multiple_groups(
        pubmed_2015_2025,
        group_cols=["dataset", "position"],
        prob_col="p_female",
        n_iterations=1000,
    )
    position_results.to_csv("data/processed/analysis_position_breakdown.csv", index=False)
    print(position_results.to_string())
    print()

    # Analysis 2: Temporal trends
    print("Analysis 2: Temporal Trends (P_female over time)...")
    temporal_results = bootstrap_by_multiple_groups(
        pubmed_2015_2025,
        group_cols=["dataset", "year"],
        prob_col="p_female",
        n_iterations=1000,
    )
    temporal_results.to_csv("data/processed/analysis_temporal_trend.csv", index=False)
    print(f"✓ {len(temporal_results)} year-dataset combinations analyzed\n")

    # Analysis 3: COVID-19 impact
    print("Analysis 3: COVID-19 Impact Analysis...")
    periods = {
        "Pre-COVID (2018-2019)": (2018, 2019),
        "Pandemic (2020-2021)": (2020, 2021),
        "Recovery (2022-2025)": (2022, 2025),
    }

    covid_results = []
    for period_name, (start_year, end_year) in periods.items():
        period_df = pubmed_2015_2025[
            (pubmed_2015_2025["year"] >= start_year)
            & (pubmed_2015_2025["year"] <= end_year)
        ]
        mean, ci_lower, ci_upper = bootstrap_pfemale(period_df["p_female"].tolist())
        covid_results.append(
            {
                "period": period_name,
                "mean": mean,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "n": len(period_df),
            }
        )

    covid_df = pd.DataFrame(covid_results)
    covid_df.to_csv("data/processed/analysis_covid_impact.csv", index=False)
    print(covid_df.to_string())
    print()

    print("=" * 70)
    print("✓ ANALYSIS COMPLETE!")
    print("=" * 70)


@cli.command()
def figures():
    """Generate publication-ready figures from analysis results."""
    print("=" * 70)
    print("GENERATING FIGURES")
    print("=" * 70)

    output_dir = "outputs/figures"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Load analysis results
    try:
        position_results = pd.read_csv("data/processed/analysis_position_breakdown.csv")
        temporal_results = pd.read_csv("data/processed/analysis_temporal_trend.csv")
        covid_df = pd.read_csv("data/processed/analysis_covid_impact.csv")
    except FileNotFoundError as e:
        raise click.ClickException(f"Missing analysis results: {e}\nRun 'python cli.py analyze' first")

    # Figure 1: Position breakdown
    print("\nGenerating Figure 1: Position breakdown...")
    fig, ax = plot_pfemale_by_position(
        position_results,
        group_col="dataset",
        output_path=f"{output_dir}/fig1_position_breakdown.png",
        figsize=(10, 6),
    )
    plt.savefig(
        f"{output_dir}/fig1_position_breakdown.svg",
        dpi=300,
        bbox_inches="tight",
        format="svg",
    )
    plt.close()
    print("✓ Saved Figure 1\n")

    # Figure 2: Temporal trend
    print("Generating Figure 2: Temporal trend...")
    fig, ax = plot_pfemale_over_time(
        temporal_results,
        group_col="dataset",
        output_path=f"{output_dir}/fig2_temporal_trend.png",
        figsize=(12, 6),
    )
    plt.savefig(
        f"{output_dir}/fig2_temporal_trend.svg",
        dpi=300,
        bbox_inches="tight",
        format="svg",
    )
    plt.close()
    print("✓ Saved Figure 2\n")

    # Figure 3: COVID-19 impact
    print("Generating Figure 3: COVID-19 impact...")
    fig, ax = plt.subplots(figsize=(10, 6))
    periods = covid_df["period"].tolist()
    means = covid_df["mean"].tolist()
    ci_lower = covid_df["ci_lower"].tolist()
    ci_upper = covid_df["ci_upper"].tolist()

    x_pos = range(len(periods))
    errors = [
        [m - l for m, l in zip(means, ci_lower)],
        [u - m for u, m in zip(ci_upper, means)],
    ]

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    ax.bar(x_pos, means, yerr=errors, capsize=5, color=colors, alpha=0.8)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(periods, fontsize=11)
    ax.set_ylabel("P(Female)", fontsize=12, fontweight="bold")
    ax.set_ylim([0, 1])
    ax.set_title("Female Authorship: COVID-19 Impact", fontsize=13, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/fig3_covid_impact.png", dpi=300, bbox_inches="tight")
    plt.savefig(
        f"{output_dir}/fig3_covid_impact.svg",
        dpi=300,
        bbox_inches="tight",
        format="svg",
    )
    plt.close()
    print("✓ Saved Figure 3\n")

    # Figure 4: Interactive temporal trend
    print("Generating Figure 4: Interactive temporal trend...")
    fig = plot_interactive_temporal_trend(
        temporal_results,
        group_col="dataset",
        output_path=f"{output_dir}/fig4_interactive_temporal_trend.html",
    )
    print("✓ Saved Figure 4\n")

    print("=" * 70)
    print("✓ FIGURES COMPLETE!")
    print("=" * 70)
    print(f"\nAll figures saved to: {output_dir}/")


@cli.command()
@click.option(
    "--start-year",
    default=2015,
    type=int,
    help="Start year for analysis (default: 2015)",
)
@click.option(
    "--end-year",
    default=2025,
    type=int,
    help="End year for analysis (default: 2025)",
)
def run(start_year, end_year):
    """Run the complete pipeline: fetch → infer → analyze → figures."""
    print("\n" + "=" * 70)
    print("GENDER GAP IN COMPUTATIONAL BIOLOGY: FULL PIPELINE")
    print("=" * 70)

    # Step 1: Fetch
    print("\n[STEP 1/4] Fetching PubMed data...")
    try:
        fetch.callback(start_year=start_year, end_year=end_year, append=False)
    except Exception as e:
        click.echo(f"Error during fetch: {e}", err=True)
        sys.exit(1)

    # Step 2: Infer
    print("\n[STEP 2/4] Gender inference...")
    print("Next, run: python run_gender_inference_db.py")
    print("Then return to run steps 3 and 4")
    sys.exit(0)

    # Step 3: Analyze (after inference completes)
    print("\n[STEP 3/4] Statistical analysis...")
    try:
        analyze.callback()
    except Exception as e:
        click.echo(f"Error during analysis: {e}", err=True)
        sys.exit(1)

    # Step 4: Figures
    print("\n[STEP 4/4] Generating figures...")
    try:
        figures.callback()
    except Exception as e:
        click.echo(f"Error during figure generation: {e}", err=True)
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✓ PIPELINE COMPLETE!")
    print("=" * 70)
    print("\nResults saved to:")
    print("  data/processed/         - CSV files with analysis results")
    print("  outputs/figures/        - Publication-ready figures")
    print("  data/gender_cache.json  - Cached gender lookups")


if __name__ == "__main__":
    cli()
