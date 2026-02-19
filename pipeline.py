#!/usr/bin/env python3
"""
Gender Gap in Computational Biology: Full Analysis Pipeline

This script runs the complete analysis pipeline:
1. Fetch PubMed data (Biology and Computational Biology)
2. Fetch arXiv data (q-bio and cs)
3. Infer gender from author names
4. Run bootstrap statistical analysis
5. Generate publication-ready figures

Usage:
    python pipeline.py                    # Run full pipeline
    python pipeline.py --skip-fetch       # Skip data fetching (use cached data)
    python pipeline.py --help             # Show options
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Import pipeline modules
from src.pubmed_fetcher import PubMedFetcher
from src.arxiv_fetcher import arXivFetcher
from src.gender_utils import GenderInference, assign_positions
from src.bootstrap import bootstrap_by_multiple_groups, bootstrap_pfemale
from src.plotting import (
    plot_pfemale_by_position,
    plot_pfemale_over_time,
    plot_interactive_temporal_trend,
)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Load environment variables
load_dotenv()


def setup_directories():
    """Create necessary directories."""
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)
    print("✓ Directories ready")


def step1_fetch_pubmed(skip_fetch=False):
    """Step 1: Fetch PubMed data."""
    print("\n" + "="*70)
    print("STEP 1: Fetching PubMed Data (Biology & Computational Biology)")
    print("="*70)

    if skip_fetch:
        print("⊘ Skipping fetch (using cached data)...")
        bio_df = pd.read_csv("data/processed/pubmed_biology_2015_2024.csv")
        comp_df = pd.read_csv("data/processed/pubmed_compbio_2015_2024.csv")
        return bio_df, comp_df

    email = os.getenv("NCBI_EMAIL")
    if not email:
        raise ValueError("NCBI_EMAIL not set in .env file")

    fetcher = PubMedFetcher(email=email)
    print(f"Email: {email}")
    print(f"API key: {'✓ Yes' if fetcher.api_key else '⚠ No (limited to 3 req/sec)'}\n")

    # Fetch Biology papers
    print("Fetching Biology papers...")
    bio_pmids = fetcher.search_biology(start_year=2015, end_year=2024)
    print(f"Fetched {len(bio_pmids)} Biology PMIDs\n")

    print("Fetching Biology paper details...")
    bio_papers = fetcher.fetch_paper_details(bio_pmids, batch_size=500)
    bio_papers = add_author_positions(bio_papers)
    bio_df = pd.DataFrame(bio_papers)
    bio_df["dataset"] = "Biology"
    bio_df.to_csv("data/processed/pubmed_biology_2015_2024.csv", index=False)
    print(f"✓ Saved {len(bio_df)} Biology papers\n")

    # Fetch Computational Biology papers
    print("Fetching Computational Biology papers...")
    comp_pmids = fetcher.search_computational_biology(start_year=2015, end_year=2024)
    print(f"Fetched {len(comp_pmids)} Computational Biology PMIDs\n")

    print("Fetching Computational Biology paper details...")
    comp_papers = fetcher.fetch_paper_details(comp_pmids, batch_size=500)
    comp_papers = add_author_positions(comp_papers)
    comp_df = pd.DataFrame(comp_papers)
    comp_df["dataset"] = "Computational Biology"
    comp_df.to_csv("data/processed/pubmed_compbio_2015_2024.csv", index=False)
    print(f"✓ Saved {len(comp_df)} Computational Biology papers\n")

    return bio_df, comp_df


def step2_fetch_arxiv(skip_fetch=False):
    """Step 2: Fetch arXiv data."""
    print("\n" + "="*70)
    print("STEP 2: Fetching arXiv Data (q-bio & cs)")
    print("="*70)

    if skip_fetch:
        print("⊘ Skipping fetch (using cached data)...")
        qbio_df = pd.read_csv("data/processed/arxiv_qbio_2015_2024.csv")
        cs_df = pd.read_csv("data/processed/arxiv_cs_2015_2024.csv")
        return qbio_df, cs_df

    fetcher = arXivFetcher(delay_seconds=3.0)

    # Fetch q-bio preprints
    print("Fetching quantitative biology (q-bio) preprints...")
    qbio_preprints = fetcher.fetch_quantitative_biology(start_year=2015, end_year=2024)
    qbio_preprints = add_author_positions(qbio_preprints)
    qbio_df = pd.DataFrame(qbio_preprints)
    qbio_df["dataset"] = "q-bio"
    qbio_df.to_csv("data/processed/arxiv_qbio_2015_2024.csv", index=False)
    print(f"✓ Saved {len(qbio_df)} q-bio preprints\n")

    # Fetch cs preprints
    print("Fetching computer science (cs) preprints...")
    cs_preprints = fetcher.fetch_computer_science(start_year=2015, end_year=2024)
    cs_preprints = add_author_positions(cs_preprints)
    cs_df = pd.DataFrame(cs_preprints)
    cs_df["dataset"] = "cs"
    cs_df.to_csv("data/processed/arxiv_cs_2015_2024.csv", index=False)
    print(f"✓ Saved {len(cs_df)} cs preprints\n")

    return qbio_df, cs_df


def step3_gender_inference():
    """Step 3: Infer gender from author names."""
    print("\n" + "="*70)
    print("STEP 3: Gender Inference")
    print("="*70)

    gi = GenderInference(cache_path="data/gender_cache.json")
    print(f"Loaded cache with {len(gi.cache)} entries\n")

    # Load all datasets
    bio_df = pd.read_csv("data/processed/pubmed_biology_2015_2024.csv")
    comp_df = pd.read_csv("data/processed/pubmed_compbio_2015_2024.csv")
    qbio_df = pd.read_csv("data/processed/arxiv_qbio_2015_2024.csv")
    cs_df = pd.read_csv("data/processed/arxiv_cs_2015_2024.csv")

    pubmed_df = pd.concat([bio_df, comp_df], ignore_index=True)
    arxiv_df = pd.concat([qbio_df, cs_df], ignore_index=True)

    # Expand to author-position level and infer gender
    print("Processing PubMed authors...")
    pubmed_author_df = expand_author_positions(pubmed_df)
    pubmed_author_df = infer_gender_batch(gi, pubmed_author_df)
    pubmed_author_df.to_csv("data/processed/pubmed_authors_with_gender.csv", index=False)
    print(f"✓ Processed {len(pubmed_author_df)} PubMed author records\n")

    print("Processing arXiv authors...")
    arxiv_author_df = expand_author_positions(arxiv_df)
    arxiv_author_df = infer_gender_batch(gi, arxiv_author_df)
    arxiv_author_df.to_csv("data/processed/arxiv_authors_with_gender.csv", index=False)
    print(f"✓ Processed {len(arxiv_author_df)} arXiv author records\n")

    # Save cache
    print(f"Saving gender cache ({len(gi.cache)} entries)...")
    gi.save_cache()
    print("✓ Cache saved\n")

    return pubmed_author_df, arxiv_author_df


def step4_analysis():
    """Step 4: Run bootstrap statistical analysis."""
    print("\n" + "="*70)
    print("STEP 4: Statistical Analysis")
    print("="*70)

    pubmed_df = pd.read_csv("data/processed/pubmed_authors_with_gender.csv")
    arxiv_df = pd.read_csv("data/processed/arxiv_authors_with_gender.csv")

    # Filter PubMed data (2015-2024)
    pubmed_2015_2024 = pubmed_df[
        (pubmed_df["year"] >= 2015) & (pubmed_df["year"] <= 2024)
    ]

    # Analysis 1: Position breakdown
    print("Analysis 1: P_female by Author Position...")
    position_results = bootstrap_by_multiple_groups(
        pubmed_2015_2024,
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
        pubmed_2015_2024,
        group_cols=["dataset", "year"],
        prob_col="p_female",
        n_iterations=1000,
    )
    temporal_results.to_csv("data/processed/analysis_temporal_trend.csv", index=False)
    print(f"✓ {len(temporal_results)} year-dataset combinations analyzed\n")

    # Analysis 3: arXiv comparison
    print("Analysis 3: arXiv Comparison (q-bio vs. cs)...")
    arxiv_position_results = bootstrap_by_multiple_groups(
        arxiv_df,
        group_cols=["dataset", "position"],
        prob_col="p_female",
        n_iterations=1000,
    )
    arxiv_position_results.to_csv(
        "data/processed/analysis_arxiv_position.csv", index=False
    )
    print(arxiv_position_results.to_string())
    print()

    # Analysis 4: COVID-19 impact
    print("Analysis 4: COVID-19 Impact Analysis...")
    periods = {
        "Pre-COVID (2018-2019)": (2018, 2019),
        "Pandemic (2020-2021)": (2020, 2021),
        "Recovery (2022-2023)": (2022, 2023),
    }

    covid_results = []
    for period_name, (start_year, end_year) in periods.items():
        period_df = pubmed_2015_2024[
            (pubmed_2015_2024["year"] >= start_year)
            & (pubmed_2015_2024["year"] <= end_year)
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

    return position_results, temporal_results, arxiv_position_results, covid_df


def step5_figures(position_results, temporal_results, arxiv_position_results, covid_df):
    """Step 5: Generate publication-ready figures."""
    print("\n" + "="*70)
    print("STEP 5: Generating Figures")
    print("="*70)

    output_dir = "outputs/figures"

    # Figure 1: Position breakdown
    print("Generating Figure 1: Position breakdown...")
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

    # Figure 3: arXiv comparison
    print("Generating Figure 3: arXiv comparison...")
    fig, ax = plot_pfemale_by_position(
        arxiv_position_results,
        group_col="dataset",
        output_path=f"{output_dir}/fig4_arxiv_comparison.png",
        figsize=(10, 6),
    )
    plt.savefig(
        f"{output_dir}/fig4_arxiv_comparison.svg",
        dpi=300,
        bbox_inches="tight",
        format="svg",
    )
    plt.close()
    print("✓ Saved Figure 3\n")

    # Figure 4: COVID-19 impact
    print("Generating Figure 4: COVID-19 impact...")
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
    plt.savefig(f"{output_dir}/fig5_covid_impact.png", dpi=300, bbox_inches="tight")
    plt.savefig(
        f"{output_dir}/fig5_covid_impact.svg",
        dpi=300,
        bbox_inches="tight",
        format="svg",
    )
    plt.close()
    print("✓ Saved Figure 4\n")

    # Figure 5: Interactive temporal trend
    print("Generating interactive figure...")
    fig = plot_interactive_temporal_trend(
        temporal_results,
        group_col="dataset",
        output_path=f"{output_dir}/interactive_temporal_trend.html",
    )
    print("✓ Saved interactive figure\n")

    print(f"✓ All figures saved to {output_dir}/")


def add_author_positions(papers):
    """Add author position information to papers."""
    for paper in papers:
        authors = paper.get("authors", [])
        paper["positions"] = assign_positions(authors)
    return papers


def expand_author_positions(df):
    """Convert from paper-level to author-position-level."""
    rows = []
    for idx, row in df.iterrows():
        positions = (
            eval(row["positions"])
            if isinstance(row["positions"], str)
            else row["positions"]
        )
        for author, position in positions:
            rows.append(
                {
                    "pmid": row.get("pmid") or row.get("arxiv_id"),
                    "year": row["year"],
                    "dataset": row["dataset"],
                    "author": author,
                    "position": position,
                }
            )
    return pd.DataFrame(rows)


def infer_gender_batch(gi, df):
    """Infer gender for all authors in dataframe."""
    from tqdm import tqdm

    unique_authors = df["author"].unique()
    author_to_gender = {}

    print(f"Inferring gender for {len(unique_authors)} unique authors...")
    for author in tqdm(unique_authors, desc="Gender inference"):
        first_name = author.split()[0] if author else ""
        result = gi.infer_gender(first_name)
        author_to_gender[author] = result

    df["p_female"] = df["author"].map(lambda x: author_to_gender[x]["probability"])
    df["gender"] = df["author"].map(lambda x: author_to_gender[x]["gender"])
    df["source"] = df["author"].map(lambda x: author_to_gender[x]["source"])

    return df


def main():
    """Run the full pipeline."""
    parser = argparse.ArgumentParser(
        description="Gender Gap in Computational Biology: Full Pipeline"
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Skip data fetching (use cached data)",
    )
    args = parser.parse_args()

    print("\n" + "="*70)
    print("GENDER GAP IN COMPUTATIONAL BIOLOGY: FULL ANALYSIS PIPELINE")
    print("="*70)

    try:
        setup_directories()

        # Step 1: Fetch PubMed
        bio_df, comp_df = step1_fetch_pubmed(skip_fetch=args.skip_fetch)

        # Step 2: Fetch arXiv
        qbio_df, cs_df = step2_fetch_arxiv(skip_fetch=args.skip_fetch)

        # Step 3: Gender inference
        pubmed_author_df, arxiv_author_df = step3_gender_inference()

        # Step 4: Analysis
        (
            position_results,
            temporal_results,
            arxiv_position_results,
            covid_df,
        ) = step4_analysis()

        # Step 5: Figures
        step5_figures(position_results, temporal_results, arxiv_position_results, covid_df)

        print("\n" + "="*70)
        print("✓ PIPELINE COMPLETE!")
        print("="*70)
        print("\nResults saved to:")
        print("  data/processed/         - CSV files with analysis results")
        print("  outputs/figures/        - Publication-ready figures")
        print("  data/gender_cache.json  - Cached gender lookups")
        print()

    except KeyboardInterrupt:
        print("\n\n⊘ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Pipeline failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
