# Experiment Design

## 日本語概要

本書は、二値化、適応的二値化、ノイズ除去、輪郭検出、正解マスク付き画像分割について、研究課題、仮説、固定条件、評価指標、選択基準を定義します。合成画像と公開画像の役割を分け、変更した条件と固定した条件を追跡できる構成にしています。

各実験の方法と追加手順は以下の英語本文を参照してください。

---

## Workflow

Each core study follows the same sequence:

`Question → Hypothesis → Controlled Prototype → Quantitative Evaluation → Interpretation → Limitations`

An experiment is considered complete only when another reader can identify what changed, what remained fixed, which metric was used, and where the claim stops.

## Research Questions

The studies ask four related questions:

1. How do fixed, histogram-based, and locally adaptive thresholds behave when foreground contrast, noise, illumination, and adaptive parameters change?
2. Can simple preprocessing make Otsu thresholding more stable under Gaussian and salt-and-pepper noise, and does filter choice matter?
3. How does controlled noise affect Canny edge detection, and how much can simple denoising recover?
4. How do intensity-only and color-and-location segmentation baselines compare when human-labeled public masks are available?

## Hypotheses

- A fixed threshold should work when foreground and background intensities are stable.
- Otsu's method should adapt when the global intensity distribution shifts.
- Adaptive thresholding should improve separation under uneven illumination, but remain sensitive to neighborhood scale, noise, and low contrast.
- Gaussian and median filtering should both reduce thresholding errors under the tested noise. Gaussian filtering should be strongest for Gaussian noise, while median filtering should better suppress isolated salt-and-pepper pixels.
- Canny should produce many false edges without noise removal. Noise-matched preprocessing should improve precision while retaining the main boundaries.

## Core Experiments

| Identifier | Evaluations | Changed factor | Held constant | Primary evidence |
| --- | ---: | --- | --- | --- |
| `thresholding` | 12 | Thresholding method and image condition | Synthetic geometry and default seed | Pixel-level IoU, precision, recall, and F1 |
| `adaptive-sensitivity` | 120 | Adaptive block size and `C` | Scenarios, seed, and thresholding implementation | Per-configuration IoU and heatmap |
| `denoising` | 6 | Noise model and preprocessing filter | Ground truth, Otsu method, and kernel size | Pixel-level segmentation metrics |
| `edge-detection` | 9 | Noise model and preprocessing filter | Canny thresholds and positional tolerance | Tolerance-aware edge precision, recall, and F1 |
| `labeled-dataset` | 18 | Segmentation baseline | Six verified public image-label pairs | Per-image metrics against trimaps |

The default suite contains 165 method-condition evaluations. This count describes coverage within the controlled designs; it is not a claim of dataset scale.

## Thresholding Methods

The reference thresholding experiment compares three OpenCV implementations:

- **Fixed threshold:** `cv2.threshold` with a threshold of `127`
- **Otsu threshold:** `cv2.threshold` with `cv2.THRESH_OTSU`
- **Adaptive threshold:** `cv2.adaptiveThreshold` with a Gaussian-weighted neighborhood, block size `127`, and `C = -10`

Otsu's method selects one threshold from the image histogram. It removes the need to choose the value manually, but remains a global method.

The adaptive method calculates a threshold for each pixel from its neighborhood. The reference block size is intentionally larger than the main foreground structures in the 256 × 256 synthetic images. A negative `C` raises the local threshold by 10 intensity levels because OpenCV subtracts `C` from the weighted neighborhood value. This is one geometry-aware experimental configuration, not a universal default.

The sensitivity analysis evaluates 30 adaptive configurations: block sizes `31`, `63`, `95`, `127`, `159`, and `191`, crossed with `C` values `-15`, `-10`, `-5`, `0`, and `5`. The same deterministic scenarios and pixel-level metrics are used for every configuration.

## Denoising and Edge Methods

The denoising experiment fixes the downstream method to Otsu thresholding and changes only the preprocessing step: no filter, a 5 × 5 Gaussian filter, or a 5 × 5 median filter. It evaluates zero-mean Gaussian noise with standard deviation `45` and salt-and-pepper noise affecting `15%` of pixels.

The edge experiment applies Canny with thresholds `125` and `250` after the same preprocessing options. Predicted boundaries are evaluated with a two-pixel positional tolerance so minor rasterization shifts do not dominate the result.

## Labeled Segmentation Methods

The labeled public-data experiment evaluates brighter-foreground Otsu, darker-foreground Otsu, and fixed-inset GrabCut masks against Oxford-IIIT Pet trimaps. The labels are used only for evaluation, not during prediction.

## Synthetic Dataset

The generator creates one binary ground-truth mask containing multiple geometric shapes and renders four grayscale scenarios:

- `uniform_clean`: clearly separated foreground and background intensities
- `shifted_low_contrast`: a smaller intensity gap shifted above the fixed threshold
- `uneven_illumination`: a horizontal illumination gradient that causes class overlap
- `high_noise`: clearly separated classes with strong Gaussian noise

The random generator uses a fixed seed. No downloaded, private, or manually collected images are required for the synthetic experiments.

## Evaluation Methodology

Binary segmentation outputs are compared with known masks using:

- Intersection over Union (IoU)
- Precision
- Recall
- F1 score

The edge experiment uses precision, recall, and F1 with the documented positional tolerance. Every experiment records its method parameters and writes machine-readable metrics to CSV.

See the [result interpretation guide](result-interpretation.md) for definitions and cross-experiment comparison boundaries.

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

Reference parameters are fixed before result interpretation and are recorded in code and result tables. The adaptive sensitivity experiment explicitly reports the finite search grid. A best value within that grid is described as the best tested configuration, not a universal optimum.

## Optional Inspected Workflow

The optional workflow runs Image Dataset Inspector before the public thresholding sample. It records unreadable files and descriptive image metrics, excludes invalid inputs from the experiment, and joins inspection and thresholding outputs in one CSV.

This workflow demonstrates traceability between input audit and algorithm comparison. It does not make dataset inspection part of the core five-experiment suite.

## Adding an Experiment

New core experiments should provide:

1. an implementation module under `src/vision_playground/`;
2. deterministic input construction or checksum-verified public data;
3. a metrics CSV and visual artifact;
4. unit tests for calculation and artifact generation;
5. interpretation and limitations in the experiment documentation;
6. a registered default runner only after the standalone experiment is reproducible.

Public samples should include source URLs, license information, checksums where practical, and a clear distinction between qualitative and accuracy-based conclusions.
