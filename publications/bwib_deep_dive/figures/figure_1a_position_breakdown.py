#!/usr/bin/env python3
"""
Generate Figure 1A: P(female) by Author Position

This figure directly replicates Bonham & Stefan's Fig 1A, showing the probability
that an author in each position is female. Compares Biology vs Computational Biology
across all author positions for 2015-2025.

Reference: https://doi.org/10.1371/journal.pcbi.1005134
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.bootstrap import bootstrap_by_multiple_groups
from .utils import get_author_data, OUTPUT_DIR, COLORS


def generate_figure_1a(data):
    """
    Generate Fig 1A: Mean P(female) by author position.
    Compares Biology, Computational Biology, and Bioinformatics.

    Args:
        data: DataFrame from get_author_data() with columns:
              name, p_female, position, dataset, year, pmid

    Returns:
        DataFrame with bootstrap results for each dataset-position combination
    """
    results = bootstrap_by_multiple_groups(
        data,
        group_cols=['dataset', 'position'],
        prob_col='p_female',
        n_iterations=1000
    )

    # Prepare data for plotting
    positions = ['first', 'second', 'other', 'penultimate', 'last']
    bio_data = {}
    comp_data = {}
    bioinf_data = {}

    for pos in positions:
        bio_row = results[(results['dataset'] == 'Biology') & (results['position'] == pos)]
        comp_row = results[(results['dataset'] == 'Computational Biology') & (results['position'] == pos)]
        bioinf_row = results[(results['dataset'] == 'Bioinformatics') & (results['position'] == pos)]

        if not bio_row.empty:
            bio_data[pos] = {
                'mean': bio_row['mean'].values[0],
                'lower': bio_row['ci_lower'].values[0],
                'upper': bio_row['ci_upper'].values[0]
            }

        if not comp_row.empty:
            comp_data[pos] = {
                'mean': comp_row['mean'].values[0],
                'lower': comp_row['ci_lower'].values[0],
                'upper': comp_row['ci_upper'].values[0]
            }

        if not bioinf_row.empty:
            bioinf_data[pos] = {
                'mean': bioinf_row['mean'].values[0],
                'lower': bioinf_row['ci_lower'].values[0],
                'upper': bioinf_row['ci_upper'].values[0]
            }

    # Create figure
    fig, ax = plt.subplots(figsize=(11, 6))

    x = np.arange(len(positions))
    width = 0.25  # Width for three bars per position

    bio_means = [bio_data[p]['mean'] if p in bio_data else 0 for p in positions]
    bio_errors_lower = [bio_data[p]['mean'] - bio_data[p]['lower'] if p in bio_data else 0 for p in positions]
    bio_errors_upper = [bio_data[p]['upper'] - bio_data[p]['mean'] if p in bio_data else 0 for p in positions]
    comp_means = [comp_data[p]['mean'] if p in comp_data else 0 for p in positions]
    comp_errors_lower = [comp_data[p]['mean'] - comp_data[p]['lower'] if p in comp_data else 0 for p in positions]
    comp_errors_upper = [comp_data[p]['upper'] - comp_data[p]['mean'] if p in comp_data else 0 for p in positions]
    bioinf_means = [bioinf_data[p]['mean'] if p in bioinf_data else 0 for p in positions]
    bioinf_errors_lower = [bioinf_data[p]['mean'] - bioinf_data[p]['lower'] if p in bioinf_data else 0 for p in positions]
    bioinf_errors_upper = [bioinf_data[p]['upper'] - bioinf_data[p]['mean'] if p in bioinf_data else 0 for p in positions]

    bio_errs = [bio_errors_lower, bio_errors_upper]
    comp_errs = [comp_errors_lower, comp_errors_upper]
    bioinf_errs = [bioinf_errors_lower, bioinf_errors_upper]

    ax.bar(x - width, bio_means, width, label='Biology', color=COLORS['Biology'], alpha=0.85,
           yerr=bio_errs, capsize=5, error_kw={'elinewidth': 1})
    ax.bar(x, comp_means, width, label='Computational Biology', color=COLORS['Computational Biology'], alpha=0.85,
           yerr=comp_errs, capsize=5, error_kw={'elinewidth': 1})
    ax.bar(x + width, bioinf_means, width, label='Bioinformatics', color=COLORS['Bioinformatics'], alpha=0.85,
           yerr=bioinf_errs, capsize=5, error_kw={'elinewidth': 1})

    ax.set_xlabel('Author Position', fontsize=12, fontweight='bold')
    ax.set_ylabel('P(female)', fontsize=12, fontweight='bold')
    ax.set_title('Primary Articles 2015-2025', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([p.capitalize() for p in positions])
    ax.set_ylim([0, 0.75])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    fig_path = OUTPUT_DIR / "Fig1A_position_breakdown.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Fig 1A saved to {fig_path}")
    return results


def main():
    """Run Figure 1A generation."""
    print("\n" + "=" * 70)
    print("FIGURE 1A: P(FEMALE) BY AUTHOR POSITION")
    print("=" * 70 + "\n")

    print("Loading author data from database...")
    data = get_author_data(start_year=2015, end_year=2025)
    print(f"✓ Loaded {len(data):,} author records\n")

    print("GENERATING FIGURE")
    print("-" * 70)
    results = generate_figure_1a(data)
    print()

    print("=" * 70)
    print("✓ FIGURE 1A COMPLETE!")
    print("=" * 70)
    print(f"\nOutput saved to: {OUTPUT_DIR / 'Fig1A_position_breakdown.png'}")
    print()


if __name__ == "__main__":
    main()
