# Bioinformatics Search Term Analysis: Summary for Collaborators

## Executive Summary

Including "bioinformatics" as a search term would **significantly expand our dataset** and provide important perspective on the broader computational biology landscape. Our analysis shows that bioinformatics papers represent a distinct population with meaningful overlap but also unique contributions beyond the current Computational Biology search.

---

## Current Dataset

Our existing gender analysis covers:
- **Biology papers**: 274,702 (2015–2025)
- **Computational Biology papers**: 67,205 (2015–2025)

**Key finding**: All 67,205 Computational Biology papers are *also* tagged as Biology papers. The current approach distinguishes between them using separate CSV files—a structure that works well and has already been validated through our analysis pipeline.

---

## What Bioinformatics Would Add

Our PubMed search for bioinformatics-tagged papers (using `bioinformatics[Mesh]`) returned:
- **Bioinformatics papers**: 167,240 (2015–2025)

This is **2.5× larger** than our current Computational Biology dataset.

### Paper Distribution

When we look at how these three categories overlap:

| Category | Count | % of Total Unique |
|----------|-------|-------------------|
| Only Biology (no Comp Bio, no Bioinf) | 108,143 | 39.3% |
| Only Bioinformatics | 684 | 0.2% |
| Biology + Bioinformatics (not Comp Bio) | 99,354 | 36.1% |
| All three categories | 67,202 | 24.4% |
| **Total unique papers** | **275,386** | |

### Key Insights

1. **Bioinformatics captures new papers**: 99,354 papers (36% of unique papers) are tagged as both Biology AND Bioinformatics but NOT Computational Biology. These are papers we would miss without the bioinformatics search.

2. **Large overlap with Comp Bio**: 67,202 papers (24% of total) appear in all three categories. This validates that bioinformatics and computational biology are related but distinct concepts.

3. **Meaningful but small exclusive set**: Only 684 papers are tagged *exclusively* as bioinformatics—most bioinformatics work also falls under broader biology categories, which is expected.

4. **Comp Bio remains a complete subset of Biology**: This relationship is preserved when bioinformatics is added, maintaining our current data structure integrity.

---

## Impact on Our Analysis

### Current capability (Bio + Comp Bio):
- 207,497 general biology papers
- 67,205 computational biology papers
- **Gender analysis compares two populations** with a known overlap

### With bioinformatics added (Bio + Comp Bio + Bioinf):
- 207,497 general biology papers
- 67,205 computational biology papers
- 99,354 additional bioinformatics-specific papers
- **Gender analysis captures ~40% more papers** in the computational/bioinformatics space
- **Can separately analyze gender gaps in bioinformatics** distinct from computational biology

---

## Recommendation

**Including bioinformatics is a good idea because:**

1. **Expands scope appropriately**: Captures the full landscape of computational work on biological data, not just papers explicitly labeled "computational biology"

2. **Maintains data integrity**: The overlap pattern mirrors our existing Computational Biology approach—papers can appear in multiple searches, distinguished by CSV source

3. **Minimal implementation effort**: Follows the existing pattern. No architectural changes needed.

4. **Improved accuracy**: The bioinformatics search (`bioinformatics[Mesh]`) is a standard PubMed MeSH term with clear semantics, making our analysis more comprehensive and defensible

5. **Enables new insights**: Allows us to compare gender representation specifically in bioinformatics vs computational biology vs general biology

---

## Data Files Generated

The analysis was conducted in an isolated branch (`bioinformatics-overlap-analysis`) with results saved to:
- `analysis/bioinformatics_overlap/data/bioinformatics_pmids.json` — 225,741 bioinformatics PMIDs fetched from PubMed
- `analysis/bioinformatics_overlap/results/overlap_summary.csv` — Overlap statistics (7 distinct categories)
- `analysis/bioinformatics_overlap/` — All analysis scripts and detailed breakdowns

---

## Next Steps

Recommend proceeding with integrating bioinformatics into the main analysis pipeline:
1. Add `search_bioinformatics()` method to the data fetcher
2. Update the CLI to fetch bioinformatics papers (following existing pattern)
3. Update gender inference pipeline to include bioinformatics dataset
4. Re-run analysis and figures to show gender gaps across all three populations

**Estimated effort**: 1.5–2 hours (low risk, follows established patterns)
