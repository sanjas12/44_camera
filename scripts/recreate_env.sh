#!/usr/bin/env bash
# Recreate .venv with runtime and build dependencies using the project's uv.lock.
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
if (( $# > 1 )); then
    echo "Usage: bash scripts/recreate_env.sh [--offline]" >&2
    exit 1
fi
args=(sync --locked --group build)
case "${1:-}" in
    "") ;;
    --offline) args+=(--offline) ;;
    *) echo "Usage: bash scripts/recreate_env.sh [--offline]" >&2; exit 1 ;;
esac
command -v uv >/dev/null 2>&1 || { echo "uv is required." >&2; exit 1; }
# Let uv recreate only its environment; do not delete project directories ourselves.
uv venv --clear .venv
uv "${args[@]}"
echo "Runtime and build environment ready."
