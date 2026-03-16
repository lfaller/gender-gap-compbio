#!/usr/bin/env python3
"""Add only new bioinformatics authors to the database."""

from pathlib import Path
from dotenv import load_dotenv
import sys
import os

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gender_utils import GenderInference
from src.db_utils import GenderDatabase
import pandas as pd
from tqdm import tqdm

load_dotenv()

print("=" * 70)
print("ADDING NEW BIOINFORMATICS AUTHORS TO DATABASE")
print("=" * 70)

# Initialize database and inference engine
db = GenderDatabase(db_path="data/gender_data.db")
gi = GenderInference(cache_path="data/gender_cache.json")
print(f"✓ Database initialized")
print(f"✓ Loaded gender cache with {len(gi.cache)} entries\n")

# Load bioinformatics CSV
print("Loading bioinformatics papers...")
bioinf_df = pd.read_csv("data/processed/pubmed_bioinformatics_2015_2025.csv")
print(f"✓ Loaded {len(bioinf_df):,} bioinformatics papers\n")

# Extract unique authors from bioinformatics papers
print("Extracting unique bioinformatics authors...")
bioinf_authors = set()
for idx, row in bioinf_df.iterrows():
    positions = (
        eval(row["positions"])
        if isinstance(row["positions"], str)
        else row["positions"]
    )
    for author, position in positions:
        bioinf_authors.add(author)

print(f"Found {len(bioinf_authors):,} unique bioinformatics authors\n")

# Get existing authors from database
print("Checking which authors already in database...")
author_df = db.get_author_data_as_dataframe()
existing_authors = set(author_df['author'].unique()) if len(author_df) > 0 else set()
print(f"Database has {len(existing_authors):,} authors\n")

# Find new authors
new_authors = bioinf_authors - existing_authors
print(f"New authors to process: {len(new_authors):,}\n")

if len(new_authors) == 0:
    print("No new authors to process! All bioinformatics authors already in database.")
    db.close()
    sys.exit(0)

# Infer gender for new authors
print(f"Inferring gender for {len(new_authors):,} new authors...\n")
new_author_map = {}

for author in tqdm(new_authors, desc="Gender inference"):
    first_name = author.split()[0] if author else ""
    result = gi.infer_gender(first_name)
    new_author_map[author] = result
    
    # Insert into database immediately
    db.insert_author(
        name=author,
        p_female=result.get("probability"),
        gender=result["gender"],
        source=result["source"],
    )

print(f"\n✓ Inferred gender for {len(new_author_map):,} new authors\n")

# Now add bioinformatics papers and positions
print("Adding bioinformatics papers to database...")
bioinf_positions = []

for idx, row in bioinf_df.iterrows():
    pmid = row.get("pmid")
    year = row["year"]
    dataset = "Bioinformatics"
    positions = (
        eval(row["positions"]) if isinstance(row["positions"], str) else row["positions"]
    )
    
    # Insert paper
    paper_id = db.insert_paper(pmid=pmid, title=row.get("title", ""), year=year, dataset=dataset)
    
    # Insert author positions
    for author, position in positions:
        bioinf_positions.append(
            {
                "pmid": pmid,
                "year": year,
                "dataset": dataset,
                "author": author,
                "position": position,
            }
        )

db.batch_insert_positions(bioinf_positions)
print(f"✓ Added {len(bioinf_df):,} bioinformatics papers\n")

# Save gender cache
print(f"Saving gender cache ({len(gi.cache)} entries)...")
gi.save_cache()
print("✓ Cache saved\n")

# Print database statistics
print("=" * 70)
print("DATABASE STATISTICS")
print("=" * 70)
print(f"Papers:            {db.count_papers():,}")
print(f"Unique authors:    {db.count_unique_authors():,}")
print(f"Author positions:  {db.count_author_positions():,}")
print(f"Database file:     {Path(db.db_path).stat().st_size / 1024 / 1024:.1f} MB")
print()

db.close()

print("=" * 70)
print("✓ BIOINFORMATICS AUTHORS ADDED!")
print("=" * 70)
print()
