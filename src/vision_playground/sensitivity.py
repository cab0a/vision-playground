"""Adaptive-threshold parameter sensitivity experiments."""

from __future__ import annotations

import csv
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from vision_playground.evaluation import calculate_binary_metrics
from vision_playground.synthetic import generate_scenarios
from vision_playground.thresholding import apply_adaptive_threshold

DEFAULT_BLOCK_SIZES = (31, 63, 95, 127, 159, 191)
DEFAULT_C_VALUES = (-15.0, -10.0, -5.0, 0.0, 5.0)
CSV_COLUMNS = (
    "scenario",
    "block_size",
    "constant_c",
    "iou",
    "precision",
    "recall",
    "f1",
)


@dataclass(frozen=True, slots=True)
class AdaptiveSensitivityRecord:
    """Metrics for one adaptive configuration and synthetic scenario."""

    scenario: str
    block_size: int
    constant_c: float
    iou: float
    precision: float
    recall: float
    f1: float


def _validate_grid(
    block_sizes: Sequence[int],
    c_values: Sequence[float],
) -> None:
    if not block_sizes or not c_values:
        raise ValueError("The parameter grid must contain block sizes and C values.")
    if len(set(block_sizes)) != len(block_sizes):
        raise ValueError("Adaptive block sizes must be unique.")
    if len(set(c_values)) != len(c_values):
        raise ValueError("Adaptive C values must be unique.")


def _write_metrics(
    records: list[AdaptiveSensitivityRecord],
    output_path: Path,
) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=CSV_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        for record in records:
            row = asdict(record)
            row["constant_c"] = f"{record.constant_c:.2f}"
            for name in ("iou", "precision", "recall", "f1"):
                row[name] = f"{getattr(record, name):.6f}"
            writer.writerow(row)


def _heatmap_color(value: float) -> tuple[int, int, int]:
    color = cv2.applyColorMap(
        np.array([[round(255 * value)]], dtype=np.uint8),
        cv2.COLORMAP_VIRIDIS,
    )[0, 0]
    return int(color[0]), int(color[1]), int(color[2])


def _create_heatmap_panel(
    scenario_name: str,
    values: dict[tuple[int, float], float],
    block_sizes: Sequence[int],
    c_values: Sequence[float],
) -> np.ndarray:
    cell_width = 78
    cell_height = 50
    left_margin = 88
    top_margin = 58
    right_margin = 18
    bottom_margin = 52
    panel = np.full(
        (
            top_margin + cell_height * len(c_values) + bottom_margin,
            left_margin + cell_width * len(block_sizes) + right_margin,
            3,
        ),
        245,
        dtype=np.uint8,
    )

    title = scenario_name.replace("_", " ")
    cv2.putText(
        panel,
        f"{title} - IoU",
        (12, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (30, 30, 30),
        1,
        cv2.LINE_AA,
    )

    for row_index, constant_c in enumerate(c_values):
        y_start = top_margin + row_index * cell_height
        cv2.putText(
            panel,
            f"C={constant_c:g}",
            (12, y_start + 31),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.44,
            (40, 40, 40),
            1,
            cv2.LINE_AA,
        )
        for column_index, block_size in enumerate(block_sizes):
            value = values[(block_size, float(constant_c))]
            x_start = left_margin + column_index * cell_width
            color = _heatmap_color(value)
            cv2.rectangle(
                panel,
                (x_start, y_start),
                (x_start + cell_width - 2, y_start + cell_height - 2),
                color,
                thickness=-1,
            )
            text_color = (255, 255, 255) if value < 0.58 else (20, 20, 20)
            cv2.putText(
                panel,
                f"{value:.3f}",
                (x_start + 12, y_start + 31),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.42,
                text_color,
                1,
                cv2.LINE_AA,
            )

    label_y = top_margin + cell_height * len(c_values) + 25
    for column_index, block_size in enumerate(block_sizes):
        x_start = left_margin + column_index * cell_width
        cv2.putText(
            panel,
            str(block_size),
            (x_start + 23, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (40, 40, 40),
            1,
            cv2.LINE_AA,
        )
    cv2.putText(
        panel,
        "block size",
        (
            left_margin + cell_width * len(block_sizes) // 2 - 38,
            label_y + 21,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        (40, 40, 40),
        1,
        cv2.LINE_AA,
    )
    return panel


def _write_heatmap(
    records: list[AdaptiveSensitivityRecord],
    block_sizes: Sequence[int],
    c_values: Sequence[float],
    output_path: Path,
) -> None:
    scenario_names = list(dict.fromkeys(record.scenario for record in records))
    panels: list[np.ndarray] = []
    for scenario_name in scenario_names:
        values = {
            (record.block_size, record.constant_c): record.iou
            for record in records
            if record.scenario == scenario_name
        }
        panels.append(
            _create_heatmap_panel(
                scenario_name,
                values,
                block_sizes,
                c_values,
            )
        )

    if len(panels) != 4:
        raise ValueError("The sensitivity heatmap expects four synthetic scenarios.")
    heatmap = cv2.vconcat(
        [
            cv2.hconcat(panels[:2]),
            cv2.hconcat(panels[2:]),
        ]
    )
    if not cv2.imwrite(str(output_path), heatmap):
        raise OSError(f"Could not write sensitivity heatmap: {output_path}")


def run_adaptive_sensitivity(
    output_dir: Path,
    seed: int = 7,
    block_sizes: Sequence[int] = DEFAULT_BLOCK_SIZES,
    c_values: Sequence[float] = DEFAULT_C_VALUES,
) -> list[AdaptiveSensitivityRecord]:
    """Evaluate an adaptive parameter grid and write CSV and heatmap artifacts."""
    _validate_grid(block_sizes, c_values)
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[AdaptiveSensitivityRecord] = []

    for scenario in generate_scenarios(seed=seed):
        for block_size in block_sizes:
            for constant_c in c_values:
                result = apply_adaptive_threshold(
                    scenario.image,
                    block_size=block_size,
                    constant_c=constant_c,
                )
                metrics = calculate_binary_metrics(
                    result.mask,
                    scenario.ground_truth,
                )
                records.append(
                    AdaptiveSensitivityRecord(
                        scenario=scenario.name,
                        block_size=block_size,
                        constant_c=float(constant_c),
                        iou=metrics.iou,
                        precision=metrics.precision,
                        recall=metrics.recall,
                        f1=metrics.f1,
                    )
                )

    _write_metrics(records, output_dir / "adaptive_sensitivity_metrics.csv")
    _write_heatmap(
        records,
        block_sizes,
        c_values,
        output_dir / "adaptive_sensitivity_heatmap.png",
    )
    return records
