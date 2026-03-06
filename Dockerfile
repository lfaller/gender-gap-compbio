# Multi-stage build for reproducible analysis environment
# Stage 1: Base image with dependencies
FROM python:3.9-slim AS base

WORKDIR /app

# Install system dependencies for scientific computing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime image with application
FROM python:3.9-slim

WORKDIR /app

# Copy Python packages from builder stage
COPY --from=base /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create directories for outputs and data
RUN mkdir -p outputs/figures data/processed data/raw

# Set Python to unbuffered output
ENV PYTHONUNBUFFERED=1

# Health check (verify CLI works)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=1 \
    CMD python -c "import sys; sys.path.insert(0, '.'); from cli import cli; print('OK')" || exit 1

# Default command runs the analysis pipeline
# Users can override with different CLI commands
ENTRYPOINT ["python", "cli.py"]
CMD ["analyze"]
