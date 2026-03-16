#!/usr/bin/env python3
"""
Complete overlap analysis: Biology, Computational Biology, and Bioinformatics.

Shows how the three datasets relate to each other and current data structure.
"""

import json
import sys
from pathlib import Path
import pandas as pd

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
    """Complete overlap analysis."""
    print("\n" + "=" * 80)
    print(" COMPREHENSIVE OVERLAP ANALYSIS: BIOLOGY, COMP BIO, & BIOINFORMATICS")
    print("=" * 80)
    print()

    # Paths
    analysis_dir = Path(__file__).parent
    repo_root = analysis_dir.parent.parent
    bio_csv = repo_root / "data/processed/pubmed_biology_2015_2025.csv"
    compbio_csv = repo_root / "data/processed/pubmed_compbio_2015_2025.csv"
    bioinf_json = analysis_dir / "data/bioinformatics_pmids.json"

    # Check files exist
    for path in [bio_csv, compbio_csv, bioinf_json]:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

    # Load data
    bio = load_pmids_from_csv(bio_csv)
    compbio = load_pmids_from_csv(compbio_csv)
    bioinf = load_pmids_from_json(bioinf_json)

    print("DATASET SIZES")
    print("-" * 80)
    print(f"  Biology:                  {len(bio):>10,} papers")
    print(f"  Computational Biology:    {len(compbio):>10,} papers")
    print(f"  Bioinformatics:           {len(bioinf):>10,} papers")
    print()

    # Current structure analysis
    print("CURRENT DATA STRUCTURE (Bio + CompBio only)")
    print("-" * 80)
    only_bio_current = bio - compbio
    only_compbio_current = compbio - bio
    both_current = bio & compbio

    print(f"  Only Biology:             {len(only_bio_current):>10,} papers ({len(only_bio_current)/len(bio)*100:>5.1f}%)")
    print(f"  Only Computational Bio:   {len(only_compbio_current):>10,} papers ({len(only_compbio_current)/len(bio)*100:>5.1f}%)")
    print(f"  Biology ∩ Comp Bio:       {len(both_current):>10,} papers ({len(both_current)/len(bio)*100:>5.1f}%)")
    print()
    print(f"  ⚠️  KEY INSIGHT: All {len(compbio):,} Comp Bio papers are ALSO tagged as Biology!")
    print(f"      → Currently distinguished by WHICH CSV file the PMID is stored in")
    print()

    # Three-way overlap
    print("THREE-WAY OVERLAP (Bio ∩ CompBio ∩ Bioinf)")
    print("-" * 80)
    all_three = bio & compbio & bioinf
    print(f"  {len(all_three):,} papers")
    print()

    # New data if we add bioinformatics
    print("IMPACT OF ADDING BIOINFORMATICS")
    print("-" * 80)

    # Bioinformatics subsets
    bioinf_only = bioinf - (bio | compbio)
    bioinf_with_bio_only = (bioinf & bio) - compbio
    bioinf_with_compbio_only = (bioinf & compbio) - bio
    bioinf_with_both = bioinf & bio & compbio

    print()
    print("Bioinformatics papers breakdown:")
    print(f"  Only Bioinformatics:                {len(bioinf_only):>10,} ({len(bioinf_only)/len(bioinf)*100:>5.1f}%)")
    print(f"  Bioinf + Biology (not Comp Bio):    {len(bioinf_with_bio_only):>10,} ({len(bioinf_with_bio_only)/len(bioinf)*100:>5.1f}%)")
    print(f"  Bioinf + Comp Bio (not Biology):    {len(bioinf_with_compbio_only):>10,} ({len(bioinf_with_compbio_only)/len(bioinf)*100:>5.1f}%)")
    print(f"  Bioinf + Biology + Comp Bio:        {len(bioinf_with_both):>10,} ({len(bioinf_with_both)/len(bioinf)*100:>5.1f}%)")
    print()

    # Overlap summary in matrix form
    print("OVERLAP MATRIX")
    print("-" * 80)
    print()
    print("  Comp Bio is:")
    if len(compbio) == len(bio & compbio):
        print(f"    ✓ A COMPLETE SUBSET of Biology ({len(compbio):,}/{len(bio):,})")
    print()
    print("  Bioinformatics is:")
    if len(bioinf_with_both) > 0:
        print(f"    ✓ PARTIALLY overlaps with both Biology AND Comp Bio")
        print(f"      - {len(bioinf_with_both):,} papers are in ALL THREE")
        print(f"      - {len(bioinf_with_bio_only):,} papers are in Biology + Bioinf (but not Comp Bio)")
        print(f"      - {len(bioinf_only):,} papers are ONLY in Bioinformatics")
    print()

    # Recommendations
    print("IMPLICATIONS FOR DATA STRUCTURE")
    print("-" * 80)
    print()
    print("Current approach (working well):")
    print("  • Maintain TWO separate CSV files (Biology & Computational Biology)")
    print("  • All papers are in Biology CSV")
    print("  • Comp Bio CSV contains papers that match BOTH criteria")
    print("  • When analyzing, distinguish by CSV source")
    print()
    print("Adding Bioinformatics - OPTIONS:")
    print()
    print("  OPTION A: Three separate CSVs (RECOMMENDED)")
    print("    • pubmed_biology_2015_2025.csv          (274,702 papers)")
    print("    • pubmed_compbio_2015_2025.csv          (67,205 papers, subset of biology)")
    print("    • pubmed_bioinformatics_2015_2025.csv   (167,240 papers)")
    print("    • Handles overlaps: papers marked by CSV source")
    print("    • Pro: Mirrors existing approach, preserves granularity")
    print("    • Con: 67,202 papers in multiple CSVs, need deduplication logic")
    print()
    print("  OPTION B: Replace Comp Bio with Bioinf (data simplification)")
    print("    • pubmed_biology_2015_2025.csv          (274,702 papers)")
    print("    • pubmed_bioinformatics_2015_2025.csv   (167,240 papers)")
    print("    • Drop computational_biology CSV")
    print("    • Pro: Simpler data structure, cleaner semantically")
    print("    • Con: Loses comp bio granularity, can't separately analyze comp bio")
    print()
    print("  OPTION C: Combine all bioinformatics into Biology")
    print("    • pubmed_biology_extended_2015_2025.csv (340,940 papers)")
    print("    • Add 'field' column to distinguish: 'biology', 'compbio', 'bioinf'")
    print("    • Pro: Single DataFrame, flexible grouping")
    print("    • Con: Different structure from current approach")
    print()

    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
