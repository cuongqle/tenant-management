FROM python:3.14-slim-bookworm AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock README.md ./
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./
COPY tests ./tests

FROM base AS test
RUN uv sync --frozen
CMD ["uv", "run", "pytest", "-q", "--tb=short"]

FROM base AS runtime
RUN uv sync --frozen --no-dev
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
