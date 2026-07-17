"""Tests for deterministic synthetic scenario generation."""

import numpy as np

from vision_playground.synthetic import generate_scenarios


def test_scenarios_are_deterministic_for_the_same_seed() -> None:
    first = generate_scenarios(seed=11)
    second = generate_scenarios(seed=11)

    assert [scenario.name for scenario in first] == [
        "uniform_clean",
        "shifted_low_contrast",
        "uneven_illumination",
        "high_noise",
    ]
    for first_scenario, second_scenario in zip(first, second, strict=True):
        assert np.array_equal(first_scenario.image, second_scenario.image)
        assert np.array_equal(
            first_scenario.ground_truth,
            second_scenario.ground_truth,
        )
