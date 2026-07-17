"""Run input inspection before the public thresholding experiment."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from run_public_image_sample import download_samples

try:
    from vision_playground.workflow import run_inspected_workflow
except ModuleNotFoundError as error:
    if error.name == "image_dataset_inspector":
        raise SystemExit(
            'Install the workflow dependencies with: python -m pip install ".[workflow]"'
        ) from error
    raise


def build_parser() -> argparse.ArgumentParser:
    """Create the inspected public-sample parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Inspect public sample images before running thresholding experiments."
        )
    )
    parser.add_argument(
        "--images",
        type=Path,
        default=Path("results/inspected_public_sample/images"),
        help="Directory used to cache downloaded images.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/inspected_public_sample"),
        help="Directory for inspection and experiment artifacts.",
    )
    parser.add_argument(
        "--fixed-threshold",
        type=int,
        default=127,
        help="Threshold used by the fixed global method.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Download, inspect, evaluate, and summarize the public images."""
    args = build_parser().parse_args(argv)
    download_samples(args.images)
    inspections, workflow_records = run_inspected_workflow(
        args.images,
        args.output,
        fixed_threshold=args.fixed_threshold,
    )

    valid_count = sum(result.status == "valid" for result in inspections)
    unreadable_count = len(inspections) - valid_count
    print(f"Inspected: {len(inspections)}")
    print(f"Valid: {valid_count}")
    print(f"Unreadable: {unreadable_count}")
    print(f"Evaluated: {len(workflow_records)}")
    print(f"Input report: {args.output / 'input_inspection.csv'}")
    print(f"Workflow summary: {args.output / 'workflow_summary.csv'}")
    print(f"Comparison: {args.output / 'thresholding_comparison.jpg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
