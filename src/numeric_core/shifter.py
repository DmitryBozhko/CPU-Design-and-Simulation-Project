from __future__ import annotations

from itertools import repeat


def _normalize_bits(bits: list[int]) -> list[int]:
    normalized: list[int] = []
    for bit in bits:
        normalized.append(bit & 1)
    return normalized


def _fill(bit_value: int, count: int) -> list[int]:
    normalized_bit = bit_value & 1
    filled: list[int] = []
    for _ in repeat(None, count):
        filled.append(normalized_bit)
    return filled


def _retain_width(bits: list[int], width: int) -> list[int]:
    if width:
        return bits[:width]
    return []


def sll(bits: list[int], shamt: int) -> list[int]:
    normalized = _normalize_bits(bits)
    width = len(normalized)
    padding = _fill(0, shamt)
    shifted: list[int] = []
    shifted.extend(padding)
    shifted.extend(normalized)
    return _retain_width(shifted, width)


def srl(bits: list[int], shamt: int) -> list[int]:
    normalized = _normalize_bits(bits)
    width = len(normalized)
    trimmed = normalized[shamt:]
    padding = _fill(0, shamt)
    trimmed.extend(padding)
    return _retain_width(trimmed, width)


def sra(bits: list[int], shamt: int) -> list[int]:
    normalized = _normalize_bits(bits)
    width = len(normalized)
    sign_bit = 0
    for bit in normalized:
        sign_bit = bit & 1
    trimmed = normalized[shamt:]
    padding = _fill(sign_bit, shamt)
    trimmed.extend(padding)
    return _retain_width(trimmed, width)