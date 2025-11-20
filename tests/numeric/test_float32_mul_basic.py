# AI-BEGIN
from __future__ import annotations
from src.numeric_core.float32 import fmul_f32


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
    idx = 0
    while idx < limit and idx < len(bits):
        bit = bits[idx] & 1
        if bit:
            value |= 1 << idx
        idx = idx + 1
    return f"{value:08X}"


# AI-END


def _extract_fields_from_hex(hex_str: str) -> tuple[int, int, int]:
    value = int(hex_str, 16)
    sign = (value >> 31) & 1
    exponent = (value >> 23) & 0xFF
    fraction = value & 0x7FFFFF
    return sign, exponent, fraction


# AI-BEGIN
def test_mul_1_times_2_is_2():
    """1.0 * 2.0 = 2.0."""
    one_bits = _bits_from_hex_ieee("3F800000")  # 1.0
    two_bits = _bits_from_hex_ieee("40000000")  # 2.0

    info = fmul_f32(one_bits, two_bits)
    result_bits = info["result"]
    hex_out = _hex_from_bits_ieee(result_bits)

    assert hex_out == "40000000"  # 2.0


def test_mul_1_5_times_2_is_3():
    """1.5 * 2.0 = 3.0 (exact)."""
    a_bits = _bits_from_hex_ieee("3FC00000")  # 1.5
    b_bits = _bits_from_hex_ieee("40000000")  # 2.0

    info = fmul_f32(a_bits, b_bits)
    result_bits = info["result"]
    hex_out = _hex_from_bits_ieee(result_bits)

    # 3.0
    assert hex_out == "40400000"


def test_mul_negative_times_positive():
    """-3.0 * 0.5 = -1.5."""
    minus_three = _bits_from_hex_ieee("C0400000")  # -3.0
    half = _bits_from_hex_ieee("3F000000")  # 0.5

    info = fmul_f32(minus_three, half)
    result_bits = info["result"]
    hex_out = _hex_from_bits_ieee(result_bits)

    # -1.5
    assert hex_out == "BFC00000"


def test_mul_zero_and_signs():
    """Zero * finite respects sign in the raw IEEE pattern."""
    plus_zero = _bits_from_hex_ieee("00000000")
    minus_zero = _bits_from_hex_ieee("80000000")
    three = _bits_from_hex_ieee("40400000")  # 3.0

    # +0 * 3.0 -> +0
    info1 = fmul_f32(plus_zero, three)
    hex1 = _hex_from_bits_ieee(info1["result"])
    assert hex1 == "00000000"

    # -0 * 3.0 -> -0
    info2 = fmul_f32(minus_zero, three)
    hex2 = _hex_from_bits_ieee(info2["result"])
    assert hex2 == "80000000"


def test_mul_infinity_and_finite():
    """±inf * finite non-zero -> ±inf, sign is XOR of operand signs."""
    inf_pos = _bits_from_hex_ieee("7F800000")  # +inf
    inf_neg = _bits_from_hex_ieee("FF800000")  # -inf
    two_bits = _bits_from_hex_ieee("40000000")  # 2.0

    # +inf * 2.0 -> +inf
    info1 = fmul_f32(inf_pos, two_bits)
    hex1 = _hex_from_bits_ieee(info1["result"])
    # AI-END
    s1, e1, f1 = _extract_fields_from_hex(hex1)
    assert e1 == 0xFF  # exponent all ones
    assert f1 == 0  # fraction zero
    assert s1 == 0  # positive
    assert hex1 == "7F800000"
    # AI-BEGIN

    # -inf * 2.0 -> -inf
    info2 = fmul_f32(inf_neg, two_bits)
    hex2 = _hex_from_bits_ieee(info2["result"])
    s2, e2, f2 = _extract_fields_from_hex(hex2)
    assert e2 == 0xFF
    assert f2 == 0
    assert s2 == 1
    assert hex2 == "FF800000"


def test_mul_zero_times_infinity_is_nan():
    """0 * inf or inf * 0 -> NaN with invalid flag set."""
    plus_zero = _bits_from_hex_ieee("00000000")
    inf_pos = _bits_from_hex_ieee("7F800000")

    # 0 * +inf
    info1 = fmul_f32(plus_zero, inf_pos)
    # AI-END
    hex1 = _hex_from_bits_ieee(info1["result"])
    _, e1, f1 = _extract_fields_from_hex(hex1)
    # NaN: exponent all ones, fraction non-zero
    assert e1 == 0xFF
    assert f1 != 0
    assert info1["flags"]["invalid"] is True
    # AI-BEGIN

    # +inf * 0
    info2 = fmul_f32(inf_pos, plus_zero)
    # AI-END
    hex2 = _hex_from_bits_ieee(info2["result"])
    _, e2, f2 = _extract_fields_from_hex(hex2)
    assert e2 == 0xFF
    assert f2 != 0
    assert info2["flags"]["invalid"] is True
