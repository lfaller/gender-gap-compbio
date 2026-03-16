"""
BWIB Deep Dive Blog Post Figures and Tables

This package contains modular scripts for generating all figures and tables
referenced in the BWIB Deep Dive blog post (2015-2025 analysis).

Scripts can be run independently:
- figure_1a_position_breakdown.py: P(female) by author position (4-category view)
- figure_1b_temporal_trend.py: P(female) over time
- figure_1c_pi_effect.py: P(female) by position and PI gender
- table_1_female_proportion.py: Proportion of female authors
- table_2_pi_effect_statistics.py: PI effect statistics
- table_search_overlap.py: Search term overlap statistics

Or all together using the legacy wrapper:
- ../reproduce_bonham_stefan.py

Reference: https://doi.org/10.1371/journal.pcbi.1005134
"""

__all__ = [
    "figure_1a_position_breakdown",
    "figure_1b_temporal_trend",
    "figure_1c_pi_effect",
    "table_1_female_proportion",
    "table_2_pi_effect_statistics",
    "table_search_overlap",
    "utils",
]
