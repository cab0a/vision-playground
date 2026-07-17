"""Canny edge detection under controlled noise."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from vision_playground.denoising import (
    DENOISING_METHODS,
    DenoisingScenario,
    apply_denoising,
    create_clean_shape_image,
    generate_denoising_scenarios,
)
from vision_playground.real_images import label_panel

CSV_COLUMNS = (
    "condition",
    "denoising_method",
    "kernel_size",
    "low_threshold",
    "high_threshold",
    "tolerance_pixels",
    "edge_pixels",
    "precision",
    "recall",
    "f1",
)


@dataclass(frozen=True, slots=True)
class EdgeMetrics:
    """Tolerance-aware metrics for one predicted edge map."""

    precision: float
    recall: float
    f1: float


@dataclass(frozen=True, slots=True)
class EdgeRecord:
    """One edge detection evaluation under a controlled condition."""

    condition: str
    denoising_method: str
    kernel_size: int | None
    low_threshold: int
    high_threshold: int
    tolerance_pixels: int
    edge_pixels: int
    precision: float
    recall: float
    f1: float


def apply_canny(
    image: np.ndarray,
    low_threshold: int = 125,
    high_threshold: int = 250,
) -> np.ndarray:
    """Apply Canny edge detection to a uint8 grayscale image."""
    if image.ndim != 2 or image.dtype != np.uint8:
        raise ValueError("Canny edge detection requires a 2D uint8 image.")
    if not 0 <= low_threshold < high_threshold <= 255:
        raise ValueError(
            "Canny thresholds must satisfy 0 <= low < high <= 255."
        )
    return cv2.Canny(image, low_threshold, high_threshold)


def calculate_edge_metrics(
    predicted: np.ndarray,
    ground_truth: np.ndarray,
    tolerance_pixels: int = 2,
) -> EdgeMetrics:
    """Calculate edge precision and recall with positional tolerance."""
    if predicted.shape != ground_truth.shape:
        raise ValueError("Predicted and ground-truth edge maps must match.")
    if predicted.ndim != 2 or ground_truth.ndim != 2:
        raise ValueError("Edge metrics require two-dimensional maps.")
    if tolerance_pixels < 0:
        raise ValueError("Edge tolerance cannot be negative.")

    kernel_size = tolerance_pixels * 2 + 1
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (kernel_size, kernel_size),
    )
    predicted_edges = predicted != 0
    ground_truth_edges = ground_truth != 0
    predicted_count = int(np.count_nonzero(predicted_edges))
    ground_truth_count = int(np.count_nonzero(ground_truth_edges))

    dilated_ground_truth = cv2.dilate(ground_truth, kernel) != 0
    dilated_prediction = cv2.dilate(predicted, kernel) != 0
    matched_predictions = int(
        np.count_nonzero(predicted_edges & dilated_ground_truth)
    )
    matched_ground_truth = int(
        np.count_nonzero(ground_truth_edges & dilated_prediction)
    )

    precision = matched_predictions / predicted_count if predicted_count else 0.0
    recall = (
        matched_ground_truth / ground_truth_count if ground_truth_count else 0.0
    )
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    return EdgeMetrics(
        precision=float(precision),
        recall=float(recall),
        f1=float(f1),
    )


def _write_metrics(records: list[EdgeRecord], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=CSV_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        for record in records:
            row = asdict(record)
            row["kernel_size"] = (
                "" if record.kernel_size is None else record.kernel_size
            )
            for name in ("precision", "recall", "f1"):
                row[name] = f"{getattr(record, name):.6f}"
            writer.writerow(row)


def run_edge_experiment(
    output_dir: Path,
    seed: int = 17,
    kernel_size: int = 5,
    low_threshold: int = 125,
    high_threshold: int = 250,
    tolerance_pixels: int = 2,
    gaussian_standard_deviation: float = 45.0,
    salt_and_pepper_fraction: float = 0.15,
) -> list[EdgeRecord]:
    """Evaluate Canny edge detection under clean and noisy conditions."""
    output_dir.mkdir(parents=True, exist_ok=True)
    clean_image, ground_truth_mask = create_clean_shape_image()
    scenarios = (
        DenoisingScenario(
            "clean",
            clean_image,
            ground_truth_mask.copy(),
        ),
        *generate_denoising_scenarios(
            seed=seed,
            gaussian_standard_deviation=gaussian_standard_deviation,
            salt_and_pepper_fraction=salt_and_pepper_fraction,
        ),
    )
    ground_truth_edges = apply_canny(
        ground_truth_mask,
        low_threshold,
        high_threshold,
    )
    records: list[EdgeRecord] = []
    comparison_rows: list[np.ndarray] = []

    for scenario in scenarios:
        panels = [
            label_panel(scenario.image, f"{scenario.noise_type}: input"),
            label_panel(ground_truth_edges, "ground-truth edges"),
        ]
        for method in DENOISING_METHODS:
            filtered_image = apply_denoising(
                scenario.image,
                method,
                kernel_size=kernel_size,
            )
            edges = apply_canny(
                filtered_image,
                low_threshold,
                high_threshold,
            )
            metrics = calculate_edge_metrics(
                edges,
                ground_truth_edges,
                tolerance_pixels=tolerance_pixels,
            )
            records.append(
                EdgeRecord(
                    condition=scenario.noise_type,
                    denoising_method=method,
                    kernel_size=None if method == "none" else kernel_size,
                    low_threshold=low_threshold,
                    high_threshold=high_threshold,
                    tolerance_pixels=tolerance_pixels,
                    edge_pixels=int(np.count_nonzero(edges)),
                    precision=metrics.precision,
                    recall=metrics.recall,
                    f1=metrics.f1,
                )
            )
            panels.append(
                label_panel(
                    edges,
                    f"{method}: F1={metrics.f1:.3f}",
                )
            )
        comparison_rows.append(cv2.hconcat(panels))

    _write_metrics(records, output_dir / "edge_detection_metrics.csv")
    comparison_path = output_dir / "edge_detection_comparison.png"
    if not cv2.imwrite(str(comparison_path), cv2.vconcat(comparison_rows)):
        raise OSError(f"Could not write edge comparison: {comparison_path}")
    return records
