# Multi-stage build for Nethical Recon
# Stage 1: Builder - Install dependencies and build wheels
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy dependency files
COPY pyproject.toml ./
COPY requirements.txt ./
COPY docs/README.md ./
COPY src/ ./src/

# Build wheels
RUN pip install --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt && \
    pip wheel --no-cache-dir --wheel-dir /build/wheels .

# Stage 2: Runtime - Minimal image with only runtime dependencies
FROM python:3.11-slim as runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/app/.local/bin:$PATH"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    nmap \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash nethical && \
    mkdir -p /app /app/evidence /app/reports && \
    chown -R nethical:nethical /app

WORKDIR /app

# Copy wheels from builder
COPY --from=builder /build/wheels /tmp/wheels

# Install Python packages from wheels
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --no-index --find-links=/tmp/wheels /tmp/wheels/*.whl && \
    rm -rf /tmp/wheels

# Copy application code
COPY --chown=nethical:nethical src/ ./src/
COPY --chown=nethical:nethical alembic.ini ./

# Switch to non-root user
USER nethical

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose API port
EXPOSE 8000

# Default command (can be overridden)
CMD ["nethical", "api", "serve", "--host", "0.0.0.0", "--port", "8000"]
