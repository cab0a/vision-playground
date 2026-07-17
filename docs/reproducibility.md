# Reproducibility

## Scope

The reproducibility target is the numeric output of the five registered core experiments. The committed comparison images support visual review, but binary image encoding can vary across OpenCV builds and is not part of the strict checksum contract.

## Environment

Python 3.10 or later is required. CI installs the project and runs tests on Python 3.10, 3.11, 3.12, 3.13, and 3.14.

Create an isolated development environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install ".[dev]"
```

On Debian or Ubuntu, install the distribution-provided `python3-venv` package first if `ensurepip` is unavailable.

The dependency declarations use compatible lower bounds rather than a permanent lock. For an archival run, record the resolved environment:

```bash
python --version
python -m pip freeze > environment.txt
```

An exact result change after a dependency update requires review; it should not be silently accepted as equivalent.

## Core Reproduction

Run and verify the core suite:

```bash
vision-playground run all
vision-playground verify
python -m pytest
```

Expected summaries:

```text
Completed experiments: 5
Evaluations: 165
Summary: results/experiment_summary.csv
```

```text
Verified files: 6
Manifest: results/reproducibility_manifest.csv
```

`vision-playground verify` checks the SHA-256 digest and byte length of:

- `thresholding_metrics.csv`
- `adaptive_sensitivity_metrics.csv`
- `denoising_metrics.csv`
- `edge_detection_metrics.csv`
- `labeled_public_dataset/labeled_dataset_metrics.csv`
- `experiment_summary.csv`

The committed [manifest](../results/reproducibility_manifest.csv) contains relative paths only.

## Deterministic Controls

| Component | Control |
| --- | --- |
| Thresholding scenarios | NumPy generator seed `7` |
| Adaptive sensitivity | NumPy generator seed `7` and fixed parameter grid |
| Denoising | NumPy generator seed `17` |
| Edge detection | NumPy generator seed `17`, fixed Canny thresholds, and fixed tolerance |
| Labeled evaluation | Fixed six-image subset, SHA-256 data manifest, and per-image OpenCV RNG seed |
| CSV serialization | Fixed column order, decimal formatting, UTF-8, and LF line endings |

## Data Provenance

The labeled Oxford-IIIT Pet subset is committed with a [data manifest and attribution](../data/oxford_pet_sample/README.md). The loader verifies every image and trimap before evaluation.

The optional photograph examples use checksum-verified sample files from scikit-image. They require network access on first use and are not part of `vision-playground run all`.

No private, customer, employer, or manually collected data is required.

## Updating the Reference Manifest

The manifest is a reviewed baseline, not an output that should be refreshed automatically. After an intentional algorithm, parameter, or dependency change:

```bash
vision-playground run all
python experiments/create_reproducibility_manifest.py
vision-playground verify
python -m pytest
```

Review the metrics diff and the visual artifacts before committing the new manifest.

## Known Boundaries

- Cross-platform image files may not be byte-identical even when their decoded pixels are equivalent.
- Floating-point and OpenCV implementation changes can alter numeric results; the manifest intentionally makes such changes visible.
- Network sample availability is outside the repository's control.
- Reproduction of the committed reference values does not establish external validity on another dataset or task.
