"""Run Canny edge stability checks on public photographs."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from run_public_image_sample import download_samples
from vision_playground.edge_sample import evaluate_edge_samples

SAMPLE_FILENAMES = {"camera.png", "coffee.png"}


def build_parser() -> argparse.ArgumentParser:
    """Create the public edge-sample parser."""
    parser = argparse.ArgumentParser(
        description="Check Canny edge stability on public photographs."
    )
    parser.add_argument(
        "--images",
        type=Path,
        default=Path("results/edge_public_sample/images"),
        help="Directory used to cache downloaded images.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/edge_public_sample"),
        help="Directory for the summary CSV and comparison image.",
    )
    parser.add_argument("--seed", type=int, default=41)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Download public images and generate edge sample artifacts."""
    args = build_parser().parse_args(argv)
    downloaded_paths = download_samples(args.images)
    image_paths = [
        path for path in downloaded_paths if path.name in SAMPLE_FILENAMES
    ]
    if len(image_paths) != len(SAMPLE_FILENAMES):
        raise ValueError("The expected edge sample images are unavailable.")
    records = evaluate_edge_samples(
        image_paths,
        output_dir=args.output,
        seed=args.seed,
    )
    print(f"Images: {len(image_paths)}")
    print(f"Noise conditions: {len({record.noise_type for record in records})}")
    print(
        "Denoising methods: "
        f"{len({record.denoising_method for record in records})}"
    )
    print(f"Evaluations: {len(records)}")
    print(f"Summary: {args.output / 'edge_detection_summary.csv'}")
    print(f"Comparison: {args.output / 'edge_detection_comparison.jpg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
