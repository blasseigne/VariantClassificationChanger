# Development Guide

This project follows the [CAPTURE](https://github.com/lasseignelab/capture) framework for reproducible computational research.

## Project Structure

```
VariantClassificationChanger/
├── .github/                    # GitHub workflows and rulesets
│   ├── settings/
│   │   └── default_ruleset.json
│   └── workflows/
│       ├── mega-linter.yml
│       └── tests.yml
├── .mega-linter.yml            # Linter configuration
├── bin/
│   ├── container/
│   │   └── Dockerfile          # Container for reproducible runs
│   └── env/                    # Conda/pip environment files
├── config/
│   ├── pipeline.sh             # Project name and random seed
│   └── environments/
│       └── default.sh          # Default environment settings
├── data/                       # Input data (git-ignored)
├── doc/                        # Documentation and supplementary materials
├── logs/                       # Execution logs (git-ignored)
├── results/                    # Generated outputs
├── src/
│   ├── variant_classifier/     # Python package
│   │   ├── evidence_codes.py   # 28 ACMG/AMP codes with point values
│   │   ├── classifier.py       # Bayesian classification engine
│   │   ├── advisor.py          # Bidirectional tier-change advisor
│   │   ├── cli.py              # Command-line interface
│   │   └── web/                # Flask web app + REST API
│   ├── 01_setup_environment.sh
│   ├── 02_run_tests.sh
│   ├── 03_run_cli.sh
│   └── 04_run_web.sh
├── tests/                      # Python test suite
├── verifications/              # Reproducibility verification scripts
├── LICENSE                     # GPL-3.0
└── README.md
```

## Setup

```bash
# With CAPTURE installed:
cap run src/01_setup_environment.sh

# Without CAPTURE:
bash src/01_setup_environment.sh
```

## Running Tests

```bash
cap run src/02_run_tests.sh
# or
bash src/02_run_tests.sh
```

## Running Verifications

```bash
cap run verifications/verify_classification.sh
# or
bash verifications/verify_classification.sh
```

Verification outputs are saved to `verifications/verify_classification.out` and should be committed to git so reviewers can `git diff` to confirm reproducibility.

## GitHub Rulesets

This repository uses GitHub rulesets (`.github/settings/default_ruleset.json`) to enforce:
- No branch deletion on default branch
- No force-push on default branch
- Pull requests require 2 approving reviews
- Stale reviews are dismissed on new pushes
- Code owner review required
- All review threads must be resolved

## Docker

```bash
docker build -t variant-classifier -f bin/container/Dockerfile .
docker run -p 8080:8080 variant-classifier
```
