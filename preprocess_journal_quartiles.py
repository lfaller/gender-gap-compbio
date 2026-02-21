#!/usr/bin/env python3
"""
Preprocess journal quartiles from ScimagoJR and cache in database.

This script performs fuzzy matching once and stores the results in the database
so future analyses don't need to repeat this slow step.

Usage:
    python preprocess_journal_quartiles.py
"""

import pandas as pd
from difflib import get_close_matches
from pathlib import Path
from src.db_utils import GenderDatabase


def load_scimagojr_data(filepath: str = "local/scimagojr 2024.csv") -> pd.DataFrame:
    """Load and parse ScimagoJR journal rankings."""
    print(f"Loading ScimagoJR data from {filepath}...")
    df = pd.read_csv(filepath, sep=";", decimal=",")

    # Normalize journal title
    df["Title_normalized"] = df["Title"].str.lower().str.strip()

    # Keep relevant columns
    df = df[["Title", "Title_normalized", "SJR Best Quartile"]].copy()
    df.rename(columns={"SJR Best Quartile": "quartile"}, inplace=True)

    # Filter to ranked journals (Q1-Q4)
    df = df[df["quartile"].isin(["Q1", "Q2", "Q3", "Q4"])].copy()

    print(f"✓ Loaded {len(df):,} ranked journals from ScimagoJR")
    return df


def load_pubmed_journals() -> list:
    """Load unique journal names from PubMed CSVs (both Biology and CompBio)."""
    print(f"\nLoading PubMed journals...")
    bio_df = pd.read_csv("data/processed/pubmed_biology_2015_2025.csv")
    comp_df = pd.read_csv("data/processed/pubmed_compbio_2015_2025.csv")
    pubmed_df = pd.concat([bio_df, comp_df], ignore_index=True)
    unique_journals = pubmed_df["journal"].dropna().unique().tolist()
    print(f"✓ Found {len(unique_journals):,} unique journals in PubMed data")
    print(f"  (Biology: {len(bio_df):,} + CompBio: {len(comp_df):,} papers)")
    return unique_journals


def match_journal_to_quartile(
    journal_name: str,
    scimagojr_titles: list,
    scimagojr_lookup: dict,
    threshold: float = 0.8
):
    """Match a journal name to a quartile via exact or fuzzy matching."""
    normalized = journal_name.lower().strip()

    # Try exact match first
    if normalized in scimagojr_lookup:
        return (scimagojr_lookup[normalized], True)

    # Try fuzzy match
    matches = get_close_matches(normalized, scimagojr_titles, n=1, cutoff=threshold)
    if matches:
        return (scimagojr_lookup[matches[0]], False)

    return (None, False)


def main():
    print("\n" + "="*70)
    print("PREPROCESSING: Journal Quartile Caching")
    print("="*70)

    try:
        # Load ScimagoJR data
        scimagojr_df = load_scimagojr_data()
        scimagojr_titles = scimagojr_df["Title_normalized"].tolist()
        scimagojr_lookup = dict(
            zip(scimagojr_df["Title_normalized"], scimagojr_df["quartile"])
        )

        # Load PubMed journals
        pubmed_journals = load_pubmed_journals()

        # Match each journal to quartile
        print("\nMatching journals to ScimagoJR rankings...")
        journal_data = []
        matched = 0
        unmatched_journals = []

        for i, journal_name in enumerate(pubmed_journals):
            if (i + 1) % 5000 == 0:
                print(f"  Progress: {i+1:,} / {len(pubmed_journals):,} ({100*(i+1)/len(pubmed_journals):.1f}%)")

            quartile, is_exact = match_journal_to_quartile(
                journal_name, scimagojr_titles, scimagojr_lookup
            )

            if quartile:
                matched += 1
                journal_data.append({
                    "journal_name": journal_name,
                    "quartile": quartile,
                    "is_exact_match": is_exact
                })
            else:
                unmatched_journals.append(journal_name)

        print(f"✓ Matched {matched:,} / {len(pubmed_journals):,} journals ({100*matched/len(pubmed_journals):.1f}%)")
        print(f"  Unmatched journals: {len(unmatched_journals)}")
        if len(unmatched_journals) <= 10:
            for j in sorted(unmatched_journals):
                print(f"    - {j}")

        # Save to database
        print("\nSaving journal quartiles to database...")
        db = GenderDatabase()
        db.batch_insert_journals(journal_data)
        db.close()

        print(f"✓ Saved {len(journal_data):,} journals to database")

        print("\n" + "="*70)
        print("✓ PREPROCESSING COMPLETE!")
        print("="*70)
        print(f"\nNext time you run analyze_journal_impact.py, it will use the cached")
        print(f"journal quartiles and skip the slow fuzzy matching step.")
        print()

    except Exception as e:
        print(f"\n✗ Preprocessing failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
