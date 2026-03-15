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

---

### Stage 9 — Docker Workflow

**Result: NOT EXECUTABLE — `docker` is not installed on this Windows system. Static audit performed instead.**

The Docker files (`Dockerfile`, `docker-compose.yml`, `.dockerignore`) were audited statically. **Two critical bugs were found that would have caused the Docker build and container to fail.**

#### Bug 1: `docker-compose.yml` — `ENTREZ_EMAIL` still used (Fix 12)

`docker-compose.yml` line 14 still referenced `ENTREZ_EMAIL`, which was missed when Fix 3 updated the Makefile and README:

```yaml
# Before (broken — cli.py reads NCBI_EMAIL, not ENTREZ_EMAIL)
ENTREZ_EMAIL: ${ENTREZ_EMAIL:-your.email@example.com}

# After (fixed)
NCBI_EMAIL: ${NCBI_EMAIL:-your.email@example.com}
```

Any `docker compose up` run followed by `cli.py fetch` would have failed with `ClickException: NCBI_EMAIL not set in .env file` even if the user had set `ENTREZ_EMAIL` in their shell environment.

#### Bug 2: `Dockerfile` — Python 3.9 incompatible with scipy 1.13 (Fix 13)

The Dockerfile used `python:3.9-slim` as both the build and runtime base. However, `scipy~=1.13.0` (pinned in Fix 11) requires Python ≥ 3.10:

- scipy 1.12 (Jan 2024): last release to support Python 3.9
- scipy 1.13 (Apr 2024): minimum Python 3.10

A `docker build` would fail during `pip install -r requirements.txt`. Building from sdist would also fail because the Dockerfile installs only `build-essential` (no `gfortran`), which scipy's Fortran extensions require.

Additionally, Python 3.9 reached end-of-life in October 2025 and receives no further security patches.

**Fix applied:** Updated both `FROM` lines and the multi-stage `COPY` path from `python:3.9` to `python:3.11`:

```dockerfile
# Before
FROM python:3.9-slim AS base
FROM python:3.9-slim
COPY --from=base /usr/local/lib/python3.9/site-packages ...

# After
FROM python:3.11-slim AS base
FROM python:3.11-slim
COPY --from=base /usr/local/lib/python3.11/site-packages ...
```

#### Static audit of remaining Docker components

| Component | Finding |
|---|---|
| `.dockerignore` | Correct — excludes `.env`, `data/*.db`, large CSVs, `venv/`; secrets are not baked into the image |
| `Makefile` docker targets | Correct — `docker-run` and `docker-shell` already pass `NCBI_EMAIL` (fixed in Fix 3) |
| `HEALTHCHECK` | Functional — imports `cli` module; heavyweight but correct |
| Default `CMD ["analyze"]` | Expected to fail without a database (by design; users must run `download-zenodo` or `infer` first) |

---

## Additional Bugs Found During Docker Audit

Two bugs were discovered during the Docker audit. Both were fixed immediately and are documented as Fixes 12–13 in [REPRODUCIBILITY_FIXES.md](./REPRODUCIBILITY_FIXES.md).

### Fix 12 — `ENTREZ_EMAIL` in `docker-compose.yml`

| Field | Detail |
|---|---|
| **File** | `docker-compose.yml` line 14 |
| **Severity** | 🔴 Critical |
| **Symptom** | `docker compose up` + `cli.py fetch` fails with `NCBI_EMAIL not set in .env file` |
| **Root cause** | Fix 3 updated Makefile and README but missed `docker-compose.yml` |
| **Fix** | `ENTREZ_EMAIL: ${ENTREZ_EMAIL:-...}` → `NCBI_EMAIL: ${NCBI_EMAIL:-...}` |

### Fix 13 — `python:3.9-slim` incompatible with `scipy~=1.13.0`

| Field | Detail |
|---|---|
| **File** | `Dockerfile` lines 3, 19, 24 |
| **Severity** | 🔴 Critical |
| **Symptom** | `docker build` fails — no scipy 1.13 wheel for Python 3.9; sdist build also fails (no gfortran) |
| **Root cause** | scipy 1.13 (Apr 2024) requires Python ≥ 3.10; Python 3.9 also EOL since Oct 2025 |
| **Fix** | Changed both `FROM python:3.9-slim` to `FROM python:3.11-slim`; updated site-packages path |

---

## Additional Bugs Found During Full Reproduction Path Audit

Four bugs were discovered while auditing all documented reproduction paths (bash downloader, DOCKER.md, journal impact script, README). All were fixed immediately and are documented as Fixes 14–17 in [REPRODUCIBILITY_FIXES.md](./REPRODUCIBILITY_FIXES.md).

### Fix 14 — Bash Zenodo downloader missing `/content` suffix

| Field | Detail |
|---|---|
| **File** | `scripts/download_zenodo_data.sh` line 33 |
| **Severity** | 🔴 Critical |
| **Symptom** | `bash scripts/download_zenodo_data.sh` downloads JSON metadata instead of binary files |
| **Root cause** | Same bug as Fix 6; the Python script was patched but the bash version was not updated |
| **Fix** | `FILE_URL="${ZENODO_URL}/${FILE}"` → `FILE_URL="${ZENODO_URL}/${FILE}/content"` |

### Fix 15 — `DOCKER.md` used `ENTREZ_EMAIL` throughout

| Field | Detail |
|---|---|
| **File** | `DOCKER.md` (12 occurrences) |
| **Severity** | 🔴 Critical |
| **Symptom** | Any user following `DOCKER.md` sets `ENTREZ_EMAIL`; container ignores it and fails on `fetch` |
| **Root cause** | Fix 3 and Fix 12 updated Makefile, README, and `docker-compose.yml` but not `DOCKER.md` |
| **Fix** | Replaced all 12 `ENTREZ_EMAIL` occurrences with `NCBI_EMAIL` |

### Fix 16 — `DOCKER.md` wrong command for preprocess step

| Field | Detail |
|---|---|
| **File** | `DOCKER.md` line 168 |
| **Severity** | 🟡 Minor |
| **Symptom** | `docker run gender-gap-compbio run_gender_inference_db.py` runs `python cli.py run_gender_inference_db.py` — not a valid CLI subcommand |
| **Root cause** | Wrong script name and incompatible with `python cli.py` ENTRYPOINT |
| **Fix** | `docker run --entrypoint python ... scripts/preprocess_journal_quartiles.py` |

### Fix 17 — Stale script paths in `analyze_journal_impact.py` and `README.md`

| Field | Detail |
|---|---|
| **Files** | `scripts/analyze_journal_impact.py` (lines 86, 265), `README.md` (line 280) |
| **Severity** | 🟡 Minor |
| **Symptom** | Error messages and README workflow step suggest bare filenames that don't exist at repo root |
| **Root cause** | Scripts moved to `scripts/` in v0.3.0; error messages and docs not updated |
| **Fix** | Updated to `python scripts/preprocess_journal_quartiles.py`, `python cli.py infer` |

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
| Docker build/run | NOT EXECUTABLE | `docker` not installed; static audit found 2 critical bugs (fixed) |
| Full path audit (bash downloader, DOCKER.md, journal scripts, README) | STATIC AUDIT | 4 additional bugs found and fixed |

**9 additional bugs found and fixed during testing, Docker audit, and full path audit** (Fixes 9–17 in `REPRODUCIBILITY_FIXES.md`), bringing the total to **17 fixes**.

The workflow is reproducible on the path that can be tested without API keys. The fast reproduction path (Zenodo download → analyze → figures) is expected to work end-to-end given that: (a) the download URL is correct in both the Python and bash downloaders, (b) all CLI commands import and exit with correct codes, (c) all module imports succeed with the pinned package versions, and (d) Docker builds are expected to succeed after the Python 3.11 and `NCBI_EMAIL` fixes.
