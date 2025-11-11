from __future__ import annotations

from .adders import ripple_carry_adder


def invert_bits(bits: list[int]) -> list[int]:
    inverted: list[int] = []
    for bit in bits:
        inverted.append((bit ^ 1) & 1)
    return inverted


def negate_twos_complement(bits: list[int]) -> list[int]:
    if not bits:
        return []
    inverted = invert_bits(bits)
    incremented, _ = ripple_carry_adder(inverted, [1])
    result: list[int] = []
    for index, bit in enumerate(incremented):
        if index >= len(bits):
            break
        result.append(bit & 1)
    while len(result) < len(bits):
        result.append(0)
    return result