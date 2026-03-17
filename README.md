# ACMG/AMP Variant Classification Advisor

A tool for clinical geneticists and variant analysts that classifies sequence variants using the **Bayesian point-based system** ([Tavtigian et al. 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC8011844/)) and advises what additional evidence would be needed to change a variant's classification from one tier to another.

This project follows the [CAPTURE](https://github.com/lasseignelab/capture) framework for reproducible computational research.

## Background

The [ACMG/AMP 2015 guidelines](https://pmc.ncbi.nlm.nih.gov/articles/PMC4544753/) (Richards et al.) established 28 evidence codes for classifying sequence variants into five tiers: **Pathogenic**, **Likely Pathogenic**, **VUS (Uncertain Significance)**, **Likely Benign**, and **Benign**.

[Tavtigian et al. (2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6336098/), [2020)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8011844/) demonstrated that these qualitative rules are mathematically compatible with a quantitative Bayesian framework, where each evidence strength maps to a point value:

| Strength | Direction | Points |
|---|---|---|
| Very Strong | Pathogenic | +8 |
| Strong | Pathogenic | +4 |
| Moderate | Pathogenic | +2 |
| Supporting | Pathogenic | +1 |
| Supporting | Benign | -1 |
| Strong | Benign | -4 |
| Stand-alone | Benign | -8 |

Classification is determined by the total point sum:

| Classification | Point Range |
|---|---|
| Pathogenic | >= 10 |
| Likely Pathogenic | 6 to 9 |
| VUS | 0 to 5 |
| Likely Benign | -1 to -6 |
| Benign | <= -7 |

This point-based system is the foundation of the [ClinGen SVI](https://clinicalgenome.org/working-groups/sequence-variant-interpretation/) recommendations and the upcoming ACMG/AMP v4 guidelines (expected mid-2026).

## Features

- **Classify variants** from any combination of the 28 ACMG/AMP evidence codes
- **Bidirectional advice**: see what evidence is needed to upgrade (toward Pathogenic) *or* downgrade (toward Benign) a variant's classification
- **Minimal combinations**: suggestions show the fewest additional codes needed to reach each tier
- **CLI and web interfaces**: use from the terminal or through an interactive browser-based UI
- **REST API**: programmatic access via JSON endpoints
- **121 comprehensive tests** covering all classification rules, boundary conditions, conflicting evidence, and validation that suggestions actually achieve their target tier
- **CAPTURE framework**: reproducible project structure with numbered pipeline scripts, verification scripts, Docker support, and CI/CD

## Installation

### With CAPTURE

```bash
git clone https://github.com/blasseigne/VariantClassificationChanger.git
cd VariantClassificationChanger
cap run src/01_setup_environment.sh
```

### Without CAPTURE

```bash
git clone https://github.com/blasseigne/VariantClassificationChanger.git
cd VariantClassificationChanger
bash src/01_setup_environment.sh
```

### Manual Setup

```bash
git clone https://github.com/blasseigne/VariantClassificationChanger.git
cd VariantClassificationChanger
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### CLI

**Classify and get advice for a set of evidence codes:**

```bash
python -m src.variant_classifier PM2 PP3
```

Example output:

```
Current Classification: VUS (Uncertain Significance)
Total Points: 3
Applied Codes: PM2, PP3

=== UPGRADES (toward Pathogenic) ===

  To reach Likely Pathogenic (need 3 more points):
    Option 1: PS1 (+4) = +4 points
    Option 2: PS2 (+4) = +4 points
    Option 3: PS3 (+4) = +4 points
    Option 4: PS4 (+4) = +4 points
    Option 5: PM1 (+2) + PP1 (+1) = +3 points
    ...

=== DOWNGRADES (toward Benign) ===

  To reach Likely Benign (need -3 points):
    Option 1: BS1 (-4) = -4 points
    Option 2: BS2 (-4) = -4 points
    ...
```

**Using CAPTURE pipeline scripts:**

```bash
cap run src/03_run_cli.sh -- PM2 PP3
# or without CAPTURE:
bash src/03_run_cli.sh PM2 PP3
```

**Interactive mode:**

```bash
python -m src.variant_classifier --interactive
```

**Classification only (no advice):**

```bash
python -m src.variant_classifier --classify-only PVS1 PM2
```

**List all evidence codes:**

```bash
python -m src.variant_classifier --list-codes
```

**Limit suggestion size (max codes per suggestion):**

```bash
python -m src.variant_classifier --max-codes 2 PM2 PP3
```

### Web Application

```bash
bash src/04_run_web.sh
# or with CAPTURE:
cap run src/04_run_web.sh
```

Then open **http://localhost:8080** in your browser.

The web UI provides:
- Checkbox selection for all 28 evidence codes, organized by strength and direction
- Point values and descriptions displayed alongside each code
- Color-coded classification badge
- Expandable upgrade and downgrade suggestions with full descriptions

### REST API

The web app exposes three JSON endpoints:

**POST `/api/classify`** -- Classify a variant

```bash
curl -X POST http://localhost:8080/api/classify \
  -H "Content-Type: application/json" \
  -d '{"codes": ["PVS1", "PM2"]}'
```

```json
{
  "classification": "Pathogenic",
  "short_label": "P",
  "total_points": 10,
  "pathogenic_points": 10,
  "benign_points": 0,
  "applied_codes": ["PVS1", "PM2"]
}
```

**POST `/api/advise`** -- Get upgrade/downgrade suggestions

```bash
curl -X POST http://localhost:8080/api/advise \
  -H "Content-Type: application/json" \
  -d '{"codes": ["PM2", "PP3"], "max_codes": 3}'
```

**GET `/api/codes`** -- List all available evidence codes

```bash
curl http://localhost:8080/api/codes
```

### Docker

```bash
docker build -t variant-classifier -f bin/container/Dockerfile .
docker run -p 8080:8080 variant-classifier
```

## Evidence Codes Reference

### Pathogenic Evidence

| Code | Strength | Points | Description |
|---|---|---|---|
| PVS1 | Very Strong | +8 | Null variant in a gene where LOF is a known mechanism of disease |
| PS1 | Strong | +4 | Same amino acid change as a previously established pathogenic variant |
| PS2 | Strong | +4 | De novo (confirmed) in a patient with disease and no family history |
| PS3 | Strong | +4 | Well-established functional studies supportive of a damaging effect |
| PS4 | Strong | +4 | Prevalence significantly increased in affected vs. controls |
| PM1 | Moderate | +2 | Located in a mutational hot spot / critical functional domain |
| PM2 | Moderate | +2 | Absent from controls in population databases |
| PM3 | Moderate | +2 | Detected in trans with a pathogenic variant (recessive) |
| PM4 | Moderate | +2 | Protein length change from in-frame indels or stop-loss |
| PM5 | Moderate | +2 | Novel missense at a residue where a different pathogenic missense exists |
| PM6 | Moderate | +2 | Assumed de novo without parental confirmation |
| PP1 | Supporting | +1 | Cosegregation with disease in multiple affected family members |
| PP2 | Supporting | +1 | Missense in a gene with low benign missense rate |
| PP3 | Supporting | +1 | Computational evidence supports a deleterious effect |
| PP4 | Supporting | +1 | Phenotype highly specific for a single-gene disease |
| PP5 | Supporting | +1 | Reputable source reports variant as pathogenic |

### Benign Evidence

| Code | Strength | Points | Description |
|---|---|---|---|
| BA1 | Stand-alone | -8 | Allele frequency >5% in population databases |
| BS1 | Strong | -4 | Allele frequency greater than expected for disorder |
| BS2 | Strong | -4 | Observed in healthy adult for early-onset fully penetrant disorder |
| BS3 | Strong | -4 | Functional studies show no damaging effect |
| BS4 | Strong | -4 | Lack of segregation in affected family members |
| BP1 | Supporting | -1 | Missense in a gene where truncating variants cause disease |
| BP2 | Supporting | -1 | Observed in trans with pathogenic (dominant) or in cis with pathogenic |
| BP3 | Supporting | -1 | In-frame indel in repetitive region without known function |
| BP4 | Supporting | -1 | Computational evidence suggests no impact |
| BP5 | Supporting | -1 | Variant found in case with alternate molecular basis |
| BP6 | Supporting | -1 | Reputable source reports variant as benign |
| BP7 | Supporting | -1 | Synonymous with no predicted splicing impact |

## Project Structure (CAPTURE)

```
VariantClassificationChanger/
├── .github/
│   ├── settings/
│   │   └── default_ruleset.json    # Branch protection rules
│   └── workflows/
│       ├── mega-linter.yml         # Code quality CI
│       └── tests.yml               # Test suite CI
├── .mega-linter.yml                # Linter configuration
├── bin/
│   ├── container/
│   │   └── Dockerfile              # Containerized reproducibility
│   └── env/                        # Environment files
├── config/
│   ├── pipeline.sh                 # Project name & random seed
│   └── environments/
│       └── default.sh              # Default environment settings
├── data/                           # Input data (git-ignored)
├── doc/                            # Documentation & supplementary materials
├── logs/                           # Execution logs (git-ignored)
├── results/                        # Generated outputs
├── src/
│   ├── variant_classifier/         # Python package
│   │   ├── __init__.py
│   │   ├── __main__.py             # Entry point
│   │   ├── evidence_codes.py       # 28 ACMG/AMP codes with point values
│   │   ├── classifier.py           # Bayesian classification engine
│   │   ├── advisor.py              # Bidirectional tier-change advisor
│   │   ├── cli.py                  # Command-line interface
│   │   └── web/
│   │       ├── __init__.py
│   │       ├── app.py              # Flask web app + REST API
│   │       └── templates/
│   │           └── index.html      # Web UI
│   ├── 01_setup_environment.sh     # Setup venv & install deps
│   ├── 02_run_tests.sh             # Run test suite
│   ├── 03_run_cli.sh               # Run CLI classifier
│   └── 04_run_web.sh               # Start web application
├── tests/
│   ├── test_evidence_codes.py      # Evidence code definitions & lookups
│   ├── test_classifier.py          # Classification rules & boundaries
│   ├── test_advisor.py             # Advisor suggestions & validation
│   └── test_web.py                 # Flask API & page tests
├── verifications/
│   └── verify_classification.sh    # Reproducibility verification
├── DEVELOPMENT.md                  # Developer guide
├── LICENSE                         # GPL-3.0
├── README.md
└── requirements.txt
```

## Testing

```bash
# With CAPTURE:
cap run src/02_run_tests.sh

# Without CAPTURE:
bash src/02_run_tests.sh

# Or directly:
source venv/bin/activate
python -m pytest tests/ -v
```

The test suite (121 tests) covers:

- **Evidence code definitions**: all 28 codes have correct points, strengths, and directions
- **Classification thresholds**: every boundary between tiers is tested
- **ACMG/AMP rule equivalents**: Pathogenic, Likely Pathogenic, VUS, Likely Benign, and Benign combinations
- **Conflicting evidence**: pathogenic + benign codes cancel correctly
- **Advisor upgrades**: suggestions for moving toward Pathogenic
- **Advisor downgrades**: suggestions for moving toward Benign
- **Suggestion validation**: every suggested combination is verified to actually achieve its target tier when applied
- **No duplicate suggestions**: already-applied codes are excluded from suggestions
- **Web API**: all endpoints tested for correct responses and error handling
- **Edge cases**: case insensitivity, invalid codes, empty input, extreme combinations

## Verification

```bash
# With CAPTURE:
cap run verifications/verify_classification.sh

# Without CAPTURE:
bash verifications/verify_classification.sh
```

Verification outputs are saved to `verifications/verify_classification.out` and should be committed so reviewers can `git diff` to confirm reproducibility.

## References

1. Richards S, et al. (2015). Standards and guidelines for the interpretation of sequence variants. *Genetics in Medicine*, 17(5):405-424. [PMID: 25741868](https://pubmed.ncbi.nlm.nih.gov/25741868/)

2. Tavtigian SV, et al. (2018). Modeling the ACMG/AMP variant classification guidelines as a Bayesian classification framework. *Genetics in Medicine*, 20(9):1054-1060. [PMID: 29300386](https://pubmed.ncbi.nlm.nih.gov/29300386/)

3. Tavtigian SV, et al. (2020). Fitting a naturally scaled point system to the ACMG/AMP variant classification guidelines. *Human Mutation*, 41(10):1734-1737. [PMID: 32720330](https://pubmed.ncbi.nlm.nih.gov/32720330/)

4. ClinGen Sequence Variant Interpretation Working Group. [Variant Classification Guidance](https://clinicalgenome.org/tools/clingen-variant-classification-guidance/).

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).
