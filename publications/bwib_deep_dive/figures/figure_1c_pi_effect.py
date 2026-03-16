#!/usr/bin/env python3
"""
Generate Figure 1C: The Female PI Effect

This figure directly replicates Bonham & Stefan's Fig 1C, showing how papers with
female last authors (presumed principal investigators) have significantly more
female co-authors at every position compared to papers with male last authors.

Reference: https://doi.org/10.1371/journal.pcbi.1005134
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.bootstrap import bootstrap_pfemale
from .utils import get_paper_author_gender_data, OUTPUT_DIR, COLORS


def generate_figure_1c(data):
    """
    Generate Fig 1C: P(female) by position stratified by PI gender.
    Compares papers with female vs male last authors.

    Args:
        data: DataFrame from get_paper_author_gender_data() with PI gender information

    Returns:
        DataFrame with results for each dataset-position-pi_gender combination
    """
    results = []

    for dataset in ['Biology', 'Computational Biology', 'Bioinformatics']:
        dataset_data = data[data['dataset'] == dataset]

        for pi_gender in ['male', 'female']:
            pi_data = dataset_data[dataset_data['last_author_gender'] == pi_gender]

            for position in ['first', 'second', 'other', 'penultimate']:
                pos_data = pi_data[pi_data['position'] == position]

                if len(pos_data) > 0:
                    probs = pos_data['p_female'].dropna().tolist()
                    mean, ci_lower, ci_upper = bootstrap_pfemale(probs, n_iterations=1000)

                    results.append({
                        'dataset': dataset,
                        'position': position,
                        'pi_gender': pi_gender,
                        'mean': mean,
                        'ci_lower': ci_lower,
                        'ci_upper': ci_upper
                    })

    results_df = pd.DataFrame(results)

    # Create figure
    fig, ax = plt.subplots(figsize=(16, 6))

    positions = ['first', 'second', 'other', 'penultimate']
    datasets = ['Biology', 'Computational Biology', 'Bioinformatics']

    colors_male = [COLORS['Biology_male'], COLORS['Computational Biology_male'], COLORS['Bioinformatics_male']]
    colors_female = [COLORS['Biology_female'], COLORS['Computational Biology_female'], COLORS['Bioinformatics_female']]

    for i, dataset in enumerate(datasets):
        ds_data = results_df[results_df['dataset'] == dataset]

        # Male PI
        male_pi = ds_data[ds_data['pi_gender'] == 'male'].sort_values('position')
        x_pos = [positions.index(p) + i*4.5 - 0.2 for p in male_pi['position']]

        ax.bar(x_pos, male_pi['mean'], width=0.35, color=colors_male[i], alpha=0.8,
               label=f'{dataset} (Male PI)',
               yerr=[male_pi['mean'] - male_pi['ci_lower'],
                     male_pi['ci_upper'] - male_pi['mean']],
               capsize=3, error_kw={'elinewidth': 1})

        # Female PI
        female_pi = ds_data[ds_data['pi_gender'] == 'female'].sort_values('position')
        x_pos = [positions.index(p) + i*4.5 + 0.2 for p in female_pi['position']]

        ax.bar(x_pos, female_pi['mean'], width=0.35, color=colors_female[i], alpha=0.8,
               label=f'{dataset} (Female PI)',
               yerr=[female_pi['mean'] - female_pi['ci_lower'],
                     female_pi['ci_upper'] - female_pi['mean']],
               capsize=3, error_kw={'elinewidth': 1})

    ax.set_xlabel('Author Position', fontsize=12, fontweight='bold')
    ax.set_ylabel('P(female)', fontsize=12, fontweight='bold')
    ax.set_title('Primary Articles 2015-2025', fontsize=13, fontweight='bold')
    ax.set_ylim([0, 0.75])
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(axis='y', alpha=0.3)

    # Custom x-axis labels for 3 datasets
    section_offsets = [0, 4.5, 9.0]
    section_labels = ['Biology', 'Computational Biology', 'Bioinformatics']
    tick_positions = []
    tick_labels = []
    for offset, ds_label in zip(section_offsets, section_labels):
        for j, pos in enumerate(positions):
            tick_positions.append(j + offset)
            tick_labels.append(f'{pos.capitalize()}\n({ds_label[:4]})')

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=9)

    plt.tight_layout()
    fig_path = OUTPUT_DIR / "Fig1C_pi_effect.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Fig 1C saved to {fig_path}")
    return results_df


def main():
    """Run Figure 1C generation."""
    print("\n" + "=" * 70)
    print("FIGURE 1C: THE FEMALE PI EFFECT")
    print("=" * 70 + "\n")

    print("Loading paper-author gender data for PI effect...")
    data = get_paper_author_gender_data(start_year=2015, end_year=2025)
    print(f"✓ Loaded {len(data):,} author records with PI gender\n")

    print("GENERATING FIGURE")
    print("-" * 70)
    results = generate_figure_1c(data)
    print()

    print("=" * 70)
    print("✓ FIGURE 1C COMPLETE!")
    print("=" * 70)
    print(f"\nOutput saved to: {OUTPUT_DIR / 'Fig1C_pi_effect.png'}")
    print()


if __name__ == "__main__":
    main()
