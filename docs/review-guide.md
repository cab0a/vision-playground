# Review Guide

This guide provides a short path through the repository for engineers, reviewers, and project stakeholders.

## Five-Minute Review

1. Read the [experiment design](experiment-design.md) to see how questions, controlled variables, metrics, and limitations are connected.
2. Open the [labeled public dataset report](../results/labeled_public_dataset/README.md) for a compact example of method selection, implementation, quantitative evaluation, and restrained interpretation.
3. Review [edge detection under controlled noise](../README.md#edge-detection-under-controlled-noise) for a synthetic experiment that isolates failure conditions.
4. Inspect the [cross-experiment result index](../results/README.md) to trace summary values to detailed CSV and visual artifacts.
5. Check the [reproducibility guide](reproducibility.md) and CI workflow to see how installation, tests, regeneration, and checksum verification are automated.

## Evidence Map

| Capability | Evidence |
| --- | --- |
| Technical investigation | Explicit research questions, hypotheses, references, and finite parameter studies |
| Python implementation | Installable `src` package, typed dataclasses, OpenCV and NumPy modules, and an argparse CLI |
| Method selection | Global, local, preprocessing, and color-and-location baselines compared under stated assumptions |
| Controlled evaluation | Deterministic synthetic ground truth, fixed seeds, parameter records, and quantitative metrics |
| Public-data evaluation | Checksum-verified Oxford-IIIT Pet subset with attribution and pixel-level labels |
| Failure analysis | Per-experiment limitations and examples where automatic methods do not improve the result |
| Reproducibility | One-command core suite, 31 tests, five-version CI, and SHA-256 result verification |
| Documentation | README narratives, result-specific reports, API boundaries, data provenance, and changelog |

## Representative Case Study

The labeled public-data experiment follows a compact research-to-evaluation workflow:

1. **Question:** How do simple label-free segmentation baselines compare with public pixel labels?
2. **Methods:** Two Otsu polarity assumptions and fixed-inset GrabCut.
3. **Data:** Six verified Oxford-IIIT Pet image-trimap pairs.
4. **Evaluation:** Per-image IoU, precision, recall, F1, and foreground fraction.
5. **Result:** GrabCut reaches 0.745 mean IoU on the selected subset and performs better than both intensity-only baselines on every selected image.
6. **Boundary:** The subset is deliberately small and cannot support a full-dataset performance claim.

The value of the example is the complete evidence chain, not the absolute score.

## Local Verification

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install ".[dev]"
vision-playground run all
vision-playground verify
python -m pytest
```

The commands reproduce 165 method-condition evaluations, verify six deterministic numeric artifacts, and run the test suite.

## Scope

This repository demonstrates small research and proof-of-concept workflows. It does not claim production-scale throughput, state-of-the-art model performance, or representative accuracy beyond the documented samples and conditions.
