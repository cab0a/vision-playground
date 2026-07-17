# Edge Detection Public Image Sample

This sample checks Canny edge stability on two freely reusable photographs after deterministic Gaussian or salt-and-pepper noise is added.

The experiment uses:

- Canny thresholds `125` and `250`
- positional tolerance of `2` pixels
- no denoising, Gaussian filtering, or median filtering
- a 5 × 5 filter kernel

Each predicted edge map is compared with the Canny edge map from the uncorrupted photograph.

## Reproduction

```bash
python experiments/run_edge_public_sample.py
```

Expected summary:

```text
Images: 2
Noise conditions: 2
Denoising methods: 3
Evaluations: 12
Summary: results/edge_public_sample/edge_detection_summary.csv
Comparison: results/edge_public_sample/edge_detection_comparison.jpg
```

## Results

The table reports tolerance-aware F1 against the clean-image Canny reference.

| Image | Noise | No denoising | Gaussian 5 × 5 | Median 5 × 5 |
| --- | --- | ---: | ---: | ---: |
| `camera.png` | Gaussian | 0.348 | 0.717 | 0.648 |
| `camera.png` | Salt and pepper | 0.367 | 0.485 | 0.671 |
| `coffee.png` | Gaussian | 0.408 | 0.691 | 0.552 |
| `coffee.png` | Salt and pepper | 0.411 | 0.542 | 0.572 |

![Public edge detection comparison](edge_detection_comparison.jpg)

## Interpretation

Without denoising, recall is nearly `1.0` but precision remains between `0.211` and `0.259`. The noisy edge maps retain most reference neighborhoods while adding tens of thousands of false edges.

Gaussian filtering gives the highest F1 for Gaussian noise on both images. Median filtering gives the highest F1 for salt-and-pepper noise, although the improvement over Gaussian filtering is smaller on the textured coffee image. The filtered results trade some recall for a substantial precision increase.

## Metric

A predicted edge is counted as matched when a reference edge exists within two pixels. Recall applies the same tolerance in the opposite direction. This reduces sensitivity to minor rasterization shifts while preserving penalties for missing or spurious structures.

The implementation is a compact diagnostic, not a one-to-one boundary assignment or the official BSDS benchmark.

## Limitations

The clean Canny output is an algorithmic reference, not a human boundary annotation. Reference F1 therefore measures robustness to added noise rather than perceptual edge quality. The selected thresholds, tolerance, kernel size, images, and noise levels are fixed experimental conditions.

## Sources and Licenses

The photographs, attributions, licenses, pinned download URLs, and checksum policy are documented in the [public image sample](../public_sample/README.md#sources-and-licenses). Downloaded source images are excluded from the repository; only derived artifacts are committed.
