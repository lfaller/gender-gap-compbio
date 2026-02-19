# Gender Representation in Computational Biology: A 2025 Update

Replicating and extending the landmark study by Bonham & Stefan (2017) on gender representation in computational biology authorship, with data through 2024.

**Project Lead:** Lina Faller, Ph.D.
**Affiliations:** [linafaller.com](https://www.linafaller.com) | VP, Boston Women in Bioinformatics (BWIB)

## Overview

This project extends the Bonham & Stefan (2017) analysis of gender representation in computational biology through 2024, examines emerging trends (including the COVID-19 pandemic's impact), and investigates subfield-specific gender gaps. Results will be published as:

1. **BWIB Deep Dive blog post** (1,200–1,800 words)
2. **LinkedIn article** (400–600 words)
3. **GitHub repository** with reproducible code and methodology

## Key Questions

- Has the female first-author rate in computational biology changed since 2017?
- Does the "female PI effect" (papers with female last authors have more female co-authors) still hold?
- What was the impact of the COVID-19 pandemic on publication patterns?
- Do gender gaps vary across computational biology subfields?

## Repository Structure

```
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/                     # Raw API outputs (gitignored)
│   ├── processed/               # Cleaned CSVs for analysis
│   └── gender_cache.json        # Cached name → gender lookups
│
├── notebooks/
│   ├── 01_pubmed_fetch.ipynb    # Fetch PubMed data
│   ├── 02_arxiv_fetch.ipynb     # Fetch arXiv data
│   ├── 03_gender_inference.ipynb # Infer gender from names
│   ├── 04_analysis.ipynb        # Bootstrap analysis & stats
│   └── 05_figures.ipynb         # Generate publication figures
│
├── src/
│   ├── __init__.py
│   ├── pubmed_fetcher.py        # PubMed API wrapper
│   ├── arxiv_fetcher.py         # arXiv API wrapper
│   ├── gender_utils.py          # Gender inference logic
│   ├── bootstrap.py             # Statistical analysis
│   └── plotting.py              # Figure generation
│
└── outputs/
    └── figures/                 # Publication-ready figures
```

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/gender-gap-compbio.git
cd gender-gap-compbio
```

### 2. Set Up Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Add NCBI API Key
Register for a free NCBI API key at https://www.ncbi.nlm.nih.gov/account/ and add it to your environment:

```bash
export NCBI_API_KEY="your_api_key_here"
```

### 4. Run the Analysis Pipeline
Follow the notebooks in order:

1. `notebooks/01_pubmed_fetch.ipynb` — Fetch PubMed data for Biology and Computational Biology
2. `notebooks/02_arxiv_fetch.ipynb` — Fetch arXiv data for quantitative biology and computer science
3. `notebooks/03_gender_inference.ipynb` — Infer gender from author first names
4. `notebooks/04_analysis.ipynb` — Run bootstrap analysis and generate statistics
5. `notebooks/05_figures.ipynb` — Create publication-ready figures

## Methodology

### Data Sources

**PubMed (1997–2024)**
- **Biology:** Papers tagged with `"Biology"[Mesh]` MeSH term
- **Computational Biology:** Papers tagged with `"Computational Biology"[Majr]` MeSH term (major term only)
- Exclusions: Reviews, comments, editorials, letters, case reports, news, biographies
- Language: English only
- Retrieved fields: PMID, publication year, journal, full author list with first names

**arXiv (2015–2024)**
- **Quantitative Biology:** `q-bio` category
- **Computer Science:** `cs` category
- Retrieved fields: arXiv ID, submission date, category, full author list

### Gender Inference Strategy

A layered approach to maximize coverage while minimizing API calls:

1. **Layer 1 — gender-guesser (offline):** Fast, offline database of ~45k names. Returns male, female, mostly_male, mostly_female, or unknown.
2. **Layer 2 — genderize.io API (fallback):** For names not resolved by gender-guesser, queries the genderize.io API (up to 1k/day free).
3. **Caching:** All lookups are cached in `data/gender_cache.json` to avoid redundant API calls.

**Probability Assignment:**
- `P_female = 1.0` for confirmed female names
- `P_female = 0.0` for confirmed male names
- `P_female = API probability` for probabilistic assignments (0.7+ threshold)
- `P_female = None` for unresolved names (excluded from analysis)

### Author Position Classification

Following the original paper's scheme:

| Author Count | Positions |
|---|---|
| 1 | first |
| 2 | first, last |
| 3 | first, second, last |
| 4+ | first, second, other (middle), penultimate, last |

### Statistical Analysis

**Bootstrap Resampling:**
For each author position and dataset, we:
1. Collect all P_female values for that position
2. Resample with replacement 1,000 times
3. Calculate the mean of each resample
4. Report: mean, 95% CI lower (2.5th percentile), 95% CI upper (97.5th percentile)

## Key Analyses

| Analysis | Description |
|---|---|
| **Position Breakdown** | P_female by author position (first, second, other, penultimate, last) for Biology vs. Comp Bio, 2015–2024 |
| **Temporal Trend** | P_female over time (1997–2024), comparing original data with new results |
| **Female PI Effect** | P_female by position, stratified by gender of last author (proxy for PI gender) |
| **Subfield Comparison** | Gender gap variation within computational biology subfields (genomics, proteomics, systems biology, etc.) |
| **COVID-19 Impact** | Year-over-year comparison highlighting 2020–2021 |
| **arXiv Comparison** | P_female in q-bio vs. cs, 2015–2024 |

## Methodological Limitations

These limitations are explicitly documented and should be transparently reported in any publication:

1. **Binary Gender Framework:** Name-based inference assigns only male/female and cannot capture non-binary or gender-nonconforming identities.
2. **Name Coverage Gaps:** Western names are better represented in gender databases; East Asian, South Asian, Arabic, and African names have lower coverage and higher misclassification rates.
3. **Exclusion Rate:** ~27% of authors in the original paper had unresolvable names. We document our own exclusion rate and test for systematic bias.
4. **MeSH Assignment:** Not all computational biology papers are tagged with the Computational Biology MeSH term; results may underrepresent some subfields.
5. **Last Author ≠ PI:** The convention of last author = PI is strongest in biology but does not universally hold across all subfields or CS-adjacent research.
6. **Authorship ≠ Workforce:** Publication rates reflect many factors beyond representation (funding, career stage distributions, productivity norms, etc.).

## References

- Bonham KS, Stefan MI (2017). Women are underrepresented in computational biology. *PLoS Comput Biol* 13(10): e1005134. https://doi.org/10.1371/journal.pcbi.1005134
- Giannos P et al. (2023). Female Dynamics in Authorship of Scientific Publications in the Public Library of Science. *EJIHPE* 13(2). https://doi.org/10.3390/ejihpe13020018
- Mihaljević H & Santamaría L (2021). Comparison and benchmark of name-to-gender inference services. *PeerJ Comput Sci* 7:e156. https://doi.org/10.7717/peerj-cs.156
- NCBI E-utilities API: https://www.ncbi.nlm.nih.gov/books/NBK25499/
- arXiv API: https://github.com/lukasschwab/arxiv.py
- gender-guesser: https://pypi.org/project/gender-guesser/
- genderize.io: https://genderize.io

## Contributing

If you find issues, have suggestions for improvements, or want to extend this analysis, please open an issue or pull request.

## License

[Add your preferred license here — e.g., MIT, CC-BY 4.0]

## Citation

If you use this project or methodology, please cite:

```
Faller, L. (2026). Gender Representation in Computational Biology: A 2025 Update.
Available at: https://github.com/yourusername/gender-gap-compbio
```

---

**Document prepared:** February 2026
**Project Lead:** Lina Faller, Ph.D.
**For use with Python and Jupyter notebooks**
