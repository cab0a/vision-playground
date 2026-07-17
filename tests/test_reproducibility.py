"""Tests for deterministic result manifests."""

from pathlib import Path

import pytest

from vision_playground.reproducibility import (
    create_reproducibility_manifest,
    verify_reproducibility_manifest,
)


def test_create_and_verify_manifest(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    (results_dir / "metrics.csv").write_text(
        "method,iou\nexample,0.750000\n",
        encoding="utf-8",
    )
    manifest_path = results_dir / "reproducibility_manifest.csv"

    entries = create_reproducibility_manifest(
        results_dir,
        manifest_path,
        relative_paths=["metrics.csv"],
    )
    verified = verify_reproducibility_manifest(results_dir, manifest_path)

    assert verified == entries


def test_verification_detects_modified_result(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    result_path = results_dir / "metrics.csv"
    result_path.write_text("metric,value\nIoU,0.75\n", encoding="utf-8")
    manifest_path = results_dir / "reproducibility_manifest.csv"
    create_reproducibility_manifest(
        results_dir,
        manifest_path,
        relative_paths=["metrics.csv"],
    )

    result_path.write_text("metric,value\nIoU,0.76\n", encoding="utf-8")

    with pytest.raises(ValueError, match="metrics.csv"):
        verify_reproducibility_manifest(results_dir, manifest_path)
