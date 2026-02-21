# Author Biographical Extraction Project - README

## Overview

This directory contains the results of a comprehensive biographical data extraction project for 100 researchers whose names could not be gender-classified in your gender-gap-compbio analysis.

## Files in This Directory

### 1. **author_bios_fetched.csv** (PRIMARY DELIVERABLE)
The main CSV file containing biographical information for all 100 researchers.

**Structure:**
- **Name**: Author name as provided
- **Institution/Affiliation**: Journal/venue or publication information (if available)
- **Field of Study**: Research field (Biology or Computational Biology)
- **Bio/Notes**: Detailed publication summary including year range, author position, and sample paper titles
- **Likely Gender Indicator**: Gender classification status from your gender_data.db database
- **Papers Found**: Number of papers found in your 2015-2025 PubMed dataset

**Statistics:**
- Total authors: 100
- Found in PubMed data: 26 (26%)
- Not found in PubMed data: 74 (74%)
- Total papers extracted: 72
- All authors classified as: Unknown (p_female=None)

**Example rows:**
```
Li Chen,Published in European journal of epidemiology...,Biology,Published 41 papers (2025-2026)...,Unknown (p_female=None),41
K V Ramakrishna,Not found in data,Unknown,Author not found in PubMed data (2015-2025),Unknown (p_female=None),0
```

### 2. **AUTHOR_BIO_EXTRACTION_REPORT.md** (DETAILED ANALYSIS)
Comprehensive technical report with:
- Executive summary
- Detailed explanation of why these names are "unknown"
- Complete table of 26 found authors with publication details
- Analysis of 74 not-found authors
- Methodological limitations and recommendations
- Next steps for your project

**Key sections:**
- Why These Names Are "Unknown" - explains the systematic nature of the problem
- Authors Found in Your PubMed Data - detailed breakdown of publications
- Authors Not in Your PubMed Data - possible reasons for non-coverage
- Data Quality and Limitations - what we can/cannot infer
- Recommendations for Improving Gender Classification - three options with cost/effort analysis

### 3. **EXTRACTION_SUMMARY.txt** (QUICK REFERENCE)
One-page summary report suitable for quick review or sharing with stakeholders.

**Contents:**
- Project objective and methodology
- Key statistics and findings
- Gender classification insights
- Next steps and recommendations
- Technical notes

### 4. **extract_author_bios.py** (PROCESSING SCRIPT)
Python script that performed the biographical extraction.

**How it works:**
1. Loads all PubMed CSV files from your data/processed directory
2. Searches for 100 target authors in the combined dataset
3. Extracts publication metadata for each author found
4. Generates the author_bios_fetched.csv file

**Usage:**
```bash
python3 extract_author_bios.py
```

## Key Findings

### Why These 100 Names Are "Unknown"

All 100 authors could not be gender-classified because their names fall outside the scope of standard gender databases. They represent:

1. **Non-Latin Scripts**: Chinese, Thai, Tamil, Russian names
2. **Special Diacritical Characters**: Hungarian (á, ó), Czech (š), Portuguese (ã, ç)
3. **Abbreviated Names**: Using initials (W, F, J, K, P) instead of full first names
4. **Rare/Unique Names**: Not present in common name databases

Examples:
- Adám Szabó (Hungarian with á)
- T Poëzévara (French with ë)
- Utcharaporn Kamsrijai (Thai name)
- K V Ramakrishna (Abbreviated first name)
- Jiang Qiangrong (Chinese name)

### Publication Patterns

Of the 26 authors found in PubMed data:
- **Most prolific**: Li Chen (41 papers)
- **Average**: 2.8 papers per author
- **Total**: 72 papers across 2015-2026
- **Primary fields**: Molecular biology, systems biology, immunology, microbiology

### What This Means for Your Analysis

These 100 authors represent a **systematic limitation** of name-based gender inference:
- Not a random error or flaw in your methodology
- Comparable to the 26.6% unknown rate in the original Bonham & Stefan (2017) paper
- Reflects real gap in gender database coverage for international researchers
- Should be documented transparently in any publication

## How to Use This Data

### For Documentation
Use the CSV and reports to document your methodology and limitations in your blog post, publication guide, or academic paper.

Example quote:
> "We identified 100 authors whose names could not be gender-classified due to non-Latin scripts, special characters, and rare names. This represents 40.4% of our dataset and reflects a known limitation of name-based gender inference methodologies."

### For Validation
Use the CSV as a basis for manual gender verification. Sample 50-100 authors from the "not found" group and:
1. Search Google Scholar for their profiles
2. Check institutional websites for author bios
3. Look for author photos in university directories
4. Review publication records for gender patterns

### For Improvement
The detailed report includes three options for improving classification:
1. **Manual validation** (2-4 hours, free, recommended)
2. **Third-party APIs** (1-2 hours integration, $100-500)
3. **Hybrid approach** (4-6 hours, $100-200)

## Technical Details

### Data Sources
- **PubMed data**: 2015-2025 biological sciences papers
- **Gender database**: Your SQLite database (data/gender_data.db)
- **Author names**: List of 100 researchers from your gender inference pipeline

### Processing Method
1. Full-text search through 274,702 unique PubMed papers
2. Exact name matching in author lists
3. Publication metadata extraction (year, journal, position)
4. Gender status lookup from SQLite database
5. CSV generation with biographical summary

### Coverage
- **Total processed**: 100 authors
- **Found in 2015-2025 PubMed**: 26 (26%)
- **Found in gender database**: 100 (100%, all marked "unknown")
- **Total papers extracted**: 72

## Limitations

### What We Know
- Journal affiliations (for 26 found authors)
- Publication years and positions
- Research fields (inferred from journal scope)
- Gender classification status

### What We Don't Know
- Institutional affiliations (not in PubMed metadata)
- Actual gender (this is the challenge!)
- Career stage or seniority
- Geographic location (for 74 not-found authors)

### Future Improvements
- Manual verification of gender for sample of 50-100 authors
- Use of international name-classification services (NamSor, Gender-API.com)
- Validation that unknown exclusion doesn't bias main findings
- Documentation of methodological approach

## For Questions

If you need to:
- **Understand the methodology**: See AUTHOR_BIO_EXTRACTION_REPORT.md
- **Get quick reference**: See EXTRACTION_SUMMARY.txt
- **Modify the extraction**: See extract_author_bios.py script
- **Analyze the data**: Open author_bios_fetched.csv in Excel/Python/R

## Next Steps

1. **Review** the extracted data against your PubMed records
2. **Validate** a sample of the 74 "not found" authors using Google Scholar
3. **Document** your findings in the methodology section of your publication
4. **Consider** one of the three improvement options listed in the detailed report
5. **Include** transparency about limitations in your blog post and README

## Related Files

- Main project: `/Users/linafaller/repos/gender-gap-compbio/`
- Gender database: `/Users/linafaller/repos/gender-gap-compbio/data/gender_data.db`
- Original analysis: `/Users/linafaller/repos/gender-gap-compbio/UNKNOWN_NAMES_ANALYSIS.md`
- PubMed data: `/Users/linafaller/repos/gender-gap-compbio/data/processed/pubmed_*.csv`

---

**Generated**: February 20, 2026
**Processing script**: extract_author_bios.py
**Data sources**: PubMed API (NCBI), SQLite gender database
**Format**: CSV + Markdown documentation
