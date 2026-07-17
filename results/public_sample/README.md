# Public Image Sample

This qualitative experiment applies the same fixed and Otsu global thresholding methods to five real images distributed with scikit-image. The download URLs are pinned to scikit-image `v0.26.0`, and every file is verified with SHA-256.

The images do not provide semantic ground-truth masks. The experiment therefore reports selected thresholds and foreground fractions without presenting IoU, F1, or accuracy claims.

## Reproduction

```bash
python experiments/run_public_image_sample.py
```

Expected summary:

```text
Images: 5
Evaluations: 10
Summary: results/public_sample/thresholding_summary.csv
Comparison: results/public_sample/thresholding_comparison.jpg
```

## Interpretation

The outputs visualize intensity partitioning, not object recognition or semantic segmentation. A white region only means that its grayscale value is above the selected threshold.

| Image | Fixed threshold | Fixed foreground | Otsu threshold | Otsu foreground |
| --- | ---: | ---: | ---: | ---: |
| `camera.png` | 127 | 64.30% | 102 | 67.90% |
| `clock_motion.png` | 127 | 87.95% | 174 | 6.49% |
| `coffee.png` | 127 | 33.10% | 104 | 48.53% |
| `hubble_deep_field.jpg` | 127 | 1.85% | 80 | 3.22% |
| `rocket.jpg` | 127 | 3.32% | 74 | 24.59% |

The camera image changes only modestly when Otsu lowers the threshold. In contrast, the bright, relatively smooth clock image exposes a major limitation of applying one fixed threshold to unrelated scenes: the fixed method classifies most of the background as foreground, while Otsu selects a much higher threshold and isolates a smaller bright region.

For the coffee image, both methods divide a scene containing several materials, shadows, and textures; neither result is a semantic cup mask. In the dark Hubble image, both thresholds retain only bright sources, although Otsu's lower threshold includes more faint regions. The rocket image shows another large change: lowering the threshold increases the selected fraction from 3.32% to 24.59%, including additional sky and structural regions.

These observations show why the selected threshold and foreground fraction are useful diagnostics, but not measures of segmentation quality. Without ground-truth masks, the experiment cannot determine which method is more accurate. A real application would need task-specific labels, metrics, and error analysis.

## Sources and Licenses

| File | Source and attribution | License |
| --- | --- | --- |
| `camera.png` | Photograph by Lav Varshney, distributed in [`skimage.data.camera`](https://scikit-image.org/docs/stable/api/skimage.data#skimage.data.camera) | CC0 |
| `coffee.png` | Photograph by Rachel Michetti, distributed in [`skimage.data.coffee`](https://scikit-image.org/docs/stable/api/skimage.data#skimage.data.coffee) | CC0 |
| `clock_motion.png` | Photograph by Stefan van der Walt, distributed in [`skimage.data.clock`](https://scikit-image.org/docs/stable/api/skimage.data#skimage.data.clock) | Public domain |
| `rocket.jpg` | SpaceX launch photograph, distributed in [`skimage.data.rocket`](https://scikit-image.org/docs/stable/api/skimage.data#skimage.data.rocket) | Public domain |
| `hubble_deep_field.jpg` | NASA Hubble Deep Field image, distributed in [`skimage.data.hubble_deep_field`](https://scikit-image.org/docs/stable/api/skimage.data#skimage.data.hubble_deep_field) | Public domain |

See the [scikit-image data documentation](https://scikit-image.org/docs/stable/api/skimage.data) for the upstream descriptions and licensing notes.
