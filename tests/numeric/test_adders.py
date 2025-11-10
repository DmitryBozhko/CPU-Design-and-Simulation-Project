from __future__ import annotations
import itertools
from src.numeric_core.adders import full_adder, half_adder


def test_half_adder_truth_table() -> None:
    expected = {
        (0, 0): (0, 0),
        (0, 1): (1, 0),
        (1, 0): (1, 0),
        (1, 1): (0, 1),
    }

    for a, b in expected:
        assert half_adder(a, b) == expected[(a, b)]


def test_full_adder_truth_table() -> None:
    expected = {
        (0, 0, 0): (0, 0),
        (0, 0, 1): (1, 0),
        (0, 1, 0): (1, 0),
        (0, 1, 1): (0, 1),
        (1, 0, 0): (1, 0),
        (1, 0, 1): (0, 1),
        (1, 1, 0): (0, 1),
        (1, 1, 1): (1, 1),
    }

    for inputs in expected:
        assert full_adder(*inputs) == expected[inputs]