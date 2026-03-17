#!/usr/bin/env bash
# Start the Flask web application
#
# Usage: cap run src/04_run_web.sh
#   or:  bash src/04_run_web.sh

set -eo pipefail

PROJECT_DIR="${CAP_PROJECT_PATH:-$(cd "$(dirname "$0")/.." && pwd)}"
VENV_DIR="${VENV_DIR:-${PROJECT_DIR}/venv}"

FLASK_PORT="${FLASK_PORT:-8080}"
FLASK_HOST="${FLASK_HOST:-127.0.0.1}"

set +u
source "${VENV_DIR}/bin/activate"
set -u
cd "${PROJECT_DIR}"

echo "=== Starting web application ==="
echo "URL: http://${FLASK_HOST}:${FLASK_PORT}"
python -m flask --app src.variant_classifier.web.app:app run --host "${FLASK_HOST}" --port "${FLASK_PORT}"
