# Denoising Public Image Sample

This sample checks how simple denoising changes Otsu-threshold stability on two freely reusable photographs. The original images are treated as clean inputs, then corrupted with deterministic Gaussian or salt-and-pepper noise.

The experiment compares:

- no denoising
- Gaussian filtering with a 5 × 5 kernel
- median filtering with a 5 × 5 kernel

Each filtered image is thresholded with Otsu's method. Its binary mask is compared with the Otsu mask from the uncorrupted image using IoU.

## Reproduction

```bash
python experiments/run_denoising_public_sample.py
```

Expected summary:

```text
Images: 2
Noise conditions: 2
Denoising methods: 3
Evaluations: 12
Summary: results/denoising_public_sample/denoising_summary.csv
Comparison: results/denoising_public_sample/denoising_comparison.jpg
```

## Conditions

- Gaussian noise: zero mean and standard deviation `45`
- Salt-and-pepper noise: `15%` of pixels replaced with equal amounts of black and white
- Random seed: `29`
- Downstream method: Otsu thresholding

The camera and coffee images were selected because they contain different intensity distributions and levels of texture while remaining easy to inspect visually.

## Results

The table reports IoU against the clean-image Otsu mask.

| Image | Noise | No denoising | Gaussian 5 × 5 | Median 5 × 5 |
| --- | --- | ---: | ---: | ---: |
| `camera.png` | Gaussian | 0.842 | 0.980 | 0.977 |
| `camera.png` | Salt and pepper | 0.892 | 0.973 | 0.984 |
| `coffee.png` | Gaussian | 0.643 | 0.840 | 0.837 |
| `coffee.png` | Salt and pepper | 0.758 | 0.811 | 0.897 |

![Denoising stability comparison](denoising_comparison.jpg)

## Interpretation

Both filters make the thresholded outputs more stable under the tested corruptions. Gaussian filtering produces the highest reference-mask IoU for Gaussian noise on both photographs, although median filtering is close. Median filtering produces the highest result for salt-and-pepper noise, with the clearest difference on the textured coffee image.

The coffee image remains more sensitive than the camera image. After Gaussian filtering, its reference-mask IoU reaches `0.840`, compared with `0.980` for the camera image. This difference shows that performance depends on the image distribution as well as the nominal noise type.

## Limitations

Reference-mask IoU measures consistency with the clean-image Otsu output. It is not semantic segmentation accuracy, and the reference mask is not a human annotation. Filtering can also move boundaries or remove fine structures even when the consistency score improves.

Only two photographs, two synthetic noise models, one noise level per model, one kernel size, and one downstream thresholding method are evaluated. Practical selection requires representative images, task-specific labels, and a relevant error metric.

## Sources and Licenses

The photographs, attributions, licenses, pinned download URLs, and checksum policy are documented in the [public image sample](../public_sample/README.md#sources-and-licenses). Downloaded source images are excluded from the repository; only derived comparison artifacts are committed.
