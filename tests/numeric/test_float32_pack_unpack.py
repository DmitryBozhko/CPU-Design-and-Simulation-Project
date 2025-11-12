from __future__ import annotations
import pytest
from src.numeric_core.conversions import hex_to_bits32
from src.numeric_core.float32 import unpack_f32, pack_f32_from_fields


def _bits_from_hex(hex_str: str) -> list[int]:
    return hex_to_bits32(hex_str)


def test_zero_positive():
    bits = _bits_from_hex("00000000")
    info = unpack_f32(bits)
    assert info["class"] == "zero"
    assert info["sign"] == 0
    assert info["exponent"] == [0] * 8
    assert all((bit & 1) == 0 for bit in info["fraction"])


def test_zero_negative():
    bits = _bits_from_hex("80000000")
    info = unpack_f32(bits)
    assert info["class"] == "zero"
    assert info["sign"] == 1


def test_infinity_positive():
    bits = _bits_from_hex("7F800000")
    info = unpack_f32(bits)
    assert info["class"] == "infinity"
    assert info["sign"] == 0


def test_infinity_negative():
    bits = _bits_from_hex("FF800000")
    info = unpack_f32(bits)
    assert info["class"] == "infinity"
    assert info["sign"] == 1


def test_nan_classification():
    bits = _bits_from_hex("7FC00001")
    info = unpack_f32(bits)
    assert info["class"] == "nan"


def test_roundtrip_fields():
    bits = _bits_from_hex("40700000")
    info = unpack_f32(bits)

    repacked = pack_f32_from_fields(
        info["sign"],
        info["exponent"],
        info["fraction"],
    )

    assert repacked == bits
