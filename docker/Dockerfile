################################################################################
# GLEH (Gammons Landing Educational Hub) - Production Dockerfile
################################################################################
# Multi-stage build for optimal image size and security
# Base: Python 3.11-slim (minimal footprint)
################################################################################

# ============================================================================
# STAGE 1: BUILDER
# ============================================================================
FROM python:3.11-slim as builder

LABEL maintainer="GLEH Development Team"
LABEL description="Gammons Landing Educational Hub - Flask-based LMS"

# Set working directory
WORKDIR /tmp/build

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# STAGE 2: RUNTIME
# ============================================================================
FROM python:3.11-slim

LABEL maintainer="GLEH Development Team"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_APP=src/app.py \
    PATH=/usr/local/bin:$PATH \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install runtime dependencies only (smaller image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    netcat-openbsd \
    ffmpeg \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY src /app/src
COPY templates /app/templates
COPY static /app/static
COPY scripts /app/scripts

# Create directories for volume mounts
RUN mkdir -p /app/data/courses /app/logs && \
    chmod 755 /app/data /app/data/courses /app/logs

# Create non-root user for security
RUN useradd -m -u 1000 edu && \
    chown -R edu:edu /app

# Switch to non-root user
USER edu

# Expose port (internal communication with Nginx)
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application (migrations will be handled separately)
CMD ["python", "-m", "waitress", "--host=0.0.0.0", "--port=5000", "src.app:app"]
