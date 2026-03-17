"""
Bayesian point-based variant classifier.

Implements the Tavtigian et al. (2020) point system for ACMG/AMP
variant classification.

Classification thresholds:
  Pathogenic:        >= 10
  Likely Pathogenic: 6 to 9
  VUS:               0 to 5
  Likely Benign:     -1 to -6
  Benign:            <= -7
"""

from dataclasses import dataclass
from enum import IntEnum

from .evidence_codes import EvidenceCode, parse_codes


class Classification(IntEnum):
    """Variant classification tiers, ordered from benign to pathogenic."""
    BENIGN = 1
    LIKELY_BENIGN = 2
    VUS = 3
    LIKELY_PATHOGENIC = 4
    PATHOGENIC = 5

    @property
    def label(self) -> str:
        return {
            Classification.BENIGN: "Benign",
            Classification.LIKELY_BENIGN: "Likely Benign",
            Classification.VUS: "VUS (Uncertain Significance)",
            Classification.LIKELY_PATHOGENIC: "Likely Pathogenic",
            Classification.PATHOGENIC: "Pathogenic",
        }[self]

    @property
    def short_label(self) -> str:
        return {
            Classification.BENIGN: "B",
            Classification.LIKELY_BENIGN: "LB",
            Classification.VUS: "VUS",
            Classification.LIKELY_PATHOGENIC: "LP",
            Classification.PATHOGENIC: "P",
        }[self]


# Threshold boundaries (inclusive)
THRESHOLDS = {
    Classification.PATHOGENIC: (10, float("inf")),
    Classification.LIKELY_PATHOGENIC: (6, 9),
    Classification.VUS: (0, 5),
    Classification.LIKELY_BENIGN: (-6, -1),
    Classification.BENIGN: (float("-inf"), -7),
}


@dataclass
class ClassificationResult:
    """Result of classifying a variant."""
    classification: Classification
    total_points: int
    applied_codes: list[EvidenceCode]
    pathogenic_points: int
    benign_points: int

    @property
    def label(self) -> str:
        return self.classification.label

    def summary(self) -> str:
        lines = [
            f"Classification: {self.classification.label}",
            f"Total points:   {self.total_points}",
            f"  Pathogenic:   +{self.pathogenic_points}",
            f"  Benign:       {self.benign_points}",
            f"Applied codes:  {', '.join(c.code for c in self.applied_codes) or 'None'}",
        ]
        return "\n".join(lines)


def calculate_points(codes: list[EvidenceCode]) -> tuple[int, int, int]:
    """Calculate total, pathogenic, and benign points from evidence codes."""
    path_points = sum(c.points for c in codes if c.points > 0)
    ben_points = sum(c.points for c in codes if c.points < 0)
    return path_points + ben_points, path_points, ben_points


def points_to_classification(total_points: int) -> Classification:
    """Convert a point total to a classification tier."""
    if total_points >= 10:
        return Classification.PATHOGENIC
    elif total_points >= 6:
        return Classification.LIKELY_PATHOGENIC
    elif total_points >= 0:
        return Classification.VUS
    elif total_points >= -6:
        return Classification.LIKELY_BENIGN
    else:
        return Classification.BENIGN


def classify(codes: list[EvidenceCode]) -> ClassificationResult:
    """Classify a variant given a list of evidence codes."""
    total, path_pts, ben_pts = calculate_points(codes)
    classification = points_to_classification(total)
    return ClassificationResult(
        classification=classification,
        total_points=total,
        applied_codes=list(codes),
        pathogenic_points=path_pts,
        benign_points=ben_pts,
    )


def classify_from_names(code_names: list[str]) -> ClassificationResult:
    """Classify a variant from a list of evidence code name strings."""
    codes = parse_codes(code_names)
    return classify(codes)
