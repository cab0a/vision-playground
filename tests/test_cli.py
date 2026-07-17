"""Tests for the unified command-line interface."""

from pathlib import Path

from vision_playground.cli import main
from vision_playground.reproducibility import (
    create_reproducibility_manifest,
)


def test_list_command_prints_registered_experiments(capsys) -> None:
    assert main(["list"]) == 0

    output = capsys.readouterr().out
    assert "thresholding:" in output
    assert "labeled-dataset:" in output


def test_run_command_writes_default_artifacts(
    tmp_path: Path,
    capsys,
) -> None:
    assert (
        main(
            [
                "run",
                "denoising",
                "--output",
                str(tmp_path),
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "Completed: denoising" in output
    assert "Evaluations: 6" in output
    assert (tmp_path / "denoising_metrics.csv").is_file()


def test_verify_command_checks_reference_manifest(
    tmp_path: Path,
    capsys,
) -> None:
    result_path = tmp_path / "metrics.csv"
    result_path.write_text("metric,value\nIoU,0.75\n", encoding="utf-8")
    manifest_path = tmp_path / "manifest.csv"
    create_reproducibility_manifest(
        tmp_path,
        manifest_path,
        relative_paths=["metrics.csv"],
    )

    assert (
        main(
            [
                "verify",
                "--results",
                str(tmp_path),
                "--manifest",
                str(manifest_path),
            ]
        )
        == 0
    )
    assert "Verified files: 1" in capsys.readouterr().out
