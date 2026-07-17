"""Quantitative baselines on a labeled Oxford-IIIT Pet subset."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from vision_playground.evaluation import calculate_binary_metrics
from vision_playground.real_images import label_panel
from vision_playground.thresholding import apply_otsu_threshold

METHODS = ("otsu_bright", "otsu_dark", "grabcut")
CSV_COLUMNS = (
    "filename",
    "method",
    "iou",
    "precision",
    "recall",
    "f1",
    "foreground_fraction",
)


@dataclass(frozen=True, slots=True)
class OxfordPetPair:
    """One public image and its pixel-level trimap."""

    filename: str
    image: np.ndarray
    trimap: np.ndarray


@dataclass(frozen=True, slots=True)
class LabeledDatasetRecord:
    """One segmentation baseline evaluated against a labeled mask."""

    filename: str
    method: str
    iou: float
    precision: float
    recall: float
    f1: float
    foreground_fraction: float


def verify_sample_manifest(data_dir: Path) -> None:
    """Verify every file listed in the sample SHA-256 manifest."""
    manifest_path = data_dir / "manifest.csv"
    with manifest_path.open(encoding="utf-8", newline="") as manifest_file:
        rows = list(csv.DictReader(manifest_file))
    if not rows:
        raise ValueError("The Oxford Pet sample manifest is empty.")

    for row in rows:
        file_path = data_dir / row["relative_path"]
        if not file_path.is_file():
            raise FileNotFoundError(f"Missing Oxford Pet sample file: {file_path}")
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if digest != row["sha256"]:
            raise ValueError(f"Checksum mismatch for Oxford Pet file: {file_path}")


def load_oxford_pet_sample(
    data_dir: Path,
    verify_checksums: bool = True,
) -> list[OxfordPetPair]:
    """Load matching images and trimaps from the committed public subset."""
    if verify_checksums:
        verify_sample_manifest(data_dir)

    pairs: list[OxfordPetPair] = []
    image_paths = sorted((data_dir / "images").glob("*.jpg"))
    if not image_paths:
        raise ValueError("The Oxford Pet sample contains no images.")

    for image_path in image_paths:
        trimap_path = data_dir / "trimaps" / f"{image_path.stem}.png"
        image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        trimap = cv2.imread(str(trimap_path), cv2.IMREAD_GRAYSCALE)
        if image is None or trimap is None:
            raise OSError(f"Could not decode Oxford Pet pair: {image_path.stem}")
        if image.shape[:2] != trimap.shape:
            raise ValueError(f"Image and trimap shapes differ: {image_path.stem}")
        if not set(np.unique(trimap)).issubset({1, 2, 3}):
            raise ValueError(f"Unexpected trimap value: {trimap_path}")
        pairs.append(OxfordPetPair(image_path.name, image, trimap))
    return pairs


def trimap_to_pet_mask(trimap: np.ndarray) -> np.ndarray:
    """Convert foreground and boundary labels to one binary pet mask."""
    if trimap.ndim != 2 or not set(np.unique(trimap)).issubset({1, 2, 3}):
        raise ValueError("Expected a two-dimensional Oxford Pet trimap.")
    return np.where(trimap != 2, 255, 0).astype(np.uint8)


def create_segmentation_baselines(
    image: np.ndarray,
    grabcut_iterations: int = 5,
    inset_fraction: float = 0.05,
    seed: int = 0,
) -> dict[str, np.ndarray]:
    """Create label-free Otsu and fixed-inset GrabCut predictions."""
    if image.ndim != 3 or image.shape[2] != 3 or image.dtype != np.uint8:
        raise ValueError("Segmentation baselines require a BGR uint8 image.")
    if grabcut_iterations < 1:
        raise ValueError("GrabCut iterations must be positive.")
    if not 0 < inset_fraction < 0.5:
        raise ValueError("GrabCut inset fraction must be between 0 and 0.5.")

    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    otsu_bright = apply_otsu_threshold(grayscale).mask
    height, width = grayscale.shape
    inset = max(1, round(min(height, width) * inset_fraction))
    rectangle = (
        inset,
        inset,
        width - 2 * inset,
        height - 2 * inset,
    )
    grabcut_labels = np.zeros((height, width), dtype=np.uint8)
    background_model = np.zeros((1, 65), dtype=np.float64)
    foreground_model = np.zeros((1, 65), dtype=np.float64)
    cv2.setRNGSeed(seed)
    cv2.grabCut(
        image,
        grabcut_labels,
        rectangle,
        background_model,
        foreground_model,
        grabcut_iterations,
        cv2.GC_INIT_WITH_RECT,
    )
    grabcut_mask = np.where(
        (grabcut_labels == cv2.GC_FGD)
        | (grabcut_labels == cv2.GC_PR_FGD),
        255,
        0,
    ).astype(np.uint8)
    return {
        "otsu_bright": otsu_bright,
        "otsu_dark": cv2.bitwise_not(otsu_bright),
        "grabcut": grabcut_mask,
    }


def _write_metrics(
    records: list[LabeledDatasetRecord],
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
            for name in (
                "iou",
                "precision",
                "recall",
                "f1",
                "foreground_fraction",
            ):
                row[name] = f"{getattr(record, name):.6f}"
            writer.writerow(row)


def evaluate_labeled_pairs(
    pairs: list[OxfordPetPair],
    output_dir: Path,
) -> list[LabeledDatasetRecord]:
    """Evaluate segmentation baselines and write metrics and a montage."""
    if not pairs:
        raise ValueError("At least one labeled image pair is required.")
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[LabeledDatasetRecord] = []
    comparison_rows: list[np.ndarray] = []

    for pair_index, pair in enumerate(pairs):
        ground_truth = trimap_to_pet_mask(pair.trimap)
        predictions = create_segmentation_baselines(
            pair.image,
            seed=pair_index,
        )
        grayscale = cv2.cvtColor(pair.image, cv2.COLOR_BGR2GRAY)
        panels = [
            label_panel(grayscale, f"{pair.filename}: grayscale"),
            label_panel(ground_truth, "labeled pet mask"),
        ]
        for method in METHODS:
            prediction = predictions[method]
            metrics = calculate_binary_metrics(prediction, ground_truth)
            foreground_fraction = float(
                np.count_nonzero(prediction) / prediction.size
            )
            records.append(
                LabeledDatasetRecord(
                    filename=pair.filename,
                    method=method,
                    iou=metrics.iou,
                    precision=metrics.precision,
                    recall=metrics.recall,
                    f1=metrics.f1,
                    foreground_fraction=foreground_fraction,
                )
            )
            panels.append(
                label_panel(
                    prediction,
                    f"{method}: IoU={metrics.iou:.3f}",
                )
            )
        comparison_rows.append(cv2.hconcat(panels))

    _write_metrics(records, output_dir / "labeled_dataset_metrics.csv")
    comparison_path = output_dir / "labeled_dataset_comparison.jpg"
    if not cv2.imwrite(str(comparison_path), cv2.vconcat(comparison_rows)):
        raise OSError(f"Could not write labeled comparison: {comparison_path}")
    return records


def run_labeled_dataset_experiment(
    data_dir: Path,
    output_dir: Path,
) -> list[LabeledDatasetRecord]:
    """Load the verified subset and run the labeled evaluation."""
    pairs = load_oxford_pet_sample(data_dir)
    return evaluate_labeled_pairs(pairs, output_dir)
