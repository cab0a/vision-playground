"""Run Canny edge detection under controlled noise."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from vision_playground.edge_detection import run_edge_experiment


def build_parser() -> argparse.ArgumentParser:
    """Create the controlled edge experiment parser."""
    parser = argparse.ArgumentParser(
        description="Evaluate Canny edge detection under controlled noise."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results"),
        help="Directory for the metrics CSV and comparison image.",
    )
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--kernel-size", type=int, default=5)
    parser.add_argument("--low-threshold", type=int, default=125)
    parser.add_argument("--high-threshold", type=int, default=250)
    parser.add_argument("--tolerance-pixels", type=int, default=2)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the controlled edge experiment and print artifact locations."""
    args = build_parser().parse_args(argv)
    records = run_edge_experiment(
        output_dir=args.output,
        seed=args.seed,
        kernel_size=args.kernel_size,
        low_threshold=args.low_threshold,
        high_threshold=args.high_threshold,
        tolerance_pixels=args.tolerance_pixels,
    )
    print(f"Conditions: {len({record.condition for record in records})}")
    print(
        "Denoising methods: "
        f"{len({record.denoising_method for record in records})}"
    )
    print(f"Evaluations: {len(records)}")
    print(f"Metrics: {args.output / 'edge_detection_metrics.csv'}")
    print(f"Comparison: {args.output / 'edge_detection_comparison.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
