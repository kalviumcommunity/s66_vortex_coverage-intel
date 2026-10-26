"""Tests for model output controls."""

from __future__ import annotations

import pytest

from coverage_intel.generation.parameters import ModelParameters


def test_parameters_normalize_stop_sequences() -> None:
    parameters = ModelParameters.from_values(temperature=0.1, max_tokens=128, stop=["END"])

    assert parameters.temperature == 0.1
    assert parameters.max_tokens == 128
    assert parameters.stop == ("END",)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"temperature": -0.1},
        {"temperature": 2.1},
        {"max_tokens": 0},
        {"stop": ["", "A", "B", "C", "D"]},
    ],
)
def test_invalid_parameters_are_rejected(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        ModelParameters.from_values(**kwargs)  # type: ignore[arg-type]
