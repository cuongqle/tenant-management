#!/bin/sh
set -e

if [ "${SKIP_MIGRATIONS:-0}" != "1" ]; then
  uv run --no-dev alembic upgrade head
fi

exec "$@"
