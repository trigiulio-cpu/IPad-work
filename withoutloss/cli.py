"""
Command-line interface for Without Loss paper generator.

Usage:
    python -m withoutloss generate --paper paper.pdf --critique critique.txt
    python -m withoutloss generate --paper paper.pdf --critique critique.txt --model claude-opus-4-6
    python -m withoutloss generate --paper paper.pdf --critique critique.txt --output my_paper --pages 7
    python -m withoutloss generate --paper paper.pdf --critique critique.txt --bib refs.bib --compile
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .engine import generate_paper


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="withoutloss",
        description="Without Loss — generate a formal theory paper from a source paper and your critique",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- generate ---
    gen = subparsers.add_parser(
        "generate",
        help="Generate a paper from a source paper + critique",
    )
    gen.add_argument(
        "--paper",
        type=Path,
        required=True,
        help="Path to the original paper (.txt, .tex, .md, or .pdf)",
    )
    gen.add_argument(
        "--critique",
        type=Path,
        required=True,
        help="Path to your critique of the paper (.txt, .tex, .md, or .pdf)",
    )
    gen.add_argument(
        "--model",
        type=str,
        default=None,
        help="Anthropic model ID (default: claude-sonnet-4-6)",
    )
    gen.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file base name (without .tex extension)",
    )
    gen.add_argument(
        "--pages",
        type=int,
        default=6,
        help="Target page count (default: 6)",
    )
    gen.add_argument(
        "--instructions",
        type=str,
        default="",
        help="Additional instructions for the model (optional)",
    )
    gen.add_argument(
        "--bib",
        type=Path,
        default=None,
        help="Path to a .bib file to include for bibliography",
    )
    gen.add_argument(
        "--compile",
        action="store_true",
        default=False,
        help="Compile the .tex output to PDF (requires pdflatex)",
    )

    args = parser.parse_args(argv)

    if args.command == "generate":
        _cmd_generate(args)
    else:
        parser.print_help()
        sys.exit(1)


def _cmd_generate(args: argparse.Namespace) -> None:
    for path, label in [(args.paper, "paper"), (args.critique, "critique")]:
        if not path.exists():
            print(f"Error: {label} file not found: {path}", file=sys.stderr)
            sys.exit(1)

    out = generate_paper(
        paper_path=args.paper,
        critique_path=args.critique,
        model=args.model,
        output_name=args.output,
        page_target=args.pages,
        additional_instructions=args.instructions,
        bib_path=args.bib,
        compile=args.compile,
    )
    print(f"Done. Output: {out}")
