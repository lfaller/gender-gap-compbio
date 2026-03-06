.PHONY: help setup install fetch infer classify preprocess-journals analyze figures run clean docker-build docker-run docker-shell docker-push

# Variables
DOCKER_IMAGE = gender-gap-compbio
DOCKER_REGISTRY ?= localhost
PYTHON := python3

help:
	@echo "========================================"
	@echo "Gender Gap in Computational Biology"
	@echo "========================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup              - One-time setup (venv, dependencies, .env)"
	@echo "  make install            - Install Python dependencies"
	@echo ""
	@echo "Pipeline Commands:"
	@echo "  make fetch              - Fetch PubMed data (2015-2025)"
	@echo "  make infer              - Infer gender for authors (offline)"
	@echo "  make classify           - Classify unknowns via Groq API (optional, paid)"
	@echo "  make preprocess-journals- Preprocess journal quartiles"
	@echo "  make analyze            - Run statistical analysis"
	@echo "  make figures            - Generate publication-ready figures"
	@echo ""
	@echo "Combined Targets:"
	@echo "  make run                - Full pipeline (fetch → infer → analyze → figures)"
	@echo "  make run-quick          - Quick analysis (requires pre-built data)"
	@echo ""
	@echo "Docker Targets:"
	@echo "  make docker-build       - Build Docker image"
	@echo "  make docker-run         - Run analysis in Docker container"
	@echo "  make docker-shell       - Start interactive shell in Docker"
	@echo "  make docker-clean       - Remove Docker image"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean              - Remove generated data (keep git files)"
	@echo "  make clean-cache        - Remove gender cache only"
	@echo "  make clean-db           - Remove database only"
	@echo ""

# ============================================================================
# SETUP & INSTALLATION
# ============================================================================

setup:
	@echo "Setting up Gender Gap Analysis environment..."
	@bash -c 'if [ ! -d venv ]; then $(PYTHON) -m venv venv; fi'
	@echo "✓ Virtual environment ready"
	@$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	@echo ""
	@echo "Creating .env file..."
	@if [ ! -f .env ]; then \
		echo "# NCBI Configuration" > .env; \
		echo "ENTREZ_EMAIL=your.email@example.com" >> .env; \
		echo "" >> .env; \
		echo "# Groq API (optional, for unknown name classification)" >> .env; \
		echo "# Get key at: https://console.groq.com/" >> .env; \
		echo "# GROQ_API_KEY=your_groq_key_here" >> .env; \
		echo "✓ Created .env file (edit with your credentials)"; \
	else \
		echo "✓ .env file already exists"; \
	fi
	@echo ""
	@echo "========================================"
	@echo "✓ Setup complete!"
	@echo "========================================"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit .env with your NCBI email"
	@echo "  2. make fetch"
	@echo "  3. make infer"
	@echo "  4. make analyze"
	@echo "  5. make figures"
	@echo ""

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

# ============================================================================
# PIPELINE COMMANDS
# ============================================================================

fetch:
	@echo "Fetching PubMed data (2015-2025)..."
	$(PYTHON) cli.py fetch --start-year 2015 --end-year 2025

infer:
	@echo "Inferring gender for authors..."
	$(PYTHON) run_gender_inference_db.py

classify:
	@echo "Classifying unknown names via Groq API..."
	$(PYTHON) classify_names.py

preprocess-journals:
	@echo "Preprocessing journal quartiles..."
	$(PYTHON) preprocess_journal_quartiles.py

analyze:
	@echo "Running statistical analysis..."
	$(PYTHON) cli.py analyze

figures:
	@echo "Generating figures..."
	$(PYTHON) cli.py figures

# ============================================================================
# COMBINED TARGETS
# ============================================================================

run: fetch infer preprocess-journals analyze figures
	@echo "✓ Full pipeline complete"

run-quick: preprocess-journals analyze figures
	@echo "✓ Quick analysis complete (using existing data)"

# ============================================================================
# DOCKER TARGETS
# ============================================================================

docker-build:
	@echo "Building Docker image: $(DOCKER_IMAGE)"
	docker build -t $(DOCKER_IMAGE):latest .
	docker tag $(DOCKER_IMAGE):latest $(DOCKER_IMAGE):$(shell date +%Y%m%d)
	@echo "✓ Built $(DOCKER_IMAGE):latest and $(DOCKER_IMAGE):$(shell date +%Y%m%d)"

docker-run: docker-build
	@if [ -z "$(ENTREZ_EMAIL)" ]; then \
		echo "ERROR: ENTREZ_EMAIL environment variable not set"; \
		echo "Usage: ENTREZ_EMAIL=your@email.com make docker-run"; \
		exit 1; \
	fi
	@echo "Running analysis in Docker container..."
	docker run --rm \
		-e ENTREZ_EMAIL=$(ENTREZ_EMAIL) \
		$(if $(NCBI_API_KEY),-e NCBI_API_KEY=$(NCBI_API_KEY),) \
		$(if $(GROQ_API_KEY),-e GROQ_API_KEY=$(GROQ_API_KEY),) \
		-v $(PWD)/outputs:/app/outputs \
		-v $(PWD)/data:/app/data \
		$(DOCKER_IMAGE):latest analyze

docker-shell: docker-build
	@echo "Starting interactive shell in Docker container..."
	docker run --rm -it \
		-e ENTREZ_EMAIL=$(ENTREZ_EMAIL) \
		$(if $(NCBI_API_KEY),-e NCBI_API_KEY=$(NCBI_API_KEY),) \
		$(if $(GROQ_API_KEY),-e GROQ_API_KEY=$(GROQ_API_KEY),) \
		-v $(PWD)/outputs:/app/outputs \
		-v $(PWD)/data:/app/data \
		$(DOCKER_IMAGE):latest /bin/bash

docker-clean:
	@echo "Removing Docker image..."
	docker rmi $(DOCKER_IMAGE):latest || true
	docker rmi $(DOCKER_IMAGE):$(shell date +%Y%m%d) || true
	@echo "✓ Docker image removed"

# ============================================================================
# MAINTENANCE
# ============================================================================

clean:
	@echo "Cleaning generated data..."
	rm -f data/gender_data.db data/gender_cache.json
	rm -f data/processed/*.csv
	rm -rf outputs/figures/*.png outputs/figures/*.svg outputs/figures/*.pdf
	@echo "✓ Cleaned (git files preserved)"

clean-cache:
	@echo "Removing gender cache..."
	rm -f data/gender_cache.json
	@echo "✓ Cache removed"

clean-db:
	@echo "Removing database..."
	rm -f data/gender_data.db
	@echo "✓ Database removed"

.NOTPARALLEL:
