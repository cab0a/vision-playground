# Oxford-IIIT Pet Evaluation Sample

This directory contains six image and trimap pairs selected from the Oxford-IIIT Pet Dataset:

- three cat images: British Shorthair, Egyptian Mau, and Ragdoll
- three dog images: Boxer, English Setter, and Samoyed

The subset is intentionally small so the labeled evaluation remains reviewable and reproducible in continuous integration. It is not statistically representative of the full 37-breed dataset.

## Provenance

The files were extracted without modification from the official archives:

- `https://www.robots.ox.ac.uk/~vgg/data/pets/data/images.tar.gz`
- `https://www.robots.ox.ac.uk/~vgg/data/pets/data/annotations.tar.gz`

Every committed file is listed with its SHA-256 digest in `manifest.csv`.

## Labels

The trimaps use the original indexed values:

- `1`: pet foreground
- `2`: background
- `3`: boundary or uncertain region

This project includes values `1` and `3` in the evaluated pet silhouette.

## License and Attribution

The Oxford-IIIT Pet Dataset is available for commercial and research purposes under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/). Copyright remains with the original image owners.

Dataset authors:

Omkar M. Parkhi, Andrea Vedaldi, Andrew Zisserman, and C. V. Jawahar, “Cats and Dogs,” IEEE Conference on Computer Vision and Pattern Recognition, 2012.

The dataset files in this directory and derived visual artifacts retain the CC BY-SA 4.0 terms. The repository's MIT License applies to the project code, not to these dataset files.
