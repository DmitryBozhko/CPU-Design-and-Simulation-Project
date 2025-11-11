from __future__ import annotations
from itertools import chain, islice, repeat
from .adders import ripple_carry_adder
from .shifters import shift_left_bits


def _normalize_operand(bits: list[int]) -> list[int]:
    normalized: list[int] = []
    for bit in bits:
        normalized.append(bit & 1)
    if normalized:
        return normalized
    return [0]


def _resolved_width(width: int) -> int:
    if width:
        return width
    return 1


def _fixed_width(bits: list[int], width: int, fill: int = 0) -> list[int]:
    resolved_width = _resolved_width(width)
    limited: list[int] = []
    source = chain(bits, repeat(fill))
    for bit in islice(source, resolved_width):
        limited.append(bit & 1)
    return limited


def _invert_bits(bits: list[int]) -> list[int]:
    inverted: list[int] = []
    for bit in bits:
        inverted.append((bit ^ 1) & 1)
    return inverted


def _two_complement(bits: list[int], width: int) -> list[int]:
    fixed = _fixed_width(bits, width, fill=0)
    inverted = _invert_bits(fixed)
    complemented, _ = ripple_carry_adder(inverted, [1])
    return _fixed_width(complemented, width, fill=0)


def increment_bits(bits: list[int]) -> list[int]:
    normalized = _normalize_operand(bits)
    result, carry = ripple_carry_adder(normalized, [1])
    if carry:
        result.append(carry & 1)
    return result


def decrement_bits(bits: list[int]) -> list[int]:
    normalized = _normalize_operand(bits)
    width = _resolved_width(len(normalized))
    negative_one = _two_complement([1], width)
    result, _ = ripple_carry_adder(normalized, negative_one)
    return _fixed_width(result, width, fill=0)


def multiply_by_power_of_two(bits: list[int], power: int) -> list[int]:
    normalized = _normalize_operand(bits)
    if power:
        return shift_left_bits(normalized, power)
    return list(normalized)