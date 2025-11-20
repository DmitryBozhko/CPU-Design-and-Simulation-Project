# AI-BEGIN
# tests/float32_host_bridge.py
from __future__ import annotations
import struct
from typing import List


def host_pack_f32(value: float) -> List[int]:
    """
    Convert a Python float into a 32-bit IEEE-754 pattern as a bit list.

    Convention: bits[i] is bit i of the 32-bit word (LSB-first).
    """
    as_bytes = struct.pack("<f", float(value))
    (word,) = struct.unpack("<I", as_bytes)
    bits: List[int] = []
    for i in range(32):
        bits.append((word >> i) & 1)
    return bits


def host_unpack_f32(bits: List[int]) -> float:
    """
    Convert a 32-bit bit list (LSB-first) back into a Python float.
    """
    word = 0
    for i, b in enumerate(bits):
        if b & 1:
            word |= 1 << i
    as_bytes = struct.pack("<I", word)
    (value,) = struct.unpack("<f", as_bytes)
    return value


# AI-END
