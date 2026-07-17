"""Compare adaptive configurations on freely reusable photographs."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from run_public_image_sample import download_samples
from vision_playground.adaptive_sample import evaluate_adaptive_samples


def build_parser() -> argparse.ArgumentParser:
    """Create the adaptive public-sample parser."""
    parser = argparse.ArgumentParser(
        description="Compare adaptive parameters on freely reusable photographs."
    )
    parser.add_argument(
        "--images",
        type=Path,
        default=Path("results/adaptive_public_sample/images"),
        help="Directory used to cache downloaded images.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/adaptive_public_sample"),
        help="Directory for the summary CSV and comparison image.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Download images and generate adaptive comparison artifacts."""
    args = build_parser().parse_args(argv)
    image_paths = download_samples(args.images)
    records = evaluate_adaptive_samples(image_paths, output_dir=args.output)

    print(f"Images: {len(image_paths)}")
    print(f"Configurations: {len({record.configuration for record in records})}")
    print(f"Evaluations: {len(records)}")
    print(f"Summary: {args.output / 'adaptive_parameter_summary.csv'}")
    print(f"Comparison: {args.output / 'adaptive_parameter_comparison.jpg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
