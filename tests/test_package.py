"""Tests for stable package metadata."""

from importlib.metadata import version

from vision_playground import __version__


def test_package_version_matches_installed_metadata() -> None:
    assert __version__ == version("vision-playground")
