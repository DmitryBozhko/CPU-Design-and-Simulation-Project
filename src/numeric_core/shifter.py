from __future__ import annotations


def _fill(value: int, count: int) -> list[int]:
    filled: list[int] = []
    for _ in range(count):
        filled.append(value & 1)
    return filled


def _normalize(bits: list[int]) -> list[int]:
    normalized: list[int] = []
    for bit in bits:
        normalized.append(bit & 1)
    return normalized


def _retain_width(bits: list[int], width: int) -> list[int]:
    retained: list[int] = []
    for index in range(width):
        if index < len(bits):
            retained.append(bits[index] & 1)
        else:
            retained.append(0)
    return retained


def sll(bits: list[int], shamt: int) -> list[int]:
    normalized = _normalize(bits)
    width = len(normalized)
    shifted = _fill(0, shamt)
    shifted.extend(normalized)
    return _retain_width(shifted, width)


def srl(bits: list[int], shamt: int) -> list[int]:
    normalized = _normalize(bits)
    width = len(normalized)
    trimmed = normalized[shamt:]
    padding = _fill(0, shamt)
    trimmed.extend(padding)
    return _retain_width(trimmed, width)


def sra(bits: list[int], shamt: int) -> list[int]:
    normalized = _normalize(bits)
    width = len(normalized)
    sign_bit = 0
    if normalized:
        sign_bit = normalized[-1]
    trimmed = normalized[shamt:]
    padding = _fill(sign_bit, shamt)
    trimmed.extend(padding)
    return _retain_width(trimmed, width)