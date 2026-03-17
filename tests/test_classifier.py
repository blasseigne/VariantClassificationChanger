"""
Comprehensive tests for the Bayesian classifier.

Tests all ACMG/AMP combining rule equivalents under the point system,
edge cases, and boundary conditions.
"""

import pytest
from src.variant_classifier.evidence_codes import ALL_CODES, get_code, parse_codes
from src.variant_classifier.classifier import (
    Classification,
    classify,
    classify_from_names,
    calculate_points,
    points_to_classification,
)


# ============================================================
# Point calculation tests
# ============================================================

class TestCalculatePoints:
    def test_empty_codes(self):
        total, path, ben = calculate_points([])
        assert total == 0
        assert path == 0
        assert ben == 0

    def test_single_pathogenic(self):
        total, path, ben = calculate_points([get_code("PVS1")])
        assert total == 8
        assert path == 8
        assert ben == 0

    def test_single_benign(self):
        total, path, ben = calculate_points([get_code("BA1")])
        assert total == -8
        assert path == 0
        assert ben == -8

    def test_mixed_evidence(self):
        codes = parse_codes(["PM2", "PP3", "BP4"])
        total, path, ben = calculate_points(codes)
        assert path == 3  # PM2(2) + PP3(1)
        assert ben == -1  # BP4(-1)
        assert total == 2

    def test_all_pathogenic_codes(self):
        codes = [c for c in ALL_CODES.values() if c.points > 0]
        total, path, ben = calculate_points(codes)
        # PVS1(8) + 4*PS(16) + 6*PM(12) + 5*PP(5) = 41
        assert path == 41
        assert ben == 0
        assert total == 41

    def test_all_benign_codes(self):
        codes = [c for c in ALL_CODES.values() if c.points < 0]
        total, path, ben = calculate_points(codes)
        # BA1(-8) + 4*BS(-16) + 7*BP(-7) = -31
        assert ben == -31
        assert path == 0
        assert total == -31


# ============================================================
# Point-to-classification threshold tests
# ============================================================

class TestPointsToClassification:
    @pytest.mark.parametrize("points,expected", [
        (10, Classification.PATHOGENIC),
        (11, Classification.PATHOGENIC),
        (50, Classification.PATHOGENIC),
        (9, Classification.LIKELY_PATHOGENIC),
        (6, Classification.LIKELY_PATHOGENIC),
        (5, Classification.VUS),
        (0, Classification.VUS),
        (3, Classification.VUS),
        (-1, Classification.LIKELY_BENIGN),
        (-6, Classification.LIKELY_BENIGN),
        (-7, Classification.BENIGN),
        (-8, Classification.BENIGN),
        (-100, Classification.BENIGN),
    ])
    def test_thresholds(self, points, expected):
        assert points_to_classification(points) == expected

    def test_boundary_pathogenic_lp(self):
        assert points_to_classification(10) == Classification.PATHOGENIC
        assert points_to_classification(9) == Classification.LIKELY_PATHOGENIC

    def test_boundary_lp_vus(self):
        assert points_to_classification(6) == Classification.LIKELY_PATHOGENIC
        assert points_to_classification(5) == Classification.VUS

    def test_boundary_vus_lb(self):
        assert points_to_classification(0) == Classification.VUS
        assert points_to_classification(-1) == Classification.LIKELY_BENIGN

    def test_boundary_lb_b(self):
        assert points_to_classification(-6) == Classification.LIKELY_BENIGN
        assert points_to_classification(-7) == Classification.BENIGN


# ============================================================
# Classification tests — ACMG/AMP rule equivalents
# ============================================================

class TestClassifyPathogenic:
    """Test combinations that should yield Pathogenic (>=10 points)."""

    def test_pvs1_plus_ps(self):
        """PVS1(8) + PS1(4) = 12 -> Pathogenic"""
        result = classify_from_names(["PVS1", "PS1"])
        assert result.classification == Classification.PATHOGENIC
        assert result.total_points == 12

    def test_pvs1_plus_pm(self):
        """PVS1(8) + PM1(2) = 10 -> Pathogenic"""
        result = classify_from_names(["PVS1", "PM1"])
        assert result.classification == Classification.PATHOGENIC
        assert result.total_points == 10

    def test_pvs1_plus_2pp(self):
        """PVS1(8) + PP1(1) + PP2(1) = 10 -> Pathogenic"""
        result = classify_from_names(["PVS1", "PP1", "PP2"])
        assert result.classification == Classification.PATHOGENIC
        assert result.total_points == 10

    def test_two_strong(self):
        """PS1(4) + PS2(4) + PM1(2) = 10 -> Pathogenic"""
        result = classify_from_names(["PS1", "PS2", "PM1"])
        assert result.classification == Classification.PATHOGENIC
        assert result.total_points == 10

    def test_ps_3pm(self):
        """PS1(4) + PM1(2) + PM2(2) + PM3(2) = 10 -> Pathogenic"""
        result = classify_from_names(["PS1", "PM1", "PM2", "PM3"])
        assert result.classification == Classification.PATHOGENIC
        assert result.total_points == 10

    def test_ps_2pm_2pp(self):
        """PS1(4) + PM1(2) + PM2(2) + PP1(1) + PP2(1) = 10 -> Pathogenic"""
        result = classify_from_names(["PS1", "PM1", "PM2", "PP1", "PP2"])
        assert result.classification == Classification.PATHOGENIC
        assert result.total_points == 10


class TestClassifyLikelyPathogenic:
    """Test combinations that should yield Likely Pathogenic (6-9 points)."""

    def test_pvs1_plus_pp(self):
        """PVS1(8) + PP1(1) = 9 -> LP"""
        result = classify_from_names(["PVS1", "PP1"])
        assert result.classification == Classification.LIKELY_PATHOGENIC
        assert result.total_points == 9

    def test_pvs1_alone(self):
        """PVS1(8) alone = 8 -> LP"""
        result = classify_from_names(["PVS1"])
        assert result.classification == Classification.LIKELY_PATHOGENIC
        assert result.total_points == 8

    def test_ps_plus_pm(self):
        """PS1(4) + PM1(2) = 6 -> LP"""
        result = classify_from_names(["PS1", "PM1"])
        assert result.classification == Classification.LIKELY_PATHOGENIC
        assert result.total_points == 6

    def test_ps_plus_2pp(self):
        """PS1(4) + PP1(1) + PP2(1) = 6 -> LP"""
        result = classify_from_names(["PS1", "PP1", "PP2"])
        assert result.classification == Classification.LIKELY_PATHOGENIC
        assert result.total_points == 6

    def test_3pm(self):
        """PM1(2) + PM2(2) + PM3(2) = 6 -> LP"""
        result = classify_from_names(["PM1", "PM2", "PM3"])
        assert result.classification == Classification.LIKELY_PATHOGENIC
        assert result.total_points == 6

    def test_2pm_2pp(self):
        """PM1(2) + PM2(2) + PP1(1) + PP2(1) = 6 -> LP"""
        result = classify_from_names(["PM1", "PM2", "PP1", "PP2"])
        assert result.classification == Classification.LIKELY_PATHOGENIC
        assert result.total_points == 6

    def test_two_strong(self):
        """PS1(4) + PS2(4) = 8 -> LP"""
        result = classify_from_names(["PS1", "PS2"])
        assert result.classification == Classification.LIKELY_PATHOGENIC
        assert result.total_points == 8


class TestClassifyVUS:
    """Test combinations that should yield VUS (0-5 points)."""

    def test_empty(self):
        result = classify([])
        assert result.classification == Classification.VUS
        assert result.total_points == 0

    def test_single_supporting(self):
        """PP3(1) = 1 -> VUS"""
        result = classify_from_names(["PP3"])
        assert result.classification == Classification.VUS
        assert result.total_points == 1

    def test_single_moderate(self):
        """PM2(2) = 2 -> VUS"""
        result = classify_from_names(["PM2"])
        assert result.classification == Classification.VUS
        assert result.total_points == 2

    def test_single_strong(self):
        """PS1(4) alone = 4 -> VUS"""
        result = classify_from_names(["PS1"])
        assert result.classification == Classification.VUS
        assert result.total_points == 4

    def test_pm_pp(self):
        """PM2(2) + PP3(1) = 3 -> VUS"""
        result = classify_from_names(["PM2", "PP3"])
        assert result.classification == Classification.VUS
        assert result.total_points == 3

    def test_conflicting_cancels(self):
        """PVS1(8) + BS1(-4) = 4 -> VUS (conflicting evidence)"""
        result = classify_from_names(["PVS1", "BS1"])
        assert result.classification == Classification.VUS
        assert result.total_points == 4

    def test_2pm(self):
        """PM1(2) + PM2(2) = 4 -> VUS"""
        result = classify_from_names(["PM1", "PM2"])
        assert result.classification == Classification.VUS
        assert result.total_points == 4

    def test_5pp_is_vus(self):
        """5 supporting = 5 -> VUS"""
        result = classify_from_names(["PP1", "PP2", "PP3", "PP4", "PP5"])
        assert result.classification == Classification.VUS
        assert result.total_points == 5


class TestClassifyLikelyBenign:
    """Test combinations that should yield Likely Benign (-6 to -1 points)."""

    def test_single_bp(self):
        """BP1(-1) = -1 -> LB"""
        result = classify_from_names(["BP1"])
        assert result.classification == Classification.LIKELY_BENIGN
        assert result.total_points == -1

    def test_bs_plus_bp(self):
        """BS1(-4) + BP1(-1) = -5 -> LB"""
        result = classify_from_names(["BS1", "BP1"])
        assert result.classification == Classification.LIKELY_BENIGN
        assert result.total_points == -5

    def test_2bp(self):
        """BP1(-1) + BP2(-1) = -2 -> LB"""
        result = classify_from_names(["BP1", "BP2"])
        assert result.classification == Classification.LIKELY_BENIGN
        assert result.total_points == -2

    def test_6bp_is_lb(self):
        """6 supporting benign = -6 -> LB (boundary)"""
        result = classify_from_names(["BP1", "BP2", "BP3", "BP4", "BP5", "BP6"])
        assert result.classification == Classification.LIKELY_BENIGN
        assert result.total_points == -6


class TestClassifyBenign:
    """Test combinations that should yield Benign (<= -7 points)."""

    def test_ba1_alone(self):
        """BA1(-8) = -8 -> Benign"""
        result = classify_from_names(["BA1"])
        assert result.classification == Classification.BENIGN
        assert result.total_points == -8

    def test_two_bs(self):
        """BS1(-4) + BS2(-4) = -8 -> Benign"""
        result = classify_from_names(["BS1", "BS2"])
        assert result.classification == Classification.BENIGN
        assert result.total_points == -8

    def test_7bp_is_benign(self):
        """7 supporting benign = -7 -> Benign (boundary)"""
        result = classify_from_names(["BP1", "BP2", "BP3", "BP4", "BP5", "BP6", "BP7"])
        assert result.classification == Classification.BENIGN
        assert result.total_points == -7

    def test_bs_plus_many_bp(self):
        """BS1(-4) + BP1(-1) + BP2(-1) + BP3(-1) = -7 -> Benign"""
        result = classify_from_names(["BS1", "BP1", "BP2", "BP3"])
        assert result.classification == Classification.BENIGN
        assert result.total_points == -7


# ============================================================
# Conflicting evidence tests
# ============================================================

class TestConflictingEvidence:
    def test_strong_path_plus_strong_benign(self):
        """PS1(4) + BS1(-4) = 0 -> VUS"""
        result = classify_from_names(["PS1", "BS1"])
        assert result.classification == Classification.VUS
        assert result.total_points == 0

    def test_pvs1_plus_ba1(self):
        """PVS1(8) + BA1(-8) = 0 -> VUS"""
        result = classify_from_names(["PVS1", "BA1"])
        assert result.classification == Classification.VUS
        assert result.total_points == 0

    def test_heavy_path_slight_benign(self):
        """PVS1(8) + PS1(4) + BP1(-1) = 11 -> still Pathogenic"""
        result = classify_from_names(["PVS1", "PS1", "BP1"])
        assert result.classification == Classification.PATHOGENIC
        assert result.total_points == 11

    def test_benign_with_slight_path(self):
        """BA1(-8) + PP1(1) = -7 -> still Benign"""
        result = classify_from_names(["BA1", "PP1"])
        assert result.classification == Classification.BENIGN
        assert result.total_points == -7


# ============================================================
# Edge cases
# ============================================================

class TestEdgeCases:
    def test_classify_from_names_case_insensitive(self):
        result = classify_from_names(["pvs1", "ps1"])
        assert result.classification == Classification.PATHOGENIC

    def test_invalid_code_raises(self):
        with pytest.raises(ValueError, match="Unknown evidence code"):
            classify_from_names(["FAKE1"])

    def test_result_summary(self):
        result = classify_from_names(["PM2", "PP3"])
        summary = result.summary()
        assert "VUS" in summary
        assert "PM2" in summary
        assert "PP3" in summary

    def test_classification_labels(self):
        assert Classification.PATHOGENIC.label == "Pathogenic"
        assert Classification.LIKELY_PATHOGENIC.label == "Likely Pathogenic"
        assert Classification.VUS.label == "VUS (Uncertain Significance)"
        assert Classification.LIKELY_BENIGN.label == "Likely Benign"
        assert Classification.BENIGN.label == "Benign"

    def test_classification_ordering(self):
        assert Classification.BENIGN < Classification.LIKELY_BENIGN
        assert Classification.LIKELY_BENIGN < Classification.VUS
        assert Classification.VUS < Classification.LIKELY_PATHOGENIC
        assert Classification.LIKELY_PATHOGENIC < Classification.PATHOGENIC
