# Reproducibility Testing Results

End-to-end workflow test in a clean environment, following all documented instructions and skipping steps that require API keys (PubMed fetch, Groq classification).

**Test date:** March 2026
**Python version:** 3.12.10
**Platform:** Windows 11 (win32)
**Tested by:** Claude Code (claude-sonnet-4-6)

---

## Test Environment

A fresh virtual environment was created with no pre-installed packages:

```bash
python -m venv .test_venv
.test_venv/Scripts/pip install -r requirements.txt
```

---

## Results by Stage

### Stage 1 — Dependency Installation

**Result: PASS with two additional fixes required**

`pip install -r requirements.txt` completed successfully. All 17 declared packages and their transitive dependencies resolved and installed without conflicts.

**Additional bug found during testing: Two-component `~=X.Y` does not pin minor versions**

The `requirements.txt` fix in `REPRODUCIBILITY_FIXES.md` used the two-component form `~=X.Y` (e.g., `groq~=0.9`). Per PEP 440, `~=X.Y` means `>=X.Y, ==X.*` which pins the major version but allows *any* minor version ≥ Y. In practice this caused:

| Package spec | Resolved version | Drift |
|---|---|---|
| `groq~=0.9` | `groq 0.37.1` | +28 minor versions |
| `matplotlib~=3.9` | `matplotlib 3.10.8` | +1 minor version |
| `pandas~=2.2` | `pandas 2.3.3` | +1 minor version |
| `scipy~=1.13` | `scipy 1.17.1` | +4 minor versions |

The 28-minor-version jump for `groq` (0.9 → 0.37) is particularly risky for a library with rapid API changes.

**Fix applied:** Updated `requirements.txt` to use three-component form `~=X.Y.0`, which is equivalent to `>=X.Y.0, ==X.Y.*` and correctly pins to the specified minor version:

```
# Before (two-component — pins major only)
groq~=0.9
matplotlib~=3.9
pandas~=2.2

# After (three-component — pins major.minor)
groq~=0.9.0        → resolves to groq 0.9.0
matplotlib~=3.9.0  → resolves to matplotlib 3.9.4
pandas~=2.2.0      → resolves to pandas 2.2.3
```

**Final resolved versions (after fix):**
```
click          8.1.8
python-dotenv  1.0.1
biopython      1.83.0
arxiv          2.1.0
requests       2.31.0
tenacity       8.2.3
gender-guesser 0.4.0
groq           0.9.0
pandas         2.2.3
numpy          1.26.4
scipy          1.13.1
tqdm           4.66.6
matplotlib     3.9.4
seaborn        0.13.2
plotly         5.22.0
jupyter        1.0.0
ipython        8.25.0
```

---

### Stage 2 — Python Syntax Check

**Result: PASS — all 13 files clean**

Every Python file was compiled with `python -m py_compile`. All passed without errors:

```
PASS: cli.py
PASS: src/pubmed_fetcher.py
PASS: src/gender_utils.py
PASS: src/db_utils.py
PASS: src/bootstrap.py
PASS: src/plotting.py
PASS: scripts/run_gender_inference_db.py
PASS: scripts/classify_names_retry.py
PASS: scripts/preprocess_journal_quartiles.py
PASS: scripts/analyze_journal_impact.py
PASS: scripts/reproduce_bonham_stefan.py
PASS: scripts/analyze_gender_with_filtering.py
PASS: scripts/download_zenodo_data.py
```

---

### Stage 3 — CLI Help and Import Test

**Result: PASS with one additional bug found and fixed**

**Additional bug found: `UnicodeEncodeError` on Windows when running `--help`**

Running `python cli.py --help` immediately raised:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 493: character maps to <undefined>
```

The `→` character (U+2192) in the `run` command docstring is not representable in Windows code page 1252. Click writes docstrings to the terminal when rendering `--help`, which triggered the encoding error.

**Fix applied:** Replaced `→` with ASCII `->` in the docstring (`cli.py` line 363):

```python
# Before
"""Run the complete pipeline: fetch → infer → analyze → figures."""

# After
"""Run the complete pipeline: fetch -> infer -> analyze -> figures."""
```

After the fix, all five `--help` outputs rendered correctly:

```
cli.py --help          PASS
cli.py fetch --help    PASS
cli.py infer --help    PASS
cli.py analyze --help  PASS
cli.py figures --help  PASS
cli.py run --help      PASS
```

---

### Stage 4 — Source Module Imports

**Result: PASS — all five modules and their key classes import correctly**

```
PASS: src.pubmed_fetcher.PubMedFetcher
PASS: src.gender_utils.GenderInference
PASS: src.db_utils.GenderDatabase
PASS: src.bootstrap.bootstrap_pfemale
PASS: src.plotting.plot_pfemale_by_position
```

---

### Stage 5 — Expected Failure Modes

Tests that each pipeline step fails gracefully (correct error message, exit code 1) when its precondition is not met.

**`cli.py fetch` (no NCBI_EMAIL set)**

```
Error: NCBI_EMAIL not set in .env file
Exit: 1
```
PASS — clear, actionable message. Correct variable name after REPRODUCIBILITY_FIXES fix.

**`cli.py analyze` (no database)**

```
Error: Database not found at data/gender_data.db
Please run: python run_gender_inference_db.py
Exit: 1
```
Result: PASS on exit code, but the error message referenced the old bare script path. **Additional fix applied:** Updated error message to `python cli.py infer`.

```
# Before
Please run: python run_gender_inference_db.py

# After
Please run: python cli.py infer
```

**`cli.py figures` (no analysis CSVs)**

```
Error: Missing analysis results: [Errno 2] No such file or directory: 'data/processed/analysis_position_breakdown.csv'
Run 'python cli.py analyze' first
Exit: 1
```
PASS — clear error, correct suggested command.

---

### Stage 6 — Zenodo Download URL Verification

**Result: PASS — fix confirmed correct**

The old URL (before fix) was probed via HTTP GET:

```
URL:           https://zenodo.org/api/records/18894714/files/gender_data.db.gz
Content-Type:  application/json
First bytes:   {"created": "2026-03-06T20:40:14.972501+...
```
Confirmed: returns JSON metadata, not the file.

The new URL (after fix, with `/content`) was probed via byte-range GET:

```
URL:           https://zenodo.org/api/records/18894714/files/gender_data.db.gz/content
HTTP status:   206 Partial Content
Content-Type:  application/octet-stream
First bytes:   b'\x1f\x8b\x08\x08...' (gzip magic bytes 0x1f 0x8b confirmed)
```
Confirmed: returns actual binary gzip content.

---

### Stage 7 — Makefile Targets

**Result: NOT TESTABLE — `make` is not installed on this Windows system**

The `make` command is not available in the system PATH. The Makefile requires a Unix-compatible `make` binary (available via Git for Windows, MSYS2, Chocolatey, or WSL).

The Makefile content was audited statically to verify:
- All `ENTREZ_EMAIL` references replaced with `NCBI_EMAIL` — confirmed ✓
- Script paths corrected to `scripts/` prefix — confirmed ✓
- `classify` target references `scripts/classify_names_retry.py` — confirmed ✓

**Note for users on Windows:** To use the Makefile, install `make` via one of:
```bash
# Option A: Chocolatey
choco install make

# Option B: Winget
winget install GnuWin32.Make

# Option C: Use WSL and run make from there
```

---

### Stage 8 — API-Dependent Steps (Skipped)

The following steps were skipped because they require API keys or result in multi-hour network operations:

| Step | Reason skipped |
|---|---|
| `cli.py fetch` | Requires `NCBI_EMAIL`; 2–4 hour PubMed API operation |
| `cli.py infer` | Requires output of `fetch` |
| `scripts/classify_names_retry.py` | Requires `GROQ_API_KEY` |
| `scripts/preprocess_journal_quartiles.py` | Requires database from `infer` |
| `cli.py analyze` | Requires database from `infer` |
| `cli.py figures` | Requires CSVs from `analyze` |
| `scripts/download_zenodo_data.py` | Would download ~550 MB; URL fix verified via probe instead |

These steps can be verified by:
1. Setting up a real `.env` file with valid API keys
2. Either running `python cli.py run` (full pipeline, ~5 hours) or `python scripts/download_zenodo_data.py` followed by `python cli.py analyze && python cli.py figures` (fast path, ~30–45 min)

---

## Additional Bugs Found During Testing

Three bugs were discovered during testing that were not in the original audit. All were fixed immediately and are documented as Fixes 8–10 in [REPRODUCIBILITY_FIXES.md](./REPRODUCIBILITY_FIXES.md).

### Fix 8 — `UnicodeEncodeError` on Windows CLI help

| Field | Detail |
|---|---|
| **File** | `cli.py` line 363 |
| **Severity** | 🔴 Critical on Windows |
| **Symptom** | `python cli.py --help` crashes with `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'` |
| **Root cause** | `→` (U+2192 RIGHT ARROW) in the `run` command docstring is not in Windows code page 1252 |
| **Fix** | Replaced `→` with ASCII `->` |
| **Affects** | Any Windows user without `PYTHONUTF8=1` or `PYTHONIOENCODING=utf-8` set |

### Fix 9 — Stale error message path in `cli.py analyze`

| Field | Detail |
|---|---|
| **File** | `cli.py` lines 185–188 |
| **Severity** | 🟡 Minor |
| **Symptom** | Error message says `python run_gender_inference_db.py` (root-level, non-existent path) |
| **Root cause** | Error message was not updated when the script was moved to `scripts/` in v0.3.0 |
| **Fix** | Updated error message to `python cli.py infer` (uses the CLI command) |

### Fix 10 — Two-component `~=X.Y` allows minor version drift

| Field | Detail |
|---|---|
| **File** | `requirements.txt` |
| **Severity** | 🟡 Minor |
| **Symptom** | `groq~=0.9` resolved to `groq 0.37.1` (28 minor versions ahead) |
| **Root cause** | PEP 440: `~=X.Y` (two components) = `>=X.Y, ==X.*`, pins major only |
| **Fix** | Switched to three-component form `~=X.Y.0` = `>=X.Y.0, ==X.Y.*`, pins major.minor |

---

## Summary

| Stage | Result | Notes |
|---|---|---|
| Dependency installation | PASS | After switching to `~=X.Y.0` pinning |
| Syntax check (13 files) | PASS | All clean |
| CLI `--help` | PASS | After fixing `→` encoding bug |
| Module imports (5 modules) | PASS | All key classes importable |
| Failure modes (3 cases) | PASS | After fixing stale error message |
| Zenodo URL | PASS | `/content` suffix confirmed to return binary data |
| Makefile | NOT TESTABLE | `make` not installed on Windows |
| API-dependent steps | SKIPPED | Require API keys / large downloads |

**3 additional bugs found and fixed during testing** (Fixes 8–10 in `REPRODUCIBILITY_FIXES.md`), bringing the total to **11 fixes**.

The workflow is reproducible on the path that can be tested without API keys. The fast reproduction path (Zenodo download → analyze → figures) is expected to work end-to-end given that: (a) the download URL is now correct, (b) all CLI commands import and exit with correct codes, and (c) all module imports succeed with the pinned package versions.
