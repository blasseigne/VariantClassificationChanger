"""Tests for evidence code definitions and lookups."""

import pytest
from src.variant_classifier.evidence_codes import (
    ALL_CODES,
    PATHOGENIC_CODES,
    BENIGN_CODES,
    EvidenceDirection,
    EvidenceStrength,
    get_code,
    parse_codes,
)


class TestEvidenceCodeDefinitions:
    def test_total_code_count(self):
        """Should have exactly 28 ACMG/AMP evidence codes."""
        assert len(ALL_CODES) == 28

    def test_pathogenic_code_count(self):
        """16 pathogenic codes: 1 PVS + 4 PS + 6 PM + 5 PP."""
        assert len(PATHOGENIC_CODES) == 16

    def test_benign_code_count(self):
        """12 benign codes: 1 BA + 4 BS + 7 BP."""
        assert len(BENIGN_CODES) == 12

    def test_pvs1_points(self):
        code = ALL_CODES["PVS1"]
        assert code.points == 8
        assert code.strength == EvidenceStrength.VERY_STRONG
        assert code.direction == EvidenceDirection.PATHOGENIC

    def test_ps_codes_points(self):
        for name in ["PS1", "PS2", "PS3", "PS4"]:
            code = ALL_CODES[name]
            assert code.points == 4
            assert code.strength == EvidenceStrength.STRONG

    def test_pm_codes_points(self):
        for name in ["PM1", "PM2", "PM3", "PM4", "PM5", "PM6"]:
            code = ALL_CODES[name]
            assert code.points == 2
            assert code.strength == EvidenceStrength.MODERATE

    def test_pp_codes_points(self):
        for name in ["PP1", "PP2", "PP3", "PP4", "PP5"]:
            code = ALL_CODES[name]
            assert code.points == 1
            assert code.strength == EvidenceStrength.SUPPORTING

    def test_ba1_points(self):
        code = ALL_CODES["BA1"]
        assert code.points == -8
        assert code.strength == EvidenceStrength.STAND_ALONE
        assert code.direction == EvidenceDirection.BENIGN

    def test_bs_codes_points(self):
        for name in ["BS1", "BS2", "BS3", "BS4"]:
            code = ALL_CODES[name]
            assert code.points == -4
            assert code.strength == EvidenceStrength.STRONG

    def test_bp_codes_points(self):
        for name in ["BP1", "BP2", "BP3", "BP4", "BP5", "BP6", "BP7"]:
            code = ALL_CODES[name]
            assert code.points == -1
            assert code.strength == EvidenceStrength.SUPPORTING

    def test_all_codes_have_descriptions(self):
        for code in ALL_CODES.values():
            assert len(code.description) > 0


class TestGetCode:
    def test_valid_code(self):
        code = get_code("PVS1")
        assert code.code == "PVS1"

    def test_case_insensitive(self):
        code = get_code("pvs1")
        assert code.code == "PVS1"

    def test_with_whitespace(self):
        code = get_code("  PM2  ")
        assert code.code == "PM2"

    def test_invalid_code_raises(self):
        with pytest.raises(ValueError, match="Unknown evidence code"):
            get_code("INVALID")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            get_code("")


class TestParseCodes:
    def test_multiple_codes(self):
        codes = parse_codes(["PVS1", "PM2", "PP3"])
        assert len(codes) == 3
        assert codes[0].code == "PVS1"
        assert codes[1].code == "PM2"
        assert codes[2].code == "PP3"

    def test_empty_list(self):
        codes = parse_codes([])
        assert codes == []

    def test_invalid_in_list_raises(self):
        with pytest.raises(ValueError):
            parse_codes(["PVS1", "FAKE", "PM2"])

    def test_duplicate_codes_raises(self):
        """Each evidence code can only be applied once."""
        with pytest.raises(ValueError, match="Duplicate"):
            parse_codes(["PVS1", "PVS1"])

    def test_duplicate_codes_case_insensitive(self):
        """Duplicates detected regardless of case."""
        with pytest.raises(ValueError, match="Duplicate"):
            parse_codes(["pvs1", "PVS1"])


class TestGetCodeTypeValidation:
    def test_non_string_raises(self):
        with pytest.raises(ValueError, match="must be a string"):
            get_code(123)

    def test_none_raises(self):
        with pytest.raises(ValueError, match="must be a string"):
            get_code(None)


class TestNoOverlappingCodes:
    def test_no_code_in_both_directions(self):
        """No code should appear in both pathogenic and benign sets."""
        overlap = set(PATHOGENIC_CODES.keys()) & set(BENIGN_CODES.keys())
        assert len(overlap) == 0, f"Codes in both sets: {overlap}"
