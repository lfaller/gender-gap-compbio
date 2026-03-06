# Docker Setup for Gender Gap Analysis

This document explains how to run the gender gap analysis using Docker, which provides a reproducible, isolated environment that works consistently across different systems.

## Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed and running
- NCBI email (required for PubMed API access)
- Optional: NCBI API key (recommended for higher rate limits)
- Optional: Groq API key (for unknown name classification, ~$0.54 cost)

### Option 1: Using `docker-compose` (Recommended)

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your credentials:
   # - ENTREZ_EMAIL (required)
   # - NCBI_API_KEY (optional, recommended)
   # - GROQ_API_KEY (optional, for full reproducibility)
   ```

2. **Run analysis:**
   ```bash
   # Build image and run analysis pipeline
   docker-compose up --build

   # Or run specific commands
   docker-compose run --rm gender-gap-analysis fetch --start-year 2015 --end-year 2025
   docker-compose run --rm gender-gap-analysis infer
   docker-compose run --rm gender-gap-analysis analyze
   docker-compose run --rm gender-gap-analysis figures
   ```

3. **Clean up:**
   ```bash
   docker-compose down
   ```

### Option 2: Using `make` Commands

```bash
# Build Docker image
make docker-build

# Run analysis in container
make docker-run ENTREZ_EMAIL=your.email@example.com

# Interactive shell
make docker-shell ENTREZ_EMAIL=your.email@example.com

# Clean up image
make docker-clean
```

### Option 3: Direct Docker Commands

```bash
# Build
docker build -t gender-gap-compbio .

# Run analysis (require pre-built data)
docker run --rm \
  -e ENTREZ_EMAIL=your.email@example.com \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/data:/app/data \
  gender-gap-compbio:latest analyze

# Interactive shell
docker run --rm -it \
  -e ENTREZ_EMAIL=your.email@example.com \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/data:/app/data \
  gender-gap-compbio:latest /bin/bash

# Fetch data
docker run --rm \
  -e ENTREZ_EMAIL=your.email@example.com \
  -v $(pwd)/data:/app/data \
  gender-gap-compbio:latest fetch --start-year 2015 --end-year 2025

# Infer gender
docker run --rm \
  -v $(pwd)/data:/app/data \
  gender-gap-compbio:latest infer

# Run analysis
docker run --rm \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/data:/app/data \
  gender-gap-compbio:latest analyze

# Generate figures
docker run --rm \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/data:/app/data \
  gender-gap-compbio:latest figures
```

## Understanding the Docker Setup

### Dockerfile Architecture

The `Dockerfile` uses a **multi-stage build** approach:

1. **Stage 1 (Builder):** Compiles dependencies in a larger intermediate image
2. **Stage 2 (Runtime):** Copies only the compiled packages, creating a smaller final image

**Benefits:**
- ✅ Smaller final image size (~500 MB vs ~1.2 GB)
- ✅ Faster rebuilds (cached dependency layer)
- ✅ Cleaner environment (no build tools in final image)

### Environment Variables

| Variable | Required | Notes |
|----------|----------|-------|
| `ENTREZ_EMAIL` | ✅ Yes | Your email for NCBI politeness policy |
| `NCBI_API_KEY` | ❌ No | Get from https://www.ncbi.nlm.nih.gov/account/ (recomm ended) |
| `GROQ_API_KEY` | ❌ No | Get from https://console.groq.com/ (for unknown names, ~$0.54 cost) |
| `PYTHONUNBUFFERED` | Default | Set to `1` for real-time logging |

### Volume Mounts

The Docker setup mounts these directories to persist data between runs:

| Container Path | Host Path | Purpose |
|----------------|-----------|---------|
| `/app/data` | `./data` | Persistent data storage (CSVs, databases) |
| `/app/outputs` | `./outputs` | Generated figures and analysis results |
| `/app/local` | `./local` | Non-git files (ScimagoJR data, etc.) |

## Complete Workflow Example

### Scenario: Reproduce the 2025 analysis from scratch

```bash
# 1. Clone repository
git clone https://github.com/yourusername/gender-gap-compbio
cd gender-gap-compbio

# 2. Set up environment
cp .env.example .env
# Edit .env with ENTREZ_EMAIL and optional keys

# 3. Build Docker image
docker build -t gender-gap-compbio .

# 4. Fetch PubMed data (2-4 hours)
docker run --rm \
  -e ENTREZ_EMAIL=your.email@example.com \
  -v $(pwd)/data:/app/data \
  gender-gap-compbio fetch --start-year 2015 --end-year 2025

# 5. Infer gender for authors (30 min)
docker run --rm \
  -v $(pwd)/data:/app/data \
  gender-gap-compbio infer

# 6. Download ScimagoJR data (if not cached)
# (See README.md for instructions)

# 7. Preprocess journal quartiles (15 min)
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/local:/app/local \
  gender-gap-compbio run_gender_inference_db.py

# 8. Run analysis (10 min)
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  gender-gap-compbio analyze

# 9. Generate figures (5 min)
docker run --rm \
  -v $(pwd)/outputs:/app/outputs \
  gender-gap-compbio figures
```

**Total time:** 3.5-5 hours (depending on NCBI API responsiveness)

### Scenario: Use pre-built database (faster)

If you have `data/gender_data.db` from a previous run:

```bash
# Just run analysis (10 min)
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  gender-gap-compbio analyze

# Generate figures (5 min)
docker run --rm \
  -v $(pwd)/outputs:/app/outputs \
  gender-gap-compbio figures
```

**Total time:** ~15 minutes

## Troubleshooting

### "Image build fails with permission error"
- Ensure Docker daemon is running
- Try: `docker ps` to verify connection

### "API rate limit exceeded"
- Add NCBI_API_KEY environment variable for higher rate limits
- Or use `--no-cache` to rebuild from scratch

### "Groq API costs money"
- This is optional for full reproducibility
- Remove `-e GROQ_API_KEY` to skip unknown name classification
- See README.md for tier-1 vs tier-2 classification

### "Data directory is empty after running"
- Ensure volume mount is correct: `-v $(pwd)/data:/app/data`
- Check permissions: `ls -la data/`
- Run with `-it` flags for interactive debugging

### "Port/Volume already in use"
- For docker-compose: `docker-compose down --volumes`
- Change container name in docker-compose.yml if needed

## Performance Notes

| Operation | Time | Parallelizable | Notes |
|-----------|------|----------------|-------|
| Fetch PubMed data | 2-4 hours | ✅ Depends on API | Each year ~3-5 min |
| Gender inference (Phase 1) | 30 min | ✅ Multi-core | SQLite operations scale |
| Groq classification (Phase 2) | 1-2 hours | ❌ Sequential | API rate limits |
| Analysis (bootstrap) | 10 min | ✅ Multi-core | 1000 resamples |
| Figure generation | 5 min | ✅ Per-figure | Matplotlib operations |

## Extending to New Years (2026+)

To update analysis with new PubMed data:

```bash
# 1. Fetch new data
docker run --rm \
  -e ENTREZ_EMAIL=your.email@example.com \
  -v $(pwd)/data:/app/data \
  gender-gap-compbio fetch --start-year 2026 --end-year 2028 --append

# 2. Infer gender for new authors
docker run --rm \
  -v $(pwd)/data:/app/data \
  gender-gap-compbio infer

# 3. Update analysis
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  gender-gap-compbio analyze

# 4. Generate new figures
docker run --rm \
  -v $(pwd)/outputs:/app/outputs \
  gender-gap-compbio figures
```

## Advanced: Custom Docker Compose Configuration

Create an override file `docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  gender-gap-analysis:
    # Override environment variables
    environment:
      ENTREZ_EMAIL: your.email@example.com
      NCBI_API_KEY: your_api_key_here

    # Override volume mounts
    volumes:
      # Add custom directories
      - ./notebooks:/app/notebooks
      - ./local/custom_data:/app/custom_data
```

Then run: `docker-compose up --build`

## References

- [Docker Documentation](https://docs.docker.com/)
- [Python Docker Best Practices](https://docs.docker.com/language/python/)
- [Multi-stage Docker Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)

---

**For questions or issues**, see [CONTRIBUTING.md](CONTRIBUTING.md) or open an issue on GitHub.
