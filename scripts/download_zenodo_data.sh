#!/bin/bash
# Download archived datasets from Zenodo for quick reproduction
# Usage: bash scripts/download_zenodo_data.sh

set -e

ZENODO_RECORD="18894714"
ZENODO_URL="https://zenodo.org/api/records/${ZENODO_RECORD}/files"

echo "========================================"
echo "Downloading datasets from Zenodo"
echo "========================================"
echo ""
echo "Record: https://zenodo.org/records/${ZENODO_RECORD}"
echo "DOI: 10.5281/zenodo.${ZENODO_RECORD}"
echo ""

# Create directories
mkdir -p data/processed
mkdir -p local

# List available files
echo "Fetching file list from Zenodo..."
FILES=$(curl -s "${ZENODO_URL}" | grep -o '"key":"[^"]*"' | sed 's/"key":"//g' | sed 's/"//g')

echo "Available files:"
echo "$FILES" | nl
echo ""

# Download each file
echo "Downloading files..."
for FILE in $FILES; do
  FILE_URL="${ZENODO_URL}/${FILE}/content"
  echo "Downloading: $FILE"

  # Determine destination
  if [[ "$FILE" == *"scimagojr"* ]]; then
    DEST="local/$FILE"
  elif [[ "$FILE" == *"gender_data.db"* ]]; then
    DEST="data/$FILE"
  else
    DEST="data/processed/$FILE"
  fi

  # Download with resume capability
  curl -# -C - -o "$DEST" "$FILE_URL"
  echo "✓ Saved to $DEST"
done

# Decompress database if needed
if [ -f "data/gender_data.db.gz" ]; then
  echo ""
  echo "Decompressing database..."
  gunzip -f data/gender_data.db.gz
  echo "✓ Database ready at data/gender_data.db"
fi

echo ""
echo "========================================"
echo "✓ Download complete!"
echo "========================================"
echo ""
echo "Quick analysis (no API calls needed):"
echo "  python cli.py analyze"
echo "  python cli.py figures"
echo ""
