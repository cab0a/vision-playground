# Experiment Design

## Workflow

Each core study follows the same sequence:

`Question → Hypothesis → Controlled Prototype → Quantitative Evaluation → Interpretation → Limitations`

The implementation is considered complete only when another reader can identify what changed, what remained fixed, which metric was used, and where the claim stops.

## Core Experiments

| Identifier | Changed factor | Held constant | Primary evidence |
| --- | --- | --- | --- |
| `thresholding` | Thresholding method and image condition | Synthetic geometry and default seed | Pixel-level IoU, precision, recall, and F1 |
| `adaptive-sensitivity` | Adaptive block size and `C` | Scenarios, seed, and thresholding implementation | Per-configuration IoU and heatmap |
| `denoising` | Noise model and preprocessing filter | Ground truth, Otsu method, and kernel size | Pixel-level segmentation metrics |
| `edge-detection` | Noise model and preprocessing filter | Canny thresholds and positional tolerance | Tolerance-aware edge precision, recall, and F1 |
| `labeled-dataset` | Segmentation baseline | Six verified public image-label pairs | Per-image metrics against trimaps |

The full default suite contains 165 method-condition evaluations. The count describes coverage within these controlled designs; it is not a claim of dataset scale.

## Selection Criteria

A core experiment must:

- ask one explicit technical question;
- use generated data or data with documented public provenance;
- avoid labels during prediction unless the method explicitly requires supervision;
- expose method parameters in code or command-line options;
- produce machine-readable metrics and a reviewable visual artifact;
- state assumptions, failure conditions, and metric limitations;
- run deterministically under the documented default configuration.

## Synthetic and Public Evidence

Synthetic images isolate variables and provide exact ground truth. They are useful for causal interpretation but cannot represent the full variation of photographs.

Public photographs add realistic texture and composition. Unlabeled samples are used only for qualitative behavior or stability checks. The labeled Oxford-IIIT Pet subset supports pixel-level accuracy metrics, but its six selected images are not a representative benchmark.

These evidence types complement one another:

1. controlled synthetic data reveals why a method changes;
2. unlabeled public data reveals whether the behavior appears in photographs;
3. labeled public data tests whether a narrow conclusion survives quantitative evaluation.

## Parameter Selection

Reference parameters are fixed before result interpretation and are recorded in code and README tables. The adaptive sensitivity experiment explicitly reports the finite search grid. A best value within that grid is described as the best tested configuration, not a universal optimum.

## Adding an Experiment

New core experiments should provide:

1. an implementation module under `src/vision_playground/`;
2. deterministic input construction or checksum-verified public data;
3. a metrics CSV and visual artifact;
4. unit tests for calculation and artifact generation;
5. an experiment-specific README section with interpretation and limitations;
6. a registered default runner only after the standalone experiment is reproducible.

Public samples should include source URLs, license information, checksums where practical, and a clear distinction between qualitative and accuracy-based conclusions.
