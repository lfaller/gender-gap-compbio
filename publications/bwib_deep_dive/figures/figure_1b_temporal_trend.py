#!/usr/bin/env python3
"""
Generate Figure 1B: P(female) Over Time (Temporal Trend)

This figure directly replicates Bonham & Stefan's Fig 1B, showing how female
representation has changed year-by-year from 2015-2025. Shows trends for both
Biology and Computational Biology.

Reference: https://doi.org/10.1371/journal.pcbi.1005134
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.bootstrap import bootstrap_by_multiple_groups
from .utils import get_author_data, OUTPUT_DIR, COLORS


def generate_figure_1b(data):
    """
    Generate Fig 1B: P(female) over time.
    Line plot showing trend for Biology, Computational Biology, and Bioinformatics.

    Args:
        data: DataFrame from get_author_data() with columns:
              name, p_female, position, dataset, year, pmid

    Returns:
        DataFrame with bootstrap results for each dataset-year combination
    """
    results = bootstrap_by_multiple_groups(
        data,
        group_cols=['dataset', 'year'],
        prob_col='p_female',
        n_iterations=1000
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    bio_data = results[results['dataset'] == 'Biology'].sort_values('year')
    comp_data = results[results['dataset'] == 'Computational Biology'].sort_values('year')
    bioinf_data = results[results['dataset'] == 'Bioinformatics'].sort_values('year')

    ax.errorbar(bio_data['year'], bio_data['mean'],
                yerr=[bio_data['mean'] - bio_data['ci_lower'],
                      bio_data['ci_upper'] - bio_data['mean']],
                marker='o', linestyle='-', label='Biology', color=COLORS['Biology'], alpha=0.8)

    ax.errorbar(comp_data['year'], comp_data['mean'],
                yerr=[comp_data['mean'] - comp_data['ci_lower'],
                      comp_data['ci_upper'] - comp_data['mean']],
                marker='s', linestyle='--', label='Computational Biology', color=COLORS['Computational Biology'], alpha=0.8)

    ax.errorbar(bioinf_data['year'], bioinf_data['mean'],
                yerr=[bioinf_data['mean'] - bioinf_data['ci_lower'],
                      bioinf_data['ci_upper'] - bioinf_data['mean']],
                marker='^', linestyle=':', label='Bioinformatics', color=COLORS['Bioinformatics'], alpha=0.8)

    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('P(female)', fontsize=12, fontweight='bold')
    ax.set_title('Primary Articles', fontsize=13, fontweight='bold')
    ax.set_ylim([0, 0.5])
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    fig_path = OUTPUT_DIR / "Fig1B_temporal_trend.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Fig 1B saved to {fig_path}")
    return results


def main():
    """Run Figure 1B generation."""
    print("\n" + "=" * 70)
    print("FIGURE 1B: P(FEMALE) OVER TIME (TEMPORAL TREND)")
    print("=" * 70 + "\n")

    print("Loading author data from database...")
    data = get_author_data(start_year=2015, end_year=2025)
    print(f"✓ Loaded {len(data):,} author records\n")

    print("GENERATING FIGURE")
    print("-" * 70)
    results = generate_figure_1b(data)
    print()

    print("=" * 70)
    print("✓ FIGURE 1B COMPLETE!")
    print("=" * 70)
    print(f"\nOutput saved to: {OUTPUT_DIR / 'Fig1B_temporal_trend.png'}")
    print()


if __name__ == "__main__":
    main()
