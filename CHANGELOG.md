# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Date Range Extended:** Updated analysis to include 2025 data (2015–2025)
  - PubMed data now includes 430,000+ papers instead of 410,000
  - COVID-19 recovery period extended to 2022–2025
  - Temporal trend analysis now includes latest year

### Added
- **Professional CLI Tool:** New `cli.py` using Click framework for flexible pipeline execution
  - Modular subcommands: `fetch`, `infer`, `analyze`, `figures`, `run`
  - Flexible parameters: `--start-year`, `--end-year`, `--append` flags
  - Support for custom date ranges and incremental data updates
  - Built-in help for each command (`python cli.py COMMAND --help`)
  - Professional error handling and user-friendly feedback
  - Replaces one-off scripts with unified interface
- **SQLite Database Backend:** Replaced CSV-based storage with SQLite for better performance and scalability
  - New `src/db_utils.py` module for database operations
  - New `run_gender_inference_db.py` script for gender inference with database persistence
  - Proper schema with papers, authors, and author_positions tables
  - Indices for fast queries on year, dataset, gender, and position fields
- **Journal Impact Analysis:** New analysis investigating gender gaps across journal quartiles
  - `preprocess_journal_quartiles.py`: Caches ScimagoJR journal rankings using fuzzy matching (one-time preprocessing)
  - `analyze_journal_impact.py`: Analyzes P_female by journal quartile and author position
  - New `journals` table in SQLite for fast journal-to-quartile lookups
  - Publication-ready figures showing female representation across Q1–Q4 journals
- **Unified Pipeline Script:** Consolidated Jupyter notebooks into `pipeline.py` for better reproducibility
  - Command-line interface with `--skip-fetch` and `--figures-only` options
  - Modular step functions for each pipeline stage
  - Better error handling and progress reporting

### Changed
- **Data Storage:** Author-position data now stored in SQLite (300-500 MB) instead of CSV files (1.2-1.5 GB)
  - ~60-75% reduction in storage footprint
  - Significant speedup in data loading and filtering
- **README.md:** Updated to document SQLite approach and new pipeline structure
  - Added architecture section explaining database design
  - Updated quick start guide with new pipeline commands
  - Clarified repository structure to reflect code-first approach
- **Pipeline Simplified:** Removed arXiv integration due to persistent API rate limiting
  - Focus on PubMed data (Biology + Computational Biology) with 410k+ papers
  - Sufficient sample size for robust statistical analysis

### Removed
- Jupyter notebooks (notebooks/01-05) — replaced by `pipeline.py`
- CSV output files for author-level data (now in database)
- **arXiv data fetching** (`src/arxiv_fetcher.py` and `run_arxiv_fetch.py`)
  - arXiv API rate limiting prevented reliable data collection
  - PubMed sample size (410k+ papers) sufficient for analysis

---

## [0.2.0] - 2025-02-19

### Added
- **Recursive Date Subdivision for PubMed:** Improved handling of large queries
  - Automatically subdivides searches when result counts exceed API limits
  - Ensures complete retrieval of papers across 2015-2024
- **arXiv Fetcher Error Handling:** Graceful handling of rate limiting and empty results
  - Implements 3-second delay between requests
  - Creates empty dataset with correct schema when no results found
  - Better progress reporting during fetches

### Changed
- **Pipeline Architecture:** Improved modularization in `pipeline.py`
  - Better separation of concerns between fetching, inference, and analysis
  - Enhanced status reporting and error messages

### Fixed
- **Empty arXiv Data Handling:** Pipeline now gracefully handles cases where arXiv searches return 0 results
  - Creates empty dataframe with correct column schema
  - Analysis continues with PubMed data only
  - No errors or missing data in final outputs

---

## [0.1.0] - 2025-02-01

### Added
- **Initial Project Setup**
  - Repository structure with src/, data/, notebooks/, outputs/
  - PubMed data fetcher (`src/pubmed_fetcher.py`)
  - arXiv data fetcher (`src/arxiv_fetcher.py`)
  - Gender inference engine (`src/gender_utils.py`) with genderize.io API integration
  - Bootstrap statistical analysis module (`src/bootstrap.py`)
  - Plotting utilities (`src/plotting.py`)
  - Jupyter notebook-based pipeline (notebooks/01-05)

### Features
- **Data Collection**
  - PubMed: Biology + Computational Biology papers (1997-2024)
  - arXiv: Quantitative Biology (q-bio) + Computer Science (cs) (2015-2024)
  - Exclusion filters: reviews, comments, editorials, non-English papers

- **Gender Inference**
  - Two-layer approach: gender-guesser (offline) + genderize.io API (fallback)
  - Caching system to minimize API calls
  - Probability-based assignment for uncertain cases

- **Author Position Classification**
  - Position-based analysis: first, second, middle, penultimate, last
  - Stratified by dataset and time period

- **Statistical Analysis**
  - Bootstrap resampling (1000 iterations)
  - Confidence interval estimation (95% CI)
  - Multi-group comparisons

- **Visualization**
  - Position breakdown charts
  - Temporal trend analysis
  - COVID-19 impact analysis
  - Interactive figures

---

## Historical Notes

This project replicates and extends the landmark study by Bonham & Stefan (2017) on gender representation in computational biology. The analysis was originally conducted through January 2017, and this update extends it through December 2024.

### Key Milestones

- **February 2025:** Initial project setup with notebook-based pipeline
- **February 2025:** PubMed/arXiv fetcher improvements for robust data collection
- **February 2026:** Migration to SQLite database and unified Python pipeline script

### Related Publications

- Bonham KS, Stefan MI (2017). Women are underrepresented in computational biology. *PLoS Comput Biol* 13(10): e1005134. https://doi.org/10.1371/journal.pcbi.1005134
