#!/usr/bin/env bash
# Run the full test suite
#
# Usage: cap run src/02_run_tests.sh
#   or:  bash src/02_run_tests.sh

set -eo pipefail

PROJECT_DIR="${CAP_PROJECT_PATH:-$(cd "$(dirname "$0")/.." && pwd)}"
VENV_DIR="${VENV_DIR:-${PROJECT_DIR}/venv}"

PYTEST_ARGS="${PYTEST_ARGS:--v}"

set +u
source "${VENV_DIR}/bin/activate"
set -u
cd "${PROJECT_DIR}"

echo "=== Running test suite ==="
python -m pytest tests/ ${PYTEST_ARGS}
echo "=== Tests complete ==="
