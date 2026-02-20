# Where Do We Stand? Updating a Landmark Study on Gender in Computational Biology

**By Lina Faller, Ph.D., VP Boston Women in Bioinformatics**
*February 2026*

---

## The Question We Asked

Right now, BWIB is collecting community data through our landscape survey (asking women in bioinformatics directly about their experiences, barriers, and aspirations). But while we listen to our community, we also wanted to know: what does the *published* literature actually tell us about where we've been?

Eight years ago, two researchers named Bonham and Stefan published a landmark paper in *PLoS Computational Biology* that answered a simple question: Are women underrepresented in computational biology authorship? Their answer was yes. But it's 2026 now. Does their finding still hold? What has changed, and what hasn't?

I decided to replicate their 2017 analysis with a decade of new data through 2025, and the results are both encouraging and sobering.

---

## What We Knew in 2017

Bonham and Stefan's 2017 study examined gender representation across biology, computational biology, and computer science using PubMed and arXiv data spanning 1997–2014. Their key findings:

- **Female authorship in computational biology lagged biology by 4–6 percentage points** across all author positions
- **Female first authors in comp bio: ~32% | Last authors: ~21%** (a gap of 11 percentage points)
- Papers with a female last author had significantly more female co-authors at all positions (the "female PI effect")
- The gender gap was narrowing, but slowly: only **~0.5 percentage points per year**

The implications were clear: computational biology had a gender representation problem, and at the rate of progress, closing the gap would take decades.

We wanted to know: have the last 10 years changed that trajectory?

---

## What's Changed and What Hasn't

### The Encouraging Trend

When I analyzed 274,702 PubMed papers and 977,731 unique authors from 2015–2025, the first thing I looked at was the long-term trend. And there's good news:

**Female representation in computational biology has grown from 37.3% (2015) to 42.3% (2025), a gain of 5 percentage points over a decade.**

That's roughly **10 times the pace Bonham and Stefan observed** in earlier decades.

Here's the year-by-year breakdown:
- 2015: 37.3%
- 2018: 38.1%
- 2020 (pandemic year): 39.9%
- 2023: 41.1%
- 2025: 42.3%

This is meaningful progress. But let me be precise about what it represents: this is P(female), the proportion of female authors at each position weighted by position type (first author, last author, middle positions). It's the right metric for understanding representation, but it's also important to note the *range* across positions.

### The Persistence of Position Gaps

When I break down female representation by author position for 2015–2025:

- **First authors: 45.4%** female
- **Second authors: 43.7%** female
- **Middle authors: 41.3%** female
- **Penultimate authors: 30.8%** female
- **Last authors: 30.9%** female

The pattern is striking: female representation drops sharply in the last two author positions. If last authorship is a proxy for being the senior investigator (PI), this means that women are underrepresented in senior leadership positions in computational biology. Still.

**The gap between first and last author positions is now 14.5 percentage points.** In 2017, it was ~11 percentage points. We've made progress on first authorship, but the senior gap persists.

### The Female PI Effect: Still Present

One of Bonham and Stefan's most interesting findings was the "female PI effect": papers with a female last author tended to have more female co-authors across all positions. This suggested a multiplier effect; women in senior positions actively recruit and support women at earlier career stages.

I tested this hypothesis in the current dataset and found it still holds. Papers where the last author (presumed PI) is female show higher female representation at every position compared to papers with male last authors. This is an important and hopeful finding: women in power in computational biology are practicing inclusive leadership.

### COVID and After

Did the pandemic affect gender representation? The numbers suggest a modest disruption:

- **Pre-COVID (2018–2019):** 38.7% female
- **During pandemic (2020–2021):** 39.9% female
- **Recovery (2022–2025):** 41.3% female

Rather than a dip, we see a *continuation* of the upward trend, even during lockdowns. This is remarkable. One interpretation: remote work and virtual conferences may have reduced some barriers that historically disadvantaged women. Another interpretation: the pandemic prompted many journals and institutions to examine their practices, including around equity and diversity.

---

## What the Numbers Can't Tell Us

Before I go further, I need to be honest about the limitations of this analysis. These insights are real, but they're not complete.

**First:** Gender inference from first names is a binary classification; it can assign male or female, but cannot represent non-binary or gender-nonconforming researchers. This analysis is invisible to them.

**Second:** Name-based gender databases work better for Western names than for East Asian, South Asian, Arabic, or African names. This likely means we're *undercounting* female authors from those regions, introducing a systematic bias. This is a known and documented problem in name-based gender studies, and it's worth acknowledging.

**Third:** About 40% of authors could not be assigned a gender using our two-layer approach (gender-guesser + genderize.io API). To validate that this doesn't bias results, I manually classified a random sample of 100 unknown names through web searches. The findings are reassuring: the unclassifiable names are roughly 56% male and 19% female, compared to 53% male and 27% female in our successfully-classified set. This suggests that excluding unknowns doesn't systematically skew our results toward one gender. The position gap (45% female first authors vs 31% female last authors) persists even when analyzing only papers with fully-classified authors, confirming that our main findings are robust to this limitation. Most unknowns are names with non-Latin scripts (Cyrillic, Greek, diacriticals from Eastern European and Mediterranean regions), which aligns with the original Bonham & Stefan 2017 study's finding that name-based inference has similar limitations across tools.

**Fourth:** What we're measuring is *authorship*, not the workforce. Publication rates depend on funding, career stage distributions, research productivity norms, and many other factors beyond gender representation. These numbers describe who publishes, not necessarily who works in the field.

That said, authorship in peer-reviewed literature is a meaningful signal; it's how scientific accomplishment is documented and credited. So these trends matter.

---

## What This Means for BWIB

The data tells us something important: progress is possible, and it's accelerating.

When Bonham and Stefan published their work in 2017, it wasn't academic; it was a call to action. And the community responded. Funding agencies, journals, and institutions began paying attention to representation. Mentorship programs, like BWIB's own, expanded. Women's visibility in computational biology grew.

The acceleration we're seeing (from 0.5 percentage points/year to 0.5 percentage points/year *or more*) suggests that intentional work on diversity and inclusion *works*.

At the same time, the 14-point gap between first and last author representation reminds us that there's still work to do, particularly around building pathways to senior leadership for women in computational biology. This is exactly where BWIB's mentorship program, leadership development initiatives, and visibility campaigns add value.

The female PI effect tells us something encouraging: women in power in this field are bringing other women along. That's not a given in many STEM disciplines. It's something to celebrate and strengthen.

---

## Join the Conversation

This analysis is open-source and reproducible. If you want to explore the data yourself, dive deeper into any finding, or extend this work to your own subfield or research question, the code and methodology are available on GitHub.

And if you haven't already, **fill out the BWIB community survey**. The quantitative data I've presented here describes the published literature, but it doesn't capture the lived experiences of women in our field (the barriers you face, the support you need, the changes you want to see). That's what the survey is designed to capture, and it's equally important.

Progress isn't inevitable. It's the result of people who care enough to ask questions, to measure what matters, and to act on what they find. That's what we're doing together.

---

**Questions? Thoughts?** Share them on the BWIB forum or reach out to me directly. And help us spread the word; share this analysis with colleagues, students, and fellow women in computational biology.

Together, we're shifting the landscape.

---

*Data through 2025 | Analysis of 274,702 papers and 977,731 authors | Code available on GitHub*
