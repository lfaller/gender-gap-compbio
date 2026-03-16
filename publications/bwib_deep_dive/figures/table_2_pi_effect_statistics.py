#!/usr/bin/env python3
"""
Generate Table 2: Proportion of Female Authors by PI Gender

This table shows the proportion of female authors stratified by the last author's
(presumed PI's) gender, demonstrating the "female PI effect" - papers with female
last authors have more female co-authors at all positions.

Reference: https://doi.org/10.1371/journal.pcbi.1005134
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.bootstrap import bootstrap_pfemale
from .utils import get_paper_author_gender_data, OUTPUT_DIR


def generate_table_2(data):
    """
    Generate Table 2: Proportion of female authors by PI gender.
    Matches Bonham & Stefan Table 2 format.

    Args:
        data: DataFrame from get_paper_author_gender_data() with PI gender information

    Returns:
        DataFrame with columns: Dataset, Position, PI Gender, Mean, 95% CI Lower, 95% CI Upper, N
    """
    results = []

    for dataset in ['Biology', 'Computational Biology', 'Bioinformatics']:
        dataset_data = data[data['dataset'] == dataset]

        for position in ['first', 'second', 'other', 'penultimate']:
            for pi_gender in ['Male', 'Female']:
                pi_gender_data = dataset_data[dataset_data['last_author_gender'] == pi_gender.lower()]
                pos_data = pi_gender_data[pi_gender_data['position'] == position]

                if len(pos_data) > 0:
                    probs = pos_data['p_female'].dropna().tolist()
                    mean, ci_lower, ci_upper = bootstrap_pfemale(probs, n_iterations=1000)

                    results.append({
                        'Dataset': dataset,
                        'Position': position,
                        'PI Gender': pi_gender,
                        'Mean': round(mean, 3) if mean else None,
                        '95% CI Lower': round(ci_lower, 3) if ci_lower else None,
                        '95% CI Upper': round(ci_upper, 3) if ci_upper else None,
                        'N': len(probs)
                    })

    df = pd.DataFrame(results)

    # Save as CSV
    csv_path = OUTPUT_DIR / "Table2_female_authors_with_female_pi.csv"
    df.to_csv(csv_path, index=False)

    # Create formatted markdown table
    markdown_path = OUTPUT_DIR / "Table2_female_authors_with_female_pi.md"
    with open(markdown_path, 'w') as f:
        f.write("## Table 2. Proportion of Female Authors by PI Gender (2015–2025)\n\n")
        f.write("| Dataset | Position | PI Gender | Mean | 95% CI Lower | 95% CI Upper |\n")
        f.write("|---------|----------|-----------|------|-------------|-------------|\n")
        for _, row in df.iterrows():
            f.write(f"| {row['Dataset']} | {row['Position']} | {row['PI Gender']} | {row['Mean']:.3f} | {row['95% CI Lower']:.3f} | {row['95% CI Upper']:.3f} |\n")

    print("✓ Table 2 saved")
    return df


def main():
    """Run Table 2 generation."""
    print("\n" + "=" * 70)
    print("TABLE 2: FEMALE AUTHORS BY PI GENDER (THE FEMALE PI EFFECT)")
    print("=" * 70 + "\n")

    print("Loading paper-author gender data for PI effect...")
    data = get_paper_author_gender_data(start_year=2015, end_year=2025)
    print(f"✓ Loaded {len(data):,} author records with PI gender\n")

    print("GENERATING TABLE")
    print("-" * 70)
    table = generate_table_2(data)
    print()

    print("=" * 70)
    print("✓ TABLE 2 COMPLETE!")
    print("=" * 70)
    print(f"\nOutput files saved to: {OUTPUT_DIR}")
    print("  - Table2_female_authors_with_female_pi.csv")
    print("  - Table2_female_authors_with_female_pi.md")
    print()


if __name__ == "__main__":
    main()
