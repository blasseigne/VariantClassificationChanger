#!/usr/bin/env bash
# Run the CLI classifier with given evidence codes
#
# Usage: cap run src/03_run_cli.sh -- PM2 PP3
#   or:  bash src/03_run_cli.sh PM2 PP3

set -eo pipefail

PROJECT_DIR="${CAP_PROJECT_PATH:-$(cd "$(dirname "$0")/.." && pwd)}"
VENV_DIR="${VENV_DIR:-${PROJECT_DIR}/venv}"

set +u
source "${VENV_DIR}/bin/activate"
set -u
cd "${PROJECT_DIR}"

python -m src.variant_classifier "$@"
