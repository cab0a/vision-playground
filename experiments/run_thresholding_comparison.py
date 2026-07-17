"""Run the synthetic thresholding comparison experiment."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from vision_playground.experiment import run_thresholding_experiment


def build_parser() -> argparse.ArgumentParser:
    """Create the experiment command-line parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Compare fixed, Otsu, and adaptive thresholding on synthetic images."
        )
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results"),
        help="Directory for the metrics CSV and comparison image.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=7,
        help="Seed used to generate deterministic image noise.",
    )
    parser.add_argument(
        "--fixed-threshold",
        type=int,
        default=127,
        help="Threshold used by the fixed global method.",
    )
    parser.add_argument(
        "--adaptive-block-size",
        type=int,
        default=127,
        help="Odd neighborhood size used by adaptive thresholding.",
    )
    parser.add_argument(
        "--adaptive-c",
        type=float,
        default=-10.0,
        help="Constant subtracted from the adaptive neighborhood statistic.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the experiment and print its output locations."""
    args = build_parser().parse_args(argv)
    records = run_thresholding_experiment(
        output_dir=args.output,
        seed=args.seed,
        fixed_threshold=args.fixed_threshold,
        adaptive_block_size=args.adaptive_block_size,
        adaptive_constant_c=args.adaptive_c,
    )
    scenario_count = len({record.scenario for record in records})

    print(f"Scenarios: {scenario_count}")
    print(f"Evaluations: {len(records)}")
    print(f"Metrics: {args.output / 'thresholding_metrics.csv'}")
    print(f"Comparison: {args.output / 'thresholding_comparison.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
