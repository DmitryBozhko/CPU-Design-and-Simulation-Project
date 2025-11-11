from __future__ import annotations
import random
from src.numeric_core.adders import full_adder, half_adder, ripple_carry_adder


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


def _int_to_bits(value: int, width: int) -> list[int]:
    return [(value >> index) & 1 for index in range(width)]


def _bits_to_int(bits: list[int]) -> int:
    result = 0
    for index, bit in enumerate(bits):
        if bit:
            result |= 1 << index
    return result


def test_ripple_carry_adder_4_bit_example() -> None:
    a_bits = [1, 0, 1, 0]
    b_bits = [1, 1, 0, 0]

    sum_bits, cout = ripple_carry_adder(a_bits, b_bits)

    assert sum_bits == [0, 0, 0, 1]
    assert cout == 0


def test_ripple_carry_adder_8_bit_overflow() -> None:
    a_bits = [1] * 8
    b_bits = [1] + [0] * 7

    sum_bits, cout = ripple_carry_adder(a_bits, b_bits)

    assert sum_bits == [0] * 8
    assert cout == 1


def test_ripple_carry_adder_random_32_bit_vectors() -> None:
    width = 32
    for _ in range(50):
        a_value = random.getrandbits(width)
        b_value = random.getrandbits(width)

        a_bits = _int_to_bits(a_value, width)
        b_bits = _int_to_bits(b_value, width)

        sum_bits, cout = ripple_carry_adder(a_bits, b_bits)
        computed_sum = _bits_to_int(sum_bits)
        expected_sum = a_value + b_value

        assert expected_sum & ((1 << width) - 1) == computed_sum
        assert (expected_sum >> width) & 1 == cout
