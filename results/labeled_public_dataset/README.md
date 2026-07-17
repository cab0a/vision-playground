# Labeled Public Dataset Evaluation

## Question

How do simple, label-free segmentation baselines perform when evaluated against pixel-level annotations from a public dataset?

## Data

The experiment uses six image and trimap pairs from the Oxford-IIIT Pet Dataset: three cat images and three dog images. The committed subset, provenance, checksums, and licensing details are documented in the [data directory](../../data/oxford_pet_sample/README.md).

The subset is deliberately small enough to inspect visually and reproduce in continuous integration. It is not a representative benchmark of all 37 breeds or the full dataset.

## Methods

Three deliberately simple baselines are evaluated:

- `otsu_bright`: Otsu thresholding with brighter pixels treated as foreground
- `otsu_dark`: the inverse Otsu mask, with darker pixels treated as foreground
- `grabcut`: OpenCV GrabCut initialized with a rectangle inset by 5% from each image boundary

None of the methods receives the trimap during prediction. The labels are used only after prediction to calculate metrics. GrabCut uses five iterations and a fixed random seed for each image.

Trimap values `1` (pet) and `3` (boundary or uncertain region) are treated as foreground. Value `2` is treated as background.

## Reproduction

From an installed development environment:

```bash
python experiments/run_labeled_dataset_evaluation.py
```

Expected summary:

```text
Images: 6
Methods: 3
Evaluations: 18
Metrics: results/labeled_public_dataset/labeled_dataset_metrics.csv
Comparison: results/labeled_public_dataset/labeled_dataset_comparison.jpg
```

The loader verifies the SHA-256 manifest before decoding the images.

## Results

| Method | Mean IoU | Mean F1 |
| --- | ---: | ---: |
| `otsu_bright` | 0.300 | 0.438 |
| `otsu_dark` | 0.322 | 0.466 |
| `grabcut` | 0.745 | 0.851 |

![Labeled dataset comparison](labeled_dataset_comparison.jpg)

The [metrics CSV](labeled_dataset_metrics.csv) contains per-image IoU, precision, recall, F1, and predicted foreground fraction.

## Interpretation

No single Otsu polarity works consistently because the pet can be brighter or darker than different parts of the background. The large variation between `otsu_bright` and `otsu_dark` across images is a concrete failure mode for intensity-only segmentation.

The fixed-inset GrabCut baseline performs better on every image in this subset. It uses both color distributions and a spatial initialization, which is a better match for photographs where the main subject is near the center and the image boundary is likely to contain background.

This result supports the value of matching a method's assumptions to the data. It does not establish GrabCut as a universal segmentation solution.

## Limitations

- Six selected images are insufficient for claims about the complete Oxford-IIIT Pet Dataset.
- The sample selection is fixed and is not a random or stratified benchmark split.
- The fixed GrabCut rectangle assumes that the subject does not touch the image boundary; other framing can violate this assumption.
- The trimap boundary is counted as foreground, so results would differ under another boundary policy.
- Mean metrics weight every image equally and do not describe class- or breed-level variation.
- These classical baselines are included for controlled comparison, not as state-of-the-art methods.

## License

The experiment code is licensed under MIT. The Oxford-IIIT Pet files and the derived comparison artifact are available under Creative Commons Attribution-ShareAlike 4.0; see the [dataset attribution](../../data/oxford_pet_sample/README.md).
