# Reproducibility Fixes

This document records all bugs found during a reproducibility audit and the exact changes made to resolve them. Each issue is classified by severity, root cause, and impact.

**Audit date:** March 2026
**Audited by:** Claude Code (claude-sonnet-4-6)

---

## Summary

11 bugs fixed in total: 8 found during the initial static audit, 3 discovered during live testing.

| # | Found | Severity | File | Issue |
|---|---|---|---|---|
| 1 | Audit | 🔴 Critical | `Makefile` | Wrong paths for three script invocations |
| 2 | Audit | 🔴 Critical | `Makefile` | `classify` target references non-existent filename |
| 3 | Audit | 🔴 Critical | `Makefile` / `cli.py` / `README.md` | `ENTREZ_EMAIL` used where code expects `NCBI_EMAIL` |
| 4 | Audit | 🔴 Critical | `cli.py` | `infer` command was a non-functional stub |
| 5 | Audit | 🔴 Critical | `cli.py` | `run` pipeline exited after Step 2; Steps 3–4 were dead code |
| 6 | Audit | 🔴 Critical | `scripts/download_zenodo_data.py` | Zenodo download URL missing `/content` suffix |
| 7 | Audit | 🟡 Minor | `requirements.txt` | Unpinned `>=` versions allow silent dependency drift |
| 8 | Audit | 🟡 Minor | `.env.example` | Missing `GROQ_API_KEY`; two stale unused keys present |
| 9 | Testing | 🔴 Critical | `cli.py` | `→` in docstring causes `UnicodeEncodeError` on Windows |
| 10 | Testing | 🟡 Minor | `cli.py` | Error message in `analyze` pointed to non-existent script path |
| 11 | Testing | 🟡 Minor | `requirements.txt` | Two-component `~=X.Y` allows minor-version drift |

---

## Fix 1 — Makefile: Wrong script paths

**File:** `Makefile`
**Lines:** 97, 101, 104
**Severity:** 🔴 Critical

### Problem

All three script-running targets in the Makefile invoked scripts from the repo root directory, but the scripts live in the `scripts/` subdirectory. Running `make infer`, `make classify`, or `make preprocess-journals` produced `No such file or directory` errors immediately.

```makefile
# Before (broken)
infer:
    $(PYTHON) run_gender_inference_db.py

classify:
    $(PYTHON) classify_names.py

preprocess-journals:
    $(PYTHON) preprocess_journal_quartiles.py
```

### Fix

Added the correct `scripts/` prefix to all three targets:

```makefile
# After (fixed)
infer:
    $(PYTHON) scripts/run_gender_inference_db.py

classify:
    $(PYTHON) scripts/classify_names_retry.py

preprocess-journals:
    $(PYTHON) scripts/preprocess_journal_quartiles.py
```

Note: The `classify` target also referenced `classify_names.py` — a filename that does not exist. The actual script is `classify_names_retry.py`. Both the path and the filename were corrected.

---

## Fix 2 — Makefile / cli.py / README: `ENTREZ_EMAIL` vs `NCBI_EMAIL`

**Files:** `Makefile` (lines 56, 137, 143, 153, 157), `README.md` (lines 143, 178)
**Severity:** 🔴 Critical

### Problem

There was a three-way inconsistency in what environment variable name was used for the NCBI email address:

| Location | Variable used |
|---|---|
| `cli.py` line 91 (code that actually reads the variable) | `NCBI_EMAIL` |
| `.env.example` | `NCBI_EMAIL` |
| `Makefile` `setup` target (writes `.env`) | `ENTREZ_EMAIL` |
| `Makefile` `docker-run` / `docker-shell` (passes to container) | `ENTREZ_EMAIL` |
| `README.md` Quick Start | `ENTREZ_EMAIL` |

Any user following `make setup` would get a `.env` file with `ENTREZ_EMAIL=...`, but the code at `cli.py:91` reads `NCBI_EMAIL` and throws a hard error if it is absent:

```python
email = os.getenv("NCBI_EMAIL")
if not email:
    raise click.ClickException("NCBI_EMAIL not set in .env file")
```

This meant `make fetch` would always fail for new users who used `make setup`.

### Fix

Standardised on `NCBI_EMAIL` everywhere (matching the code and `.env.example`):

- `Makefile` `setup` target: `ENTREZ_EMAIL=...` → `NCBI_EMAIL=...`
- `Makefile` `docker-run`: `-e ENTREZ_EMAIL=$(ENTREZ_EMAIL)` → `-e NCBI_EMAIL=$(NCBI_EMAIL)`
- `Makefile` `docker-shell`: same change
- `Makefile` error message: updated to reference `NCBI_EMAIL`
- `Makefile` usage hint: `ENTREZ_EMAIL=your@email.com make docker-run` → `NCBI_EMAIL=your@email.com make docker-run`
- `README.md`: `export ENTREZ_EMAIL=...` → `export NCBI_EMAIL=...`
- `README.md`: `make docker-run ENTREZ_EMAIL=...` → `make docker-run NCBI_EMAIL=...`

---

## Fix 3 — cli.py: `infer` command was a non-functional stub

**File:** `cli.py`
**Lines:** 160–172
**Severity:** 🔴 Critical

### Problem

The `cli.py infer` command printed instructions telling the user to run the inference script manually, but it did not actually execute anything. Calling `python cli.py infer` was a no-op from an automation perspective:

```python
# Before (broken stub)
@cli.command()
def infer():
    """Run gender inference on PubMed data (populates SQLite database)."""
    print("=" * 70)
    print("GENDER INFERENCE WITH SQLITE DATABASE")
    print("=" * 70)
    print("\nTo run gender inference, execute:")
    print("  python run_gender_inference_db.py")
    print("\nThis will:")
    print("  1. Load paper data from CSV files")
    ...
```

This is problematic because:
1. It deceives the user into thinking inference ran when it did not.
2. The `run` command (which calls `infer.callback()`) silently skipped inference entirely.

### Fix

Replaced the stub body with a `subprocess.run` call that actually executes `scripts/run_gender_inference_db.py` using the same Python interpreter that invoked `cli.py`. A non-zero exit code is surfaced as a `ClickException`:

```python
# After (functional)
@cli.command()
def infer():
    """Run gender inference on PubMed data (populates SQLite database)."""
    import subprocess
    print("=" * 70)
    print("GENDER INFERENCE WITH SQLITE DATABASE")
    print("=" * 70)
    script_path = Path(__file__).parent / "scripts" / "run_gender_inference_db.py"
    result = subprocess.run([sys.executable, str(script_path)])
    if result.returncode != 0:
        raise click.ClickException(
            f"Gender inference script exited with code {result.returncode}"
        )
```

Using `Path(__file__).parent` makes the path resolution relative to `cli.py`'s location, so it works regardless of the current working directory. Using `sys.executable` ensures the same virtual environment Python is used.

---

## Fix 4 — cli.py: `run` pipeline exited after Step 2

**File:** `cli.py`
**Lines:** 377–396
**Severity:** 🔴 Critical

### Problem

The `cli.py run` command — advertised as a "Full pipeline: fetch → infer → analyze → figures" — contained a hard `sys.exit(0)` immediately after Step 2 (infer). Steps 3 (analyze) and 4 (figures) were dead code that could never execute:

```python
# Before (broken)
# Step 2: Infer
print("\n[STEP 2/4] Gender inference...")
print("Next, run: python run_gender_inference_db.py")
print("Then return to run steps 3 and 4")
sys.exit(0)                                    # ← exits here unconditionally

# Step 3: Analyze (after inference completes)  ← unreachable
...
# Step 4: Figures                              ← unreachable
...
```

Running `python cli.py run` would fetch PubMed data and then exit silently with code 0, giving no indication that the pipeline was incomplete.

### Fix

Removed `sys.exit(0)` and the surrounding instructional print statements. Step 2 now calls `infer.callback()` (which, after Fix 3, actually runs the inference script), and the pipeline continues to Steps 3 and 4:

```python
# After (fixed)
# Step 2: Infer
print("\n[STEP 2/4] Gender inference...")
try:
    infer.callback()
except Exception as e:
    click.echo(f"Error during inference: {e}", err=True)
    sys.exit(1)

# Step 3: Analyze
print("\n[STEP 3/4] Statistical analysis...")
try:
    analyze.callback()
...
```

---

## Fix 5 — download_zenodo_data.py: Wrong Zenodo API download URL

**File:** `scripts/download_zenodo_data.py`
**Line:** 128
**Severity:** 🔴 Critical

### Problem

The script constructed file download URLs using the Zenodo Files API listing endpoint:

```python
ZENODO_API = f"https://zenodo.org/api/records/{ZENODO_RECORD}/files"

file_url = f"{ZENODO_API}/{filename}"
# → https://zenodo.org/api/records/18894714/files/gender_data.db.gz
```

That URL returns a **JSON metadata object** describing the file (size, checksum, links), not the file's binary content. `curl` would download a small JSON blob instead of the actual data file, causing `gzip.open()` to throw `BadGzipFile` and `pd.read_csv()` to throw a parse error.

The correct Zenodo REST API v2 URL for downloading a file's content appends `/content`:

```
https://zenodo.org/api/records/{id}/files/{filename}/content
```

### Fix

Added `/content` to the file URL construction:

```python
# Before (broken — returns JSON metadata)
file_url = f"{ZENODO_API}/{filename}"

# After (fixed — returns binary file content)
file_url = f"{ZENODO_API}/{filename}/content"
```

---

## Fix 6 — requirements.txt: Unpinned dependency versions

**File:** `requirements.txt`
**Severity:** 🟡 Minor

### Problem

All 17 packages used `>=` minimum-version specifiers:

```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
...
```

`>=` allows pip to install any version at or above the minimum, including future major versions with breaking changes. This means two people running `pip install -r requirements.txt` months apart may get different dependency trees, causing silent behavioural differences or outright failures. For an archived research dataset this is particularly problematic, as future reproduction attempts may fail.

### Fix

Switched all packages to the compatible-release operator `~=`, which pins to the specified minor version but allows patch updates (`~=2.2` is equivalent to `>=2.2, ==2.*`):

```
pandas~=2.2
numpy~=1.26
matplotlib~=3.9
...
```

This balances reproducibility (no unexpected minor/major version jumps) with practicality (security and bug-fix patches still install). For strict byte-for-byte reproduction, generate a lock file after installation:

```bash
pip freeze > requirements-lock.txt
pip install -r requirements-lock.txt   # exact replay
```

---

## Fix 7 — .env.example: Missing GROQ_API_KEY; stale unused keys

**File:** `.env.example`
**Severity:** 🟡 Minor

### Problem

The `.env.example` template was missing `GROQ_API_KEY`, which is required by `scripts/classify_names_retry.py` for Tier 2 LLM-based gender classification. Any user who copied `.env.example` to `.env` without knowing to add this key would either get an API authentication error or silently skip Tier 2 classification.

Additionally, the template contained two keys that are not referenced anywhere in the codebase:
- `ARXIV_DELAY_SECONDS` — the arXiv integration is listed in `requirements.txt` but the delay setting is not read by any script.
- `GENDERIZE_API_KEY` — genderize.io is not used; the project uses `gender-guesser` (offline) and Groq (LLM) instead.

These stale keys add confusion about what services the project actually uses.

### Fix

Rewrote `.env.example` to contain exactly the three keys the codebase actually uses, with accurate descriptions and links:

```bash
# NCBI E-utilities Configuration
# Required for PubMed data fetching (cli.py fetch)
NCBI_EMAIL=your.email@example.com
NCBI_API_KEY=your_ncbi_api_key_here

# Groq API Configuration
# Required for Tier 2 LLM-based gender classification (scripts/classify_names_retry.py)
GROQ_API_KEY=your_groq_api_key_here
```

---

## Fix 8 — cli.py: UnicodeEncodeError on Windows when running --help

**File:** `cli.py`
**Line:** 363
**Severity:** 🔴 Critical (Windows only)
**Found:** During live testing

### Problem

Running `python cli.py --help` on Windows immediately raised a fatal error:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'
in position 493: character maps to <undefined>
```

The `run` command docstring contained `→` (U+2192 RIGHT ARROW), which is not representable in Windows code page 1252 (the default terminal encoding). Click writes command docstrings to stdout when rendering `--help`, triggering the codec error before any output was produced. The entire CLI was unusable on any standard Windows terminal without first setting `PYTHONUTF8=1` or `PYTHONIOENCODING=utf-8`.

This bug was invisible in static review because it only manifests at runtime on Windows terminals.

### Fix

Replaced the non-ASCII arrow with its ASCII equivalent in the docstring:

```python
# Before (crashes on Windows cp1252 terminals)
"""Run the complete pipeline: fetch → infer → analyze → figures."""

# After (works on all platforms)
"""Run the complete pipeline: fetch -> infer -> analyze -> figures."""
```

---

## Fix 9 — cli.py: Stale script path in analyze error message

**File:** `cli.py`
**Lines:** 185–188
**Severity:** 🟡 Minor
**Found:** During live testing

### Problem

When `cli.py analyze` was run without a database, it printed the following error:

```
Error: Database not found at data/gender_data.db
Please run: python run_gender_inference_db.py
```

The suggested command (`python run_gender_inference_db.py`) referred to a bare filename that does not exist at the repo root. The script was moved to `scripts/` in v0.3.0 but this error message was not updated. Following the suggestion would produce a second error: `python: can't open file 'run_gender_inference_db.py': [Errno 2] No such file or directory`.

Additionally, the correct entry point for inference is now `python cli.py infer`, not a direct script invocation.

### Fix

Updated the error message to reference the CLI command:

```python
# Before
raise click.ClickException(
    "Database not found at data/gender_data.db\n"
    "Please run: python run_gender_inference_db.py"
)

# After
raise click.ClickException(
    "Database not found at data/gender_data.db\n"
    "Please run: python cli.py infer"
)
```

---

## Fix 10 — requirements.txt: Two-component ~= does not pin minor versions

**File:** `requirements.txt`
**Severity:** 🟡 Minor
**Found:** During live testing (follow-up to Fix 7)

### Problem

Fix 7 switched from `>=` to two-component `~=X.Y`, which appeared to pin versions but did not. Per PEP 440, the two-component form `~=X.Y` means `>=X.Y, ==X.*` — it pins the **major** version but allows *any* minor version ≥ Y. Live installation revealed the full extent of the drift:

| Spec | Resolved | Minor versions jumped |
|---|---|---|
| `groq~=0.9` | `groq 0.37.1` | +28 |
| `scipy~=1.13` | `scipy 1.17.1` | +4 |
| `pandas~=2.2` | `pandas 2.3.3` | +1 |
| `matplotlib~=3.9` | `matplotlib 3.10.8` | +1 |

The `groq` jump from 0.9 to 0.37 is particularly risky: the Groq client library has undergone significant API changes across those releases.

The correct operator for pinning to a **minor** version is the three-component form `~=X.Y.0`, which expands to `>=X.Y.0, ==X.Y.*` and only allows patch updates within the specified minor series.

### Fix

Updated all 17 package specs to three-component form:

```
# Before (two-component — pins major only)
groq~=0.9        # could install 0.37.x
matplotlib~=3.9  # could install 3.10.x, 3.11.x, ...
pandas~=2.2      # could install 2.3.x, 2.4.x, ...

# After (three-component — pins major.minor)
groq~=0.9.0        # only 0.9.x
matplotlib~=3.9.0  # only 3.9.x
pandas~=2.2.0      # only 2.2.x
```

**Verified resolved versions after fix:**

```
click          8.1.8    numpy  1.26.4   tqdm    4.66.6
python-dotenv  1.0.1    scipy  1.13.1   matplotlib  3.9.4
biopython      1.83.0   groq   0.9.0    seaborn     0.13.2
arxiv          2.1.0    pandas 2.2.3    plotly      5.22.0
requests       2.31.0   jupyter 1.0.0   ipython     8.25.0
tenacity       8.2.3    gender-guesser  0.4.0
```

---

## Verification Checklist

After applying all 11 fixes, the following sequence should work end-to-end without errors:

```bash
# 1. Setup
cp .env.example .env
# Edit .env: set NCBI_EMAIL and (optionally) NCBI_API_KEY, GROQ_API_KEY
pip install -r requirements.txt         # pinned to minor versions via ~=X.Y.0 ✓

# 2. Check CLI renders correctly on all platforms (Fix 8)
python cli.py --help                    # no UnicodeEncodeError on Windows ✓
python cli.py run --help                # shows "fetch -> infer -> analyze -> figures" ✓

# 3. Full pipeline via Make
make fetch               # calls cli.py fetch — reads NCBI_EMAIL from .env ✓
make infer               # calls scripts/run_gender_inference_db.py ✓
make classify            # calls scripts/classify_names_retry.py ✓
make preprocess-journals # calls scripts/preprocess_journal_quartiles.py ✓
make analyze             # calls cli.py analyze ✓
make figures             # calls cli.py figures ✓

# OR: Full pipeline in one shot
make run                 # fetch -> infer -> analyze -> figures, no early exit ✓

# 4. Fast reproduction via Zenodo
python scripts/download_zenodo_data.py  # downloads actual binary files ✓
python cli.py analyze                   # clear error if DB missing (Fix 9) ✓
python cli.py figures

# 5. Docker
make docker-run NCBI_EMAIL=your@email.com  # correct variable name ✓
```
