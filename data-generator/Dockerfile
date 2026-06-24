# syntax=docker/dockerfile:1

# --------------------------------------------------------------------------- #
# Builder: produce a wheel with Poetry (build tools stay out of the runtime).
# --------------------------------------------------------------------------- #
FROM python:3.12-slim AS builder

ENV POETRY_VERSION=1.8.3 \
    POETRY_NO_INTERACTION=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app
# Copy only what the build needs first for better layer caching.
COPY pyproject.toml README.md ./
COPY src ./src
RUN poetry build --format wheel

# --------------------------------------------------------------------------- #
# Runtime: slim, non-root, no build tools or Poetry.
# --------------------------------------------------------------------------- #
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:$PATH"

# Isolated venv + an unprivileged user to run as.
RUN python -m venv /opt/venv \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app --create-home appuser

WORKDIR /app

COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl

USER appuser

ENTRYPOINT ["hospital-datagen"]
CMD ["seed"]
