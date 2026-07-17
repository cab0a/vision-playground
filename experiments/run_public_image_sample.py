"""Download freely reusable photographs and compare global thresholds."""

from __future__ import annotations

import argparse
import hashlib
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from vision_playground.real_images import evaluate_real_images


@dataclass(frozen=True, slots=True)
class PublicSample:
    """Metadata for one pinned, freely reusable sample image."""

    filename: str
    url: str
    sha256: str


BASE_URL = (
    "https://raw.githubusercontent.com/scikit-image/scikit-image/"
    "v0.26.0/src/skimage/data"
)
SAMPLES = (
    PublicSample(
        "camera.png",
        f"{BASE_URL}/camera.png",
        "b0793d2adda0fa6ae899c03989482bff9a42d3d5690fc7e3648f2795d730c23a",
    ),
    PublicSample(
        "coffee.png",
        f"{BASE_URL}/coffee.png",
        "cc02f8ca188b167c775a7101b5d767d1e71792cf762c33d6fa15a4599b5a8de7",
    ),
    PublicSample(
        "clock_motion.png",
        f"{BASE_URL}/clock_motion.png",
        "f029226b28b642e80113d86622e9b215ee067a0966feaf5e60604a1e05733955",
    ),
    PublicSample(
        "rocket.jpg",
        f"{BASE_URL}/rocket.jpg",
        "c2dd0de7c538df8d111e479619b129464d0269d0ae5fd18ca91d33a7fdfea95c",
    ),
    PublicSample(
        "hubble_deep_field.jpg",
        f"{BASE_URL}/hubble_deep_field.jpg",
        "3a19c5dd8a927a9334bb1229a6d63711b1c0c767fb27e2286e7c84a3e2c2f5f4",
    ),
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_samples(images_dir: Path) -> list[Path]:
    """Download all pinned sample images and verify their SHA-256 hashes."""
    images_dir.mkdir(parents=True, exist_ok=True)
    image_paths: list[Path] = []
    for sample in SAMPLES:
        destination = images_dir / sample.filename
        if not (
            destination.is_file()
            and _sha256(destination.read_bytes()) == sample.sha256
        ):
            request = urllib.request.Request(
                sample.url,
                headers={"User-Agent": "vision-playground-public-sample"},
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
            if _sha256(data) != sample.sha256:
                raise ValueError(
                    f"Checksum verification failed for {sample.filename}."
                )
            destination.write_bytes(data)
        image_paths.append(destination)
    return image_paths


def build_parser() -> argparse.ArgumentParser:
    """Create the public-image experiment parser."""
    parser = argparse.ArgumentParser(
        description="Compare global thresholds on freely reusable photographs."
    )
    parser.add_argument(
        "--images",
        type=Path,
        default=Path("results/public_sample/images"),
        help="Directory used to cache downloaded images.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/public_sample"),
        help="Directory for the summary CSV and comparison image.",
    )
    parser.add_argument(
        "--fixed-threshold",
        type=int,
        default=127,
        help="Threshold used by the fixed global method.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Download the images and generate qualitative comparison artifacts."""
    args = build_parser().parse_args(argv)
    image_paths = download_samples(args.images)
    records = evaluate_real_images(
        image_paths,
        output_dir=args.output,
        fixed_threshold=args.fixed_threshold,
    )

    print(f"Images: {len(image_paths)}")
    print(f"Evaluations: {len(records)}")
    print(f"Summary: {args.output / 'thresholding_summary.csv'}")
    print(f"Comparison: {args.output / 'thresholding_comparison.jpg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
