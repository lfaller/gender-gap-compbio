#!/usr/bin/env python3
"""Standalone arXiv fetcher script - can run in parallel with gender inference."""

from src.arxiv_fetcher import arXivFetcher
from src.gender_utils import assign_positions
import pandas as pd
from pathlib import Path

print("="*70)
print("ARXIV DATA FETCHER (Standalone)")
print("="*70)
print("\nThis script can run in parallel with gender inference.")
print("It will fetch q-bio and cs preprints from 2015-2024.\n")

# Create output directory
Path("data/processed").mkdir(parents=True, exist_ok=True)

fetcher = arXivFetcher(delay_seconds=5.0)

# Fetch q-bio preprints
print("="*70)
print("Fetching quantitative biology (q-bio) preprints...")
print("="*70)
qbio_preprints = fetcher.fetch_quantitative_biology(start_year=2015, end_year=2024)

if len(qbio_preprints) > 0:
    qbio_preprints = assign_positions(qbio_preprints)
    qbio_df = pd.DataFrame(qbio_preprints)
else:
    # Create empty dataframe with correct schema
    qbio_df = pd.DataFrame(columns=["arxiv_id", "title", "year", "published_date", "authors", "author_count", "category", "positions"])

qbio_df["dataset"] = "q-bio"
qbio_df.to_csv("data/processed/arxiv_qbio_2015_2024.csv", index=False)
print(f"✓ Saved {len(qbio_df)} q-bio preprints\n")

# Fetch cs preprints
print("="*70)
print("Fetching computer science (cs) preprints...")
print("="*70)
cs_preprints = fetcher.fetch_computer_science(start_year=2015, end_year=2024)

if len(cs_preprints) > 0:
    cs_preprints = assign_positions(cs_preprints)
    cs_df = pd.DataFrame(cs_preprints)
else:
    # Create empty dataframe with correct schema
    cs_df = pd.DataFrame(columns=["arxiv_id", "title", "year", "published_date", "authors", "author_count", "category", "positions"])

cs_df["dataset"] = "cs"
cs_df.to_csv("data/processed/arxiv_cs_2015_2024.csv", index=False)
print(f"✓ Saved {len(cs_df)} cs preprints\n")

# Summary
print("="*70)
print("✓ ARXIV FETCH COMPLETE!")
print("="*70)
print(f"\nResults:")
print(f"  q-bio preprints: {len(qbio_df):,}")
print(f"  cs preprints:    {len(cs_df):,}")
print(f"  Total arXiv:     {len(qbio_df) + len(cs_df):,}")
print(f"\nFiles saved:")
print(f"  data/processed/arxiv_qbio_2015_2024.csv")
print(f"  data/processed/arxiv_cs_2015_2024.csv")
print()
