#!/bin/sh
set -e

if [ "${1#-}" != "$1" ] || [ -z "$1" ]; then
  set -- uv run uvicorn url_alias.main:app --host 0.0.0.0 --port 8000 "$@"
fi

exec "$@" 