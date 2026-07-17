# Changelog

All notable project changes are documented in this file.

## [1.0.0]

### Added

- A concise review guide mapping research, implementation, evaluation, failure analysis, and reproducibility evidence.
- `vision-playground --version`.
- Package metadata and CLI version consistency tests.
- Repository, issue tracker, and changelog URLs in package metadata.

### Changed

- Declared the documented CLI, Python APIs, experiment identifiers, dataclasses, and manifest schema stable.
- Reworked the README opening and project status for an evidence-led portfolio review.
- Added installed-command checks to every supported Python CI job.

## [0.9.0]

### Added

- Documentation for experiment design, result interpretation, the public API, and reproducibility.
- A SHA-256 manifest for six deterministic numeric result artifacts.
- `vision-playground verify` and a reviewed manifest maintenance script.
- Tests for manifest creation, verification, and modified-result detection.

### Changed

- Defined the supported CLI and Python API surface ahead of v1.0.
- Added strict numeric-result verification to the Python 3.12 CI job.

## [0.8.0]

### Added

- A unified `vision-playground` command with stable experiment identifiers.
- One-command reproduction of five experiments and 165 evaluations.
- An evidence-oriented cross-experiment summary and result index.

## [0.7.0]

### Added

- Quantitative evaluation on six checksum-verified Oxford-IIIT Pet image-trimap pairs.
- Brighter-foreground Otsu, darker-foreground Otsu, and fixed-inset GrabCut baselines.
- Per-image metrics, a comparison artifact, attribution, and dataset limitations.

## [0.6.0]

### Added

- Canny edge detection under controlled Gaussian and salt-and-pepper noise.
- Tolerance-aware edge precision, recall, and F1.
- A public-photograph stability sample.

## [0.5.0]

### Added

- Gaussian and median denoising before Otsu thresholding.
- Controlled noise evaluation and a public-photograph stability sample.

## [0.4.0]

### Added

- Adaptive-threshold parameter-grid evaluation.
- Scenario-level sensitivity metrics and an IoU heatmap.

## [0.3.0]

### Added

- Adaptive-threshold comparison on freely reusable public photographs.
- Parameter-focused qualitative outputs and interpretation.

## [0.2.0]

### Added

- An inspected public-image workflow integrating Image Dataset Inspector.
- Joined input-quality and thresholding diagnostics.

## [0.1.1]

### Added

- Checksum-verified public photograph samples with attribution.
- Qualitative fixed and Otsu thresholding comparisons.

## [0.1.0]

### Added

- Deterministic synthetic thresholding scenarios.
- Fixed, Otsu, and adaptive thresholding implementations.
- Pixel-level metrics, comparison artifacts, tests, and CI.
