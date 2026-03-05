# Author Gender Classification: Methods and Results

## Author Gender Classification

### Data and Author Cohort

We compiled a cohort of 977,731 unique authors from 274,702 publications indexed in PubMed (2015–2025) retrieved using controlled vocabulary searches: `"Biology"[Mesh]` for biology articles and `"Computational Biology"[Majr]` for computational biology articles. Publications were queried using the NCBI Entrez API and stored in a SQLite database (gender_data.db) with the following fields: PMID, publication year, journal name, and complete author lists with first and last names.

### Gender Classification Procedure

We employed a hybrid three-tiered classification strategy to infer author gender from first names, as gender in scientific authorship provides an important metric for quantifying representation across career stages and author positions.

#### Tier 1: Offline Gender Database
We initially classified 569,108 authors (58.3%) and 400,227 authors (41.0%) using the offline gender-guesser Python package, which contains approximately 45,000 curated first names with gender associations. This tier required no external API calls and provided immediate classification for common Western names.

#### Tier 2: Online API Classification
For the 8,405 names unresolved by the offline database (0.9%), we queried the genderize.io API, which uses a probabilistic model trained on millions of name-gender associations from online services and historical databases. Each name query returned a probability-based gender classification (male/female) with an associated confidence score.

#### Tier 3: Large Language Model-Based Classification
Following Tiers 1 and 2, we identified 392,610 author names (40.2% of the total cohort) with unresolved or missing gender classifications. To maximize classification coverage while managing computational costs, we developed a three-phase LLM-based pipeline using the Groq API (llama-3.1-8b-instant model, inference speed: 840 tokens per second, context window: 128k tokens).

**Phase 1 – Free Tier Exploration (5.6% coverage):** We conducted exploratory testing on the free Groq API tier, processing all 392,610 unknown names in batches of 100 names per request using structured JSON prompts. The free tier consumed 500,000 tokens per 24 hours and achieved initial classification of 21,957 names (5.6% of the unknown cohort) before reaching rate limits. Cost: $0.

**Phase 2 – Scaled Production Processing (93.4% coverage):** Following transition to a paid Groq API account, we resumed processing of the remaining 371,894 unclassified names from Phase 1. The paid tier successfully classified 347,280 additional names (93.4% of the Phase 2 input). Systematic failures in JSON response parsing affected 24,614 names (6.6% of Phase 2 input). Cost: $0.54 (3.4M input tokens, 4.6M output tokens, 8.0M total tokens).

**Phase 3 – Robustness Enhancement through Parsing Refinement (93.8% recovery):** To recover classifications from the 24,614 Phase 2 parsing failures, we implemented an iterative four-level JSON response parsing strategy:
1. Direct JSON parsing using Python's standard json decoder
2. Markdown code block extraction (handling responses wrapped in ```json...``` delimiters)
3. Automated JSON repair (removal of trailing commas, quote normalization)
4. Regex-based key-value pattern extraction for edge cases (`"name": "gender"` patterns)

This multi-strategy approach successfully recovered 41,968 classifications (93.8% of Phase 3 input, n=44,864). The remaining 2,896 unresolved names from Phase 3 were merged with the 6,391 names from Phase 2 that failed all parsing strategies, yielding a final unclassified pool of 6,391 names. Cost: $0 (processing cost included in Phase 2).

### Classification Outcomes and Coverage

Across all three classification tiers, we achieved the following results:
- **Total authors classified:** 969,340 of 977,731 (99.1% coverage)
  - Male: 569,108 (58.3% of classified)
  - Female: 400,227 (41.0% of classified)
  - Other classifications: 5 (0.01% of classified)
- **Unknown/unclassified:** 6,391 (0.7% of total cohort)
- **Blank/missing names:** 97 (0.01% of total cohort)

For the LLM-based Phase (Tier 3) specifically:
- **Input:** 392,610 unknown names
- **Successfully classified:** 386,219 names (98.4%)
- **Unresolved following all parsing strategies:** 6,391 names (1.6%)
- **Total classification cost:** $0.54 (8.0M tokens)
- **Cost per successfully classified name:** $1.40 × 10⁻⁶

### Quality Control and Validation

We assessed the reliability of unclassified names through two validation approaches:

**Unclassified Name Characteristics:** Analysis of the 6,391 unclassified names revealed they predominantly featured non-Latin script systems (Cyrillic, Greek, Arabic, East Asian), complex diacritical marks, encoding inconsistencies, or genuine gender-ambiguous names used across populations. These characteristics align with known limitations of name-based gender inference in multilingual and cross-cultural contexts.

**Successful Classification Examples:** To demonstrate the robustness of our hybrid approach, we confirmed successful classification across challenging name categories:
- International names: Chen Qiao (female, Mandarin), Behrooz Torabi Moghadam (male, Persian)
- Names with diacritical marks: Léo Pioger (male, French), María José García (female, Spanish)
- Complex name structures: Q J Peng (male), M Karlsson (male)
- Mononymous names: Shana Thomas (female), Bettina Schuppelius (female)

### Data Filtering and Inclusion Criteria

**Ambiguous Initial Name Exclusion:** We identified 62,417 authors (6.4% of the total cohort) whose first name component consisted of initials or initial-like patterns that lack sufficient contextual information for reliable gender inference. This category includes:
- Simple initials: "A Smith", "J Johnson" (60,903 authors)
- Hyphenated initials: "A-C Smith", "W-D Xi" (1,321 authors)
- Initials with punctuation: "A. Smith", "A' Smith", "J'Nan Wittler" (193 authors)

These initial variants are functionally equivalent in terms of gender inference ambiguity (e.g., "A-C" could represent "Anton-Claus" [male] or "Anne-Carolina" [female]) and introduce systematic ambiguity independent of classification methodology.

To assess the impact of excluding all initial variants, we conducted a comparative analysis:

| Metric | Full Dataset | Filtered Dataset | Absolute Change | Percentage Change |
|--------|-------------|-----------------|-----------------|-------------------|
| Total authors | 977,731 | 915,314 | -62,417 | -6.4% |
| Male (count) | 569,108 | 524,066 | -45,042 | -7.9% |
| Male (%) | 58.2% | 57.3% | -0.95 pp | -1.6% |
| Female (count) | 400,227 | 386,335 | -13,892 | -3.5% |
| Female (%) | 40.9% | 42.2% | +1.27 pp | +3.1% |
| Unknown (count) | 6,488 | 3,779 | -2,709 | -41.7% |
| Unknown (%) | 0.7% | 0.4% | -0.27 pp | -38.6% |
| Male/Female ratio | 1.422 | 1.357 | -0.065 | -4.6% |

The filtering of all initial variants (simple, hyphenated, and punctuated) resulted in minimal changes to gender proportion estimates (<1.3 percentage points) while substantially improving classification reliability. The expanded filtering removed an additional 1,514 hyphenated and punctuated initial names beyond the simple initials, with negligible impact on the overall gender distribution (-0.03pp for male, +0.04pp for female). Subsequent analyses presented herein used the filtered dataset of 915,314 authors unless otherwise specified.

### Statistical Approach

Female representation at each author position and across temporal periods was calculated as the proportion of female authors among all authors in that position or time period. We present point estimates with 95% confidence intervals derived from bootstrap resampling (1,000 iterations per group), with confidence intervals calculated as the 2.5th and 97.5th percentiles of the bootstrap distribution.

### Sources of Variation and Limitations

**Binary Gender Classification:** The name-based approach classifies authors into male or female categories and does not capture non-binary, genderqueer, or non-gender-conforming identities, thereby excluding these populations from representation in the present analysis.

**Systematic Bias in Non-Western Names:** Name-based gender inference exhibits documented performance variation across geographical and cultural regions. Studies indicate that such inference models perform more reliably for Western European and North American names than for East Asian, South Asian, Arabic, or African names, potentially leading to undercounting of female authors from these regions.

**Unclassified Names:** The 6,391 unclassified names (1.6% of the LLM-processed cohort) represent a potential source of bias if their gender distribution differs systematically from the classified cohort. However, qualitative inspection suggests these represent genuinely ambiguous or non-Latin names rather than systematic classification failures.

**Publication Lag:** Publications indexed in 2024–2025 reflect scientific work conducted 1–3 years prior. Consequently, our observations of gender representation in the most recent data reflect the state of the field from 2021–2023, not the current state.

### Code and Data Availability

Classification scripts, execution logs, and complete methodological documentation are available at: https://github.com/lfaller/gender-gap-compbio

The gender_data.db SQLite database containing all 977,731 authors with gender classifications is available upon request.
