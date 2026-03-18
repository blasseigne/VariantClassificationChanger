"""
Comprehensive tests for the bidirectional classification advisor.
"""

import pytest
from src.variant_classifier.evidence_codes import get_code, parse_codes
from src.variant_classifier.classifier import Classification, classify
from src.variant_classifier.advisor import (
    advise,
    advise_from_names,
    format_advice,
    _min_points_for_tier,
    _max_points_for_tier,
    _find_minimal_combinations,
)


# ============================================================
# Advisor core logic tests
# ============================================================

class TestAdvisorUpgrades:
    """Test upgrade suggestions (toward Pathogenic)."""

    def test_vus_to_lp_suggestions(self):
        """From VUS with PM2+PP3 (3pts), should suggest ways to reach LP (6pts)."""
        result = advise_from_names(["PM2", "PP3"])
        assert result.current_classification == Classification.VUS
        assert result.total_points == 3

        # Should have upgrades to LP and P
        upgrade_tiers = [u.target_tier for u in result.upgrades]
        assert Classification.LIKELY_PATHOGENIC in upgrade_tiers
        assert Classification.PATHOGENIC in upgrade_tiers

        # LP needs 3 more points
        lp_change = next(u for u in result.upgrades if u.target_tier == Classification.LIKELY_PATHOGENIC)
        assert lp_change.points_needed == 3
        assert len(lp_change.possible_additions) > 0

        # Verify that each suggested combo actually provides enough points
        for combo in lp_change.possible_additions:
            combo_pts = sum(c.points for c in combo)
            assert combo_pts >= 3

    def test_vus_to_pathogenic_suggestions(self):
        """From VUS with single PS1 (4pts), need 6 more for Pathogenic."""
        result = advise_from_names(["PS1"])
        assert result.current_classification == Classification.VUS

        p_change = next(u for u in result.upgrades if u.target_tier == Classification.PATHOGENIC)
        assert p_change.points_needed == 6

        # Each combo should provide >= 6 points
        for combo in p_change.possible_additions:
            assert sum(c.points for c in combo) >= 6

    def test_lp_to_pathogenic(self):
        """From LP with PVS1 (8pts), need 2 more for Pathogenic."""
        result = advise_from_names(["PVS1"])
        assert result.current_classification == Classification.LIKELY_PATHOGENIC

        p_change = next(u for u in result.upgrades if u.target_tier == Classification.PATHOGENIC)
        assert p_change.points_needed == 2

        # Should suggest moderate or 2 supporting codes
        for combo in p_change.possible_additions:
            assert sum(c.points for c in combo) >= 2

    def test_pathogenic_no_upgrades(self):
        """Already Pathogenic: no upgrades available."""
        result = advise_from_names(["PVS1", "PS1"])
        assert result.current_classification == Classification.PATHOGENIC
        assert len(result.upgrades) == 0

    def test_empty_codes_upgrades(self):
        """No codes applied (VUS at 0pts)."""
        result = advise(codes=[])
        assert result.current_classification == Classification.VUS
        assert len(result.upgrades) > 0

        lp_change = next(u for u in result.upgrades if u.target_tier == Classification.LIKELY_PATHOGENIC)
        assert lp_change.points_needed == 6


class TestAdvisorDowngrades:
    """Test downgrade suggestions (toward Benign)."""

    def test_vus_to_lb_suggestions(self):
        """From VUS with PM2 (2pts), should suggest ways to reach LB."""
        result = advise_from_names(["PM2"])
        assert result.current_classification == Classification.VUS

        downgrade_tiers = [d.target_tier for d in result.downgrades]
        assert Classification.LIKELY_BENIGN in downgrade_tiers

        lb_change = next(d for d in result.downgrades if d.target_tier == Classification.LIKELY_BENIGN)
        # Need to go from 2 to -1, so need -3 points of benign evidence
        assert lb_change.points_needed == -3

        for combo in lb_change.possible_additions:
            assert sum(c.points for c in combo) <= -3

    def test_vus_to_benign_suggestions(self):
        """From VUS at 0pts, need -7 to reach Benign."""
        result = advise(codes=[])
        b_change = next(d for d in result.downgrades if d.target_tier == Classification.BENIGN)
        assert b_change.points_needed == -7

    def test_lp_to_vus_downgrade(self):
        """From LP with PVS1 (8pts), show how to get back to VUS."""
        result = advise_from_names(["PVS1"])
        assert result.current_classification == Classification.LIKELY_PATHOGENIC

        vus_change = next(d for d in result.downgrades if d.target_tier == Classification.VUS)
        # Need to go from 8 to 5, so need -3 points
        assert vus_change.points_needed == -3

    def test_benign_no_downgrades(self):
        """Already Benign: no downgrades available."""
        result = advise_from_names(["BA1"])
        assert result.current_classification == Classification.BENIGN
        assert len(result.downgrades) == 0

    def test_lb_to_benign(self):
        """From LB with BS1+BP1 (-5pts), need -2 more for Benign."""
        result = advise_from_names(["BS1", "BP1"])
        assert result.current_classification == Classification.LIKELY_BENIGN

        b_change = next(d for d in result.downgrades if d.target_tier == Classification.BENIGN)
        assert b_change.points_needed == -2


class TestAdvisorBidirectional:
    """Test that both upgrade and downgrade suggestions appear for VUS."""

    def test_vus_has_both_directions(self):
        result = advise_from_names(["PM2", "PP3"])
        assert len(result.upgrades) > 0
        assert len(result.downgrades) > 0

    def test_lb_has_both_directions(self):
        """LB should have upgrades back to VUS and downgrades to Benign."""
        result = advise_from_names(["BP1", "BP2"])
        assert result.current_classification == Classification.LIKELY_BENIGN

        upgrade_tiers = [u.target_tier for u in result.upgrades]
        assert Classification.VUS in upgrade_tiers

        downgrade_tiers = [d.target_tier for d in result.downgrades]
        assert Classification.BENIGN in downgrade_tiers


# ============================================================
# Suggestion validation: verify suggestions actually work
# ============================================================

class TestSuggestionsActuallyWork:
    """Critical: verify that applying suggested codes actually achieves the target tier."""

    def test_vus_upgrade_to_lp_works(self):
        """Apply each suggested upgrade combo and verify it reaches LP."""
        base_codes = parse_codes(["PM2", "PP3"])
        result = advise(base_codes)
        lp_change = next(u for u in result.upgrades if u.target_tier == Classification.LIKELY_PATHOGENIC)

        for combo in lp_change.possible_additions:
            all_codes = base_codes + combo
            new_result = classify(all_codes)
            assert new_result.classification >= Classification.LIKELY_PATHOGENIC, (
                f"Adding {[c.code for c in combo]} to PM2+PP3 gave "
                f"{new_result.classification.label} ({new_result.total_points}pts), "
                f"expected at least LP"
            )

    def test_vus_upgrade_to_pathogenic_works(self):
        """Apply each suggested upgrade combo and verify it reaches Pathogenic."""
        base_codes = parse_codes(["PS1"])
        result = advise(base_codes)
        p_change = next(u for u in result.upgrades if u.target_tier == Classification.PATHOGENIC)

        for combo in p_change.possible_additions:
            all_codes = base_codes + combo
            new_result = classify(all_codes)
            assert new_result.classification >= Classification.PATHOGENIC, (
                f"Adding {[c.code for c in combo]} to PS1 gave "
                f"{new_result.classification.label} ({new_result.total_points}pts), "
                f"expected Pathogenic"
            )

    def test_vus_downgrade_to_lb_works(self):
        """Apply each suggested downgrade combo and verify it reaches LB."""
        base_codes = parse_codes(["PM2"])
        result = advise(base_codes)
        lb_change = next(d for d in result.downgrades if d.target_tier == Classification.LIKELY_BENIGN)

        for combo in lb_change.possible_additions:
            all_codes = base_codes + combo
            new_result = classify(all_codes)
            assert new_result.classification <= Classification.LIKELY_BENIGN, (
                f"Adding {[c.code for c in combo]} to PM2 gave "
                f"{new_result.classification.label} ({new_result.total_points}pts), "
                f"expected at most LB"
            )

    def test_lp_upgrade_to_pathogenic_works(self):
        """From LP, verify upgrade suggestions reach Pathogenic."""
        base_codes = parse_codes(["PVS1"])
        result = advise(base_codes)
        p_change = next(u for u in result.upgrades if u.target_tier == Classification.PATHOGENIC)

        for combo in p_change.possible_additions:
            all_codes = base_codes + combo
            new_result = classify(all_codes)
            assert new_result.classification == Classification.PATHOGENIC

    def test_lp_downgrade_to_vus_works(self):
        """From LP, verify downgrade suggestions reach VUS."""
        base_codes = parse_codes(["PVS1"])
        result = advise(base_codes)
        vus_change = next(d for d in result.downgrades if d.target_tier == Classification.VUS)

        for combo in vus_change.possible_additions:
            all_codes = base_codes + combo
            new_result = classify(all_codes)
            assert new_result.classification <= Classification.VUS


# ============================================================
# Excluded codes tests
# ============================================================

class TestExcludedCodes:
    """Verify suggestions don't include already-applied codes."""

    def test_no_duplicate_suggestions(self):
        result = advise_from_names(["PVS1", "PM1"])
        for change in result.upgrades + result.downgrades:
            for combo in change.possible_additions:
                combo_codes = {c.code for c in combo}
                assert "PVS1" not in combo_codes
                assert "PM1" not in combo_codes


# ============================================================
# Format output tests
# ============================================================

class TestFormatAdvice:
    def test_format_includes_classification(self):
        result = advise_from_names(["PM2", "PP3"])
        text = format_advice(result)
        assert "VUS" in text
        assert "PM2" in text
        assert "PP3" in text

    def test_format_includes_upgrades(self):
        result = advise_from_names(["PM2", "PP3"])
        text = format_advice(result)
        assert "UPGRADES" in text
        assert "Likely Pathogenic" in text

    def test_format_includes_downgrades(self):
        result = advise_from_names(["PM2", "PP3"])
        text = format_advice(result)
        assert "DOWNGRADES" in text
        assert "Likely Benign" in text

    def test_format_pathogenic_no_upgrades(self):
        result = advise_from_names(["PVS1", "PS1"])
        text = format_advice(result)
        assert "UPGRADES" not in text

    def test_format_benign_no_downgrades(self):
        result = advise_from_names(["BA1"])
        text = format_advice(result)
        assert "DOWNGRADES" not in text


# ============================================================
# Min points helper tests
# ============================================================

class TestMinPointsForTier:
    def test_pathogenic_threshold(self):
        assert _min_points_for_tier(Classification.PATHOGENIC) == 10

    def test_lp_threshold(self):
        assert _min_points_for_tier(Classification.LIKELY_PATHOGENIC) == 6

    def test_vus_threshold(self):
        assert _min_points_for_tier(Classification.VUS) == 0

    def test_lb_threshold(self):
        assert _min_points_for_tier(Classification.LIKELY_BENIGN) == -6

    def test_benign_threshold(self):
        assert _min_points_for_tier(Classification.BENIGN) == -7


class TestMaxPointsForTier:
    def test_pathogenic_max(self):
        assert _max_points_for_tier(Classification.PATHOGENIC) == 999

    def test_lp_max(self):
        assert _max_points_for_tier(Classification.LIKELY_PATHOGENIC) == 9

    def test_vus_max(self):
        assert _max_points_for_tier(Classification.VUS) == 5

    def test_lb_max(self):
        assert _max_points_for_tier(Classification.LIKELY_BENIGN) == -1

    def test_benign_max(self):
        assert _max_points_for_tier(Classification.BENIGN) == -7


class TestMaxCodesParameter:
    """Test that max_codes parameter is respected."""

    def test_max_codes_1_limits_suggestions(self):
        result = advise_from_names(["PM2", "PP3"], max_codes=1)
        for change in result.upgrades:
            for combo in change.possible_additions:
                assert len(combo) <= 1

    def test_max_codes_2(self):
        result = advise_from_names(["PM2", "PP3"], max_codes=2)
        for change in result.upgrades:
            for combo in change.possible_additions:
                assert len(combo) <= 2


class TestFormatAdviceMaxCodes:
    """Test that format_advice uses the correct max_codes in messages."""

    def test_format_uses_custom_max_codes(self):
        result = advise_from_names(["PM2", "PP3"], max_codes=2)
        text = format_advice(result, max_codes=2)
        # Should not say "up to 4" when max_codes is 2
        assert "up to 4" not in text
