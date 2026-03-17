"""
Bidirectional classification change advisor.

Given a set of current evidence codes, determines what additional codes
would be needed to move the variant's classification up (toward Pathogenic)
or down (toward Benign).
"""

from dataclasses import dataclass
from itertools import combinations

from .evidence_codes import (
    EvidenceCode,
    ALL_CODES,
    PATHOGENIC_CODES,
    BENIGN_CODES,
    parse_codes,
)
from .classifier import (
    Classification,
    classify,
    calculate_points,
    points_to_classification,
)


@dataclass
class TierChange:
    """A possible path to reach a different classification tier."""
    target_tier: Classification
    points_needed: int
    possible_additions: list[list[EvidenceCode]]

    @property
    def target_label(self) -> str:
        return self.target_tier.label


@dataclass
class AdvisorResult:
    """Full advisor output: current state + possible tier changes."""
    current_classification: Classification
    total_points: int
    applied_codes: list[EvidenceCode]
    upgrades: list[TierChange]
    downgrades: list[TierChange]


def _min_points_for_tier(tier: Classification) -> int:
    """Return the minimum point value needed to enter a tier."""
    thresholds = {
        Classification.PATHOGENIC: 10,
        Classification.LIKELY_PATHOGENIC: 6,
        Classification.VUS: 0,
        Classification.LIKELY_BENIGN: -6,
        Classification.BENIGN: -7,
    }
    return thresholds[tier]


def _max_points_for_tier(tier: Classification) -> int:
    """Return the maximum point value for a tier (for downgrade targets)."""
    thresholds = {
        Classification.PATHOGENIC: 999,
        Classification.LIKELY_PATHOGENIC: 9,
        Classification.VUS: 5,
        Classification.LIKELY_BENIGN: -1,
        Classification.BENIGN: -7,
    }
    return thresholds[tier]


def _find_minimal_combinations(
    available_codes: list[EvidenceCode],
    points_needed: int,
    direction: str,
    max_codes: int = 4,
) -> list[list[EvidenceCode]]:
    """
    Find minimal combinations of available codes that provide enough points.

    For upgrades (direction="up"): find combos whose sum >= points_needed (positive).
    For downgrades (direction="down"): find combos whose sum <= points_needed (negative).

    Returns combinations sorted by size (fewest codes first), then by
    total absolute points (most efficient first). Limited to max_codes
    per combination to keep results manageable.
    """
    results = []

    for r in range(1, min(max_codes, len(available_codes)) + 1):
        for combo in combinations(available_codes, r):
            combo_points = sum(c.points for c in combo)
            if direction == "up" and combo_points >= points_needed:
                results.append(list(combo))
            elif direction == "down" and combo_points <= points_needed:
                results.append(list(combo))

        # If we found solutions at this size, no need to check larger combos
        if results:
            break

    # Sort by total points (most efficient first for the direction)
    if direction == "up":
        results.sort(key=lambda combo: sum(c.points for c in combo))
    else:
        results.sort(key=lambda combo: sum(c.points for c in combo), reverse=True)

    return results[:20]


def advise(codes: list[EvidenceCode], max_codes: int = 4) -> AdvisorResult:
    """
    Given current evidence codes, advise on what's needed to change tiers.

    Args:
        codes: Currently applied evidence codes.
        max_codes: Maximum number of additional codes in a suggestion (default 4).

    Returns:
        AdvisorResult with upgrade and downgrade options.
    """
    result = classify(codes)
    current_tier = result.classification
    total_pts = result.total_points
    applied_set = {c.code for c in codes}

    # Available codes the user hasn't applied yet
    available_pathogenic = [
        c for c in PATHOGENIC_CODES.values() if c.code not in applied_set
    ]
    available_benign = [
        c for c in BENIGN_CODES.values() if c.code not in applied_set
    ]

    upgrades = []
    downgrades = []

    # --- Upgrades (toward Pathogenic) ---
    for tier in Classification:
        if tier <= current_tier:
            continue
        min_pts = _min_points_for_tier(tier)
        gap = min_pts - total_pts
        if gap <= 0:
            continue

        combos = _find_minimal_combinations(
            available_pathogenic, gap, "up", max_codes
        )
        upgrades.append(TierChange(
            target_tier=tier,
            points_needed=gap,
            possible_additions=combos,
        ))

    # --- Downgrades (toward Benign) ---
    for tier in reversed(Classification):
        if tier >= current_tier:
            continue
        max_pts = _max_points_for_tier(tier)
        gap = max_pts - total_pts  # This will be negative
        if gap >= 0:
            continue

        combos = _find_minimal_combinations(
            available_benign, gap, "down", max_codes
        )
        downgrades.append(TierChange(
            target_tier=tier,
            points_needed=gap,
            possible_additions=combos,
        ))

    return AdvisorResult(
        current_classification=current_tier,
        total_points=total_pts,
        applied_codes=list(codes),
        upgrades=upgrades,
        downgrades=downgrades,
    )


def advise_from_names(code_names: list[str], max_codes: int = 4) -> AdvisorResult:
    """Advise from a list of evidence code name strings."""
    codes = parse_codes(code_names)
    return advise(codes, max_codes)


def format_advice(result: AdvisorResult) -> str:
    """Format advisor results as a human-readable string."""
    lines = [
        f"Current Classification: {result.current_classification.label}",
        f"Total Points: {result.total_points}",
        f"Applied Codes: {', '.join(c.code for c in result.applied_codes) or 'None'}",
        "",
    ]

    if result.upgrades:
        lines.append("=== UPGRADES (toward Pathogenic) ===")
        for change in result.upgrades:
            lines.append(f"\n  To reach {change.target_label} (need {change.points_needed} more points):")
            if change.possible_additions:
                for i, combo in enumerate(change.possible_additions, 1):
                    codes_str = " + ".join(
                        f"{c.code} ({c.points:+d})" for c in combo
                    )
                    total = sum(c.points for c in combo)
                    lines.append(f"    Option {i}: {codes_str} = {total:+d} points")
            else:
                lines.append("    No single combination of up to 4 codes is sufficient.")
        lines.append("")

    if result.downgrades:
        lines.append("=== DOWNGRADES (toward Benign) ===")
        for change in result.downgrades:
            lines.append(f"\n  To reach {change.target_label} (need {change.points_needed} points):")
            if change.possible_additions:
                for i, combo in enumerate(change.possible_additions, 1):
                    codes_str = " + ".join(
                        f"{c.code} ({c.points:+d})" for c in combo
                    )
                    total = sum(c.points for c in combo)
                    lines.append(f"    Option {i}: {codes_str} = {total:+d} points")
            else:
                lines.append("    No single combination of up to 4 codes is sufficient.")
        lines.append("")

    if not result.upgrades and not result.downgrades:
        lines.append("No tier changes are possible (already at an extreme).")

    return "\n".join(lines)
