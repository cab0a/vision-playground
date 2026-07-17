"""Run the adaptive-threshold parameter sensitivity experiment."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from vision_playground.sensitivity import (
    DEFAULT_BLOCK_SIZES,
    DEFAULT_C_VALUES,
    run_adaptive_sensitivity,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the sensitivity experiment command-line parser."""
    parser = argparse.ArgumentParser(
        description="Evaluate adaptive thresholding over a parameter grid."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results"),
        help="Directory for the metrics CSV and heatmap.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=7,
        help="Seed used to generate deterministic image noise.",
    )
    parser.add_argument(
        "--block-sizes",
        type=int,
        nargs="+",
        default=DEFAULT_BLOCK_SIZES,
        help="Odd adaptive neighborhood sizes to evaluate.",
    )
    parser.add_argument(
        "--c-values",
        type=float,
        nargs="+",
        default=DEFAULT_C_VALUES,
        help="Constants subtracted from the adaptive neighborhood statistic.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the parameter grid and print its output locations."""
    args = build_parser().parse_args(argv)
    records = run_adaptive_sensitivity(
        output_dir=args.output,
        seed=args.seed,
        block_sizes=args.block_sizes,
        c_values=args.c_values,
    )
    scenario_count = len({record.scenario for record in records})
    configuration_count = len(args.block_sizes) * len(args.c_values)

    print(f"Scenarios: {scenario_count}")
    print(f"Configurations: {configuration_count}")
    print(f"Evaluations: {len(records)}")
    print(f"Metrics: {args.output / 'adaptive_sensitivity_metrics.csv'}")
    print(f"Heatmap: {args.output / 'adaptive_sensitivity_heatmap.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
