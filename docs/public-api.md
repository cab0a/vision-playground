# Public API

## Supported Surface

The supported interface consists of:

- the `vision-playground` command;
- experiment metadata and default runners in `vision_playground.runner`;
- checksum creation and verification in `vision_playground.reproducibility`;
- `vision_playground.__version__`.

Other modules remain importable for tests and detailed experiments, but their private helpers and dataclass layouts are not part of the compatibility commitment.

## Command-Line Interface

List registered experiments:

```bash
vision-playground list
```

Run one documented default configuration:

```bash
vision-playground run thresholding --output results
```

Valid identifiers are:

- `thresholding`
- `adaptive-sensitivity`
- `denoising`
- `edge-detection`
- `labeled-dataset`

Run all registered defaults:

```bash
vision-playground run all \
  --output results \
  --data data/oxford_pet_sample
```

Verify numeric reference artifacts:

```bash
vision-playground verify \
  --results results \
  --manifest results/reproducibility_manifest.csv
```

The `--data` argument is used by the labeled experiment. Existing standalone scripts remain available when non-default experiment parameters are required.

## Python Interface

Run one experiment:

```python
from pathlib import Path

from vision_playground.runner import run_experiment

outcome = run_experiment(
    experiment_id="thresholding",
    output_dir=Path("results"),
    data_dir=Path("data/oxford_pet_sample"),
)
print(outcome.metrics_path)
```

Discover registered experiments:

```python
from vision_playground.runner import EXPERIMENTS

for definition in EXPERIMENTS:
    print(definition.experiment_id, definition.question)
```

Run the suite and verify its numeric artifacts:

```python
from pathlib import Path

from vision_playground.reproducibility import (
    verify_reproducibility_manifest,
)
from vision_playground.runner import run_all_experiments

results_dir = Path("results")
run_all_experiments(
    output_dir=results_dir,
    data_dir=Path("data/oxford_pet_sample"),
)
verify_reproducibility_manifest(
    results_dir=results_dir,
    manifest_path=results_dir / "reproducibility_manifest.csv",
)
```

## Errors

The API raises standard exceptions rather than hiding failures:

- `ValueError` for an unknown experiment, invalid parameters, unexpected schemas, or checksum mismatches;
- `FileNotFoundError` for missing data or reference artifacts;
- `OSError` when OpenCV cannot write an artifact.

An unreadable optional public sample is handled by its experiment-specific workflow. Core runs fail early when required committed data is missing or modified.

## Compatibility

During the `0.x` series, documented interfaces may change when the review identifies a clearer design. Such changes are recorded in [CHANGELOG.md](../CHANGELOG.md).

The v1.0 compatibility commitment will cover the commands, identifiers, functions, dataclasses, and manifest schema listed in this document. Private names beginning with `_` are never part of that commitment.
