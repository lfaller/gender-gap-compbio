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
- **Docker Containerization:** Full Docker support for reproducible environments
  - `Dockerfile`: Multi-stage build optimizing for speed and image size (~500 MB)
  - `docker-compose.yml`: Easy orchestration with environment variable management
  - `Makefile`: Convenient shortcuts for all common tasks (setup, fetch, analyze, docker-build, docker-run, etc.)
  - `.dockerignore`: Excludes unnecessary files from build context
  - `DOCKER.md`: Comprehensive documentation for Docker workflows
  - Enables one-command reproduction across different systems/Python versions
  - Eliminates dependency chaos and improves reproducibility (5/10 → 8/10)
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
- **Documentation:** Added explicit DOI links to landmark Bonham & Stefan (2017) paper
  - All references now include direct links to https://doi.org/10.1371/journal.pcbi.1005134
  - Improves discoverability and citation tracking across README, blog posts, source code, and docs
- **Dependencies:** Updated `requirements.txt` with missing CLI dependencies
  - Added `click>=8.0.0` (required by `cli.py`)
  - Added `groq>=0.4.0` (required by `classify_names.py` for LLM-based classification)
  - Removed duplicate `dotenv` entry (use `python-dotenv` instead)
- **Data Storage:** Author-position data now stored in SQLite (300-500 MB) instead of CSV files (1.2-1.5 GB)
  - ~60-75% reduction in storage footprint
  - Significant speedup in data loading and filtering
- **README.md:** Updated to document Docker setup and dependency management
  - Added Docker quick start section with examples
  - Added reference to comprehensive DOCKER.md documentation
  - Maintained original quick start for local installation
- **Pipeline Simplified:** Removed arXiv integration due to persistent API rate limiting
  - Focus on PubMed data (Biology + Computational Biology) with 410k+ papers
  - Sufficient sample size for robust statistical analysis

### Removed
- Jupyter notebooks (notebooks/01-05) — replaced by `pipeline.py`
- CSV output files for author-level data (now in database)
- **arXiv data fetching** (`src/arxiv_fetcher.py` and `run_arxiv_fetch.py`)
  - arXiv API rate limiting prevented reliable data collection
  - PubMed sample size (410k+ papers) sufficient for analysis
- **Legacy and non-reproducible code (reproducibility audit):**
  - `pipeline.py` — deprecated monolithic script, superseded by `cli.py`
  - `src/arxiv_fetcher.py` — unused in PubMed-only analysis, removed from exports
  - `generate_gender_classification_figures.py` — used hardcoded statistics instead of reading from database
  - Dead genderize.io code from `src/gender_utils.py` — never used in actual pipeline (Groq LLM is Tier 2)

### Fixed
- **arXiv File References:** Removed stale arXiv data loading code from `run_gender_inference_db.py`
  - Removed attempts to load non-existent `arxiv_qbio_2015_2025.csv` and `arxiv_cs_2015_2025.csv` files
  - Removed arXiv processing block that was left over after arXiv integration removal
  - Script now processes PubMed data only, matching actual data availability
  - Fixes critical FileNotFoundError blocker that prevented pipeline execution
  - Resolves reproducibility issue identified in REPRODUCIBILITY_ASSESSMENT.md
- **Reproducibility:** Critical filename mismatch in `run_gender_inference_db.py`
  - Changed hardcoded `2015_2024.csv` to `2015_2025.csv` to match `cli.py` output
  - Pipeline would have failed at step 2 (database population) with "file not found" error
- **Documentation:** Updated README to document LLM classification pipeline and Groq API key requirement
  - Added two-phase gender inference explanation
  - Clarified that Groq API is optional but recommended for full reproducibility (~$0.54 cost)

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
  - Gender inference engine with offline database and Groq LLM API
  - Bootstrap statistical analysis module (`src/bootstrap.py`)
  - Plotting utilities (`src/plotting.py`)
  - Jupyter notebook-based pipeline (notebooks/01-05)

### Features
- **Data Collection**
  - PubMed: Biology + Computational Biology papers (1997-2024)
  - arXiv: Quantitative Biology (q-bio) + Computer Science (cs) (2015-2024)
  - Exclusion filters: reviews, comments, editorials, non-English papers

- **Gender Inference**
  - Two-tier approach: gender-guesser (offline) + Groq LLM API (fallback)
  - Three-phase LLM processing with robust JSON parsing fallback strategies
  - 98.4% classification coverage on unresolved names

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

This project replicates and extends the landmark study by [Bonham & Stefan (2017)](https://doi.org/10.1371/journal.pcbi.1005134) on gender representation in computational biology. The analysis was originally conducted through January 2017, and this update extends it through December 2024.

### Key Milestones

- **February 2025:** Initial project setup with notebook-based pipeline
- **February 2025:** PubMed/arXiv fetcher improvements for robust data collection
- **February 2026:** Migration to SQLite database and unified Python pipeline script

### Related Publications

- Bonham KS, Stefan MI (2017). Women are underrepresented in computational biology. *PLoS Comput Biol* 13(10): e1005134. https://doi.org/10.1371/journal.pcbi.1005134
