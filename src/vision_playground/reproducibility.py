"""Checksums for deterministic numeric reference artifacts."""

from __future__ import annotations

import csv
import hashlib
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

__all__ = [
    "REFERENCE_RESULT_FILES",
    "ReproducibilityEntry",
    "create_reproducibility_manifest",
    "verify_reproducibility_manifest",
]

REFERENCE_RESULT_FILES = (
    "thresholding_metrics.csv",
    "adaptive_sensitivity_metrics.csv",
    "denoising_metrics.csv",
    "edge_detection_metrics.csv",
    "labeled_public_dataset/labeled_dataset_metrics.csv",
    "experiment_summary.csv",
)
MANIFEST_COLUMNS = ("relative_path", "sha256", "bytes")


@dataclass(frozen=True, slots=True)
class ReproducibilityEntry:
    """Expected identity of one deterministic numeric artifact."""

    relative_path: str
    sha256: str
    bytes: int


def _validate_relative_path(relative_path: str) -> Path:
    path = Path(relative_path)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(
            f"Manifest paths must remain under the results directory: "
            f"{relative_path}"
        )
    return path


def _create_entry(results_dir: Path, relative_path: str) -> ReproducibilityEntry:
    path = _validate_relative_path(relative_path)
    artifact_path = results_dir / path
    if not artifact_path.is_file():
        raise FileNotFoundError(f"Missing reference artifact: {artifact_path}")
    content = artifact_path.read_bytes()
    return ReproducibilityEntry(
        relative_path=path.as_posix(),
        sha256=hashlib.sha256(content).hexdigest(),
        bytes=len(content),
    )


def create_reproducibility_manifest(
    results_dir: Path,
    manifest_path: Path,
    relative_paths: Sequence[str] = REFERENCE_RESULT_FILES,
) -> list[ReproducibilityEntry]:
    """Create a deterministic manifest for selected numeric artifacts."""
    if not relative_paths:
        raise ValueError("At least one reference artifact is required.")
    if len(relative_paths) != len(set(relative_paths)):
        raise ValueError("Reference artifact paths must be unique.")

    entries = [
        _create_entry(results_dir, relative_path)
        for relative_path in relative_paths
    ]
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=MANIFEST_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(asdict(entry) for entry in entries)
    return entries


def verify_reproducibility_manifest(
    results_dir: Path,
    manifest_path: Path,
) -> list[ReproducibilityEntry]:
    """Verify selected result files against a committed SHA-256 manifest."""
    with manifest_path.open(encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file)
        if tuple(reader.fieldnames or ()) != MANIFEST_COLUMNS:
            raise ValueError("Unexpected reproducibility manifest schema.")
        rows = list(reader)
    if not rows:
        raise ValueError("The reproducibility manifest is empty.")

    relative_paths = [row["relative_path"] for row in rows]
    if len(relative_paths) != len(set(relative_paths)):
        raise ValueError("The reproducibility manifest contains duplicate paths.")

    verified: list[ReproducibilityEntry] = []
    for row in rows:
        actual = _create_entry(results_dir, row["relative_path"])
        try:
            expected_size = int(row["bytes"])
        except ValueError as error:
            raise ValueError(
                f"Invalid byte count for {row['relative_path']}."
            ) from error
        if actual.bytes != expected_size or actual.sha256 != row["sha256"]:
            raise ValueError(
                f"Reproducibility check failed for {row['relative_path']}."
            )
        verified.append(actual)
    return verified
