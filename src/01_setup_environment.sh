#!/usr/bin/env bash
# Setup the Python virtual environment and install dependencies
#
# Usage: cap run src/01_setup_environment.sh
#   or:  bash src/01_setup_environment.sh

set -eo pipefail

PROJECT_DIR="${CAP_PROJECT_PATH:-$(cd "$(dirname "$0")/.." && pwd)}"
VENV_DIR="${VENV_DIR:-${PROJECT_DIR}/venv}"

echo "=== Setting up environment ==="
echo "Project directory: ${PROJECT_DIR}"
echo "Virtual environment: ${VENV_DIR}"

# Create virtual environment if it doesn't exist
if [ ! -d "${VENV_DIR}" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "${VENV_DIR}"
fi

# Activate (disable nounset temporarily — activate scripts may reference unset vars)
set +u
source "${VENV_DIR}/bin/activate"
set -u
echo "Installing dependencies..."
pip install -r "${PROJECT_DIR}/requirements.txt"

echo "=== Environment setup complete ==="
