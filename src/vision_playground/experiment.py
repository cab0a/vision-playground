"""Experiment orchestration and artifact generation."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from vision_playground.evaluation import calculate_binary_metrics
from vision_playground.synthetic import generate_scenarios
from vision_playground.thresholding import (
    apply_fixed_threshold,
    apply_otsu_threshold,
)

CSV_COLUMNS = (
    "scenario",
    "method",
    "threshold",
    "iou",
    "precision",
    "recall",
    "f1",
)


@dataclass(frozen=True, slots=True)
class ExperimentRecord:
    """One method evaluation for one synthetic scenario."""

    scenario: str
    method: str
    threshold: float
    iou: float
    precision: float
    recall: float
    f1: float


def _create_record(
    scenario_name: str,
    method: str,
    threshold: float,
    predicted: np.ndarray,
    ground_truth: np.ndarray,
) -> ExperimentRecord:
    metrics = calculate_binary_metrics(predicted, ground_truth)
    return ExperimentRecord(
        scenario=scenario_name,
        method=method,
        threshold=threshold,
        iou=metrics.iou,
        precision=metrics.precision,
        recall=metrics.recall,
        f1=metrics.f1,
    )


def _label_panel(image: np.ndarray, label: str) -> np.ndarray:
    color_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    panel = cv2.copyMakeBorder(
        color_image,
        34,
        0,
        0,
        0,
        cv2.BORDER_CONSTANT,
        value=(30, 30, 30),
    )
    cv2.putText(
        panel,
        label,
        (8, 23),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    return panel


def _write_metrics(records: list[ExperimentRecord], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=CSV_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        for record in records:
            row = asdict(record)
            row["threshold"] = f"{record.threshold:.2f}"
            for name in ("iou", "precision", "recall", "f1"):
                row[name] = f"{getattr(record, name):.6f}"
            writer.writerow(row)


def run_thresholding_experiment(
    output_dir: Path,
    seed: int = 7,
    fixed_threshold: int = 127,
) -> list[ExperimentRecord]:
    """Run all synthetic scenarios and write reproducible artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[ExperimentRecord] = []
    comparison_rows: list[np.ndarray] = []

    for scenario in generate_scenarios(seed=seed):
        fixed_result = apply_fixed_threshold(
            scenario.image,
            threshold=fixed_threshold,
        )
        otsu_result = apply_otsu_threshold(scenario.image)

        records.extend(
            [
                _create_record(
                    scenario.name,
                    fixed_result.method,
                    fixed_result.threshold,
                    fixed_result.mask,
                    scenario.ground_truth,
                ),
                _create_record(
                    scenario.name,
                    otsu_result.method,
                    otsu_result.threshold,
                    otsu_result.mask,
                    scenario.ground_truth,
                ),
            ]
        )

        comparison_rows.append(
            cv2.hconcat(
                [
                    _label_panel(scenario.image, f"{scenario.name}: input"),
                    _label_panel(scenario.ground_truth, "ground truth"),
                    _label_panel(
                        fixed_result.mask,
                        f"fixed: T={fixed_result.threshold:.0f}",
                    ),
                    _label_panel(
                        otsu_result.mask,
                        f"Otsu: T={otsu_result.threshold:.0f}",
                    ),
                ]
            )
        )

    _write_metrics(records, output_dir / "thresholding_metrics.csv")
    comparison = cv2.vconcat(comparison_rows)
    comparison_path = output_dir / "thresholding_comparison.png"
    if not cv2.imwrite(str(comparison_path), comparison):
        raise OSError(f"Could not write comparison image: {comparison_path}")
    return records
