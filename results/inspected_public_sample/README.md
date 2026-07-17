# Inspected Public Sample Workflow

## Objective

This workflow connects two independently usable repositories into one traceable sequence:

`Input Inspection → Thresholding Prototype → Qualitative Evaluation → Interpretation`

[Image Dataset Inspector](https://github.com/cab0a/image-dataset-inspector) first verifies that each input can be decoded and records dimensions, channels, brightness, contrast, and Laplacian variance. Vision Playground then evaluates only the valid images with the existing fixed and Otsu global thresholding methods.

## Reproduction

From the Vision Playground repository:

```bash
python -m pip install ".[workflow]"
python experiments/run_inspected_public_sample.py
```

The `workflow` dependency is pinned to the public `image-dataset-inspector` `v0.1.2` tag.

Expected summary:

```text
Inspected: 5
Valid: 5
Unreadable: 0
Evaluated: 5
Input report: results/inspected_public_sample/input_inspection.csv
Workflow summary: results/inspected_public_sample/workflow_summary.csv
Comparison: results/inspected_public_sample/thresholding_comparison.jpg
```

## Artifacts

- `input_inspection.csv`: complete input audit, including status and decode failures
- `thresholding_summary.csv`: one row per image and thresholding method
- `workflow_summary.csv`: inspection metrics and both method outputs joined by image
- `thresholding_comparison.jpg`: grayscale inputs and the resulting binary masks

## Combined Results

| Image | Brightness | Contrast | Blur score | Fixed foreground | Otsu foreground | Difference |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `camera.png` | 129.1 | 73.6 | 1133.2 | 64.30% | 67.90% | 3.60 pp |
| `clock_motion.png` | 146.3 | 20.9 | 24.3 | 87.95% | 6.49% | 81.46 pp |
| `coffee.png` | 103.7 | 58.1 | 1541.2 | 33.10% | 48.53% | 15.43 pp |
| `hubble_deep_field.jpg` | 19.4 | 26.2 | 537.2 | 1.85% | 3.22% | 1.37 pp |
| `rocket.jpg` | 61.0 | 30.6 | 820.9 | 3.32% | 24.59% | 21.27 pp |

## Interpretation

The clock image has the highest mean brightness but the lowest contrast and Laplacian variance in this sample. It also produces the largest difference between the two thresholding methods. The fixed threshold selects most of its bright, smooth background, while Otsu selects a much higher threshold and retains a smaller region.

The rocket image produces the second-largest foreground difference. Its low mean brightness causes the fixed threshold to retain very little of the scene, while Otsu lowers the threshold and selects additional sky and structural regions. The camera image has a broad intensity distribution and changes relatively little between the two methods.

Joining the stages makes these relationships easier to investigate, but it does not establish causation or segmentation accuracy. The images have no semantic ground-truth masks, and brightness, contrast, blur score, and foreground fraction are descriptive diagnostics. A task-specific conclusion would require labeled data and quantitative error analysis.

## Data Provenance

The five source images are CC0 or public-domain files distributed with scikit-image. Downloads are pinned to scikit-image `v0.26.0` and verified with SHA-256. Raw downloads are ignored by Git; only the reproducible workflow, derived artifacts, and attribution are committed.

See the [public image sample documentation](../public_sample/README.md) for image-level sources and licensing details.
