#!/usr/bin/env python3
"""
Generate Table 1: Proportion of Female Authors by Dataset and Position

This table directly replicates Bonham & Stefan Table 1 format, showing the
probability that an author in each position is female across Biology and
Computational Biology datasets for 2015-2025.

Reference: https://doi.org/10.1371/journal.pcbi.1005134
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.bootstrap import bootstrap_pfemale
from .utils import get_author_data, OUTPUT_DIR, save_table_to_files


def generate_table_1(data):
    """
    Generate Table 1: Proportion of female authors by dataset and position.
    Matches Bonham & Stefan Table 1 format.

    Args:
        data: DataFrame from get_author_data() with columns:
              name, p_female, position, dataset, year, pmid

    Returns:
        DataFrame with columns: Dataset, Position, Mean, 95% CI Lower, 95% CI Upper, N
    """
    results = []

    for dataset in ['Biology', 'Computational Biology', 'Bioinformatics']:
        dataset_data = data[data['dataset'] == dataset]

        for position in ['first', 'second', 'other', 'penultimate', 'last']:
            pos_data = dataset_data[dataset_data['position'] == position]

            if len(pos_data) > 0:
                probs = pos_data['p_female'].dropna().tolist()
                mean, ci_lower, ci_upper = bootstrap_pfemale(probs, n_iterations=1000)

                results.append({
                    'Dataset': dataset,
                    'Position': position,
                    'Mean': round(mean, 3) if mean else None,
                    '95% CI Lower': round(ci_lower, 3) if ci_lower else None,
                    '95% CI Upper': round(ci_upper, 3) if ci_upper else None,
                    'N': len(probs)
                })

    df = pd.DataFrame(results)

    # Save as CSV
    csv_path = OUTPUT_DIR / "Table1_proportion_female_authors.csv"
    df.to_csv(csv_path, index=False)

    # Create formatted markdown table
    markdown_path = OUTPUT_DIR / "Table1_proportion_female_authors.md"
    with open(markdown_path, 'w') as f:
        f.write("## Table 1. Proportion of Female Authors (2015–2025)\n\n")
        f.write("| Dataset | Position | Mean | 95% CI Lower | 95% CI Upper |\n")
        f.write("|---------|----------|------|-------------|-------------|\n")
        for _, row in df.iterrows():
            f.write(f"| {row['Dataset']} | {row['Position']} | {row['Mean']:.3f} | {row['95% CI Lower']:.3f} | {row['95% CI Upper']:.3f} |\n")

    print("✓ Table 1 saved")
    return df


def main():
    """Run Table 1 generation."""
    print("\n" + "=" * 70)
    print("TABLE 1: PROPORTION OF FEMALE AUTHORS")
    print("=" * 70 + "\n")

    print("Loading author data from database...")
    data = get_author_data(start_year=2015, end_year=2025)
    print(f"✓ Loaded {len(data):,} author records\n")

    print("GENERATING TABLE")
    print("-" * 70)
    table = generate_table_1(data)
    print()

    print("=" * 70)
    print("✓ TABLE 1 COMPLETE!")
    print("=" * 70)
    print(f"\nOutput files saved to: {OUTPUT_DIR}")
    print("  - Table1_proportion_female_authors.csv")
    print("  - Table1_proportion_female_authors.md")
    print()


if __name__ == "__main__":
    main()
