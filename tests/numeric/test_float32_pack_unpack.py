from __future__ import annotations
import pytest

from src.numeric_core.float32 import (
    unpack_f32_fields,
    pack_f32_from_fields,
)
from tests.float32_host_bridge import host_pack_f32, host_unpack_f32


# AI-BEGIN
def _bits_from_hex(hex_str: str) -> list[int]:
    """Interpret hex as canonical IEEE-754 float32 bits, LSB-first."""
    value = int(hex_str, 16)
    bits: list[int] = []
    i = 0
    while i < 32:
        bits.append((value >> i) & 1)
        i = i + 1
    return bits


# AI-END


def test_zero_positive():
    bits = _bits_from_hex("00000000")
    info = unpack_f32_fields(bits)
    assert info["class"] == "zero"
    assert info["sign"] == 0
    assert info["exponent"] == [0] * 8
    assert all((bit & 1) == 0 for bit in info["fraction"])


def test_zero_negative():
    bits = _bits_from_hex("80000000")
    info = unpack_f32_fields(bits)
    assert info["class"] == "zero"
    assert info["sign"] == 1


def test_infinity_positive():
    bits = _bits_from_hex("7F800000")
    info = unpack_f32_fields(bits)
    assert info["class"] == "infinity"
    assert info["sign"] == 0


def test_infinity_negative():
    bits = _bits_from_hex("FF800000")
    info = unpack_f32_fields(bits)
    assert info["class"] == "infinity"
    assert info["sign"] == 1


def test_nan_classification():
    bits = _bits_from_hex("7FC00001")
    info = unpack_f32_fields(bits)
    assert info["class"] == "nan"


def test_roundtrip_fields():
    bits = _bits_from_hex("40700000")
    info = unpack_f32_fields(bits)
    repacked = pack_f32_from_fields(
        info["sign"],
        info["exponent"],
        info["fraction"],
    )
    assert repacked == bits


def test_pack_f32_matches_hex():
    bits = host_pack_f32(3.75)
    assert bits == _bits_from_hex("40700000")


def test_unpack_f32_to_python_float():
    bits = _bits_from_hex("C1200000")
    value = host_unpack_f32(bits)
    assert value == pytest.approx(-10.0)
