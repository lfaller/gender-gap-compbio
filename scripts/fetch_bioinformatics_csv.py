#!/usr/bin/env python3
"""
Fetch full paper details for bioinformatics papers.

Uses pre-fetched PMIDs from the overlap analysis to avoid re-running the PMID search.
Deduplicates and fetches author information, then saves to CSV.

This is a one-time run script to populate pubmed_bioinformatics_2015_2025.csv
before running the main inference pipeline.

Usage:
    python scripts/fetch_bioinformatics_csv.py
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pubmed_fetcher import PubMedFetcher
from src.gender_utils import assign_positions
import pandas as pd

load_dotenv()


def main():
    """Fetch bioinformatics paper details and save to CSV."""
    print("=" * 70)
    print("FETCHING BIOINFORMATICS PAPER DETAILS")
    print("=" * 70)
    print()

    # Setup
    email = os.getenv("NCBI_EMAIL")
    if not email:
        raise ValueError("NCBI_EMAIL not set in .env file")

    fetcher = PubMedFetcher(email=email)
    print(f"Email: {email}")
    print(f"API key: {'✓ Yes' if fetcher.api_key else '⚠ No (limited to 3 req/sec)'}\n")

    # Load pre-fetched bioinformatics PMIDs from overlap analysis
    pmid_json = Path("analysis/bioinformatics_overlap/data/bioinformatics_pmids.json")

    if pmid_json.exists():
        print(f"Loading pre-fetched PMIDs from {pmid_json}...")
        with open(pmid_json, "r") as f:
            data = json.load(f)
        pmids = list(set(data["pmids"]))  # Deduplicate
        print(f"Loaded {len(pmids):,} unique bioinformatics PMIDs\n")
    else:
        print(f"WARNING: {pmid_json} not found!")
        print("Fetching bioinformatics PMIDs fresh from PubMed...")
        pmids = fetcher.search_bioinformatics(start_year=2015, end_year=2025)
        pmids = list(set(pmids))  # Deduplicate
        print(f"Fetched {len(pmids):,} unique bioinformatics PMIDs\n")

    # Fetch full paper details
    print("Fetching paper details...")
    papers = fetcher.fetch_paper_details(pmids, batch_size=500)

    # Add author positions
    print(f"Processing {len(papers)} papers...")
    for paper in papers:
        authors = paper.get("authors", [])
        paper["positions"] = assign_positions(authors)

    # Create DataFrame
    df = pd.DataFrame(papers)
    df["dataset"] = "Bioinformatics"

    # Save to CSV
    output_path = Path("data/processed/pubmed_bioinformatics_2015_2025.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print()
    print("=" * 70)
    print("✓ FETCH COMPLETE!")
    print("=" * 70)
    print(f"\nResults saved to: {output_path}")
    print(f"Total papers: {len(df):,}")
    print(f"Columns: {', '.join(df.columns.tolist())}")
    print()


if __name__ == "__main__":
    main()
