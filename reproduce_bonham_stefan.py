#!/usr/bin/env python3
"""
Reproduce Bonham & Stefan (2017) figures and tables with current data (2015-2025).

This script replicates:
- Fig 1A: P(female) by author position
- Fig 1B: P(female) over time
- Fig 1C: P(female) by position and PI gender
- Table 1: Proportion of female authors
- Table 2: Proportion of female authors with female/male PI

Reference: https://doi.org/10.1371/journal.pcbi.1005134
"""

import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from src.bootstrap import bootstrap_by_multiple_groups, bootstrap_pfemale

# Configuration
DB_PATH = "data/gender_data.db"
OUTPUT_DIR = Path("outputs/bonham_stefan_reproduction")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_author_data(start_year=2015, end_year=2025):
    """Load author data from database and CSV files to distinguish Biology vs Comp Bio."""
    conn = sqlite3.connect(DB_PATH)

    # Load biology data
    bio_query = """
    SELECT
        a.name,
        a.p_female,
        ap.position,
        'Biology' as dataset,
        p.year,
        p.pmid
    FROM author_positions ap
    JOIN authors a ON ap.author_id = a.id
    JOIN papers p ON ap.paper_id = p.id
    WHERE p.year >= ? AND p.year <= ?
    ORDER BY p.pmid
    """

    bio_df = pd.read_sql_query(bio_query, conn, params=(start_year, end_year))

    # Load computational biology PMIDs from CSV to filter
    comp_pmids = set()
    comp_csv = Path("data/processed/pubmed_compbio_2015_2025.csv")
    if comp_csv.exists():
        comp_csv_df = pd.read_csv(comp_csv, usecols=['pmid'])
        comp_pmids = set(comp_csv_df['pmid'].astype(str).unique())

    # Mark papers that are in the comp bio CSV as Computational Biology
    bio_df['dataset'] = bio_df['pmid'].astype(str).apply(
        lambda x: 'Computational Biology' if x in comp_pmids else 'Biology'
    )

    conn.close()
    return bio_df


def get_paper_author_gender_data(start_year=2015, end_year=2025):
    """Get paper-level data for PI effect analysis with Biology vs Comp Bio distinction."""
    conn = sqlite3.connect(DB_PATH)

    # Get last author gender for each paper
    query = """
    WITH last_authors AS (
        SELECT
            ap.paper_id,
            a.p_female as last_author_pfemale
        FROM author_positions ap
        JOIN authors a ON ap.author_id = a.id
        WHERE ap.position = 'last'
    )
    SELECT
        a.name,
        a.p_female,
        ap.position,
        'Biology' as dataset,
        p.year,
        p.pmid,
        CASE
            WHEN la.last_author_pfemale > 0.8 THEN 'female'
            WHEN la.last_author_pfemale < 0.2 THEN 'male'
            ELSE 'unknown'
        END as last_author_gender
    FROM author_positions ap
    JOIN authors a ON ap.author_id = a.id
    JOIN papers p ON ap.paper_id = p.id
    JOIN last_authors la ON p.id = la.paper_id
    WHERE p.year >= ? AND p.year <= ?
    AND la.last_author_pfemale IS NOT NULL
    ORDER BY p.pmid
    """

    df = pd.read_sql_query(query, conn, params=(start_year, end_year))

    # Load computational biology PMIDs from CSV to filter
    comp_pmids = set()
    comp_csv = Path("data/processed/pubmed_compbio_2015_2025.csv")
    if comp_csv.exists():
        comp_csv_df = pd.read_csv(comp_csv, usecols=['pmid'])
        comp_pmids = set(comp_csv_df['pmid'].astype(str).unique())

    # Mark papers that are in the comp bio CSV as Computational Biology
    df['dataset'] = df['pmid'].astype(str).apply(
        lambda x: 'Computational Biology' if x in comp_pmids else 'Biology'
    )

    conn.close()
    return df


def table1_proportion_of_female_authors(data):
    """
    Generate Table 1: Proportion of female authors by dataset and position.
    Matches Bonham & Stefan Table 1 format.
    """
    results = []

    for dataset in ['Biology', 'Computational Biology']:
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
        f.write("## Table 1. Proportion of Female Authors\n\n")
        f.write("| Dataset | Position | Mean | 95% CI Lower | 95% CI Upper |\n")
        f.write("|---------|----------|------|-------------|-------------|\n")
        for _, row in df.iterrows():
            f.write(f"| {row['Dataset']} | {row['Position']} | {row['Mean']:.3f} | {row['95% CI Lower']:.3f} | {row['95% CI Upper']:.3f} |\n")

    print("✓ Table 1 saved")
    return df


def table2_proportion_female_with_female_pi(data):
    """
    Generate Table 2: Proportion of female authors by PI gender.
    Matches Bonham & Stefan Table 2 format.
    """
    results = []

    for dataset in ['Biology', 'Computational Biology']:
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
        f.write("## Table 2. Proportion of Female Authors by PI Gender\n\n")
        f.write("| Dataset | Position | PI Gender | Mean | 95% CI Lower | 95% CI Upper |\n")
        f.write("|---------|----------|-----------|------|-------------|-------------|\n")
        for _, row in df.iterrows():
            f.write(f"| {row['Dataset']} | {row['Position']} | {row['PI Gender']} | {row['Mean']:.3f} | {row['95% CI Lower']:.3f} | {row['95% CI Upper']:.3f} |\n")

    print("✓ Table 2 saved")
    return df


def fig1a_position_breakdown(data):
    """
    Generate Fig 1A: Mean P(female) by author position.
    Compares Biology vs Computational Biology.
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

    for pos in positions:
        bio_row = results[(results['dataset'] == 'Biology') & (results['position'] == pos)]
        comp_row = results[(results['dataset'] == 'Computational Biology') & (results['position'] == pos)]

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

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(positions))
    width = 0.35

    bio_means = [bio_data[p]['mean'] if p in bio_data else 0 for p in positions]
    bio_errors_lower = [bio_data[p]['mean'] - bio_data[p]['lower'] if p in bio_data else 0 for p in positions]
    bio_errors_upper = [bio_data[p]['upper'] - bio_data[p]['mean'] if p in bio_data else 0 for p in positions]
    comp_means = [comp_data[p]['mean'] if p in comp_data else 0 for p in positions]
    comp_errors_lower = [comp_data[p]['mean'] - comp_data[p]['lower'] if p in comp_data else 0 for p in positions]
    comp_errors_upper = [comp_data[p]['upper'] - comp_data[p]['mean'] if p in comp_data else 0 for p in positions]

    bio_errs = [bio_errors_lower, bio_errors_upper]
    comp_errs = [comp_errors_lower, comp_errors_upper]

    ax.bar(x - width/2, bio_means, width, label='Biology', color='black', alpha=0.8,
           yerr=bio_errs, capsize=5, error_kw={'elinewidth': 1})
    ax.bar(x + width/2, comp_means, width, label='Comp Bio', color='gray', alpha=0.8,
           yerr=comp_errs, capsize=5, error_kw={'elinewidth': 1})

    ax.set_xlabel('Author Position', fontsize=12, fontweight='bold')
    ax.set_ylabel('P(female)', fontsize=12, fontweight='bold')
    ax.set_title('Primary Articles 2015-2025', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([p.capitalize() for p in positions])
    ax.set_ylim([0, 0.5])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    fig_path = OUTPUT_DIR / "Fig1A_position_breakdown.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Fig 1A saved to {fig_path}")
    return results


def fig1b_temporal_trend(data):
    """
    Generate Fig 1B: P(female) over time.
    Line plot showing trend for Biology vs Computational Biology.
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

    ax.errorbar(bio_data['year'], bio_data['mean'],
                yerr=[bio_data['mean'] - bio_data['ci_lower'],
                      bio_data['ci_upper'] - bio_data['mean']],
                marker='o', linestyle='-', label='Biology', color='black', alpha=0.8)

    ax.errorbar(comp_data['year'], comp_data['mean'],
                yerr=[comp_data['mean'] - comp_data['ci_lower'],
                      comp_data['ci_upper'] - comp_data['mean']],
                marker='s', linestyle='--', label='Comp Bio', color='gray', alpha=0.8)

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


def fig1c_pi_effect(data):
    """
    Generate Fig 1C: P(female) by position stratified by PI gender.
    Compares papers with female vs male last authors.
    """
    results = []

    for dataset in ['Biology', 'Computational Biology']:
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
    fig, ax = plt.subplots(figsize=(14, 6))

    positions = ['first', 'second', 'other', 'penultimate']
    datasets = ['Biology', 'Computational Biology']

    colors_male = ['black', 'gray']
    colors_female = ['darkred', 'lightcoral']

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
    ax.set_ylim([0, 0.6])
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(axis='y', alpha=0.3)

    # Custom x-axis labels
    ax.set_xticks(range(len(positions)*2))
    ax.set_xticklabels(
        [f'{p}\n(Bio)' for p in positions] + [f'{p}\n(Comp)' for p in positions],
        fontsize=10
    )

    plt.tight_layout()
    fig_path = OUTPUT_DIR / "Fig1C_pi_effect.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Fig 1C saved to {fig_path}")
    return results_df


def main():
    """Run all analyses to reproduce Bonham & Stefan figures and tables."""
    print("\n" + "=" * 70)
    print("REPRODUCING BONHAM & STEFAN (2017) WITH 2015-2025 DATA")
    print("=" * 70 + "\n")

    # Load data
    print("Loading author data from database...")
    data = get_author_data(start_year=2015, end_year=2025)
    print(f"✓ Loaded {len(data)} author records\n")

    print("Loading paper-author gender data for PI effect...")
    pi_data = get_paper_author_gender_data(start_year=2015, end_year=2025)
    print(f"✓ Loaded {len(pi_data)} author records with PI gender\n")

    # Generate Tables
    print("GENERATING TABLES")
    print("-" * 70)
    table1 = table1_proportion_of_female_authors(data)
    table2 = table2_proportion_female_with_female_pi(pi_data)
    print()

    # Generate Figures
    print("GENERATING FIGURES")
    print("-" * 70)
    fig1a = fig1a_position_breakdown(data)
    fig1b = fig1b_temporal_trend(data)
    fig1c = fig1c_pi_effect(pi_data)
    print()

    print("=" * 70)
    print("✓ ALL REPRODUCTIONS COMPLETE!")
    print("=" * 70)
    print(f"\nOutput files saved to: {OUTPUT_DIR}")
    print("\nFiles created:")
    print("  Figures:")
    print("    - Fig1A_position_breakdown.png")
    print("    - Fig1B_temporal_trend.png")
    print("    - Fig1C_pi_effect.png")
    print("  Tables:")
    print("    - Table1_proportion_female_authors.csv & .md")
    print("    - Table2_female_authors_with_female_pi.csv & .md")
    print()


if __name__ == "__main__":
    main()
