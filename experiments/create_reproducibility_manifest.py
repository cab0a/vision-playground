"""Create the numeric reference-artifact checksum manifest."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from vision_playground.reproducibility import create_reproducibility_manifest


def build_parser() -> argparse.ArgumentParser:
    """Create the manifest maintenance parser."""
    parser = argparse.ArgumentParser(
        description="Create checksums for deterministic numeric artifacts."
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=Path("results"),
        help="Directory containing reproduced result files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path; defaults to RESULTS/reproducibility_manifest.csv.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Create the manifest and report its location."""
    args = build_parser().parse_args(argv)
    output_path = (
        args.output
        if args.output is not None
        else args.results / "reproducibility_manifest.csv"
    )
    entries = create_reproducibility_manifest(args.results, output_path)
    print(f"Reference files: {len(entries)}")
    print(f"Manifest: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
