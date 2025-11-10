from __future__ import annotations

from itertools import repeat


def shift_left_bits(bits: list[int], amount: int) -> list[int]:

    normalized: list[int] = []
    for bit in bits:
        normalized.append(bit & 1)

    shifted: list[int] = []
    for _ in repeat(None, amount):
        shifted.append(0)

    shifted.extend(normalized)

    return shifted