# Gender Representation in Computational Biology: A 2025 Update
## Project Summary for Claude Code Implementation

**Project lead:** Lina Faller, Ph.D.  
**Affiliations:** [linafaller.com](https://www.linafaller.com) | VP, Boston Women in Bioinformatics (BWIB)  
**Based on:** Bonham & Stefan (2017), *PLoS Computational Biology*, DOI: 10.1371/journal.pcbi.1005134  
**Goal:** Replicate and extend the 2017 analysis through ~2024, produce visualizations, and publish findings as a BWIB Deep Dive blog post, a personal site post, and a LinkedIn article.

---

## Background & Motivation

Bonham & Stefan (2017) examined gender representation in authorship across biology, computational biology, and computer science using PubMed and arXiv data from 1997–2014. Key findings:

- Female authorship in computational biology lagged biology overall by **4–6 percentage points** across all author positions
- Female first authors in comp bio: **~32%** | Last authors: **~21%**
- Comp bio sat between biology and computer science in gender representation
- Papers with a female last author (proxy for female PI) had significantly more female co-authors at all positions — the "female PI effect"
- The gender gap was narrowing, but slowly (~0.5 percentage points/year)

A 2023 follow-up study covering PLoS journals 2010–2020 found that **PLoS Computational Biology had the lowest female authorship of all PLoS journals**: 23.7% female first authors and 17.2% female last authors. No full replication of the Bonham & Stefan methodology with post-2014 PubMed data exists in the literature.

**Why now:** BWIB is actively running a community survey on the landscape of the field. This analysis provides the published-literature backdrop that contextualizes why that survey matters.

---

## Recommended GitHub Repository Structure

```
gender-gap-compbio-2025/
│
├── README.md
├── requirements.txt
│
├── data/
│   ├── raw/                  # Raw API outputs (gitignored if large)
│   ├── processed/            # Cleaned CSVs used for analysis
│   └── gender_cache.json     # Cached name → gender lookups (never re-query)
│
├── notebooks/
│   ├── 01_pubmed_fetch.ipynb
│   ├── 02_arxiv_fetch.ipynb
│   ├── 03_gender_inference.ipynb
│   ├── 04_analysis.ipynb
│   └── 05_figures.ipynb
│
├── src/
│   ├── pubmed_fetcher.py
│   ├── arxiv_fetcher.py
│   ├── gender_utils.py
│   ├── bootstrap.py
│   └── plotting.py
│
└── outputs/
    └── figures/
```

---

## Recommended Python Tools & Libraries

### Data Collection

| Library | Purpose | Install |
|---|---|---|
| `biopython` | PubMed/NCBI E-utilities API wrapper | `pip install biopython` |
| `arxiv` | arXiv API Python wrapper | `pip install arxiv` |
| `requests` | HTTP calls for gender APIs | `pip install requests` |
| `time` / `tenacity` | Rate limiting and retry logic | built-in / `pip install tenacity` |

### Gender Inference (layered strategy — see below)

| Library/Service | Purpose | Cost |
|---|---|---|
| `gender-guesser` | Offline first-pass, ~45k names, no API calls | Free, `pip install gender-guesser` |
| `genderize.io` API | Fallback for unknowns, returns probability + count | Free up to 1k/day; ~$9/mo for 100k |
| `NamSor` API (optional) | Uses first + last name together, better for non-Western names | Freemium |

### Data Processing & Analysis

| Library | Purpose | Install |
|---|---|---|
| `pandas` | DataFrames, groupby, filtering | `pip install pandas` |
| `numpy` | Bootstrap resampling | `pip install numpy` |
| `scipy` | Statistical tests if needed | `pip install scipy` |
| `tqdm` | Progress bars for long API loops | `pip install tqdm` |
| `sqlite3` | Optional: store large datasets locally | built-in |

### Visualization

| Library | Purpose | Install |
|---|---|---|
| `matplotlib` | Base plotting (matches original paper style) | `pip install matplotlib` |
| `seaborn` | Prettier statistical plots | `pip install seaborn` |
| `plotly` | Interactive figures for web/blog | `pip install plotly` |

---

## Step-by-Step Implementation Plan

---

### Step 1: PubMed Data Collection

**What to fetch:** All English-language primary articles tagged with MeSH terms `"Biology"` and `"Computational Biology"` from 2015–2024 (to extend the original 1997–2014 dataset). Optionally re-pull 1997–2014 to have everything in one pipeline.

**Filters to apply (matching original paper):**
- Exclude: Review, Comment, Editorial, Letter, Case Reports, News, Biography
- Language: English only
- For comp bio: use `[Majr]` (Major MeSH term only, not incidental)

**PubMed search strings:**

```python
# Biology dataset
bio_query = (
    '"Biology"[Mesh] NOT ('
    'Review[ptyp] OR Comment[ptyp] OR Editorial[ptyp] OR '
    'Letter[ptyp] OR "Case Reports"[ptyp] OR News[ptyp] OR '
    '"Biography"[Publication Type]) '
    'AND ("2015/01/01"[PDAT]: "2024/12/31"[PDAT]) '
    'AND english[language]'
)

# Computational Biology dataset
comp_query = (
    '"Computational Biology"[Majr] NOT ('
    'Review[ptyp] OR Comment[ptyp] OR Editorial[ptyp] OR '
    'Letter[ptyp] OR "Case Reports"[ptyp] OR News[ptyp] OR '
    '"Biography"[Publication Type]) '
    'AND ("2015/01/01"[PDAT]: "2024/12/31"[PDAT]) '
    'AND english[language]'
)
```

**Key fields to extract per record:**
- PMID
- Publication year
- Journal name (for impact factor analysis)
- Full author list with first names (from `<ForeName>` tag in XML)
- Author count (to assign positions: first, second, other, penultimate, last)

**NCBI API setup:**
- Register a free NCBI API key at: https://www.ncbi.nlm.nih.gov/account/
- With API key: 10 requests/second (vs. 3/second without)
- Fetch in batches of 500 PMIDs at a time using `usehistory="y"` + WebEnv

**Practical notes:**
- The biology dataset will likely be 100k+ records — expect several hours of fetching
- Save raw XML locally and parse separately so you don't re-fetch if something breaks
- Author names in PubMed XML are in `<Author><ForeName>` and `<Author><LastName>` — you want `ForeName` for gender inference

---

### Step 2: arXiv Data Collection

**What to fetch:** All preprints in categories `q-bio` (quantitative biology) and `cs` (computer science) from 2015–2024.

**Python approach:**

```python
import arxiv

client = arxiv.Client(page_size=1000, delay_seconds=3.0, num_retries=5)

search = arxiv.Search(
    query="cat:q-bio",
    max_results=None,  # get everything
    sort_by=arxiv.SortCriterion.SubmittedDate
)

for result in client.results(search):
    # result.authors gives list of Author objects with .name attribute
    # result.published gives datetime
    # result.categories gives list of category strings
    pass
```

**Alternative for bulk download:** Use arXiv's OAI-PMH endpoint or download the full dataset from Kaggle (arXiv Dataset) — much faster than API pagination for large date ranges.

**Fields to extract:**
- arXiv ID
- Submission date (year)
- Category / primary category
- Full author list (names only — no first/last split, so you'll need to parse)
- Note: arXiv author names are often formatted as "First Last" — extract first token as given name

**Important caveat:** arXiv author name formatting is inconsistent — some authors use initials only, some use full names. Plan for a higher `unknown` rate than PubMed.

---

### Step 3: Gender Inference

**The layered strategy:**

```python
import gender_guesser.detector as gender
import requests
import json

# Load cache (never re-query a name you've already looked up)
try:
    with open("data/gender_cache.json") as f:
        cache = json.load(f)
except FileNotFoundError:
    cache = {}

detector = gender.Detector(case_sensitive=False)

def infer_gender(first_name: str) -> dict:
    """
    Returns dict with keys: name, gender, probability, source
    gender values: 'male', 'female', 'unknown'
    """
    if not first_name or len(first_name) <= 1:
        return {"name": first_name, "gender": "unknown", "probability": None, "source": None}

    # Check cache first
    if first_name in cache:
        return cache[first_name]

    # Layer 1: gender-guesser (offline, instant)
    result = detector.get_gender(first_name)
    
    if result == "female":
        out = {"name": first_name, "gender": "female", "probability": 1.0, "source": "gender-guesser"}
    elif result == "male":
        out = {"name": first_name, "gender": "male", "probability": 1.0, "source": "gender-guesser"}
    elif result == "mostly_female":
        out = {"name": first_name, "gender": "female", "probability": 0.75, "source": "gender-guesser"}
    elif result == "mostly_male":
        out = {"name": first_name, "gender": "male", "probability": 0.75, "source": "gender-guesser"}
    else:
        # Layer 2: genderize.io API for unknowns
        out = query_genderize(first_name)

    cache[first_name] = out
    return out

def query_genderize(first_name: str) -> dict:
    """Query genderize.io — only call for names gender-guesser couldn't resolve."""
    try:
        r = requests.get(f"https://api.genderize.io?name={first_name}")
        data = r.json()
        if data.get("gender") and data.get("probability", 0) >= 0.7:
            return {
                "name": first_name,
                "gender": data["gender"],
                "probability": data["probability"],
                "source": "genderize"
            }
    except Exception:
        pass
    return {"name": first_name, "gender": "unknown", "probability": None, "source": None}

# Save cache periodically
def save_cache():
    with open("data/gender_cache.json", "w") as f:
        json.dump(cache, f)
```

**Probability threshold:** Following the original paper's approach, assign:
- `P_female = 1.0` for confirmed female names
- `P_female = 0.0` for confirmed male names  
- `P_female = probability` for probabilistic assignments
- Exclude `unknown` names from analysis (note exclusion rate in write-up)

**Important methodological note to document:** Name-based binary gender inference has known limitations — it cannot capture non-binary identities, performs worse on East Asian and Middle Eastern names, and may introduce systematic bias. These limitations should be explicitly stated in any publication or blog post.

---

### Step 4: Assign Author Positions

Replicating the original paper's position scheme:

```python
def assign_positions(author_list: list) -> list:
    """
    Returns list of (author_name, position) tuples.
    Positions: 'first', 'second', 'penultimate', 'last', 'other'
    """
    n = len(author_list)
    if n == 1:
        return [(author_list[0], "first")]
    if n == 2:
        return [(author_list[0], "first"), (author_list[1], "last")]
    if n == 3:
        return [(author_list[0], "first"), (author_list[1], "second"), (author_list[2], "last")]
    if n == 4:
        return [
            (author_list[0], "first"), (author_list[1], "second"),
            (author_list[2], "penultimate"), (author_list[3], "last")
        ]
    # 5+ authors
    positions = (
        [(author_list[0], "first"), (author_list[1], "second")] +
        [(a, "other") for a in author_list[2:-2]] +
        [(author_list[-2], "penultimate"), (author_list[-1], "last")]
    )
    return positions
```

---

### Step 5: Bootstrap Analysis

Replicating the original's statistical approach:

```python
import numpy as np

def bootstrap_pfemale(probabilities: list, n_iterations: int = 1000) -> tuple:
    """
    Given a list of P_female values (0.0–1.0) for a set of authors,
    returns (mean_pfemale, ci_lower, ci_upper) via bootstrap.
    Excludes None (unknown) values.
    """
    probs = [p for p in probabilities if p is not None]
    if not probs:
        return (None, None, None)
    
    probs = np.array(probs)
    means = []
    
    for _ in range(n_iterations):
        sample = np.random.choice(probs, size=len(probs), replace=True)
        means.append(np.mean(sample))
    
    means = np.array(means)
    return (
        np.mean(means),
        np.percentile(means, 2.5),
        np.percentile(means, 97.5)
    )
```

---

### Step 6: Key Analyses to Run

Replicating original figures + new analyses:

**Figure 1A equivalent:** P_female by author position (first, second, other, penultimate, last) for Bio vs. Comp datasets, 2015–2024. Compare to original paper's numbers directly.

**Figure 1B equivalent:** P_female over time (by year) for Bio vs. Comp. Extend the original trend lines through 2024. Look for the COVID dip (2020–2022).

**Figure 1C equivalent:** P_female by position, split by whether last author is male vs. female. Test whether the "female PI effect" persists.

**New analysis — subfield breakdown:** Within the comp bio MeSH dataset, look at sub-MeSH terms (genomics, proteomics, systems biology, computational neuroscience, bioinformatics) to see if gender gaps vary by subfield.

**New analysis — COVID effect:** Compare 2019 vs. 2020–2021 female authorship rates. Was there a measurable dip?

**arXiv comparison:** P_female in q-bio vs. cs by author position, 2015–2024. Compare to original's 2007–2016 numbers.

---

### Step 7: Figures for Publication

All figures should be exported at 300 DPI for print and as SVG/PNG for web.

| Figure | Description |
|---|---|
| Fig 1 | Bar chart: P_female by author position, Bio vs. Comp, 2015–2024 |
| Fig 2 | Line chart: P_female over time 1997–2024 (stitching original + new data) |
| Fig 3 | Bar chart: Female PI effect — P_female by position, male vs. female last author |
| Fig 4 | Line chart: arXiv q-bio vs. cs, P_female over time |
| Fig 5 (new) | COVID dip: year-by-year 2018–2023 with 2020 highlighted |
| Fig 6 (new) | Subfield comparison bar chart |

---

## Methodological Limitations to Document

These should be addressed explicitly in the blog post and any future academic write-up:

1. **Binary gender framework:** Name inference can only assign male/female. Non-binary and gender-nonconforming researchers are not represented.
2. **Name coverage gaps:** Western names are better covered than East Asian, South Asian, Arabic, and African names. This may systematically undercount or misclassify authors from those regions.
3. **Exclusion rate:** ~27% of authors in the original paper had unresolvable names. Document your own exclusion rate and check whether it varies systematically by dataset or year.
4. **MeSH term assignment is manual and incomplete:** Not all relevant comp bio papers are tagged with the Computational Biology MeSH term.
5. **Last author ≠ PI universally:** The convention of last author = PI is strongest in biology; it does not hold in all subfields or in CS-adjacent work.
6. **This is authorship data, not workforce data:** Publication rates reflect many factors beyond representation — funding, productivity norms, career stage distributions, etc.

---

## Publication Plan

---

### Publication 1: BWIB Deep Dive Blog Post

**Platform:** boston-wib.org/blog (Deep Dive category) + linafaller.com  
**Target length:** 1,200–1,800 words  
**Target publish date:** After analysis is complete; ideally while BWIB community survey is still open  
**Byline:** Lina Faller, Ph.D. — VP, Boston Women in Bioinformatics

**Suggested title:**  
*"Where Do We Stand? Updating a Landmark Study on Gender in Computational Biology"*

**Outline:**

1. **Hook (150 words):** Open with the BWIB community survey — we're collecting data on the landscape of women in bioinformatics right now, which made us ask: what does the *published* literature actually tell us about where we've been? Introduce the Bonham & Stefan 2017 paper as the foundation.

2. **What we knew in 2017 (200 words):** Summarize key findings from the original paper clearly and accessibly. Include 1–2 of the original figures or recreated versions for reference. Emphasize the "female PI effect" finding — it's the most actionable result and relevant to BWIB's mentorship program.

3. **What's changed — and what hasn't (400 words):** Present your updated numbers. Lead with the most striking finding. Structure as: overall trend, the COVID question, the PI effect update, arXiv comparison. Use your new figures here.

4. **What the numbers can't tell us (200 words):** Be transparent about limitations — binary gender framework, name coverage gaps, authorship ≠ workforce representation. This section builds credibility and models good scientific communication for the community.

5. **What this means for BWIB (200 words):** Connect findings directly to BWIB programs — the mentorship program (addressing the PI effect), the community survey (filling gaps the literature can't), event programming. This is where the post earns its place on the BWIB site rather than just being generic content.

6. **Call to action (100 words):** Fill out the BWIB survey. Share the post. Link to GitHub repo for anyone who wants to build on the analysis.

**Visuals to include:** Fig 2 (trend over time — the most intuitive), Fig 1 (position breakdown), Fig 3 (PI effect). Keep figures clean and label axes clearly for a non-specialist audience.

---

### Publication 2: LinkedIn Article

**Platform:** Lina Faller's LinkedIn + BWIB LinkedIn Group  
**Target length:** 400–600 words (LinkedIn article format, not a post)  
**Timing:** Same day or day after BWIB blog post goes live

**Suggested title:**  
*"I Updated a 2017 Study on Women in Computational Biology. Here's What 10 More Years of Data Shows."*

**Structure:**

- **Opening line (no cutoff):** Lead with the most surprising or concrete finding. Example: *"In 2017, a landmark study found that women made up just 21% of last authors in computational biology papers. We wanted to know: has that changed?"*
- **2–3 short paragraphs** covering the key findings — keep it punchy, one idea per paragraph, no jargon
- **One key figure** embedded (the trend-over-time line chart works best on LinkedIn)
- **The nuance paragraph:** One honest paragraph on what name-based analysis can and can't tell us — this signals rigor and tends to get engagement from technical audiences
- **The so-what:** Connect to BWIB, the mentorship program, and the community survey
- **Closing CTA:** Link to full BWIB blog post + survey link

**LinkedIn-specific tips:**
- The first 2 lines are what show before "see more" — make them count
- Tag BWIB's LinkedIn group in the post
- Hashtags to include: #WomenInSTEM #Bioinformatics #ComputationalBiology #WomenInScience #DataScience
- Post on a Tuesday or Wednesday morning for best reach

---

### Optional Publication 3: GitHub README as standalone resource

The repo README itself can function as a third publication format — a technical write-up for people who want to reproduce or extend the analysis. Include:
- Project motivation and connection to Bonham & Stefan 2017
- Quickstart instructions
- Summary of findings with figures
- Explicit methodology and limitations section
- How to contribute or extend

This makes the repo citable and reusable by other researchers, and signals rigor to anyone who finds your work via search.

---

## Timeline Suggestion

| Week | Task |
|---|---|
| 1 | Set up repo, write PubMed + arXiv fetchers, start data collection |
| 2 | Run gender inference pipeline, build processed datasets |
| 3 | Run bootstrap analysis, generate all figures |
| 4 | Write BWIB Deep Dive post, create LinkedIn version |
| 5 | Review + edit, coordinate with BWIB for cross-posting, publish |

---

## Key References

- Bonham KS, Stefan MI (2017). Women are underrepresented in computational biology. *PLoS Comput Biol* 13(10): e1005134. https://doi.org/10.1371/journal.pcbi.1005134
- Giannos P et al. (2023). Female Dynamics in Authorship of Scientific Publications in the Public Library of Science. *EJIHPE* 13(2). https://doi.org/10.3390/ejihpe13020018
- Mihaljević H & Santamaría L (2021). Comparison and benchmark of name-to-gender inference services. *PeerJ Comput Sci* 7:e156. https://doi.org/10.7717/peerj-cs.156
- Gender-guesser Python package: https://pypi.org/project/gender-guesser/
- Genderize.io API: https://genderize.io
- NCBI E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25499/
- arXiv Python wrapper: https://github.com/lukasschwab/arxiv.py
- Original paper's data and code (archived): https://doi.org/10.5281/zenodo.60090

---

*Document prepared: February 2026*  
*Project lead: Lina Faller, Ph.D.*  
*For use with Claude Code for Python implementation*
