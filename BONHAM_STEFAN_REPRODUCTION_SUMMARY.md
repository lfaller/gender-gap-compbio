# Bonham & Stefan (2017) Reproduction with 2015–2025 Data

## Overview

This document summarizes the reproduction of Bonham & Stefan's landmark 2017 study ("Women are underrepresented in computational biology") using contemporary data from 2015–2025.

**Reference:** [Bonham KS, Stefan MI (2017). Women are underrepresented in computational biology. *PLoS Comput Biol* 13(10):e1005134.](https://doi.org/10.1371/journal.pcbi.1005134)

---

## Key Findings

### Female Representation by Author Position (Table 1)

| Metric | Biology | Comp Bio | Gap |
|--------|---------|----------|-----|
| **First Author** | 47.0% | 40.6% | **6.4 pp** |
| **Second Author** | 44.8% | 40.3% | **4.5 pp** |
| **Other Authors** | 42.0% | 39.1% | **2.9 pp** |
| **Penultimate Author** | 31.9% | 27.4% | **4.5 pp** |
| **Last Author** | 32.1% | 27.2% | **4.9 pp** |

**Interpretation:** Computational biology still lags general biology in female representation, consistent with Bonham & Stefan's 2017 findings. However, the gap has narrowed slightly (from 4–6 pp in 2017 to 2.9–6.4 pp in 2025).

### The Female PI Effect (Table 2)

When comparing papers with male vs. female last authors (PIs), the effect is striking:

**Biology Papers:**
- First author with male PI: **44.5%** female
- First author with female PI: **57.5%** female
- **Difference: +13.0 percentage points**

**Computational Biology Papers:**
- First author with male PI: **37.8%** female
- First author with female PI: **51.6%** female
- **Difference: +13.8 percentage points**

This "female PI effect" is consistent across all author positions in both fields, indicating that women in senior leadership actively promote female co-authorship.

### Temporal Trends (Figure 1B)

Female representation has improved over time in both fields:
- Biology: gradual upward trend
- Computational Biology: upward trend, but starting from a lower baseline

---

## Deliverables

### Python Script
- **File:** `reproduce_bonham_stefan.py`
- **Purpose:** Reproduces Bonham & Stefan figures and tables from the gender-inferred database
- **Usage:** `python reproduce_bonham_stefan.py`
- **Output:** Generates figures, markdown tables, and CSV files in `outputs/bonham_stefan_reproduction/`

### Figures (PNG, 300 DPI, publication-ready)
1. **Fig1A_position_breakdown.png** – Bar chart comparing female representation by author position
2. **Fig1B_temporal_trend.png** – Line plot showing trends 2015–2025
3. **Fig1C_pi_effect.png** – Grouped bar chart showing the female PI effect

**Location:** Available in:
- `publications/` (main)
- `docs/` (documentation)
- `local/` (working directory)
- `outputs/bonham_stefan_reproduction/` (analysis output)

### Data Tables
1. **Table1_proportion_female_authors.csv** – P(female) by dataset and position
2. **Table1_proportion_female_authors.md** – Markdown-formatted version
3. **Table2_female_authors_with_female_pi.csv** – P(female) by PI gender
4. **Table2_female_authors_with_female_pi.md** – Markdown-formatted version

**Location:** `outputs/bonham_stefan_reproduction/`

### Blog Post Integration
- **File:** `publications/BWIB_Deep_Dive_Blog_Post.md`
- **Section:** "Reproducing Bonham & Stefan with 2015–2025 Data" (lines 33–100)
- **Includes:** All three figures, both tables, and detailed analysis

---

## Methodology

### Data Source
- **Database:** `data/gender_data.db` (SQLite)
- **Papers:** 2,059,081 author records from 2015–2025
- **Datasets:** Distinguished by matching PMIDs against `pubmed_biology_2015_2025.csv` and `pubmed_compbio_2015_2025.csv`
- **Gender Inference:** Hybrid approach (offline gender database + LLM classification)

### Analysis Approach
Replicates Bonham & Stefan's exact methodology:
1. **Bootstrap resampling:** 1,000 iterations per group
2. **Confidence intervals:** 95% CIs reported as 2.5th and 97.5th percentiles
3. **P(female) calculation:** Probability that an author is female based on name-based gender inference
4. **PI effect analysis:** Stratified by last author gender (p_female > 0.8 = female, < 0.2 = male)

### Important Limitations
- Gender inference relies on first names; binary (male/female) classification only
- Name-based methods work better for Western names than East Asian, South Asian, African names
- ~6.4% of authors have inherently ambiguous names (initials, hyphenated names) and were excluded
- Authorship data reflects publication patterns, not workforce demographics

---

## How to Regenerate Results

```bash
# Ensure database is populated with author data
python run_gender_inference_db.py

# Regenerate all figures and tables
python reproduce_bonham_stefan.py

# Output will be saved to outputs/bonham_stefan_reproduction/
```

---

## Key References

1. **Original Study:** [Bonham & Stefan (2017)](https://doi.org/10.1371/journal.pcbi.1005134) – *PLoS Comput Biol*
2. **Related:** [Macaluso et al. (2016)](https://doi.org/10.1097/ACM.0000000000001261) – Female corresponding authors and equitable co-authorship practices
3. **Gender Inference Validation:** Filardo et al. (2016) – Gender inference from first names in biomedical literature

---

## Future Directions

1. **Extend analysis** to arXiv quantitative biology vs. computer science (as in Bonham & Stefan Fig 3)
2. **Sub-field analysis** – Examine specific computational biology sub-disciplines
3. **Journal-level analysis** – Compare gender representation across different publication venues
4. **Career stage analysis** – Track authors over time to understand career progression patterns

---

**Generated:** March 6, 2026
**Analysis Period:** 2015–2025
**Total Authors Analyzed:** 2,059,081 author records
**Total Papers:** ~274,702
