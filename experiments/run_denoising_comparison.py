"""Run the controlled denoising comparison experiment."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from vision_playground.denoising import run_denoising_experiment


def build_parser() -> argparse.ArgumentParser:
    """Create the denoising experiment command-line parser."""
    parser = argparse.ArgumentParser(
        description="Compare denoising methods before Otsu thresholding."
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
        default=17,
        help="Seed used to generate deterministic image noise.",
    )
    parser.add_argument(
        "--kernel-size",
        type=int,
        default=5,
        help="Odd Gaussian and median filter kernel size.",
    )
    parser.add_argument(
        "--gaussian-std",
        type=float,
        default=45.0,
        help="Standard deviation of the synthetic Gaussian noise.",
    )
    parser.add_argument(
        "--salt-pepper-fraction",
        type=float,
        default=0.15,
        help="Fraction of pixels replaced by salt-and-pepper noise.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the denoising experiment and print artifact locations."""
    args = build_parser().parse_args(argv)
    records = run_denoising_experiment(
        output_dir=args.output,
        seed=args.seed,
        kernel_size=args.kernel_size,
        gaussian_standard_deviation=args.gaussian_std,
        salt_and_pepper_fraction=args.salt_pepper_fraction,
    )

    print(f"Noise conditions: {len({record.noise_type for record in records})}")
    print(
        "Denoising methods: "
        f"{len({record.denoising_method for record in records})}"
    )
    print(f"Evaluations: {len(records)}")
    print(f"Metrics: {args.output / 'denoising_metrics.csv'}")
    print(f"Comparison: {args.output / 'denoising_comparison.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
