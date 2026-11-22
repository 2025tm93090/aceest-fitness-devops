# Multi-Stage Production Dockerfile for ACEest Fitness & Gym
# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies to wheels cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final Minimal Runtime Image
FROM python:3.11-slim AS runner

# Metadata labels
LABEL maintainer="ACEest DevOps Team <devops@aceestfitness.com>"
LABEL course="DevOps CI/CD CSIZG514/SEZG514"
LABEL version="3.0.0"
LABEL description="ACEest Fitness & Gym Management Web Application"

# Install curl for healthcheck probe
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user for security best practices
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

WORKDIR /app

# Copy python dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=ACEest_Fitness.py
ENV ACEEST_DB_PATH=/app/data/aceest_fitness.db
ENV APP_VERSION=v3.0.0

# Prepare directories and assign ownership
RUN mkdir -p /app/data && chown -R appuser:appgroup /app

# Copy application source code
COPY --chown=appuser:appgroup . /app

# Switch to unprivileged non-root user
USER appuser

# Expose internal HTTP port
EXPOSE 5000

# Docker native Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Production WSGI server command (Gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--threads", "2", "--access-logfile", "-", "--error-logfile", "-", "ACEest_Fitness:app"]
