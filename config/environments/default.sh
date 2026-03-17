#!/usr/bin/env bash
# Default environment configuration
# This must work for any reproducer without lab-specific settings

# Python virtual environment
export VENV_DIR="${CAP_PROJECT_PATH}/venv"

# Web app settings
export FLASK_PORT=8080
export FLASK_HOST="127.0.0.1"

# Test settings
export PYTEST_ARGS="-v"
