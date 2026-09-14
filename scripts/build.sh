#!/usr/bin/env bash
# Build from .venv; --prepare syncs dependencies, --prepare-offline uses uv cache.
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
if (( $# > 1 )); then
    echo "Usage: bash scripts/build.sh [--prepare|--prepare-offline]" >&2
    exit 1
fi
case "${1:-}" in
    "") ;;
    --prepare|--prepare-offline)
        args=(sync --locked --group build)
        if [[ "$1" == --prepare-offline ]]; then args+=(--offline); fi
        uv "${args[@]}"
        ;;
    *) echo "Usage: bash scripts/build.sh [--prepare|--prepare-offline]" >&2; exit 1 ;;
esac
if [[ -f .venv/Scripts/python.exe ]]; then
    PYTHON_EXE="$PROJECT_ROOT/.venv/Scripts/python.exe"
else
    PYTHON_EXE="$PROJECT_ROOT/.venv/bin/python"
fi
if [[ ! -f "$PYTHON_EXE" ]] || ! "$PYTHON_EXE" -c 'import cx_Freeze' >/dev/null 2>&1; then
    echo "Build environment missing. Run: bash scripts/build.sh --prepare" >&2
    exit 1
fi
"$PYTHON_EXE" build.py build_exe
echo "Build completed: $PROJECT_ROOT/build"
