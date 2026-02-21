#!/usr/bin/env python3
"""
Journal Impact Analysis: Do female authors publish in lower-impact journals?

This script analyzes whether female authors in computational biology tend to
publish in journals with lower impact rankings (lower quartile scores), using
ScimagoJR journal rankings.

Usage:
    python analyze_journal_impact.py
"""

import sys
from pathlib import Path
from typing import Tuple

import pandas as pd
import matplotlib.pyplot as plt

from src.db_utils import GenderDatabase
from src.bootstrap import bootstrap_by_multiple_groups
from src.plotting import (
    plot_pfemale_by_journal_quartile,
    plot_journal_quartile_distribution,
)


def load_and_prepare_data(
    skip_db_read: bool = False
) -> pd.DataFrame:
    """
    Load PubMed CSV and gender data, then join with cached journal quartiles.

    Uses pre-cached journal quartiles from the database (populated by
    preprocess_journal_quartiles.py) to avoid slow fuzzy matching.

    Args:
        skip_db_read: If True, skip loading from DB (for testing)

    Returns:
        Merged DataFrame with columns: pmid, author, position, p_female, year, journal, quartile
    """
    print("\n" + "="*70)
    print("Loading and merging data...")
    print("="*70)

    # Load PubMed CSVs (both Biology and CompBio, matching gender inference)
    print("Loading PubMed publications...")
    bio_df = pd.read_csv("data/processed/pubmed_biology_2015_2025.csv")
    comp_df = pd.read_csv("data/processed/pubmed_compbio_2015_2025.csv")
    pubmed_df = pd.concat([bio_df, comp_df], ignore_index=True)
    pubmed_df = pubmed_df.drop_duplicates(subset=['pmid', 'year'])
    print(f"✓ Loaded {len(pubmed_df):,} papers (Biology: {len(bio_df):,} + CompBio: {len(comp_df):,})")

    # Load gender data from database
    print("Loading gender data from database...")
    db = GenderDatabase(db_path="data/gender_data.db")
    gender_df = db.get_author_data_as_dataframe()
    db.close()

    # Filter to 2015-2025
    gender_df = gender_df[(gender_df["year"] >= 2015) & (gender_df["year"] <= 2025)]
    print(f"✓ Loaded {len(gender_df):,} author records")

    # Select relevant columns from PubMed
    pubmed_df = pubmed_df[["pmid", "journal", "year"]].copy()

    # Ensure pmid is string type in both dataframes
    gender_df["pmid"] = gender_df["pmid"].astype(str)
    pubmed_df["pmid"] = pubmed_df["pmid"].astype(str)

    # Merge on pmid and year
    print("Merging gender and PubMed data...")
    merged_df = gender_df.merge(pubmed_df, on=["pmid", "year"], how="left")
    print(f"✓ Merged to {len(merged_df):,} records")

    # Load journal quartiles from database
    print("\nLoading journal quartiles from database...")
    db_journal = GenderDatabase(db_path="data/gender_data.db")
    journal_df = db_journal.get_journals_as_dataframe()
    db_journal.close()

    if len(journal_df) == 0:
        raise ValueError(
            "No journal quartiles found in database.\n"
            "Please run: python preprocess_journal_quartiles.py"
        )

    # Create lookup dict from database
    journal_lookup_db = dict(
        zip(journal_df["journal_name"], journal_df["quartile"])
    )

    print(f"✓ Loaded {len(journal_lookup_db):,} journals from database")

    # Map journals to quartiles using database lookup
    print("Mapping journals to quartiles...")
    matched = 0
    unmatched_journals = set()

    def assign_quartile_from_db(journal_name):
        nonlocal matched, unmatched_journals
        if pd.isna(journal_name):
            return None

        if journal_name in journal_lookup_db:
            matched += 1
            return journal_lookup_db[journal_name]
        else:
            unmatched_journals.add(journal_name)
            return None

    merged_df["quartile"] = merged_df["journal"].apply(assign_quartile_from_db)

    # Remove rows with no journal quartile assignment
    initial_rows = len(merged_df)
    merged_df = merged_df.dropna(subset=["quartile"])

    match_rate = (matched / initial_rows * 100) if initial_rows > 0 else 0
    print(f"✓ Matched {len(merged_df):,} / {initial_rows:,} author records ({match_rate:.1f}%)")
    print(f"  Unmatched journals: {len(unmatched_journals)}")
    if len(unmatched_journals) <= 10:
        for j in sorted(unmatched_journals):
            print(f"    - {j}")

    return merged_df


def run_analysis(merged_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run bootstrap analysis by journal quartile and author position.

    Args:
        merged_df: Merged dataframe with pmid, author, position, p_female, quartile

    Returns:
        Tuple of (quartile_position_results, quartile_year_results)
    """
    print("\n" + "="*70)
    print("Running statistical analysis...")
    print("="*70)

    # Analysis 1: Journal quartile × author position
    print("\nAnalysis 1: P_female by Journal Quartile and Author Position...")
    print("  Running 1000 bootstrap iterations (this may take several minutes)...")
    quartile_position = bootstrap_by_multiple_groups(
        merged_df,
        group_cols=["quartile", "position"],
        prob_col="p_female",
        n_iterations=1000,
    )
    quartile_position = quartile_position.rename(columns={"group": "quartile"})
    quartile_position.to_csv(
        "data/processed/analysis_journal_quartile_by_position.csv",
        index=False
    )
    print("✓ Analysis 1 complete")
    print(quartile_position.to_string())

    # Analysis 2: Journal quartile × year
    print("\nAnalysis 2: P_female by Journal Quartile over Time...")
    print("  Running 1000 bootstrap iterations (this may take several minutes)...")
    quartile_year = bootstrap_by_multiple_groups(
        merged_df,
        group_cols=["quartile", "year"],
        prob_col="p_female",
        n_iterations=1000,
    )
    quartile_year.to_csv(
        "data/processed/analysis_journal_quartile_by_year.csv",
        index=False
    )
    print(f"✓ Analysis 2 complete - Analyzed {len(quartile_year)} year-quartile combinations\n")

    return quartile_position, quartile_year


def generate_figures(
    quartile_position: pd.DataFrame,
    quartile_year: pd.DataFrame,
    merged_df: pd.DataFrame
):
    """
    Generate publication-ready figures.

    Args:
        quartile_position: Bootstrap results by quartile and position
        quartile_year: Bootstrap results by quartile and year
        merged_df: Original merged data for distribution plots
    """
    print("\n" + "="*70)
    print("Generating figures...")
    print("="*70)

    output_dir = "outputs/figures"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Figure 1: P_female by journal quartile and author position
    print("Figure 1: P_female by Journal Quartile and Author Position...")
    print("  Generating plot...")
    fig, ax = plot_pfemale_by_journal_quartile(
        quartile_position,
        output_path=f"{output_dir}/fig_journal_impact_by_position.png",
        figsize=(12, 6)
    )
    print("  Saving PNG and SVG...")
    plt.savefig(
        f"{output_dir}/fig_journal_impact_by_position.svg",
        dpi=300,
        bbox_inches="tight",
        format="svg"
    )
    plt.close()
    print("✓ Saved Figure 1\n")

    # Figure 2: Distribution of journal quartiles by author gender
    print("Figure 2: Journal Quartile Distribution by Author Gender...")
    print("  Generating plot...")
    fig, ax = plot_journal_quartile_distribution(
        merged_df,
        output_path=f"{output_dir}/fig_journal_quartile_distribution.png",
        figsize=(10, 6)
    )
    print("  Saving PNG and SVG...")
    plt.savefig(
        f"{output_dir}/fig_journal_quartile_distribution.svg",
        dpi=300,
        bbox_inches="tight",
        format="svg"
    )
    plt.close()
    print("✓ Saved Figure 2\n")

    print(f"✓ All figures saved to {output_dir}/")


def main():
    """Run the full journal impact analysis."""
    print("\n" + "="*70)
    print("JOURNAL IMPACT ANALYSIS: Female Authors & Journal Quartiles")
    print("="*70)

    try:
        # Step 1: Load and merge data (using pre-cached journal quartiles from database)
        merged_df = load_and_prepare_data()

        # Step 2: Run analysis
        quartile_position, quartile_year = run_analysis(merged_df)

        # Step 3: Generate figures
        generate_figures(quartile_position, quartile_year, merged_df)

        print("\n" + "="*70)
        print("✓ ANALYSIS COMPLETE!")
        print("="*70)
        print("\nResults saved to:")
        print("  data/processed/analysis_journal_quartile_by_position.csv")
        print("  data/processed/analysis_journal_quartile_by_year.csv")
        print("  outputs/figures/fig_journal_impact_*.{png,svg}")
        print()

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("Make sure you have run the gender inference pipeline first:")
        print("  python run_gender_inference_db.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
