"""Tests for the unified command-line interface."""

from pathlib import Path

from vision_playground.cli import main


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
