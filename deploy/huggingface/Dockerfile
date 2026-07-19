# Hugging Face Docker Space for the Litmus backend.
# Reuses the exact backend code + lockfile from the public repo (no duplication):
# it clones the repo at build time and runs the same app. HF Spaces run as user
# 1000, so we create that user before installing.
#
# Copy this file and README.md into a new HF Space (SDK: Docker), then set the
# DATABASE_URL (Neon) and CORS_ORIGINS (Vercel URL) secrets in Space settings.

FROM python:3.12-slim

# uv for fast, reproducible installs; git to fetch the app.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 user

USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

WORKDIR /home/user/app

# Which repo/ref to deploy (override as build args if you fork).
ARG LITMUS_REPO=https://github.com/oussamaelbourakadi/litmus
ARG LITMUS_REF=main

RUN git clone --depth 1 --branch ${LITMUS_REF} ${LITMUS_REPO} /tmp/litmus \
    && cp -r /tmp/litmus/backend/. /home/user/app/ \
    && rm -rf /tmp/litmus

RUN uv sync --frozen --no-dev
ENV PATH="/home/user/app/.venv/bin:$PATH"

EXPOSE 8000

# Apply migrations (idempotent), then serve on the port HF exposes (app_port).
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
