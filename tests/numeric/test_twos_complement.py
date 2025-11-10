from __future__ import annotations

from src.numeric_core.twos_complement import invert_bits, negate_twos_complement


def _int_to_bits(value: int, width: int) -> list[int]:
    return [(value >> index) & 1 for index in range(width)]


def _signed_to_bits(value: int, width: int) -> list[int]:
    mask = (1 << width) - 1
    return _int_to_bits(value & mask, width)


def test_invert_bits_flips_all_bits() -> None:
    assert invert_bits([0, 1, 0, 1]) == [1, 0, 1, 0]


def test_negate_zero_is_zero() -> None:
    zero_bits = _signed_to_bits(0, 8)

    assert negate_twos_complement(zero_bits) == zero_bits


def test_negate_one_is_all_ones() -> None:
    one_bits = _signed_to_bits(1, 8)
    expected = [1] * 8

    assert negate_twos_complement(one_bits) == expected


def test_negate_min_value_wraps() -> None:
    min_bits = _signed_to_bits(0x80, 8)

    assert negate_twos_complement(min_bits) == min_bits