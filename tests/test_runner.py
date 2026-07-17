"""Tests for unified experiment execution and summaries."""

import csv
from pathlib import Path

import pytest

from vision_playground.runner import (
    EXPERIMENTS,
    ExperimentOutcome,
    get_experiment,
    run_experiment,
    write_experiment_summary,
)


def test_registry_has_unique_stable_identifiers() -> None:
    identifiers = [definition.experiment_id for definition in EXPERIMENTS]

    assert len(identifiers) == len(set(identifiers))
    assert identifiers == [
        "thresholding",
        "adaptive-sensitivity",
        "denoising",
        "edge-detection",
        "labeled-dataset",
    ]
    with pytest.raises(ValueError, match="Unknown experiment"):
        get_experiment("unknown")


def test_run_experiment_uses_common_output_root(tmp_path: Path) -> None:
    outcome = run_experiment(
        "thresholding",
        tmp_path,
        Path("data/oxford_pet_sample"),
    )

    assert outcome.experiment == "thresholding"
    assert outcome.evaluations == 12
    assert (tmp_path / outcome.metrics_path).is_file()
    assert (tmp_path / outcome.visual_artifact).is_file()


def test_write_experiment_summary(tmp_path: Path) -> None:
    outcome = ExperimentOutcome(
        experiment="example",
        question="What does this example measure?",
        evaluations=3,
        summary_metric="IoU",
        reference_value=0.75,
        evidence_scope="one controlled condition",
        metrics_path="metrics.csv",
        visual_artifact="comparison.png",
    )
    output_path = tmp_path / "experiment_summary.csv"

    write_experiment_summary([outcome], output_path)

    with output_path.open(encoding="utf-8", newline="") as input_file:
        rows = list(csv.DictReader(input_file))
    assert rows == [
        {
            "experiment": "example",
            "question": "What does this example measure?",
            "evaluations": "3",
            "summary_metric": "IoU",
            "reference_value": "0.750000",
            "evidence_scope": "one controlled condition",
            "metrics_path": "metrics.csv",
            "visual_artifact": "comparison.png",
        }
    ]
