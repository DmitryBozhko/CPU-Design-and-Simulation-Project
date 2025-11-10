from __future__ import annotations

from itertools import zip_longest


def _as_bit(value: int) -> int:
    return value & 1


def half_adder(a: int, b: int) -> tuple[int, int]:

    a_bit = _as_bit(a)
    b_bit = _as_bit(b)

    sum_bit = (a_bit ^ b_bit) & 1
    carry_bit = a_bit & b_bit

    return sum_bit, carry_bit


def full_adder(a: int, b: int, cin: int) -> tuple[int, int]:

    cin_bit = _as_bit(cin)
    first_sum, first_carry = half_adder(a, b)
    final_sum, second_carry = half_adder(first_sum, cin_bit)
    final_carry = first_carry | second_carry

    return final_sum & 1, final_carry & 1


def ripple_carry_adder(
    a_bits: list[int],
    b_bits: list[int],
    cin: int = 0,
) -> tuple[list[int], int]:

    carry = _as_bit(cin)
    result_bits: list[int] = []

    for a_bit, b_bit in zip_longest(a_bits, b_bits, fillvalue=0):
        sum_bit, carry = full_adder(a_bit, b_bit, carry)
        result_bits.append(sum_bit)

    return result_bits, carry