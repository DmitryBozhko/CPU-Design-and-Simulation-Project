from __future__ import annotations

from itertools import zip_longest

from .adders import ripple_carry_adder

_MISSING = object()


def is_zero(bits: list[int]) -> bool:

    for bit in bits:
        if bit & 1:
            return False

    return True


def _sign_bit(bits: list[int]) -> int:

    if bits:
        return bits[-1] & 1

    return 0


def _align_bits(
    a_bits: list[int],
    a_fill: int,
    b_bits: list[int],
    b_fill: int,
) -> tuple[list[int], list[int]]:

    aligned_a: list[int] = []
    aligned_b: list[int] = []

    for a_bit, b_bit in zip_longest(a_bits, b_bits, fillvalue=_MISSING):
        if a_bit is _MISSING:
            a_bit = a_fill
        if b_bit is _MISSING:
            b_bit = b_fill

        aligned_a.append(a_bit & 1)
        aligned_b.append(b_bit & 1)

    if not aligned_a:
        aligned_a.append(a_fill & 1)
        aligned_b.append(b_fill & 1)

    return aligned_a, aligned_b


def _invert_bits(bits: list[int]) -> list[int]:

    inverted: list[int] = []
    for bit in bits:
        inverted.append((bit ^ 1) & 1)

    return inverted


def _subtract_aligned(a_bits: list[int], b_bits: list[int]) -> tuple[list[int], int]:

    inverted_b = _invert_bits(b_bits)
    difference, carry_out = ripple_carry_adder(a_bits, inverted_b, cin=1)
    borrow = (carry_out ^ 1) & 1

    return difference, borrow


def compare_unsigned(a_bits: list[int], b_bits: list[int]) -> int:

    aligned_a, aligned_b = _align_bits(a_bits, 0, b_bits, 0)
    difference, borrow = _subtract_aligned(aligned_a, aligned_b)

    if borrow:
        return -1

    if is_zero(difference):
        return 0

    return 1


def compare_signed(a_bits: list[int], b_bits: list[int]) -> int:

    a_sign = _sign_bit(a_bits)
    b_sign = _sign_bit(b_bits)
    if a_sign ^ b_sign:
        if a_sign:
            return -1

        return 1
    aligned_a, aligned_b = _align_bits(a_bits, a_sign, b_bits, b_sign)
    aligned_a.append(a_sign)
    aligned_b.append(b_sign)

    difference, _ = _subtract_aligned(aligned_a, aligned_b)

    if is_zero(difference):
        return 0

    if difference[-1] & 1:
        return -1

    return 1