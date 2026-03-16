"""
Shared utilities for BWIB Deep Dive analysis figures.

Provides common data loading and helper functions for all figures and tables.
"""

import sqlite3
from pathlib import Path
import pandas as pd


# Okabe-Ito colorblind-friendly palette
# Reference: https://jfly.uni-koeln.de/color/
COLORS = {
    'Biology':                         '#E69F00',   # Orange
    'Computational Biology':           '#0072B2',   # Blue
    'Bioinformatics':                  '#009E73',   # Teal
    'Overlap':                         '#CC79A7',   # Pink
    # Fig 1C PI-gender pairs (male = base dataset color)
    'Biology_male':                    '#E69F00',
    'Biology_female':                  '#D55E00',   # Vermillion
    'Computational Biology_male':      '#0072B2',
    'Computational Biology_female':    '#CC79A7',   # Pink
    'Bioinformatics_male':             '#009E73',
    'Bioinformatics_female':           '#56B4E9',   # Sky Blue
}

# Configuration
DB_PATH = "data/gender_data.db"
OUTPUT_DIR = Path("publications/bwib_deep_dive")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _label_dataset(pmid_str, bio_pmids, comp_pmids, bioinf_pmids, show_overlap=False):
    """Assign a dataset label to a paper by its PMID string.

    When show_overlap=False (default):
        Priority: Computational Biology > Bioinformatics > Biology
        Papers appear in exactly one group.

    When show_overlap=True:
        Papers in 2+ searches -> 'Overlap'
        Papers in exactly 1 search -> that search's name
        Papers in 0 searches -> 'Biology' (default fallback)
    """
    in_bio    = pmid_str in bio_pmids
    in_comp   = pmid_str in comp_pmids
    in_bioinf = pmid_str in bioinf_pmids

    if show_overlap:
        match_count = int(in_bio) + int(in_comp) + int(in_bioinf)
        if match_count >= 2:
            return 'Overlap'
        elif in_comp:
            return 'Computational Biology'
        elif in_bioinf:
            return 'Bioinformatics'
        else:
            return 'Biology'
    else:
        # Original priority logic
        if in_comp:
            return 'Computational Biology'
        elif in_bioinf:
            return 'Bioinformatics'
        else:
            return 'Biology'


def get_author_data(start_year=2015, end_year=2025, show_overlap=False):
    """
    Load author data from database and CSV files to distinguish Biology vs Comp Bio vs Bioinformatics.

    Args:
        start_year: Start year for data range (default 2015)
        end_year: End year for data range (default 2025)
        show_overlap: If True, show papers in 2+ searches as 'Overlap' category (default False)

    Returns:
        DataFrame with columns: name, p_female, position, dataset, year, pmid
    """
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

    # Load biology PMIDs from CSV to filter
    bio_pmids = set()
    bio_csv = Path("data/processed/pubmed_biology_2015_2025.csv")
    if bio_csv.exists():
        bio_csv_df = pd.read_csv(bio_csv, usecols=['pmid'])
        bio_pmids = set(bio_csv_df['pmid'].astype(str).unique())

    # Load computational biology PMIDs from CSV to filter
    comp_pmids = set()
    comp_csv = Path("data/processed/pubmed_compbio_2015_2025.csv")
    if comp_csv.exists():
        comp_csv_df = pd.read_csv(comp_csv, usecols=['pmid'])
        comp_pmids = set(comp_csv_df['pmid'].astype(str).unique())

    # Load bioinformatics PMIDs from CSV to filter
    bioinf_pmids = set()
    bioinf_csv = Path("data/processed/pubmed_bioinformatics_2015_2025.csv")
    if bioinf_csv.exists():
        bioinf_csv_df = pd.read_csv(bioinf_csv, usecols=['pmid'])
        bioinf_pmids = set(bioinf_csv_df['pmid'].astype(str).unique())

    # Label papers by dataset membership
    bio_df['dataset'] = bio_df['pmid'].astype(str).apply(
        lambda p: _label_dataset(p, bio_pmids, comp_pmids, bioinf_pmids, show_overlap)
    )

    conn.close()
    return bio_df


def get_paper_author_gender_data(start_year=2015, end_year=2025, show_overlap=False):
    """
    Get paper-level data for PI effect analysis with Biology vs Comp Bio vs Bioinformatics distinction.

    Args:
        start_year: Start year for data range (default 2015)
        end_year: End year for data range (default 2025)
        show_overlap: If True, show papers in 2+ searches as 'Overlap' category (default False)

    Returns:
        DataFrame with columns: name, p_female, position, dataset, year, pmid, last_author_gender
    """
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

    # Load biology PMIDs from CSV to filter
    bio_pmids = set()
    bio_csv = Path("data/processed/pubmed_biology_2015_2025.csv")
    if bio_csv.exists():
        bio_csv_df = pd.read_csv(bio_csv, usecols=['pmid'])
        bio_pmids = set(bio_csv_df['pmid'].astype(str).unique())

    # Load computational biology PMIDs from CSV to filter
    comp_pmids = set()
    comp_csv = Path("data/processed/pubmed_compbio_2015_2025.csv")
    if comp_csv.exists():
        comp_csv_df = pd.read_csv(comp_csv, usecols=['pmid'])
        comp_pmids = set(comp_csv_df['pmid'].astype(str).unique())

    # Load bioinformatics PMIDs from CSV to filter
    bioinf_pmids = set()
    bioinf_csv = Path("data/processed/pubmed_bioinformatics_2015_2025.csv")
    if bioinf_csv.exists():
        bioinf_csv_df = pd.read_csv(bioinf_csv, usecols=['pmid'])
        bioinf_pmids = set(bioinf_csv_df['pmid'].astype(str).unique())

    # Label papers by dataset membership
    df['dataset'] = df['pmid'].astype(str).apply(
        lambda p: _label_dataset(p, bio_pmids, comp_pmids, bioinf_pmids, show_overlap)
    )

    conn.close()
    return df


def save_table_to_files(df, prefix, title):
    """
    Save a table to both CSV and markdown formats.

    Args:
        df: DataFrame to save
        prefix: Filename prefix (e.g., "Table1_proportion_female_authors")
        title: Human-readable title for markdown file
    """
    # Save as CSV
    csv_path = OUTPUT_DIR / f"{prefix}.csv"
    df.to_csv(csv_path, index=False)

    print(f"✓ {title} saved to {csv_path}")
    return csv_path
