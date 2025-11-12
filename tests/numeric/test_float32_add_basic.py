# tests/numeric/test_float32_add_basic.py
from __future__ import annotations

import pytest

from src.numeric_core.float32 import (
    fadd_f32,
    fsub_f32,
    unpack_f32,
)


# Helper: interpret hex as *canonical* IEEE-754 32-bit,
# then convert to little-endian bit list where bits[i] is bit i (LSB-first).
def _bits_from_hex_ieee(hex_str: str) -> list[int]:
    value = int(hex_str, 16)
    bits: list[int] = []
    for i in range(32):
        bits.append((value >> i) & 1)
    return bits


def _hex_from_bits_ieee(bits: list[int]) -> str:
    # Inverse of _bits_from_hex_ieee
    value = 0
    limit = 32
    for i in range(limit):
        if i < len(bits) and (bits[i] & 1):
            value |= (1 << i)
    return f"{value:08X}"


# Known patterns (canonical IEEE-754 float32):
# 1.0       -> 0x3F800000
# 2.0       -> 0x40000000
# 1.5       -> 0x3FC00000
# 2.25      -> 0x40100000
# 3.75      -> 0x40700000
# +inf      -> 0x7F800000
# -inf      -> 0xFF800000
# +0.0      -> 0x00000000
# -0.0      -> 0x80000000
# quiet NaN -> 0x7FC00001 (for classification)


def test_add_simple_1_plus_1():
    one_bits = _bits_from_hex_ieee("3F800000")
    two_bits = _bits_from_hex_ieee("40000000")

    info = fadd_f32(one_bits, one_bits)
    result_bits = info["result"]
    hex_out = _hex_from_bits_ieee(result_bits)

    assert hex_out == "40000000"  # 2.0
    flags = info["flags"]
    assert flags["overflow"] is False
    assert flags["underflow"] is False
    assert flags["invalid"] is False


def test_add_1_5_plus_2_25():
    """1.5 + 2.25 = 3.75, all exactly representable."""
    a_bits = _bits_from_hex_ieee("3FC00000")  # 1.5
    b_bits = _bits_from_hex_ieee("40100000")  # 2.25

    info = fadd_f32(a_bits, b_bits)
    result_bits = info["result"]
    hex_out = _hex_from_bits_ieee(result_bits)

    assert hex_out == "40700000"  # 3.75
    flags = info["flags"]
    assert flags["overflow"] is False
    assert flags["underflow"] is False
    assert flags["invalid"] is False


def test_add_cancel_to_zero():
    """a + (-a) should produce a zero (sign handling can be +0)."""
    a_bits = _bits_from_hex_ieee("3F800000")   # +1.0
    neg_a_bits = _bits_from_hex_ieee("BF800000")  # -1.0

    info = fadd_f32(a_bits, neg_a_bits)
    res = unpack_f32(info["result"])

    assert res["class"] == "zero"
    # We don't force a particular sign of zero here.
    assert info["flags"]["overflow"] is False
    assert info["flags"]["invalid"] is False


def test_sub_self_is_zero():
    """a - a should be exactly zero."""
    a_bits = _bits_from_hex_ieee("40000000")  # 2.0

    info = fsub_f32(a_bits, a_bits)
    res = unpack_f32(info["result"])

    assert res["class"] == "zero"
    assert info["flags"]["overflow"] is False
    assert info["flags"]["invalid"] is False


def test_add_infinity_and_finite():
    """+inf + finite -> +inf; finite + -inf -> -inf."""
    inf_pos = _bits_from_hex_ieee("7F800000")
    inf_neg = _bits_from_hex_ieee("FF800000")
    one_bits = _bits_from_hex_ieee("3F800000")

    # +inf + 1.0 -> +inf
    info1 = fadd_f32(inf_pos, one_bits)
    res1 = unpack_f32(info1["result"])
    assert res1["class"] == "infinity"
    assert res1["sign"] == 0
    assert info1["flags"]["invalid"] is False

    # -inf + 1.0 -> -inf
    info2 = fadd_f32(inf_neg, one_bits)
    res2 = unpack_f32(info2["result"])
    assert res2["class"] == "infinity"
    assert res2["sign"] == 1
    assert info2["flags"]["invalid"] is False


def test_add_inf_plus_neg_inf_is_nan():
    """+inf + -inf should be classified as NaN with invalid flag."""
    inf_pos = _bits_from_hex_ieee("7F800000")
    inf_neg = _bits_from_hex_ieee("FF800000")

    info = fadd_f32(inf_pos, inf_neg)
    res = unpack_f32(info["result"])

    assert res["class"] == "nan"
    flags = info["flags"]
    assert flags["invalid"] is True


def test_add_with_nan_propagation():
    """NaN + anything -> NaN, invalid flag set."""
    nan_bits = _bits_from_hex_ieee("7FC00001")
    one_bits = _bits_from_hex_ieee("3F800000")

    info1 = fadd_f32(nan_bits, one_bits)
    res1 = unpack_f32(info1["result"])
    assert res1["class"] == "nan"
    assert info1["flags"]["invalid"] is True

    info2 = fadd_f32(one_bits, nan_bits)
    res2 = unpack_f32(info2["result"])
    assert res2["class"] == "nan"
    assert info2["flags"]["invalid"] is True
