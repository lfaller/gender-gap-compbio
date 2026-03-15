#!/usr/bin/env python3
"""
Download archived datasets from Zenodo for quick reproduction.

Usage:
    python scripts/download_zenodo_data.py

This script downloads the Gender Gap in Computational Biology datasets
from Zenodo (https://zenodo.org/records/18894714) and extracts them
to the appropriate directories.

Note: Requires curl or requests library (automatically uses curl if available)
"""

import os
import subprocess
import sys
import gzip
import shutil
from pathlib import Path

ZENODO_RECORD = "18894714"
ZENODO_API = f"https://zenodo.org/api/records/{ZENODO_RECORD}/files"

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 40)
    print(text)
    print("=" * 40)

def fetch_file_list():
    """Get list of files from Zenodo API."""
    try:
        result = subprocess.run(
            ["curl", "-s", ZENODO_API],
            capture_output=True,
            text=True,
            check=True
        )
        # Simple extraction of keys using grep-like logic
        import json
        data = json.loads(result.stdout)
        return [f["key"] for f in data.get("entries", [])]
    except Exception as e:
        print(f"Error fetching file list: {e}")
        print("Attempting alternative method...")
        return []

def download_file(file_url, destination):
    """Download a file from Zenodo with curl."""
    # Ensure parent directory exists
    Path(destination).parent.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            ["curl", "-#", "-C", "-", "-o", destination, file_url],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to download {file_url}")
        return False

def decompress_database():
    """Decompress the gzipped database file."""
    gz_path = "data/gender_data.db.gz"
    db_path = "data/gender_data.db"

    if os.path.exists(gz_path):
        print(f"\nDecompressing database...")
        try:
            with gzip.open(gz_path, 'rb') as f_in:
                with open(db_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(gz_path)
            print(f"✓ Database ready at {db_path}")
            return True
        except Exception as e:
            print(f"✗ Failed to decompress: {e}")
            return False
    return False

def main():
    """Main download orchestration."""
    print_header("Gender Gap in Computational Biology")
    print(f"\nZenodo Record: https://zenodo.org/records/{ZENODO_RECORD}")
    print(f"DOI: 10.5281/zenodo.{ZENODO_RECORD}")

    # Check if curl is available
    try:
        subprocess.run(["curl", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n✗ Error: curl not found. Please install curl to download files.")
        print("  On macOS: brew install curl")
        print("  On Ubuntu: sudo apt-get install curl")
        sys.exit(1)

    # Create directories
    print("\nPreparing directories...")
    for directory in ["data/processed", "local", "scripts"]:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ {directory}/")

    # Fetch file list (with fallback)
    print("\nFetching file list from Zenodo...")
    files = fetch_file_list()

    if not files:
        # Fallback: list common files expected in the archive
        print("⚠ Could not fetch file list from API, using fallback list")
        files = [
            "pubmed_biology_2015_2025.csv",
            "pubmed_compbio_2015_2025.csv",
            "gender_data.db.gz",
            "scimagojr_2024_archived.csv",
        ]

    print(f"\nAvailable files ({len(files)}):")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")

    # Download files
    print("\nDownloading files...")
    print("-" * 40)

    downloaded = 0
    for filename in files:
        file_url = f"{ZENODO_API}/{filename}/content"

        # Determine destination
        if "scimagojr" in filename:
            dest = f"local/{filename}"
        elif filename.endswith(".db.gz"):
            dest = f"data/{filename}"
        else:
            dest = f"data/processed/{filename}"

        print(f"\n{filename}")
        if download_file(file_url, dest):
            print(f"✓ Saved to {dest}")
            downloaded += 1
        else:
            print(f"⚠ Skipped {filename}")

    # Decompress database
    decompress_database()

    # Summary
    print_header("Download Summary")
    print(f"\nDownloaded: {downloaded}/{len(files)} files")
    print("\n✓ Archive extraction complete!")

    print("\nNext steps:")
    print("  1. Verify files are in place:")
    print("     ls data/processed/*.csv")
    print("     ls data/gender_data.db")
    print("     ls local/scimagojr*.csv")
    print("\n  2. Run analysis immediately (no API calls needed):")
    print("     python cli.py analyze")
    print("     python cli.py figures")
    print("")

if __name__ == "__main__":
    main()
