"""Run segmentation baselines on the labeled Oxford Pet subset."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from vision_playground.labeled_dataset import run_labeled_dataset_experiment


def build_parser() -> argparse.ArgumentParser:
    """Create the labeled dataset experiment parser."""
    parser = argparse.ArgumentParser(
        description="Evaluate segmentation baselines on labeled public data."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/oxford_pet_sample"),
        help="Directory containing images, trimaps, and manifest.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/labeled_public_dataset"),
        help="Directory for the metrics CSV and comparison image.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the labeled evaluation and print artifact locations."""
    args = build_parser().parse_args(argv)
    records = run_labeled_dataset_experiment(args.data, args.output)
    print(f"Images: {len({record.filename for record in records})}")
    print(f"Methods: {len({record.method for record in records})}")
    print(f"Evaluations: {len(records)}")
    print(f"Metrics: {args.output / 'labeled_dataset_metrics.csv'}")
    print(f"Comparison: {args.output / 'labeled_dataset_comparison.jpg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
