# Bot Dockerfile using uv
# Uses workspace uv.lock for offline builds

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/

# ---
# Stage 1: Build the application
# ---
FROM ${REGISTRY_PREFIX}astral/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy workspace files
COPY pyproject.toml uv.lock ./

# Copy member packages
COPY bot/pyproject.toml bot/
COPY backend/pyproject.toml backend/

# Sync from lock file (works offline with cached packages)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Copy source code
COPY bot/ bot/
COPY backend/ backend/

# Reinstall to include project packages
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# ---
# Stage 2: Final runtime image
# ---
FROM ${REGISTRY_PREFIX}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Setup non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy application from builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Add uv environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

USER nonroot

WORKDIR /app

# Run the bot
CMD ["python", "bot/bot.py"]
