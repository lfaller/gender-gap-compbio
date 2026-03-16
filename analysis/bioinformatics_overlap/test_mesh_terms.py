#!/usr/bin/env python3
"""Test different MeSH terms for bioinformatics."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from Bio import Entrez

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.pubmed_fetcher import PubMedFetcher

load_dotenv()

email = os.getenv("NCBI_EMAIL")
Entrez.email = email
Entrez.api_key = os.getenv("NCBI_API_KEY")

print("Testing different MeSH terms for bioinformatics...\n")

# Test different query formats
queries = [
    '"Bioinformatics"[Majr]',
    '"Bioinformatics"[Mesh]',
    'bioinformatics[Majr]',
    'bioinformatics[Mesh]',
    '"Bioinformatics"[MAJR]',
]

for query in queries:
    print(f"Testing: {query}")
    try:
        search_handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=0
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()
        count = int(search_results.get("Count", 0))
        print(f"  Result count: {count:,}")
    except Exception as e:
        print(f"  Error: {e}")
    print()
