# Limitations

These boundaries apply to the committed experiments and results. They are part of the evidence, not exceptions to it.

## Shared Boundaries

- The scenarios are synthetic and do not represent the full variation of real images.
- IoU and F1 measure agreement with generated or public masks, not downstream task performance.
- Cross-experiment reference values have different targets and aggregation policies and must not be interpreted as a ranking.
- Conclusions are limited to the generated conditions and should be validated on task-specific public data before practical use.

## Thresholding and Adaptive Parameters

- The fixed and Otsu methods use one global threshold and are expected to struggle under spatially varying illumination.
- The selected fixed threshold is intentionally not tuned per scenario.
- The reference comparison uses one adaptive configuration across scenarios; the separate sensitivity grid is finite and tuned to the scale of the synthetic generator.
- Adaptive thresholding can amplify local noise or remove foreground interiors when its neighborhood and offset do not match the image structure.
- Foreground fraction on the public photographs describes output behavior but is not a segmentation-quality metric.

## Denoising and Edge Detection

- The denoising study uses two synthetic noise models, one severity per model, and one kernel size; it does not establish a universal filter choice.
- Public-image reference-mask IoU measures consistency with Otsu's clean-image output, not agreement with human labels.
- Edge reference F1 uses a dilation-based positional tolerance without one-to-one boundary matching.
- Public-image edge references are Canny outputs rather than human annotations.

## Labeled Public Data

- The labeled public evaluation uses six selected images and cannot support dataset-wide or breed-level claims.
- The fixed-inset GrabCut baseline assumes that the subject is separated from the image boundary.
- Dataset labels are used only for evaluation, but the chosen subset and metric policy still influence the reported result.

## Optional Inspected Workflow

- The inspected workflow requires unique basenames for valid input images when results are joined.
