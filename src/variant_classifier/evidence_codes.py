"""
ACMG/AMP evidence codes with Bayesian point values.

Based on Tavtigian et al. (2020) "Fitting a naturally scaled point system
to the ACMG/AMP variant classification guidelines."

Point values:
  - Very Strong pathogenic: 8
  - Strong pathogenic:      4
  - Moderate pathogenic:    2
  - Supporting pathogenic:  1
  - Supporting benign:     -1
  - Strong benign:         -4
  - Stand-alone benign:    -8
"""

from enum import Enum
from dataclasses import dataclass


class EvidenceDirection(Enum):
    PATHOGENIC = "pathogenic"
    BENIGN = "benign"


class EvidenceStrength(Enum):
    SUPPORTING = "supporting"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"
    STAND_ALONE = "stand_alone"


@dataclass(frozen=True)
class EvidenceCode:
    code: str
    direction: EvidenceDirection
    strength: EvidenceStrength
    points: int
    description: str


# --- Pathogenic evidence codes ---

PVS1 = EvidenceCode(
    code="PVS1",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.VERY_STRONG,
    points=8,
    description="Null variant in a gene where LOF is a known mechanism of disease",
)

PS1 = EvidenceCode(
    code="PS1",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.STRONG,
    points=4,
    description="Same amino acid change as a previously established pathogenic variant",
)

PS2 = EvidenceCode(
    code="PS2",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.STRONG,
    points=4,
    description="De novo (both maternity and paternity confirmed) in a patient with the disease and no family history",
)

PS3 = EvidenceCode(
    code="PS3",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.STRONG,
    points=4,
    description="Well-established in vitro or in vivo functional studies supportive of a damaging effect",
)

PS4 = EvidenceCode(
    code="PS4",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.STRONG,
    points=4,
    description="Prevalence of the variant in affected individuals is significantly increased compared with controls",
)

PM1 = EvidenceCode(
    code="PM1",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.MODERATE,
    points=2,
    description="Located in a mutational hot spot and/or critical and well-established functional domain",
)

PM2 = EvidenceCode(
    code="PM2",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.MODERATE,
    points=2,
    description="Absent from controls (or at extremely low frequency if recessive) in population databases",
)

PM3 = EvidenceCode(
    code="PM3",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.MODERATE,
    points=2,
    description="For recessive disorders, detected in trans with a pathogenic variant",
)

PM4 = EvidenceCode(
    code="PM4",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.MODERATE,
    points=2,
    description="Protein length changes as a result of in-frame deletions/insertions or stop-loss variants",
)

PM5 = EvidenceCode(
    code="PM5",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.MODERATE,
    points=2,
    description="Novel missense change at an amino acid residue where a different pathogenic missense change has been seen before",
)

PM6 = EvidenceCode(
    code="PM6",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.MODERATE,
    points=2,
    description="Assumed de novo, but without confirmation of paternity and maternity",
)

PP1 = EvidenceCode(
    code="PP1",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.SUPPORTING,
    points=1,
    description="Cosegregation with disease in multiple affected family members",
)

PP2 = EvidenceCode(
    code="PP2",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.SUPPORTING,
    points=1,
    description="Missense variant in a gene with a low rate of benign missense variation and where missense variants are a common mechanism of disease",
)

PP3 = EvidenceCode(
    code="PP3",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.SUPPORTING,
    points=1,
    description="Multiple lines of computational evidence support a deleterious effect on the gene or gene product",
)

PP4 = EvidenceCode(
    code="PP4",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.SUPPORTING,
    points=1,
    description="Patient's phenotype or family history is highly specific for a disease with a single genetic etiology",
)

PP5 = EvidenceCode(
    code="PP5",
    direction=EvidenceDirection.PATHOGENIC,
    strength=EvidenceStrength.SUPPORTING,
    points=1,
    description="Reputable source recently reports variant as pathogenic, but evidence is not available to the laboratory (note: ClinGen SVI recommends against using this code)",
)

# --- Benign evidence codes ---

BA1 = EvidenceCode(
    code="BA1",
    direction=EvidenceDirection.BENIGN,
    strength=EvidenceStrength.STAND_ALONE,
    points=-8,
    description="Allele frequency is >5% in population databases",
)

BS1 = EvidenceCode(
    code="BS1",
    direction=EvidenceDirection.BENIGN,
    strength=EvidenceStrength.STRONG,
    points=-4,
    description="Allele frequency is greater than expected for disorder",
)

BS2 = EvidenceCode(
    code="BS2",
    direction=EvidenceDirection.BENIGN,
    strength=EvidenceStrength.STRONG,
    points=-4,
    description="Observed in a healthy adult individual for a recessive, dominant, or X-linked disorder with full penetrance expected at an early age",
)

BS3 = EvidenceCode(
    code="BS3",
    direction=EvidenceDirection.BENIGN,
    strength=EvidenceStrength.STRONG,
    points=-4,
    description="Well-established in vitro or in vivo functional studies show no damaging effect on protein function or splicing",
)

BS4 = EvidenceCode(
    code="BS4",
    direction=EvidenceDirection.BENIGN,
    strength=EvidenceStrength.STRONG,
    points=-4,
    description="Lack of segregation in affected members of a family",
)

BP1 = EvidenceCode(
    code="BP1",
    direction=EvidenceDirection.BENIGN,
    strength=EvidenceStrength.SUPPORTING,
    points=-1,
    description="Missense variant in a gene for which primarily truncating variants are known to cause disease",
)

BP2 = EvidenceCode(
    code="BP2",
    direction=EvidenceDirection.BENIGN,
    strength=EvidenceStrength.SUPPORTING,
    points=-1,
    description="Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder, or in cis with a pathogenic variant in any inheritance pattern",
)

BP3 = EvidenceCode(
    code="BP3",
    direction=EvidenceDirection.BENIGN,
    strength=EvidenceStrength.SUPPORTING,
    points=-1,
    description="In-frame deletions/insertions in a repetitive region without a known function",
)

BP4 = EvidenceCode(
    code="BP4",
    direction=EvidenceDirection.BENIGN,
    strength=EvidenceStrength.SUPPORTING,
    points=-1,
    description="Multiple lines of computational evidence suggest no impact on gene or gene product",
)

BP5 = EvidenceCode(
    code="BP5",
    direction=EvidenceDirection.BENIGN,
    strength=EvidenceStrength.SUPPORTING,
    points=-1,
    description="Variant found in a case with an alternate molecular basis for disease",
)

BP6 = EvidenceCode(
    code="BP6",
    direction=EvidenceDirection.BENIGN,
    strength=EvidenceStrength.SUPPORTING,
    points=-1,
    description="Reputable source recently reports variant as benign, but evidence is not available to the laboratory (note: ClinGen SVI recommends against using this code)",
)

BP7 = EvidenceCode(
    code="BP7",
    direction=EvidenceDirection.BENIGN,
    strength=EvidenceStrength.SUPPORTING,
    points=-1,
    description="A synonymous variant for which splicing prediction algorithms predict no impact and the nucleotide is not highly conserved",
)

# --- Lookup dictionaries ---

ALL_CODES: dict[str, EvidenceCode] = {
    code.code: code
    for code in [
        PVS1,
        PS1, PS2, PS3, PS4,
        PM1, PM2, PM3, PM4, PM5, PM6,
        PP1, PP2, PP3, PP4, PP5,
        BA1,
        BS1, BS2, BS3, BS4,
        BP1, BP2, BP3, BP4, BP5, BP6, BP7,
    ]
}

PATHOGENIC_CODES = {k: v for k, v in ALL_CODES.items() if v.direction == EvidenceDirection.PATHOGENIC}
BENIGN_CODES = {k: v for k, v in ALL_CODES.items() if v.direction == EvidenceDirection.BENIGN}


def get_code(code_name: str) -> EvidenceCode:
    """Look up an evidence code by name (case-insensitive)."""
    if not isinstance(code_name, str):
        raise ValueError(
            f"Evidence code must be a string, got {type(code_name).__name__}: {code_name!r}"
        )
    key = code_name.strip().upper()
    if key not in ALL_CODES:
        raise ValueError(
            f"Unknown evidence code: '{code_name}'. "
            f"Valid codes: {', '.join(sorted(ALL_CODES.keys()))}"
        )
    return ALL_CODES[key]


def parse_codes(code_names: list[str]) -> list[EvidenceCode]:
    """Parse a list of code name strings into EvidenceCode objects.

    Raises ValueError if any code is duplicated, since each ACMG/AMP
    evidence code should be applied at most once per variant.
    """
    seen: set[str] = set()
    codes: list[EvidenceCode] = []
    for name in code_names:
        code = get_code(name)
        if code.code in seen:
            raise ValueError(
                f"Duplicate evidence code: '{code.code}'. "
                f"Each code can only be applied once per variant."
            )
        seen.add(code.code)
        codes.append(code)
    return codes
