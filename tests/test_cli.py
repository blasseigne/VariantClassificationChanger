"""Tests for the CLI interface."""

import pytest
from unittest.mock import patch
from io import StringIO

from src.variant_classifier.cli import main, list_codes, run_interactive


class TestMainClassify:
    """Test CLI classification output."""

    def test_classify_only(self, capsys):
        with patch("sys.argv", ["prog", "--classify-only", "PVS1", "PS1"]):
            main()
        output = capsys.readouterr().out
        assert "Pathogenic" in output
        assert "12" in output

    def test_classify_vus(self, capsys):
        with patch("sys.argv", ["prog", "--classify-only", "PM2", "PP3"]):
            main()
        output = capsys.readouterr().out
        assert "VUS" in output

    def test_advise_mode(self, capsys):
        with patch("sys.argv", ["prog", "PM2", "PP3"]):
            main()
        output = capsys.readouterr().out
        assert "UPGRADES" in output
        assert "DOWNGRADES" in output
        assert "Likely Pathogenic" in output

    def test_advise_with_max_codes(self, capsys):
        with patch("sys.argv", ["prog", "--max-codes", "1", "PM2", "PP3"]):
            main()
        output = capsys.readouterr().out
        assert "UPGRADES" in output


class TestMainErrorHandling:
    """Test CLI error paths."""

    def test_no_codes_prints_help(self, capsys):
        with patch("sys.argv", ["prog"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_invalid_code_exits(self, capsys):
        with patch("sys.argv", ["prog", "FAKE_CODE"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
        output = capsys.readouterr().err
        assert "Unknown evidence code" in output

    def test_duplicate_code_exits(self, capsys):
        with patch("sys.argv", ["prog", "PVS1", "PVS1"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
        output = capsys.readouterr().err
        assert "Duplicate" in output

    def test_max_codes_too_low(self, capsys):
        with patch("sys.argv", ["prog", "--max-codes", "0", "PM2"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_max_codes_too_high(self, capsys):
        with patch("sys.argv", ["prog", "--max-codes", "99", "PM2"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1


class TestListCodes:
    """Test --list-codes output."""

    def test_list_codes_output(self, capsys):
        list_codes()
        output = capsys.readouterr().out
        assert "PVS1" in output
        assert "BA1" in output
        assert "Pathogenic Evidence Codes" in output
        assert "Benign Evidence Codes" in output

    def test_list_codes_via_main(self, capsys):
        with patch("sys.argv", ["prog", "--list-codes"]):
            main()
        output = capsys.readouterr().out
        assert "PVS1" in output


class TestInteractiveMode:
    """Test interactive mode."""

    def test_interactive_quit(self, capsys):
        with patch("builtins.input", return_value="quit"):
            run_interactive()
        output = capsys.readouterr().out
        assert "Goodbye!" in output

    def test_interactive_exit(self, capsys):
        with patch("builtins.input", return_value="exit"):
            run_interactive()
        output = capsys.readouterr().out
        assert "Goodbye!" in output

    def test_interactive_classify(self, capsys):
        inputs = iter(["PM2 PP3", "quit"])
        with patch("builtins.input", side_effect=inputs):
            run_interactive()
        output = capsys.readouterr().out
        assert "VUS" in output

    def test_interactive_list(self, capsys):
        inputs = iter(["list", "quit"])
        with patch("builtins.input", side_effect=inputs):
            run_interactive()
        output = capsys.readouterr().out
        assert "PVS1" in output

    def test_interactive_invalid_code(self, capsys):
        inputs = iter(["FAKE", "quit"])
        with patch("builtins.input", side_effect=inputs):
            run_interactive()
        output = capsys.readouterr().out
        assert "Error" in output

    def test_interactive_empty_input(self, capsys):
        inputs = iter(["", "quit"])
        with patch("builtins.input", side_effect=inputs):
            run_interactive()
        output = capsys.readouterr().out
        assert "Goodbye!" in output

    def test_interactive_eof(self, capsys):
        with patch("builtins.input", side_effect=EOFError):
            run_interactive()
        output = capsys.readouterr().out
        assert "Goodbye!" in output

    def test_interactive_keyboard_interrupt(self, capsys):
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            run_interactive()
        output = capsys.readouterr().out
        assert "Goodbye!" in output

    def test_interactive_respects_max_codes(self, capsys):
        inputs = iter(["PM2 PP3", "quit"])
        with patch("builtins.input", side_effect=inputs):
            run_interactive(max_codes=1)
        output = capsys.readouterr().out
        assert "VUS" in output
