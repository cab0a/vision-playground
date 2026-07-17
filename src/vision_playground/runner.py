"""Unified experiment registry, execution, and summary generation."""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from vision_playground.denoising import run_denoising_experiment
from vision_playground.edge_detection import run_edge_experiment
from vision_playground.experiment import run_thresholding_experiment
from vision_playground.labeled_dataset import run_labeled_dataset_experiment
from vision_playground.sensitivity import run_adaptive_sensitivity

SUMMARY_COLUMNS = (
    "experiment",
    "question",
    "evaluations",
    "summary_metric",
    "reference_value",
    "evidence_scope",
    "metrics_path",
    "visual_artifact",
)


@dataclass(frozen=True, slots=True)
class ExperimentDefinition:
    """Stable metadata for one reproducible experiment."""

    experiment_id: str
    title: str
    question: str


@dataclass(frozen=True, slots=True)
class ExperimentOutcome:
    """Common metadata, without treating unlike metrics as a ranking."""

    experiment: str
    question: str
    evaluations: int
    summary_metric: str
    reference_value: float
    evidence_scope: str
    metrics_path: str
    visual_artifact: str


EXPERIMENTS = (
    ExperimentDefinition(
        "thresholding",
        "Thresholding Comparison",
        "How do global and adaptive thresholds respond to controlled conditions?",
    ),
    ExperimentDefinition(
        "adaptive-sensitivity",
        "Adaptive Parameter Sensitivity",
        "How sensitive is adaptive thresholding to block size and C?",
    ),
    ExperimentDefinition(
        "denoising",
        "Denoising Before Thresholding",
        "Which simple filter best matches each controlled noise model?",
    ),
    ExperimentDefinition(
        "edge-detection",
        "Edge Detection Under Controlled Noise",
        "How does preprocessing affect Canny edges under controlled noise?",
    ),
    ExperimentDefinition(
        "labeled-dataset",
        "Labeled Public Dataset Evaluation",
        "How do simple segmentation baselines compare with public labels?",
    ),
)

_DEFINITIONS = {
    definition.experiment_id: definition for definition in EXPERIMENTS
}


def get_experiment(experiment_id: str) -> ExperimentDefinition:
    """Return one registered experiment or raise a clear error."""
    try:
        return _DEFINITIONS[experiment_id]
    except KeyError as error:
        available = ", ".join(_DEFINITIONS)
        raise ValueError(
            f"Unknown experiment '{experiment_id}'. Available: {available}"
        ) from error


def _outcome(
    experiment_id: str,
    evaluations: int,
    summary_metric: str,
    reference_value: float,
    evidence_scope: str,
    metrics_path: str,
    visual_artifact: str,
) -> ExperimentOutcome:
    definition = get_experiment(experiment_id)
    return ExperimentOutcome(
        experiment=definition.experiment_id,
        question=definition.question,
        evaluations=evaluations,
        summary_metric=summary_metric,
        reference_value=reference_value,
        evidence_scope=evidence_scope,
        metrics_path=metrics_path,
        visual_artifact=visual_artifact,
    )


def _run_thresholding(output_dir: Path) -> ExperimentOutcome:
    records = run_thresholding_experiment(output_dir)
    reference = next(
        record
        for record in records
        if record.scenario == "uneven_illumination"
        and record.method == "adaptive"
    )
    return _outcome(
        "thresholding",
        len(records),
        "IoU",
        reference.iou,
        "adaptive method on uneven_illumination",
        "thresholding_metrics.csv",
        "thresholding_comparison.png",
    )


def _run_adaptive_sensitivity(output_dir: Path) -> ExperimentOutcome:
    records = run_adaptive_sensitivity(output_dir)
    grouped_scores: dict[tuple[int, float], list[float]] = defaultdict(list)
    for record in records:
        grouped_scores[(record.block_size, record.constant_c)].append(record.iou)
    best_parameters, scores = max(
        grouped_scores.items(),
        key=lambda item: sum(item[1]) / len(item[1]),
    )
    block_size, constant_c = best_parameters
    return _outcome(
        "adaptive-sensitivity",
        len(records),
        "mean IoU",
        sum(scores) / len(scores),
        (
            "best tested shared configuration across four scenarios: "
            f"block={block_size}, C={constant_c:g}"
        ),
        "adaptive_sensitivity_metrics.csv",
        "adaptive_sensitivity_heatmap.png",
    )


def _run_denoising(output_dir: Path) -> ExperimentOutcome:
    records = run_denoising_experiment(output_dir)
    reference = next(
        record
        for record in records
        if record.noise_type == "salt_and_pepper"
        and record.denoising_method == "median"
    )
    return _outcome(
        "denoising",
        len(records),
        "IoU",
        reference.iou,
        "median filter under salt-and-pepper noise",
        "denoising_metrics.csv",
        "denoising_comparison.png",
    )


def _run_edge_detection(output_dir: Path) -> ExperimentOutcome:
    records = run_edge_experiment(output_dir)
    reference = next(
        record
        for record in records
        if record.condition == "salt_and_pepper"
        and record.denoising_method == "median"
    )
    return _outcome(
        "edge-detection",
        len(records),
        "F1",
        reference.f1,
        "median filter under salt-and-pepper noise",
        "edge_detection_metrics.csv",
        "edge_detection_comparison.png",
    )


def _run_labeled_dataset(
    output_dir: Path,
    data_dir: Path,
) -> ExperimentOutcome:
    labeled_output = output_dir / "labeled_public_dataset"
    records = run_labeled_dataset_experiment(data_dir, labeled_output)
    grabcut_scores = [
        record.iou for record in records if record.method == "grabcut"
    ]
    return _outcome(
        "labeled-dataset",
        len(records),
        "mean IoU",
        sum(grabcut_scores) / len(grabcut_scores),
        "fixed-inset GrabCut across the selected six-image subset",
        "labeled_public_dataset/labeled_dataset_metrics.csv",
        "labeled_public_dataset/labeled_dataset_comparison.jpg",
    )


def run_experiment(
    experiment_id: str,
    output_dir: Path,
    data_dir: Path,
) -> ExperimentOutcome:
    """Run one registered experiment with its documented default settings."""
    get_experiment(experiment_id)
    if experiment_id == "thresholding":
        return _run_thresholding(output_dir)
    if experiment_id == "adaptive-sensitivity":
        return _run_adaptive_sensitivity(output_dir)
    if experiment_id == "denoising":
        return _run_denoising(output_dir)
    if experiment_id == "edge-detection":
        return _run_edge_detection(output_dir)
    return _run_labeled_dataset(output_dir, data_dir)


def write_experiment_summary(
    outcomes: list[ExperimentOutcome],
    output_path: Path,
) -> None:
    """Write one evidence-oriented row per completed experiment."""
    if not outcomes:
        raise ValueError("At least one experiment outcome is required.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=SUMMARY_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        for outcome in outcomes:
            row = asdict(outcome)
            row["reference_value"] = f"{outcome.reference_value:.6f}"
            writer.writerow(row)


def run_all_experiments(
    output_dir: Path,
    data_dir: Path,
) -> list[ExperimentOutcome]:
    """Run every registered experiment and write a cross-experiment summary."""
    outcomes = [
        run_experiment(definition.experiment_id, output_dir, data_dir)
        for definition in EXPERIMENTS
    ]
    write_experiment_summary(
        outcomes,
        output_dir / "experiment_summary.csv",
    )
    return outcomes
