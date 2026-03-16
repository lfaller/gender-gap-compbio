#!/usr/bin/env python3
"""
Reproduce Bonham & Stefan (2017) figures and tables with current data (2015-2025).

LEGACY WRAPPER: This script now calls the modular figure/table generation scripts
from publications/bwib_deep_dive/figures/ to regenerate all outputs at once.

Individual figures and tables can be run independently. See:
  publications/bwib_deep_dive/figures/README.md

This replicates:
- Fig 1A: P(female) by author position
- Fig 1B: P(female) over time
- Fig 1C: P(female) by position and PI gender
- Table 1: Proportion of female authors
- Table 2: Proportion of female authors with female/male PI

Reference: https://doi.org/10.1371/journal.pcbi.1005134
"""

from pathlib import Path
import sys

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from publications.bwib_deep_dive.figures import (
    figure_1a_position_breakdown,
    figure_1b_temporal_trend,
    figure_1c_pi_effect,
    table_1_female_proportion,
    table_2_pi_effect_statistics,
    table_search_overlap,
)


def main():
    """Run all analyses to reproduce Bonham & Stefan figures and tables."""
    print("\n" + "=" * 70)
    print("REPRODUCING BONHAM & STEFAN (2017) WITH 2015-2025 DATA")
    print("=" * 70 + "\n")

    print("Running modular figure and table generation scripts...")
    print("-" * 70)
    print()

    # Generate Tables
    print("GENERATING TABLES")
    print("-" * 70)
    table_1_female_proportion.main()
    table_2_pi_effect_statistics.main()
    table_search_overlap.main()

    # Generate Figures
    print("GENERATING FIGURES")
    print("-" * 70)
    figure_1a_position_breakdown.main()
    figure_1b_temporal_trend.main()
    figure_1c_pi_effect.main()
    print()

    output_dir = Path("publications/bwib_deep_dive")
    print("=" * 70)
    print("✓ ALL REPRODUCTIONS COMPLETE!")
    print("=" * 70)
    print(f"\nOutput files saved to: {output_dir}")
    print("\nFiles created:")
    print("  Figures:")
    print("    - Fig1A_position_breakdown.png")
    print("    - Fig1B_temporal_trend.png")
    print("    - Fig1C_pi_effect.png")
    print("  Tables:")
    print("    - Table1_proportion_female_authors.csv & .md")
    print("    - Table2_female_authors_with_female_pi.csv & .md")
    print("    - Table_search_overlap.csv & .md")
    print()
    print("For individual figure regeneration, see:")
    print("  publications/bwib_deep_dive/figures/README.md")
    print()


if __name__ == "__main__":
    main()
