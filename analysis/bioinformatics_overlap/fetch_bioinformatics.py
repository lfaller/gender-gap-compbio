#!/usr/bin/env python3
"""
Fetch bioinformatics papers from PubMed.

Fetches only PMIDs (not full paper details) for papers tagged with
"Bioinformatics"[Majr] from 2015-2025, saving to JSON for overlap analysis.

Usage:
    python analysis/bioinformatics_overlap/fetch_bioinformatics.py
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path so we can import src modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.pubmed_fetcher import PubMedFetcher

load_dotenv()


def main():
    """Fetch bioinformatics PMIDs and save to JSON."""
    output_dir = Path(__file__).parent
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("FETCHING BIOINFORMATICS PMIDS FROM PUBMED (2015-2025)")
    print("=" * 70)

    # Setup
    email = os.getenv("NCBI_EMAIL")
    if not email:
        raise ValueError("NCBI_EMAIL not set in .env file")

    fetcher = PubMedFetcher(email=email)
    api_key = fetcher.api_key
    print(f"\nEmail: {email}")
    print(f"API key: {'✓ Yes' if api_key else '⚠ No (limited to 3 req/sec)'}\n")

    # Fetch bioinformatics PMIDs (only PMIDs, not full details)
    print("Fetching bioinformatics PMIDs...")
    bioinformatics_pmids = fetcher._search_by_year_range(
        mesh_term='bioinformatics[Mesh]',
        start_year=2015,
        end_year=2025
    )

    print(f"\nFetched {len(bioinformatics_pmids):,} bioinformatics PMIDs\n")

    # Save to JSON
    output_path = data_dir / "bioinformatics_pmids.json"
    with open(output_path, "w") as f:
        json.dump({
            "count": len(bioinformatics_pmids),
            "pmids": bioinformatics_pmids
        }, f, indent=2)

    print("=" * 70)
    print("✓ FETCH COMPLETE!")
    print("=" * 70)
    print(f"\nResults saved to: {output_path}")
    print(f"Total bioinformatics PMIDs: {len(bioinformatics_pmids):,}")


if __name__ == "__main__":
    main()
