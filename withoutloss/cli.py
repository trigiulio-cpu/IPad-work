"""
Command-line interface for Without Loss paper generator.

Usage:
    python -m withoutloss generate configs/my_paper.json
    python -m withoutloss generate configs/my_paper.json --model claude-opus-4-6
    python -m withoutloss generate configs/my_paper.json --output my_paper
"""

import argparse
import json
import sys
from pathlib import Path

from .engine import generate_paper


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="withoutloss",
        description="Without Loss — automated economic theory paper generator",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- generate ---
    gen = subparsers.add_parser(
        "generate", help="Generate a paper from a config JSON file"
    )
    gen.add_argument(
        "config",
        type=Path,
        help="Path to a JSON config file specifying the paper",
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

    # --- validate ---
    val = subparsers.add_parser(
        "validate", help="Validate a config file without generating"
    )
    val.add_argument("config", type=Path)

    args = parser.parse_args(argv)

    if args.command == "generate":
        _cmd_generate(args)
    elif args.command == "validate":
        _cmd_validate(args)
    else:
        parser.print_help()
        sys.exit(1)


def _load_config(path: Path) -> dict:
    """Load and validate a paper config JSON file."""
    if not path.exists():
        print(f"Error: config file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        config = json.load(f)

    required = ["topic", "research_question", "conjecture", "model_primitives"]
    missing = [k for k in required if k not in config]
    if missing:
        print(
            f"Error: config missing required keys: {missing}",
            file=sys.stderr,
        )
        sys.exit(1)
    return config


def _cmd_generate(args: argparse.Namespace) -> None:
    config = _load_config(args.config)
    out = generate_paper(config, model=args.model, output_name=args.output)
    print(f"Done. Output: {out}")


def _cmd_validate(args: argparse.Namespace) -> None:
    config = _load_config(args.config)
    print(f"Config OK. Keys: {list(config.keys())}")
