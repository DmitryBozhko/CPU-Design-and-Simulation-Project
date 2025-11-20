from __future__ import annotations
from src.numeric_core.float32 import (
    fadd_f32,
    fmul_f32,
    unpack_f32_fields,
)
from tests.float32_host_bridge import host_pack_f32


def _bits_from_hex_ieee(hex_str: str) -> list[int]:
    """Convert 8-hex-digit IEEE-754 word to LSB-first bit list (length 32)."""
    value = int(hex_str, 16)
    bits: list[int] = []
    for i in range(32):
        bits.append((value >> i) & 1)
    return bits


def _hex_from_bits_ieee(bits: list[int]) -> str:
    """Convert LSB-first bit list (length >= 32) to 8-hex-digit IEEE-754 word."""
    value = 0
    limit = 32
    for i in range(limit):
        if i < len(bits) and (bits[i] & 1):
            value |= 1 << i
    return f"{value:08X}"


# AI-BEGIN
def test_add_rounding_0_1_plus_0_2():
    """Check rounding and inexact flag for 0.1 + 0.2."""
    a_bits = host_pack_f32(0.1)
    b_bits = host_pack_f32(0.2)

    info = fadd_f32(a_bits, b_bits)
    result_bits = info["result"]

    # Compare against host float32 oracle via host_pack_f32(0.1 + 0.2)
    expected_bits = host_pack_f32(0.1 + 0.2)
    hex_out = _hex_from_bits_ieee(result_bits)
    expected_hex = _hex_from_bits_ieee(expected_bits)

    assert hex_out == expected_hex
    flags = info["flags"]
    assert flags["overflow"] is False
    assert flags["underflow"] is False
    assert flags["invalid"] is False
    # 0.1 + 0.2 is not exactly representable in float32
    assert flags["inexact"] is True


def test_mul_overflow_to_infinity():
    """Large * 2 -> +inf with overflow flag set."""
    # Largest finite float32: 0x7F7FFFFF ~= 3.4028235e38
    max_finite = _bits_from_hex_ieee("7F7FFFFF")
    two_bits = _bits_from_hex_ieee("40000000")  # 2.0

    info = fmul_f32(max_finite, two_bits)
    res = unpack_f32_fields(info["result"])

    assert res["class"] == "infinity"
    assert res["sign"] == 0  # +inf
    flags = info["flags"]
    assert flags["overflow"] is True
    assert flags["underflow"] is False
    assert flags["invalid"] is False


def test_mul_underflow_to_subnormal():
    """Smallest normal * 0.5 -> subnormal, underflow flag set."""
    # Smallest normal float32: 2^-126 -> 0x00800000
    min_normal = _bits_from_hex_ieee("00800000")
    half = _bits_from_hex_ieee("3F000000")  # 0.5

    info = fmul_f32(min_normal, half)
    res = unpack_f32_fields(info["result"])

    assert res["class"] == "subnormal"
    flags = info["flags"]
    assert flags["underflow"] is True
    assert flags["overflow"] is False
    assert flags["invalid"] is False


# AI-END
