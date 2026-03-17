#!/usr/bin/env python3
"""
CLI interface for the ACMG/AMP Variant Classification Advisor.

Usage:
    python -m src.cli PM2 PP3 PP5
    python -m src.cli --interactive
    python -m src.cli --list-codes
"""

import argparse
import sys

from .evidence_codes import ALL_CODES, EvidenceDirection
from .classifier import classify_from_names
from .advisor import advise_from_names, format_advice


def list_codes():
    """Print all available evidence codes."""
    print("\n=== Pathogenic Evidence Codes ===\n")
    print(f"  {'Code':<6} {'Strength':<14} {'Points':>6}  Description")
    print(f"  {'─'*6} {'─'*14} {'─'*6}  {'─'*60}")
    for code in ALL_CODES.values():
        if code.direction == EvidenceDirection.PATHOGENIC:
            print(f"  {code.code:<6} {code.strength.value:<14} {code.points:>+6}  {code.description}")

    print("\n=== Benign Evidence Codes ===\n")
    print(f"  {'Code':<6} {'Strength':<14} {'Points':>6}  Description")
    print(f"  {'─'*6} {'─'*14} {'─'*6}  {'─'*60}")
    for code in ALL_CODES.values():
        if code.direction == EvidenceDirection.BENIGN:
            print(f"  {code.code:<6} {code.strength.value:<14} {code.points:>+6}  {code.description}")
    print()


def run_interactive():
    """Run interactive mode where users can enter codes repeatedly."""
    print("ACMG/AMP Variant Classification Advisor (Bayesian Point System)")
    print("Type evidence codes separated by spaces, or 'quit' to exit.")
    print("Type 'list' to see all available codes.\n")

    while True:
        try:
            user_input = input("Enter evidence codes> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if user_input.lower() == "list":
            list_codes()
            continue

        code_names = user_input.split()
        try:
            result = advise_from_names(code_names)
            print()
            print(format_advice(result))
            print()
        except ValueError as e:
            print(f"Error: {e}\n")


def main():
    parser = argparse.ArgumentParser(
        description="ACMG/AMP Variant Classification Advisor (Bayesian Point System)",
        epilog="Example: python -m src.cli PM2 PP3 PP5",
    )
    parser.add_argument(
        "codes",
        nargs="*",
        help="Evidence codes to evaluate (e.g., PVS1 PM2 PP3)",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode",
    )
    parser.add_argument(
        "--list-codes", "-l",
        action="store_true",
        help="List all available evidence codes",
    )
    parser.add_argument(
        "--classify-only", "-c",
        action="store_true",
        help="Only show classification, skip upgrade/downgrade advice",
    )
    parser.add_argument(
        "--max-codes", "-m",
        type=int,
        default=4,
        help="Maximum number of additional codes per suggestion (default: 4)",
    )

    args = parser.parse_args()

    if args.list_codes:
        list_codes()
        return

    if args.interactive:
        run_interactive()
        return

    if not args.codes:
        parser.print_help()
        sys.exit(1)

    try:
        if args.classify_only:
            result = classify_from_names(args.codes)
            print(result.summary())
        else:
            result = advise_from_names(args.codes, max_codes=args.max_codes)
            print(format_advice(result))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
