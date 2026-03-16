#!/usr/bin/env python3
"""
Analyze overlaps between existing Biology and Computational Biology datasets.

Determines how many papers are tagged with both search terms.
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path so we can import src modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def load_pmids_from_csv(csv_path):
    """Load PMIDs from a CSV file."""
    df = pd.read_csv(csv_path, usecols=["pmid"])
    return set(df["pmid"].astype(str).unique())


def main():
    """Analyze overlaps between Biology and Computational Biology."""
    print("=" * 70)
    print("ANALYZING EXISTING DATASET OVERLAPS")
    print("(Biology vs Computational Biology)")
    print("=" * 70)
    print()

    # Paths
    analysis_dir = Path(__file__).parent
    repo_root = analysis_dir.parent.parent
    bio_csv = repo_root / "data/processed/pubmed_biology_2015_2025.csv"
    compbio_csv = repo_root / "data/processed/pubmed_compbio_2015_2025.csv"

    # Check that files exist
    for path in [bio_csv, compbio_csv]:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

    # Load PMIDs
    print("Loading existing datasets...")
    bio_pmids = load_pmids_from_csv(bio_csv)
    compbio_pmids = load_pmids_from_csv(compbio_csv)

    print(f"  Biology PMIDs:              {len(bio_pmids):,}")
    print(f"  Computational Biology PMIDs: {len(compbio_pmids):,}")
    print()

    # Compute overlaps
    print("Computing overlaps...")

    only_bio = bio_pmids - compbio_pmids
    only_compbio = compbio_pmids - bio_pmids
    both = bio_pmids & compbio_pmids
    union = bio_pmids | compbio_pmids

    print()
    print("=" * 70)
    print("OVERLAP SUMMARY")
    print("=" * 70)
    print()

    print(f"Only Biology (not in Comp Bio):     {len(only_bio):,} ({len(only_bio)/len(union)*100:.1f}%)")
    print(f"Only Comp Bio (not in Biology):     {len(only_compbio):,} ({len(only_compbio)/len(union)*100:.1f}%)")
    print(f"Both Biology AND Comp Bio:          {len(both):,} ({len(both)/len(union)*100:.1f}%)")
    print()
    print(f"Total unique papers (union):        {len(union):,}")
    print()

    # Sanity check
    total_parts = len(only_bio) + len(only_compbio) + len(both)
    if total_parts == len(union):
        print("✓ Sanity check PASSED")
    else:
        print(f"✗ WARNING: {total_parts} != {len(union)}")

    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if len(both) == 0:
        print("✓ The datasets have NO overlap - they're disjoint.")
        print("  Comp Bio papers are a separate set from Biology papers.")
    elif len(both) == len(compbio_pmids):
        print("⚠ ALL Computational Biology papers are also in Biology!")
        print(f"  {len(compbio_pmids):,} papers match both search criteria.")
        print("  Comp Bio is a SUBSET of Biology.")
    else:
        overlap_pct = len(both) / len(compbio_pmids) * 100
        print(f"⚠ {overlap_pct:.1f}% of Comp Bio papers are also in Biology")
        print(f"  {len(both):,} papers match both search criteria.")
        print("  There IS partial overlap.")

    print()


if __name__ == "__main__":
    main()
