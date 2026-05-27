# ContratIA Abierta — production image (lean MVP route)
#
# Builds an image that exposes the FastAPI lean API on $PORT (default 8000)
# with PUBLIC_READ_ONLY=true. The image bakes the sample fixtures + scoring
# marts so the container is self-contained: no Socrata network call needed
# at boot. Suitable for Render / Fly / Railway free tiers.
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl \
 && rm -rf /var/lib/apt/lists/*

# install uv (fast resolver)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
 && ln -s /root/.local/bin/uv /usr/local/bin/uv

WORKDIR /app

# Install deps first (better layer cache)
COPY pyproject.toml uv.lock ./
RUN uv pip install --system -r <(uv pip compile pyproject.toml --quiet) \
 || uv pip install --system -e .

# Copy project
COPY . .

# Bake the lean product pipeline so the image is self-contained.
# PRODUCT_SOURCE_MODE=fixtures uses versioned sample data (no Socrata at build).
ENV PRODUCT_SOURCE_MODE=fixtures
RUN python -m src.extract.secop_api \
 && python -m src.transform.build_process_master \
 && python -m src.scoring.score_processes \
 || echo "Build-time pipeline pre-warm skipped (will run at first request)"

EXPOSE 8000

ENV PUBLIC_READ_ONLY=true \
    DASH_ALLOW_DB_FALLBACK=0

# Default: serve the lean read-only API. Override CMD to serve the Dash UI.
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
