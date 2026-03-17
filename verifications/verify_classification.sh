#!/usr/bin/env bash
# Verification script: run known classification test cases and compare outputs
#
# This script runs the classifier against a set of known-correct inputs
# and verifies the outputs match expected results. Results are saved to
# verifications/verify_classification.out for git diff comparison.
#
# Usage: cap run verifications/verify_classification.sh
#   or:  bash verifications/verify_classification.sh

set -eo pipefail

PROJECT_DIR="${CAP_PROJECT_PATH:-$(cd "$(dirname "$0")/.." && pwd)}"
VENV_DIR="${VENV_DIR:-${PROJECT_DIR}/venv}"
OUT_FILE="${PROJECT_DIR}/verifications/verify_classification.out"

# Temporarily disable nounset — venv activate scripts may reference unset vars
set +u
source "${VENV_DIR}/bin/activate"
set -u
cd "${PROJECT_DIR}"

echo "=== Running classification verification ===" | tee "${OUT_FILE}"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "${OUT_FILE}"
echo "" | tee -a "${OUT_FILE}"

PASS=0
FAIL=0

# Helper function to run a test case
run_test() {
    local codes="$1"
    local expected="$2"

    # Run classifier and extract classification line
    # shellcheck disable=SC2086
    output=$(python -m src.variant_classifier --classify-only ${codes} 2>&1)
    actual=$(echo "${output}" | grep "Classification:" | sed 's/Classification: *//')

    if [ "${actual}" = "${expected}" ]; then
        echo "PASS: [${codes}] -> ${actual}" | tee -a "${OUT_FILE}"
        PASS=$((PASS + 1))
    else
        echo "FAIL: [${codes}] -> ${actual} (expected: ${expected})" | tee -a "${OUT_FILE}"
        FAIL=$((FAIL + 1))
    fi
}

# --- Pathogenic test cases ---
run_test "PVS1 PS1"    "Pathogenic"
run_test "PVS1 PM1"    "Pathogenic"
run_test "PVS1 PP1 PP2" "Pathogenic"

# --- Likely Pathogenic test cases ---
run_test "PVS1"        "Likely Pathogenic"
run_test "PS1 PM1"     "Likely Pathogenic"
run_test "PM1 PM2 PM3" "Likely Pathogenic"

# --- VUS test cases ---
run_test "PM2 PP3"              "VUS (Uncertain Significance)"
run_test "PS1"                  "VUS (Uncertain Significance)"
run_test "PP1 PP2 PP3 PP4 PP5" "VUS (Uncertain Significance)"

# --- Likely Benign test cases ---
run_test "BP1"      "Likely Benign"
run_test "BS1 BP1"  "Likely Benign"

# --- Benign test cases ---
run_test "BA1"                          "Benign"
run_test "BS1 BS2"                      "Benign"
run_test "BP1 BP2 BP3 BP4 BP5 BP6 BP7" "Benign"

echo "" | tee -a "${OUT_FILE}"
echo "Results: ${PASS} passed, ${FAIL} failed out of $((PASS + FAIL)) tests" | tee -a "${OUT_FILE}"

if [ "${FAIL}" -gt 0 ]; then
    echo "VERIFICATION FAILED" | tee -a "${OUT_FILE}"
    exit 1
else
    echo "VERIFICATION PASSED" | tee -a "${OUT_FILE}"
fi
