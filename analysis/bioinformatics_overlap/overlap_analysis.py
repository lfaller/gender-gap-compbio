#!/usr/bin/env python3
"""
Analyze overlaps between Biology, Computational Biology, and Bioinformatics papers.

Compares PMID sets from three sources to quantify:
- Exclusive papers in each category
- Pairwise overlaps
- Papers matching all three criteria

Usage:
    python analysis/bioinformatics_overlap/overlap_analysis.py
"""

import json
import sys
from pathlib import Path
import pandas as pd

# Add project root to path so we can import src modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def load_pmids_from_csv(csv_path):
    """Load PMIDs from a CSV file."""
    df = pd.read_csv(csv_path, usecols=["pmid"])
    return set(df["pmid"].astype(str).unique())


def load_pmids_from_json(json_path):
    """Load PMIDs from a JSON file."""
    with open(json_path, "r") as f:
        data = json.load(f)
    return set(data["pmids"])


def main():
    """Analyze overlaps between the three datasets."""
    print("=" * 70)
    print("BIOINFORMATICS OVERLAP ANALYSIS")
    print("=" * 70)
    print()

    # Paths
    analysis_dir = Path(__file__).parent
    repo_root = analysis_dir.parent.parent
    bio_csv = repo_root / "data/processed/pubmed_biology_2015_2025.csv"
    compbio_csv = repo_root / "data/processed/pubmed_compbio_2015_2025.csv"
    bioinf_json = analysis_dir / "data/bioinformatics_pmids.json"

    # Check that files exist
    for path in [bio_csv, compbio_csv, bioinf_json]:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

    # Load PMIDs
    print("Loading PMIDs from existing datasets...")
    bio_pmids = load_pmids_from_csv(bio_csv)
    compbio_pmids = load_pmids_from_csv(compbio_csv)
    bioinf_pmids = load_pmids_from_json(bioinf_json)

    print(f"  Biology:              {len(bio_pmids):,} papers")
    print(f"  Computational Biology: {len(compbio_pmids):,} papers")
    print(f"  Bioinformatics:       {len(bioinf_pmids):,} papers")
    print()

    # Compute overlaps using set operations
    print("Computing overlaps...")

    # Exclusive papers (only in one category)
    only_bio = bio_pmids - (compbio_pmids | bioinf_pmids)
    only_compbio = compbio_pmids - (bio_pmids | bioinf_pmids)
    only_bioinf = bioinf_pmids - (bio_pmids | compbio_pmids)

    # Pairwise overlaps (in two categories but not the third)
    bio_compbio_only = (bio_pmids & compbio_pmids) - bioinf_pmids
    bio_bioinf_only = (bio_pmids & bioinf_pmids) - compbio_pmids
    compbio_bioinf_only = (compbio_pmids & bioinf_pmids) - bio_pmids

    # All three
    all_three = bio_pmids & compbio_pmids & bioinf_pmids

    print()

    # Print summary
    print("=" * 70)
    print("OVERLAP SUMMARY")
    print("=" * 70)
    print()

    # Total unique papers
    all_unique = bio_pmids | compbio_pmids | bioinf_pmids
    print(f"Total unique papers (union of all three):         {len(all_unique):,}")
    print()

    # Exclusive papers
    print("EXCLUSIVE PAPERS (in only one category):")
    print(f"  Only Biology:              {len(only_bio):,}")
    print(f"  Only Computational Biology: {len(only_compbio):,}")
    print(f"  Only Bioinformatics:       {len(only_bioinf):,}")
    print()

    # Pairwise overlaps
    print("PAIRWISE OVERLAPS (in two categories, excluding the third):")
    print(f"  Biology ∩ Comp Bio (no Bioinf):    {len(bio_compbio_only):,}")
    print(f"  Biology ∩ Bioinf (no Comp Bio):    {len(bio_bioinf_only):,}")
    print(f"  Comp Bio ∩ Bioinf (no Biology):    {len(compbio_bioinf_only):,}")
    print()

    # All three
    print("ALL THREE CATEGORIES:")
    print(f"  Biology ∩ Comp Bio ∩ Bioinf:      {len(all_three):,}")
    print()

    # Sanity check: all groups should sum to total unique
    total_from_groups = (
        len(only_bio) + len(only_compbio) + len(only_bioinf) +
        len(bio_compbio_only) + len(bio_bioinf_only) + len(compbio_bioinf_only) +
        len(all_three)
    )

    print("=" * 70)
    print("SANITY CHECK")
    print("=" * 70)
    print(f"Sum of all 7 groups:          {total_from_groups:,}")
    print(f"Total unique papers (union):  {len(all_unique):,}")

    if total_from_groups == len(all_unique):
        print("✓ Sanity check PASSED - groups partition the union correctly")
    else:
        print(f"✗ WARNING: Mismatch! {total_from_groups} != {len(all_unique)}")
    print()

    # Save results to CSV
    results_dir = analysis_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    results_df = pd.DataFrame({
        "category": [
            "Only Biology",
            "Only Computational Biology",
            "Only Bioinformatics",
            "Biology ∩ Comp Bio (no Bioinf)",
            "Biology ∩ Bioinf (no Comp Bio)",
            "Comp Bio ∩ Bioinf (no Biology)",
            "Biology ∩ Comp Bio ∩ Bioinf",
        ],
        "count": [
            len(only_bio),
            len(only_compbio),
            len(only_bioinf),
            len(bio_compbio_only),
            len(bio_bioinf_only),
            len(compbio_bioinf_only),
            len(all_three),
        ]
    })

    csv_path = results_dir / "overlap_summary.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"Results saved to: {csv_path}")
    print()


if __name__ == "__main__":
    main()
