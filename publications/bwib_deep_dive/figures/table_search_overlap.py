#!/usr/bin/env python3
"""
Generate Table: PubMed Search Term Overlap

Shows how many papers appear in each combination of the three searches
(Biology, Computational Biology, Bioinformatics) with P(female) statistics
for first and last author positions.
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .utils import OUTPUT_DIR, get_author_data, save_table_to_files


def _load_pmid_sets():
    """Load and return three PMID sets from the processed CSV files."""
    bio_csv   = Path("data/processed/pubmed_biology_2015_2025.csv")
    comp_csv  = Path("data/processed/pubmed_compbio_2015_2025.csv")
    bioinf_csv = Path("data/processed/pubmed_bioinformatics_2015_2025.csv")

    bio_pmids   = set(pd.read_csv(bio_csv,   usecols=['pmid'])['pmid'].astype(str).unique())
    comp_pmids  = set(pd.read_csv(comp_csv,  usecols=['pmid'])['pmid'].astype(str).unique())
    bioinf_pmids = set(pd.read_csv(bioinf_csv, usecols=['pmid'])['pmid'].astype(str).unique())
    return bio_pmids, comp_pmids, bioinf_pmids


def _classify_region(pmid_str, bio, comp, bioinf):
    """Return which search region a PMID belongs to."""
    b = pmid_str in bio
    c = pmid_str in comp
    i = pmid_str in bioinf
    key = f"{'1' if b else '0'}{'1' if c else '0'}{'1' if i else '0'}"
    return key


def _compute_region_stats(author_data, bio, comp, bioinf):
    """Compute statistics (counts and P(female)) per region."""
    author_data = author_data.copy()
    author_data['region'] = author_data['pmid'].astype(str).apply(
        lambda p: _classify_region(p, bio, comp, bioinf)
    )

    region_labels = {
        '100': 'Biology only',
        '010': 'Computational Biology only',
        '110': 'Biology + Computational Biology',
        '001': 'Bioinformatics only',
        '101': 'Biology + Bioinformatics',
        '011': 'Computational Biology + Bioinformatics',
        '111': 'All three searches',
    }

    results = []
    total_papers = author_data['pmid'].nunique()

    for region_key in ['100', '010', '110', '001', '101', '011', '111']:
        reg_data = author_data[author_data['region'] == region_key]
        n_papers = reg_data['pmid'].nunique()
        pct = (n_papers / total_papers * 100) if total_papers > 0 else 0

        # P(female) by position
        pfemale_stats = {}
        for pos in ['first', 'last']:
            pos_data = reg_data[reg_data['position'] == pos]['p_female'].dropna()
            pfemale_stats[pos] = pos_data.mean() if len(pos_data) > 0 else None

        results.append({
            'Search Term Combination': region_labels[region_key],
            'Papers': n_papers,
            'Percent': pct,
            'P(female) First Author': pfemale_stats['first'],
            'P(female) Last Author': pfemale_stats['last'],
        })

    # Add total row
    results.append({
        'Search Term Combination': 'TOTAL',
        'Papers': total_papers,
        'Percent': 100.0,
        'P(female) First Author': None,
        'P(female) Last Author': None,
    })

    return pd.DataFrame(results)


def generate_table_overlap(bio_pmids, comp_pmids, bioinf_pmids, author_data):
    """Generate table showing search overlap statistics."""
    df = _compute_region_stats(author_data, bio_pmids, comp_pmids, bioinf_pmids)

    # Format for display
    df_display = df.copy()
    df_display['Papers'] = df_display['Papers'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "—")
    df_display['Percent'] = df_display['Percent'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
    df_display['P(female) First Author'] = df_display['P(female) First Author'].apply(
        lambda x: f"{x:.3f}" if pd.notna(x) else "—"
    )
    df_display['P(female) Last Author'] = df_display['P(female) Last Author'].apply(
        lambda x: f"{x:.3f}" if pd.notna(x) else "—"
    )

    return df_display


def main():
    """Run table generation."""
    print("\n" + "=" * 70)
    print("TABLE: PUBMED SEARCH TERM OVERLAP (2015-2025)")
    print("=" * 70 + "\n")

    print("Loading PMID sets from CSV files...")
    bio_pmids, comp_pmids, bioinf_pmids = _load_pmid_sets()
    print(f"  Biology:        {len(bio_pmids):,}")
    print(f"  Comp Bio:       {len(comp_pmids):,}")
    print(f"  Bioinformatics: {len(bioinf_pmids):,}\n")

    print("Loading author data...")
    author_data = get_author_data(start_year=2015, end_year=2025, show_overlap=False)
    print(f"✓ Loaded {len(author_data):,} author records\n")

    print("GENERATING TABLE")
    print("-" * 70)
    df = generate_table_overlap(bio_pmids, comp_pmids, bioinf_pmids, author_data)

    # Save table
    csv_path = OUTPUT_DIR / "Table_search_overlap.csv"
    df.to_csv(csv_path, index=False)
    print(f"✓ Table saved to {csv_path}")

    # Save markdown version
    md_path = OUTPUT_DIR / "Table_search_overlap.md"
    with open(md_path, 'w') as f:
        f.write("## Table. PubMed Search Term Overlap (2015-2025)\n\n")
        # Write markdown table manually
        columns = ['Search Term Combination', 'Papers', 'Percent', 'P(female) First Author', 'P(female) Last Author']
        f.write("| " + " | ".join(columns) + " |\n")
        f.write("| " + " | ".join(["---"] * len(columns)) + " |\n")
        for _, row in df.iterrows():
            values = [str(row[col]) for col in columns]
            f.write("| " + " | ".join(values) + " |\n")
        f.write("\n")
    print(f"✓ Markdown saved to {md_path}")

    print()
    print("=" * 70)
    print("✓ TABLE SEARCH OVERLAP COMPLETE!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
