# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Reproducibility audit: 17 bugs fixed** (see [REPRODUCIBILITY_FIXES.md](./REPRODUCIBILITY_FIXES.md) for full details)
  - **Makefile — wrong script paths (Critical):** `make infer`, `make classify`, and `make preprocess-journals` all invoked scripts without the `scripts/` path prefix, causing immediate "file not found" errors. `make classify` also referenced a non-existent filename (`classify_names.py` instead of `classify_names_retry.py`).
  - **Environment variable mismatch (Critical):** `make setup` wrote `ENTREZ_EMAIL` to `.env` but `cli.py` reads `NCBI_EMAIL`. Any user following `make setup` would have a broken `make fetch`. Standardised on `NCBI_EMAIL` throughout `Makefile`, `README.md`, `.env.example`, `docker-compose.yml`, and `DOCKER.md`.
  - **`cli.py infer` was a non-functional stub (Critical):** The command only printed instructions instead of running inference. Fixed to invoke `scripts/run_gender_inference_db.py` via `subprocess`.
  - **`cli.py run` exited early (Critical):** Hard `sys.exit(0)` after Step 2 made Steps 3 (analyze) and 4 (figures) unreachable dead code. Removed early exit; full pipeline now runs to completion.
  - **Zenodo download URL returned JSON instead of file data (Critical):** Missing `/content` suffix in both `scripts/download_zenodo_data.py` and `scripts/download_zenodo_data.sh` caused downloads to return a JSON metadata blob instead of binary file content.
  - **`cli.py --help` crashed on Windows (Critical):** `→` (U+2192) in the `run` command docstring caused `UnicodeEncodeError` on Windows cp1252 terminals. Replaced with `->`.
  - **Docker — `docker-compose.yml` used `ENTREZ_EMAIL` (Critical):** Updated to `NCBI_EMAIL`.
  - **Docker — `python:3.9-slim` incompatible with `scipy~=1.13.0` (Critical):** scipy 1.13 requires Python ≥ 3.10; the Dockerfile used `python:3.9-slim` (also EOL since October 2025). `docker build` would fail with no matching wheel. Updated to `python:3.11-slim`.
  - **`DOCKER.md` — `ENTREZ_EMAIL` throughout and wrong preprocess command (Critical/Minor):** All 12 `ENTREZ_EMAIL` references updated to `NCBI_EMAIL`. Step 7 of the complete workflow example had the wrong script name and used CMD override (incompatible with the `python cli.py` ENTRYPOINT) — fixed with `--entrypoint python scripts/preprocess_journal_quartiles.py`.
  - **Stale script paths in error messages and README (Minor):** Four stale bare-script-name references (`python run_gender_inference_db.py`, `python preprocess_journal_quartiles.py`) replaced with the correct CLI commands or `scripts/`-prefixed paths across `cli.py`, `analyze_journal_impact.py`, and `README.md`.
  - **`requirements.txt` unpinned versions (Minor):** Changed from `>=` to three-component `~=X.Y.0` (e.g. `pandas~=2.2.0`). Two-component `~=X.Y` (intermediate fix) was found to pin major only, allowing `groq 0.9` to resolve to `0.37.1`.
  - **`.env.example` missing `GROQ_API_KEY` (Minor):** Added the key required for Tier 2 LLM classification. Removed two stale unused keys (`ARXIV_DELAY_SECONDS`, `GENDERIZE_API_KEY`).

### Changed
- **Journal Impact Blog Post:** Enhanced clarity and consistency
  - Added Acknowledgments section recognizing Dr. Samantha Klasfeld and Amulya Shastry
  - Updated publication date to March 2026
  - Aligned P_female notation and probability language with Deep Dive blog post for consistency
  - Removed em-dashes throughout, rephrased using commas, semicolons, colons, and parentheses for improved readability

## [0.3.0] - 2026-03-10

### Changed
- **Date Range Extended:** Updated analysis to include 2025 data (2015–2025)
  - PubMed data now includes 430,000+ papers instead of 410,000
  - COVID-19 recovery period extended to 2022–2025
  - Temporal trend analysis now includes latest year
- **Repository Organization:** Reorganized Python scripts for clarity and maintainability
  - Moved all utility scripts (`run_gender_inference_db.py`, `preprocess_journal_quartiles.py`, `analyze_journal_impact.py`, `classify_names_retry.py`, `analyze_gender_with_filtering.py`) to `scripts/` folder
  - Kept only `cli.py` in root as the single main entry point
  - Updated all documentation and CLI help to reflect new paths
  - Follows Python project conventions for cleaner root directory

### Added
- **MIT License:** Added MIT License file for open-source distribution
  - Clarified usage rights and attribution requirements
  - Enables broader adoption and collaboration
- **Modular Deep Dive Figure Scripts:** Refactored blog post figure generation into independent, reproducible modules
  - Created `publications/bwib_deep_dive/figures/` directory with separate scripts:
    - `figure_1a_position_breakdown.py` — P(female) by author position
    - `figure_1b_temporal_trend.py` — P(female) over time
    - `figure_1c_pi_effect.py` — The female PI effect (PI gender stratification)
    - `table_1_female_proportion.py` — Female proportion statistics by position
    - `table_2_pi_effect_statistics.py` — PI effect statistics table
  - Each script can be run independently: `python -m publications.bwib_deep_dive.figures.figure_1a_position_breakdown`
  - Created `publications/bwib_deep_dive/figures/utils.py` with shared utilities to reduce duplication
  - Added comprehensive [Deep Dive Figures README](publications/bwib_deep_dive/figures/README.md) with documentation
  - Legacy wrapper (`scripts/reproduce_bonham_stefan.py`) calls all modular scripts for backward compatibility
  - Self-contained blog post structure: `publications/bwib_deep_dive/` includes markdown, figures, and code
- **Enhanced README:** Comprehensive documentation updates
  - Added "Published Blog Posts" section with direct links to blog markdown and figures
  - Documented both legacy wrapper and modular approaches for figure reproduction
  - Updated repository structure diagram to show new organization
  - Added section "Reproduce the BWIB Deep Dive Blog Post Figures" with examples

### Removed
- **Interactive Visualizations:** Removed unused interactive HTML figures
  - Deleted `outputs/figures/fig4_interactive_temporal_trend.html` (Plotly-based temporal trend)
  - Deleted `outputs/figures/classification_strategy_sankey.html` (Sankey diagram)
  - Removed `plot_interactive_temporal_trend()` function from `src/plotting.py`
  - Removed plotly dependencies from visualization module
- **Validation Directory:** Removed unused validation folder
  - Deleted `validation/` directory with test data and README
  - Not part of final reproducibility pipeline
- **Runtime Artifacts:** Cleaned up temporary process and log files
  - Deleted process ID files: `classify.pid`, `monitor.pid`
  - Deleted log files: `classify_output.log`, `classify_retry.log`, `classify_run.log`, `classify_run_paid.log`
  - Deleted monitoring script: `monitor_progress.sh`

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
