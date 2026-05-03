# syntax=docker/dockerfile:1.7
# ───────────────────────────────────────────────────────────
# Streamlit dashboard — production image
# Target: Cloud Run (Google Cloud / Firebase-compatible)
# ───────────────────────────────────────────────────────────

FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Minimal system deps — no shell utilities beyond what pip needs
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Non-root user (Cloud Run best practice)
RUN groupadd --system app && useradd --system --gid app --home /app app

WORKDIR /app

# Install dependencies first (layer cache friendly)
COPY --chown=app:app requirements.txt ./
RUN pip install --no-cache-dir --require-hashes=false -r requirements.txt

# Copy application code (respects .dockerignore)
COPY --chown=app:app . .

USER app

# Cloud Run injects $PORT (default 8080); Streamlit must bind to it.
ENV PORT=8080
EXPOSE 8080

# Health endpoint check
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl --fail --silent http://localhost:${PORT}/_stcore/health || exit 1

CMD ["sh", "-c", "streamlit run dashboard_v3.py --server.port=${PORT} --server.address=0.0.0.0"]
