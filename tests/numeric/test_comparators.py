from __future__ import annotations
from src.numeric_core.comparators import (
    compare_signed,
    compare_unsigned,
    is_zero,
)


def _int_to_bits(value: int, width: int) -> list[int]:
    return [(value >> index) & 1 for index in range(width)]


def _signed_to_bits(value: int, width: int) -> list[int]:
    mask = (1 << width) - 1
    return _int_to_bits(value & mask, width)


def test_is_zero_detects_zero_vector() -> None:
    assert is_zero([0, 0, 0, 0]) is True


def test_is_zero_detects_non_zero_vector() -> None:
    assert is_zero([0, 1, 0, 0]) is False


def test_compare_unsigned_less_than() -> None:
    a_bits = _int_to_bits(5, 4)
    b_bits = _int_to_bits(10, 4)
    assert compare_unsigned(a_bits, b_bits) == -1


def test_compare_unsigned_greater_than() -> None:
    a_bits = _int_to_bits(0xFFFFFFFF, 32)
    b_bits = _int_to_bits(1, 32)
    assert compare_unsigned(a_bits, b_bits) == 1


def test_compare_unsigned_equality() -> None:
    a_bits = _int_to_bits(42, 8)
    b_bits = _int_to_bits(42, 8)
    assert compare_unsigned(a_bits, b_bits) == 0


def test_compare_signed_negative_vs_zero() -> None:
    a_bits = _signed_to_bits(-1, 8)
    b_bits = _signed_to_bits(0, 8)
    assert compare_signed(a_bits, b_bits) == -1


def test_compare_signed_positive_vs_negative() -> None:
    a_bits = _signed_to_bits(7, 8)
    b_bits = _signed_to_bits(-2, 8)
    assert compare_signed(a_bits, b_bits) == 1


def test_compare_signed_equality() -> None:
    a_bits = _signed_to_bits(-4, 8)
    b_bits = _signed_to_bits(-4, 8)
    assert compare_signed(a_bits, b_bits) == 0
