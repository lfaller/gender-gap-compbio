#!/usr/bin/env python3
"""Gender inference with SQLite database backend."""

from pathlib import Path
from dotenv import load_dotenv
import sys
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gender_utils import GenderInference
from src.db_utils import GenderDatabase
import pandas as pd
from tqdm import tqdm

load_dotenv()

print("="*70)
print("GENDER INFERENCE WITH SQLITE DATABASE")
print("="*70)

# Initialize database
db = GenderDatabase(db_path="data/gender_data.db")
print(f"✓ Database initialized at: data/gender_data.db\n")

# Load gender inference engine
gi = GenderInference(cache_path="data/gender_cache.json")
print(f"✓ Loaded gender cache with {len(gi.cache)} entries\n")

# Load all datasets
print("Loading paper data...")
bio_df = pd.read_csv("data/processed/pubmed_biology_2015_2025.csv")
comp_df = pd.read_csv("data/processed/pubmed_compbio_2015_2025.csv")
bioinf_df = pd.read_csv("data/processed/pubmed_bioinformatics_2015_2025.csv")

pubmed_df = pd.concat([bio_df, comp_df, bioinf_df], ignore_index=True)

print(f"✓ Loaded {len(pubmed_df)} PubMed papers")
print(f"  Biology:               {len(bio_df):,}")
print(f"  Computational Biology: {len(comp_df):,}")
print(f"  Bioinformatics:        {len(bioinf_df):,}\n")

# Extract unique author names and infer gender
print("Inferring gender for unique authors...")

all_dfs = [pubmed_df]
unique_authors = set()

for df in all_dfs:
    for idx, row in df.iterrows():
        positions = (
            eval(row["positions"])
            if isinstance(row["positions"], str)
            else row["positions"]
        )
        for author, position in positions:
            unique_authors.add(author)

print(f"Found {len(unique_authors)} unique authors")

# Infer gender and store in database
author_gender_map = {}
print(f"Inferring gender for {len(unique_authors)} unique authors...\n")

for author in tqdm(unique_authors, desc="Gender inference"):
    first_name = author.split()[0] if author else ""
    result = gi.infer_gender(first_name)
    author_gender_map[author] = result

    # Insert into database immediately
    db.insert_author(
        name=author,
        p_female=result.get("probability"),
        gender=result["gender"],
        source=result["source"],
    )

print(f"\n✓ Inferred gender for {len(author_gender_map)} authors\n")

# Process PubMed papers
print("Processing PubMed papers...")
pubmed_positions = []

for idx, row in pubmed_df.iterrows():
    pmid = row.get("pmid")
    year = row["year"]
    dataset = row["dataset"]
    positions = (
        eval(row["positions"]) if isinstance(row["positions"], str) else row["positions"]
    )

    # Insert paper
    paper_id = db.insert_paper(pmid=pmid, title=row.get("title", ""), year=year, dataset=dataset)

    # Insert author positions
    for author, position in positions:
        pubmed_positions.append(
            {
                "pmid": pmid,
                "year": year,
                "dataset": dataset,
                "author": author,
                "position": position,
            }
        )

db.batch_insert_positions(pubmed_positions)
print(f"✓ Processed {len(pubmed_df)} PubMed papers\n")

# Save gender cache
print(f"Saving gender cache ({len(gi.cache)} entries)...")
gi.save_cache()
print("✓ Cache saved\n")

# Print database statistics
print("="*70)
print("DATABASE STATISTICS")
print("="*70)
print(f"Papers:            {db.count_papers():,}")
print(f"Unique authors:    {db.count_unique_authors():,}")
print(f"Author positions:  {db.count_author_positions():,}")
print(f"Database file:     {Path(db.db_path).stat().st_size / 1024 / 1024:.1f} MB")
print()

db.close()

print("="*70)
print("✓ GENDER INFERENCE COMPLETE!")
print("="*70)
print("Data stored in: data/gender_data.db")
print()
