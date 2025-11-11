from __future__ import annotations

import random

from src.numeric_core.small_ops import (
    decrement_bits,
    increment_bits,
    multiply_by_power_of_two,
)
from src.numeric_core.shifters import shift_left_bits

random.seed(0)


def int_to_bits(value: int, width: int) -> list[int]:
    bits: list[int] = []
    for idx in range(width):
        bits.append((value >> idx) & 1)
    return bits


def bits_to_int(bits: list[int]) -> int:
    value = 0
    for idx, bit in enumerate(bits):
        if bit & 1:
            value |= 1 << idx
    return value


def test_increment_bits_carries_across_width() -> None:
    bits = int_to_bits(5, 4)
    result = increment_bits(bits)
    assert bits_to_int(result) == 6


def test_increment_bits_appends_new_bit_on_overflow() -> None:
    bits = int_to_bits(15, 4)
    result = increment_bits(bits)
    assert bits_to_int(result) == 16
    assert len(result) == 5


def test_decrement_bits_wraps_zero_with_twos_complement() -> None:
    bits = int_to_bits(0, 4)
    result = decrement_bits(bits)
    assert bits_to_int(result) == 15


def test_decrement_bits_handles_wider_values() -> None:
    bits = int_to_bits(16, 5)
    result = decrement_bits(bits)
    assert bits_to_int(result) == 15
    assert len(result) == 5


def test_multiply_by_power_of_two_matches_python_shift() -> None:
    bits = int_to_bits(3, 4)
    result = multiply_by_power_of_two(bits, 2)
    assert bits_to_int(result) == 12


def test_multiply_by_power_of_two_zero_power_returns_copy() -> None:
    bits = int_to_bits(7, 3)
    result = multiply_by_power_of_two(bits, 0)
    assert result == bits
    assert result is not bits


def test_shift_left_bits_inserts_zeros_on_lsb_side() -> None:
    bits = int_to_bits(6, 3)
    shifted = shift_left_bits(bits, 2)
    assert bits_to_int(shifted) == 24


def test_increment_and_decrement_random_pairs() -> None:
    for _ in range(10):
        width = random.randint(1, 8)
        base = random.randint(0, (1 << width) - 1)
        inc_bits = increment_bits(int_to_bits(base, width))
        dec_bits = decrement_bits(int_to_bits(base, width))
        assert bits_to_int(inc_bits) == base + 1
        assert bits_to_int(dec_bits) == (base - 1) % (1 << width)
