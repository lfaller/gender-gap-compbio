#!/usr/bin/env python3
"""
Classify new bioinformatics authors using gender-guesser first, then Groq for unknowns.

Layer 1: gender-guesser (offline, ~45k names)
Layer 2: Groq LLM for unknown names
"""

from pathlib import Path
from dotenv import load_dotenv
import sys
import os
import sqlite3

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gender_utils import GenderInference
from src.db_utils import GenderDatabase
import pandas as pd
from tqdm import tqdm

load_dotenv()

print("=" * 70)
print("CLASSIFYING NEW BIOINFORMATICS AUTHORS")
print("=" * 70)

# Initialize database and gender inference
db = GenderDatabase(db_path="data/gender_data.db")
gi = GenderInference(cache_path="data/gender_cache.json")
print(f"✓ Database initialized")
print(f"✓ Loaded gender cache with {len(gi.cache)} entries\n")

# Get new authors (those with unknown/null gender added by bioinformatics)
print("Finding newly added bioinformatics authors...")
conn = sqlite3.connect("data/gender_data.db")
cursor = conn.cursor()
cursor.execute("""
    SELECT DISTINCT a.id, a.name 
    FROM authors a
    WHERE (a.gender IS NULL OR a.gender = 'unknown')
    AND LENGTH(a.name) > 1
    LIMIT 100000
""")
unknown_authors = cursor.fetchall()
conn.close()

print(f"Found {len(unknown_authors):,} authors with unknown gender\n")

if len(unknown_authors) == 0:
    print("No unknown authors to classify!")
    db.close()
    sys.exit(0)

# Layer 1: Classify using gender-guesser (offline)
print("Layer 1: Classifying with gender-guesser...")
gender_guesser_results = []
groq_needed = []

for author_id, full_name in tqdm(unknown_authors, desc="gender-guesser"):
    first_name = full_name.split()[0] if full_name else ""
    if not first_name:
        groq_needed.append((author_id, full_name))
        continue
    
    result = gi.infer_gender(first_name)
    
    if result["gender"] == "unknown":
        # Need Groq classification
        groq_needed.append((author_id, full_name))
    else:
        # Successfully classified with gender-guesser
        gender_guesser_results.append((author_id, result))

print(f"✓ Gender-guesser classified: {len(gender_guesser_results):,}")
print(f"✓ Need Groq classification: {len(groq_needed):,}\n")

# Update database with gender-guesser results
print("Updating database with gender-guesser results...")
for author_id, result in gender_guesser_results:
    conn = sqlite3.connect("data/gender_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE authors 
        SET gender = ?, p_female = ?, source = ?
        WHERE id = ?
    """, (result["gender"], result["probability"], result["source"], author_id))
    conn.commit()
    conn.close()

print(f"✓ Updated {len(gender_guesser_results):,} authors\n")

# Layer 2: Prepare Groq classification for unknowns
if len(groq_needed) > 0:
    print(f"Layer 2: Preparing {len(groq_needed):,} names for Groq classification")
    print("\nTo classify the remaining unknown names, run:")
    print("  python scripts/classify_names_retry.py")
    print()
else:
    print("All authors successfully classified!")

# Save updated cache
gi.save_cache()
print(f"✓ Saved gender cache\n")

db.close()

print("=" * 70)
print("✓ CLASSIFICATION COMPLETE")
print("=" * 70)
print()
