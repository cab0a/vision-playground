"""Tests for the labeled public dataset evaluation."""

from pathlib import Path

import cv2

from vision_playground.labeled_dataset import (
    evaluate_labeled_pairs,
    load_oxford_pet_sample,
    verify_sample_manifest,
)

DATA_DIR = Path("data/oxford_pet_sample")


def test_oxford_pet_sample_manifest_and_pairs() -> None:
    verify_sample_manifest(DATA_DIR)
    pairs = load_oxford_pet_sample(DATA_DIR)

    assert len(pairs) == 6
    assert all(pair.image.shape[:2] == pair.trimap.shape for pair in pairs)


def test_labeled_evaluation_writes_artifacts_and_metrics(
    tmp_path: Path,
) -> None:
    pair = load_oxford_pet_sample(DATA_DIR)[0]
    records = evaluate_labeled_pairs([pair], tmp_path)

    assert len(records) == 3
    assert {record.method for record in records} == {
        "otsu_bright",
        "otsu_dark",
        "grabcut",
    }
    assert (tmp_path / "labeled_dataset_metrics.csv").is_file()
    comparison_path = tmp_path / "labeled_dataset_comparison.jpg"
    assert comparison_path.is_file()
    assert cv2.imread(str(comparison_path)) is not None
    grabcut = next(record for record in records if record.method == "grabcut")
    assert grabcut.iou > 0.5
