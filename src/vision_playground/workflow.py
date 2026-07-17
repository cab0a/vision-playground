"""Input inspection and qualitative vision experiment orchestration."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

from image_dataset_inspector.inspector import InspectionResult, inspect_directory
from image_dataset_inspector.reporting import write_csv_report

from vision_playground.real_images import RealImageRecord, evaluate_real_images

WORKFLOW_COLUMNS = (
    "relative_path",
    "file_size_bytes",
    "width",
    "height",
    "channels",
    "brightness",
    "contrast",
    "blur_score",
    "fixed_threshold",
    "fixed_foreground_fraction",
    "otsu_threshold",
    "otsu_foreground_fraction",
    "foreground_fraction_delta",
)


@dataclass(frozen=True, slots=True)
class WorkflowRecord:
    """Combined inspection and thresholding data for one valid image."""

    relative_path: str
    file_size_bytes: int
    width: int
    height: int
    channels: int
    brightness: float
    contrast: float
    blur_score: float
    fixed_threshold: float
    fixed_foreground_fraction: float
    otsu_threshold: float
    otsu_foreground_fraction: float
    foreground_fraction_delta: float


def _require_inspection_metrics(
    result: InspectionResult,
) -> tuple[int, int, int, int, float, float, float]:
    if (
        result.file_size_bytes is None
        or result.width is None
        or result.height is None
        or result.channels is None
        or result.brightness is None
        or result.contrast is None
        or result.blur_score is None
    ):
        raise ValueError(
            f"Valid inspection record has missing metrics: {result.relative_path}"
        )
    return (
        result.file_size_bytes,
        result.width,
        result.height,
        result.channels,
        result.brightness,
        result.contrast,
        result.blur_score,
    )


def _index_threshold_records(
    records: list[RealImageRecord],
) -> dict[str, dict[str, RealImageRecord]]:
    indexed: dict[str, dict[str, RealImageRecord]] = {}
    for record in records:
        methods = indexed.setdefault(record.filename, {})
        if record.method in methods:
            raise ValueError(
                f"Duplicate thresholding method for image: {record.filename}"
            )
        methods[record.method] = record
    return indexed


def create_workflow_records(
    inspections: list[InspectionResult],
    threshold_records: list[RealImageRecord],
) -> list[WorkflowRecord]:
    """Combine valid input metrics with fixed and Otsu thresholding results."""
    valid_names = [
        Path(result.relative_path).name
        for result in inspections
        if result.status == "valid"
    ]
    if len(valid_names) != len(set(valid_names)):
        raise ValueError("Valid images must have unique filenames for this workflow.")

    indexed = _index_threshold_records(threshold_records)
    workflow_records: list[WorkflowRecord] = []

    for inspection in inspections:
        if inspection.status != "valid":
            continue

        filename = Path(inspection.relative_path).name
        methods = indexed.get(filename, {})
        if set(methods) != {"fixed", "otsu"}:
            raise ValueError(
                f"Expected fixed and Otsu results for image: {inspection.relative_path}"
            )

        (
            file_size,
            width,
            height,
            channels,
            brightness,
            contrast,
            blur_score,
        ) = _require_inspection_metrics(inspection)
        fixed = methods["fixed"]
        otsu = methods["otsu"]
        workflow_records.append(
            WorkflowRecord(
                relative_path=inspection.relative_path,
                file_size_bytes=file_size,
                width=width,
                height=height,
                channels=channels,
                brightness=brightness,
                contrast=contrast,
                blur_score=blur_score,
                fixed_threshold=fixed.threshold,
                fixed_foreground_fraction=fixed.foreground_fraction,
                otsu_threshold=otsu.threshold,
                otsu_foreground_fraction=otsu.foreground_fraction,
                foreground_fraction_delta=abs(
                    otsu.foreground_fraction - fixed.foreground_fraction
                ),
            )
        )
    return workflow_records


def write_workflow_summary(
    records: list[WorkflowRecord],
    output_path: Path,
) -> None:
    """Write the combined workflow records to CSV."""
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=WORKFLOW_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        for record in records:
            row = asdict(record)
            for name in (
                "brightness",
                "contrast",
                "blur_score",
                "fixed_threshold",
                "fixed_foreground_fraction",
                "otsu_threshold",
                "otsu_foreground_fraction",
                "foreground_fraction_delta",
            ):
                row[name] = f"{getattr(record, name):.6f}"
            writer.writerow(row)


def run_inspected_workflow(
    images_dir: Path,
    output_dir: Path,
    fixed_threshold: int = 127,
) -> tuple[list[InspectionResult], list[WorkflowRecord]]:
    """Inspect inputs, evaluate valid images, and write traceable artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    inspections = inspect_directory(images_dir)
    write_csv_report(inspections, output_dir / "input_inspection.csv")

    valid_paths = [
        images_dir / result.relative_path
        for result in inspections
        if result.status == "valid"
    ]
    if not valid_paths:
        raise ValueError("The workflow requires at least one valid image.")

    threshold_records = evaluate_real_images(
        valid_paths,
        output_dir,
        fixed_threshold=fixed_threshold,
    )
    workflow_records = create_workflow_records(inspections, threshold_records)
    write_workflow_summary(
        workflow_records,
        output_dir / "workflow_summary.csv",
    )
    return inspections, workflow_records
