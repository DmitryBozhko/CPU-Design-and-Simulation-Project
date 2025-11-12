from __future__ import annotations

from typing import Literal

from .adders import ripple_carry_adder
from .comparators import compare_unsigned, is_zero
from .shifter import srl, sll
from .twos_complement import negate_twos_complement

FloatClass = Literal["zero", "subnormal", "normal", "infinity", "nan"]

_EXP_WIDTH = 8
_FRAC_WIDTH = 23
_MANT_WIDTH = 24        # 23 frac bits + 1 implicit bit
_MANT_EXT_WIDTH = 25    # extended mantissa width for add (not used yet, but reserved)
_WORD_WIDTH = 32
_EXP_BIAS_BITS_127 = [1, 1, 1, 1, 1, 1, 1, 0]

# Nibble <-> bits helpers (LSB-first for each nibble)
_HEX_TO_BITS_LSB = {
    "0": [0, 0, 0, 0],
    "1": [1, 0, 0, 0],
    "2": [0, 1, 0, 0],
    "3": [1, 1, 0, 0],
    "4": [0, 0, 1, 0],
    "5": [1, 0, 1, 0],
    "6": [0, 1, 1, 0],
    "7": [1, 1, 1, 0],
    "8": [0, 0, 0, 1],
    "9": [1, 0, 0, 1],
    "A": [0, 1, 0, 1],
    "B": [1, 1, 0, 1],
    "C": [0, 0, 1, 1],
    "D": [1, 0, 1, 1],
    "E": [0, 1, 1, 1],
    "F": [1, 1, 1, 1],
}

_BITS_TO_HEX = {
    (0, 0, 0, 0): "0",
    (1, 0, 0, 0): "1",
    (0, 1, 0, 0): "2",
    (1, 1, 0, 0): "3",
    (0, 0, 1, 0): "4",
    (1, 0, 1, 0): "5",
    (0, 1, 1, 0): "6",
    (1, 1, 1, 0): "7",
    (0, 0, 0, 1): "8",
    (1, 0, 0, 1): "9",
    (0, 1, 0, 1): "A",
    (1, 1, 0, 1): "B",
    (0, 0, 1, 1): "C",
    (1, 0, 1, 1): "D",
    (0, 1, 1, 1): "E",
    (1, 1, 1, 1): "F",
}


def _import_bits32_to_hex() -> "bits32_to_hex":
    from .conversions import bits32_to_hex

    return bits32_to_hex


def _import_hex_to_bits32() -> "hex_to_bits32":
    from .conversions import hex_to_bits32

    return hex_to_bits32


# ==========
# Utilities
# ==========


def _ensure_word32(bits32: list[int]) -> list[int]:
    """Normalize and validate a 32-bit input list."""
    normalized: list[int] = []
    for bit in bits32[:_WORD_WIDTH]:
        normalized.append(bit & 1)

    try:
        _ = bits32[31]
    except IndexError as exc:  # pragma: no cover - defensive
        raise ValueError("float32 value must contain 32 bits") from exc

    if bits32[32:]:
        raise ValueError("float32 value must contain exactly 32 bits")

    return normalized


def _all_zero(bits: list[int]) -> bool:
    for bit in bits:
        if bit & 1:
            return False
    return True


def _all_ones(bits: list[int]) -> bool:
    if not bits:
        return False
    for bit in bits:
        if (bit & 1) ^ 1:
            return False
    return True


def _normalize_bits_to_width(bits: list[int], width: int) -> list[int]:
    """Return a copy of bits truncated/padded with zeros to 'width'."""
    normalized: list[int] = []
    length = len(bits)
    index = 0
    while index < width:
        if index < length:
            normalized.append(bits[index] & 1)
        else:
            normalized.append(0)
        index = index + 1
    return normalized


def _split_fields_no_plus(bits32: list[int]) -> tuple[int, list[int], list[int]]:
    """Decode IEEE-754 fields using the canonical hex representation.

    Strategy:
      * bits32 -> hex via bits32_to_hex (using existing conversions logic)
      * hex -> canonical bits[0..31] where index = bit position (LSB-first)
      * slice out sign, exponent, fraction from canonical bits
    """
    word = _ensure_word32(bits32)

    bits32_to_hex = _import_bits32_to_hex()
    hex_str = bits32_to_hex(word)

    canonical: list[int] = []
    pos = 7
    while pos >= 0:
        ch = hex_str[pos].upper()
        nibble_bits = _HEX_TO_BITS_LSB[ch]
        for b in nibble_bits:
            canonical.append(b & 1)
        pos = pos - 1

    sign = canonical[31] & 1

    exponent: list[int] = []
    i = 0
    while i < _EXP_WIDTH:
        exponent.append(canonical[23 + i] & 1)
        i = i + 1

    fraction: list[int] = []
    j = 0
    while j < _FRAC_WIDTH:
        fraction.append(canonical[j] & 1)
        j = j + 1

    return sign, exponent, fraction


def _assemble_fields(sign: int, exponent: list[int], fraction: list[int]) -> list[int]:
    """Assemble IEEE-754 pattern from fields, then map back to bits32 layout."""
    exp_norm = _normalize_bits_to_width(exponent, _EXP_WIDTH)
    frac_norm = _normalize_bits_to_width(fraction, _FRAC_WIDTH)

    canonical: list[int] = []
    k = 0
    while k < _WORD_WIDTH:
        canonical.append(0)
        k = k + 1

    # Fraction bits 0..22
    i = 0
    while i < _FRAC_WIDTH:
        canonical[i] = frac_norm[i] & 1
        i = i + 1

    # Exponent bits 23..30 (LSB-first)
    j = 0
    while j < _EXP_WIDTH:
        canonical[23 + j] = exp_norm[j] & 1
        j = j + 1

    # Sign bit 31
    canonical[31] = sign & 1

    # Canonical bits -> hex string
    chars: list[str] = []

    n0 = (canonical[0] & 1, canonical[1] & 1, canonical[2] & 1, canonical[3] & 1)
    chars.append(_BITS_TO_HEX[n0])

    n1 = (canonical[4] & 1, canonical[5] & 1, canonical[6] & 1, canonical[7] & 1)
    chars.append(_BITS_TO_HEX[n1])

    n2 = (canonical[8] & 1, canonical[9] & 1, canonical[10] & 1, canonical[11] & 1)
    chars.append(_BITS_TO_HEX[n2])

    n3 = (canonical[12] & 1, canonical[13] & 1, canonical[14] & 1, canonical[15] & 1)
    chars.append(_BITS_TO_HEX[n3])

    n4 = (canonical[16] & 1, canonical[17] & 1, canonical[18] & 1, canonical[19] & 1)
    chars.append(_BITS_TO_HEX[n4])

    n5 = (canonical[20] & 1, canonical[21] & 1, canonical[22] & 1, canonical[23] & 1)
    chars.append(_BITS_TO_HEX[n5])

    n6 = (canonical[24] & 1, canonical[25] & 1, canonical[26] & 1, canonical[27] & 1)
    chars.append(_BITS_TO_HEX[n6])

    n7 = (canonical[28] & 1, canonical[29] & 1, canonical[30] & 1, canonical[31] & 1)
    chars.append(_BITS_TO_HEX[n7])

    chars.reverse()
    hex_str = "".join(chars)

    hex_to_bits32 = _import_hex_to_bits32()
    return hex_to_bits32(hex_str)


def _classify(exponent: list[int], fraction: list[int]) -> FloatClass:
    exp_all_zero = _all_zero(exponent)
    exp_all_ones = _all_ones(exponent)
    frac_all_zero = _all_zero(fraction)

    if exp_all_zero and frac_all_zero:
        return "zero"
    if exp_all_zero and (not frac_all_zero):
        return "subnormal"
    if exp_all_ones and frac_all_zero:
        return "infinity"
    if exp_all_ones and (not frac_all_zero):
        return "nan"
    return "normal"


def _split_fields_ieee(bits: list[int]) -> tuple[int, list[int], list[int]]:
    """Decode IEEE-754 float32 from canonical LSB-first bits."""
    canonical: list[int] = []
    idx = 0
    while idx < _WORD_WIDTH:
        canonical.append(bits[idx] & 1)
        idx = idx + 1

    sign = canonical[31] & 1

    exponent: list[int] = []
    i = 0
    while i < _EXP_WIDTH:
        exponent.append(canonical[23 + i] & 1)
        i = i + 1

    fraction: list[int] = []
    j = 0
    while j < _FRAC_WIDTH:
        fraction.append(canonical[j] & 1)
        j = j + 1

    return sign, exponent, fraction


def _assemble_ieee(sign: int, exponent: list[int], fraction: list[int]) -> list[int]:
    """Assemble IEEE-754 float32 into canonical LSB-first bits."""
    exp_norm = _normalize_bits_to_width(exponent, _EXP_WIDTH)
    frac_norm = _normalize_bits_to_width(fraction, _FRAC_WIDTH)

    bits: list[int] = []
    k = 0
    while k < _WORD_WIDTH:
        bits.append(0)
        k = k + 1

    i = 0
    while i < _FRAC_WIDTH:
        bits[i] = frac_norm[i] & 1
        i = i + 1

    j = 0
    while j < _EXP_WIDTH:
        bits[23 + j] = exp_norm[j] & 1
        j = j + 1

    bits[31] = sign & 1

    return bits


def _increment_bits(bits: list[int]) -> list[int]:
    """Increment a bit-vector by 1 (little-endian) using ripple_carry_adder."""
    one: list[int] = [1]
    inc, _ = ripple_carry_adder(bits, one)
    return _normalize_bits_to_width(inc, len(bits))


def _decrement_bits(bits: list[int]) -> list[int]:
    """Decrement a bit-vector by 1: x - 1 = x + (-1) in two's complement."""
    width = len(bits)
    negative_one: list[int] = []
    c = 0
    while c < width:
        negative_one.append(1)
        c = c + 1
    dec, _ = ripple_carry_adder(bits, negative_one)
    return _normalize_bits_to_width(dec, width)


def _compare_magnitude(mant_a: list[int], mant_b: list[int]) -> int:
    """Unsigned compare mantissas (same width). Return -1, 0, 1."""
    return compare_unsigned(mant_a, mant_b)


def _build_mantissa(fclass: FloatClass, fraction: list[int]) -> list[int]:
    """Build a 24-bit mantissa with correct implicit bit."""
    mantissa: list[int] = []
    i = 0
    while i < _MANT_WIDTH:
        mantissa.append(0)
        i = i + 1

    frac_norm = _normalize_bits_to_width(fraction, _FRAC_WIDTH)

    idx = 0
    while idx < _FRAC_WIDTH:
        mantissa[idx] = frac_norm[idx] & 1
        idx = idx + 1

    if fclass == "normal":
        mantissa[_FRAC_WIDTH] = 1

    return mantissa


def _mantissa_is_zero(mant: list[int]) -> bool:
    return is_zero(mant)


# =========================
# Public pack / unpack API
# =========================


def pack_f32_from_fields(
    sign: int,
    exponent_bits: list[int],
    fraction_bits: list[int],
) -> list[int]:
    return _assemble_fields(sign, exponent_bits, fraction_bits)


def unpack_f32(bits32: list[int]) -> dict:
    sign, exponent, fraction = _split_fields_no_plus(bits32)
    fclass = _classify(exponent, fraction)
    return {
        "sign": sign,
        "exponent": exponent,
        "fraction": fraction,
        "class": fclass,
    }


def pack_f32_raw(bits32: list[int]) -> list[int]:
    return _ensure_word32(bits32)


# =========================
# Arithmetic: fadd / fsub / fmul
# =========================


def _make_quiet_nan() -> list[int]:
    """Return a canonical quiet NaN bit pattern in project bits32 layout."""
    exponent: list[int] = []
    i = 0
    while i < _EXP_WIDTH:
        exponent.append(1)
        i = i + 1

    fraction: list[int] = []
    # quiet NaN: any non-zero fraction; set the top stored bit
    fraction.append(1)
    while len(fraction) < _FRAC_WIDTH:
        fraction.append(0)

    return _assemble_fields(0, exponent, fraction)


def fadd_f32(a_bits: list[int], b_bits: list[int]) -> dict:
    """Float32 addition: a + b (first-pass implementation)."""
    trace: list[dict[str, object]] = []

    a_sign, a_exp, a_frac = _split_fields_ieee(a_bits)
    b_sign, b_exp, b_frac = _split_fields_ieee(b_bits)

    a_class = _classify(a_exp, a_frac)
    b_class = _classify(b_exp, b_frac)

    # ---- Special cases: NaNs ----
    if a_class == "nan" or b_class == "nan":
        return {
            "result": _make_quiet_nan(),
            "flags": {
                "overflow": False,
                "underflow": False,
                "invalid": True,
                "inexact": True,
            },
            "trace": trace,
        }

    # ---- Special cases: infinities ----
    if a_class == "infinity" and b_class == "infinity":
        if (a_sign ^ b_sign) & 1:
            return {
                "result": _make_quiet_nan(),
                "flags": {
                    "overflow": False,
                    "underflow": False,
                    "invalid": True,
                    "inexact": True,
                },
                "trace": trace,
            }
        return {
            "result": _assemble_ieee(a_sign, a_exp, a_frac),
            "flags": {
                "overflow": False,
                "underflow": False,
                "invalid": False,
                "inexact": False,
            },
            "trace": trace,
        }

    if a_class == "infinity":
        return {
            "result": _assemble_fields(a_sign, a_exp, a_frac),
            "flags": {
                "overflow": False,
                "underflow": False,
                "invalid": False,
                "inexact": False,
            },
            "trace": trace,
        }

    if b_class == "infinity":
        return {
            "result": _assemble_fields(b_sign, b_exp, b_frac),
            "flags": {
                "overflow": False,
                "underflow": False,
                "invalid": False,
                "inexact": False,
            },
            "trace": trace,
        }

    # ---- Zero handling ----
    if a_class == "zero" and b_class == "zero":
        result_sign = a_sign & b_sign
        zero_exp = _normalize_bits_to_width(a_exp, _EXP_WIDTH)
        zero_frac = _normalize_bits_to_width(a_frac, _FRAC_WIDTH)
        return {
            "result": _assemble_ieee(result_sign, zero_exp, zero_frac),
            "flags": {
                "overflow": False,
                "underflow": False,
                "invalid": False,
                "inexact": False,
            },
            "trace": trace,
        }

    if a_class == "zero":
        return {
            "result": _assemble_ieee(b_sign, b_exp, b_frac),
            "flags": {
                "overflow": False,
                "underflow": False,
                "invalid": False,
                "inexact": False,
            },
            "trace": trace,
        }

    if b_class == "zero":
        return {
            "result": _assemble_fields(a_sign, a_exp, a_frac),
            "flags": {
                "overflow": False,
                "underflow": False,
                "invalid": False,
                "inexact": False,
            },
            "trace": trace,
        }

    # ---- Build mantissas (normal/subnormal) ----
    mant_a = _build_mantissa(a_class, a_frac)
    mant_b = _build_mantissa(b_class, b_frac)

    exp_a = _normalize_bits_to_width(a_exp, _EXP_WIDTH)
    exp_b = _normalize_bits_to_width(b_exp, _EXP_WIDTH)

    # ---- Make sure A has >= exponent ----
    cmp_exp = compare_unsigned(exp_a, exp_b)
    if cmp_exp == -1:
        tmp_sign = a_sign
        a_sign = b_sign
        b_sign = tmp_sign

        tmp_class = a_class
        a_class = b_class
        b_class = tmp_class

        tmp_exp = exp_a
        exp_a = exp_b
        exp_b = tmp_exp

        tmp_mant = mant_a
        mant_a = mant_b
        mant_b = tmp_mant

    # ---- Align exponents ----
    while True:
        cmp_exp = compare_unsigned(exp_a, exp_b)
        if cmp_exp == 0:
            break

        mant_b = srl(mant_b, 1)
        exp_b = _increment_bits(exp_b)

        if _mantissa_is_zero(mant_b):
            break

    trace.append(
        {
            "stage": "aligned",
            "a_sign": a_sign,
            "b_sign": b_sign,
            "exp_a": exp_a[:],
            "exp_b": exp_b[:],
            "mant_a": mant_a[:],
            "mant_b": mant_b[:],
        }
    )

    result_sign = a_sign
    overflow_flag = False
    underflow_flag = False

    if a_sign == b_sign:
        mant_sum, carry = ripple_carry_adder(mant_a, mant_b)

        if carry:
            mant_shifted = srl(mant_sum, 1)
            mant_result = _normalize_bits_to_width(mant_shifted, _MANT_WIDTH)
            exp_a = _increment_bits(exp_a)
            if _all_ones(exp_a):
                overflow_flag = True
        else:
            mant_result = _normalize_bits_to_width(mant_sum, _MANT_WIDTH)

    else:
        cmp_m = _compare_magnitude(mant_a, mant_b)
        if cmp_m == 0:
            zero_exp: list[int] = []
            i = 0
            while i < _EXP_WIDTH:
                zero_exp.append(0)
                i = i + 1
            zero_frac: list[int] = []
            j = 0
            while j < _FRAC_WIDTH:
                zero_frac.append(0)
                j = j + 1
            result_bits = _assemble_ieee(0, zero_exp, zero_frac)
            return {
                "result": result_bits,
                "flags": {
                    "overflow": False,
                    "underflow": False,
                    "invalid": False,
                    "inexact": False,
                },
                "trace": trace,
            }

        if cmp_m == -1:
            mant_a, mant_b = mant_b, mant_a
            result_sign = b_sign

        neg_b = negate_twos_complement(mant_b)
        mant_diff, _ = ripple_carry_adder(mant_a, neg_b)
        mant_result = _normalize_bits_to_width(mant_diff, _MANT_WIDTH)

        msb_index = _MANT_WIDTH - 1
        top_bit = mant_result[msb_index] & 1
        if (top_bit ^ 1) & 1 and (not _mantissa_is_zero(mant_result)):
            mant_result = sll(mant_result, 1)
            exp_a = _decrement_bits(exp_a)
            if _all_zero(exp_a):
                underflow_flag = True

    trace.append(
        {
            "stage": "mantissa_combined",
            "sign": result_sign,
            "exp": exp_a[:],
            "mant": mant_result[:],
        }
    )

    # ---- Pack back into float32 layout ----
    fraction_result: list[int] = []
    idx = 0
    while idx < _FRAC_WIDTH:
        fraction_result.append(mant_result[idx] & 1)
        idx = idx + 1

    exponent_result = _normalize_bits_to_width(exp_a, _EXP_WIDTH)
    result_bits = _assemble_ieee(result_sign, exponent_result, fraction_result)

    flags = {
        "overflow": overflow_flag,
        "underflow": underflow_flag,
        "invalid": False,
        "inexact": False,
    }

    return {
        "result": result_bits,
        "flags": flags,
        "trace": trace,
    }


def fsub_f32(a_bits: list[int], b_bits: list[int]) -> dict:
    """Float32 subtraction: a - b where bits are IEEE canonical (LSB-first)."""
    b_norm: list[int] = []
    idx = 0
    while idx < _WORD_WIDTH:
        bit = b_bits[idx] & 1
        if idx == 31:  # sign bit
            bit = bit ^ 1
        b_norm.append(bit)
        idx = idx + 1
    return fadd_f32(a_bits, b_norm)


def fmul_f32(a_bits: list[int], b_bits: list[int]) -> dict:
    """Float32 multiplication: a * b using bit-vectors only.

    Steps (IEEE-754-ish):
      * Handle NaN / Inf / zero special cases
      * Build 24-bit significands (with implicit bit for normals)
      * Add exponents and subtract bias
      * Multiply significands via shift-add into a 48-bit product
      * Normalize and repack
    Rounding is simplified to truncation toward zero, with a coarse inexact flag.
    """
    trace: list[dict[str, object]] = []

    # Unpack from canonical IEEE LSB-first bits
    a_sign, a_exp, a_frac = _split_fields_ieee(a_bits)
    b_sign, b_exp, b_frac = _split_fields_ieee(b_bits)

    a_class = _classify(a_exp, a_frac)
    b_class = _classify(b_exp, b_frac)

    # -----------------------
    # Special cases: NaNs
    # -----------------------
    if a_class == "nan" or b_class == "nan":
        return {
            "result": _make_quiet_nan(),
            "flags": {
                "overflow": False,
                "underflow": False,
                "invalid": True,
                "inexact": True,
            },
            "trace": trace,
        }

    # -----------------------
    # Special cases: infinities and zeros
    # -----------------------
    is_a_zero = a_class == "zero"
    is_b_zero = b_class == "zero"
    is_a_inf = a_class == "infinity"
    is_b_inf = b_class == "infinity"

    # 0 * Inf or Inf * 0 -> NaN (invalid)
    if (is_a_zero and is_b_inf) or (is_b_zero and is_a_inf):
        return {
            "result": _make_quiet_nan(),
            "flags": {
                "overflow": False,
                "underflow": False,
                "invalid": True,
                "inexact": True,
            },
            "trace": trace,
        }

    # Any infinity * finite non-zero -> infinity (sign XOR)
    if is_a_inf or is_b_inf:
        res_sign = (a_sign ^ b_sign) & 1
        exp_all_ones: list[int] = []
        idx = 0
        while idx < _EXP_WIDTH:
            exp_all_ones.append(1)
            idx = idx + 1
        frac_zero: list[int] = []
        j = 0
        while j < _FRAC_WIDTH:
            frac_zero.append(0)
            j = j + 1
        result_bits = _assemble_ieee(res_sign, exp_all_ones, frac_zero)
        return {
            "result": result_bits,
            "flags": {
                "overflow": False,   # IEEE says inf is representable
                "underflow": False,
                "invalid": False,
                "inexact": False,
            },
            "trace": trace,
        }

    # Any zero * finite non-infinity -> zero (sign XOR)
    if is_a_zero or is_b_zero:
        res_sign = (a_sign ^ b_sign) & 1
        exp_zero: list[int] = []
        idx = 0
        while idx < _EXP_WIDTH:
            exp_zero.append(0)
            idx = idx + 1
        frac_zero: list[int] = []
        j = 0
        while j < _FRAC_WIDTH:
            frac_zero.append(0)
            j = j + 1
        result_bits = _assemble_ieee(res_sign, exp_zero, frac_zero)
        return {
            "result": result_bits,
            "flags": {
                "overflow": False,
                "underflow": False,
                "invalid": False,
                "inexact": False,
            },
            "trace": trace,
        }

    # -----------------------
    # Finite, non-zero operands
    # -----------------------
    res_sign = (a_sign ^ b_sign) & 1

    # Build 24-bit mantissas (with implicit bit for normals)
    mant_a = _build_mantissa(a_class, a_frac)
    mant_b = _build_mantissa(b_class, b_frac)

    # Effective exponents for subnormals: treat exponent as 1 for math
    # (so that subnormal has exponent 1 - bias).
    exp_a_eff = _normalize_bits_to_width(a_exp, _EXP_WIDTH)
    if a_class == "subnormal":
        exp_a_eff = []
        k = 0
        while k < _EXP_WIDTH:
            exp_a_eff.append(0)
            k = k + 1
        exp_a_eff[0] = 1  # value = 1

    exp_b_eff = _normalize_bits_to_width(b_exp, _EXP_WIDTH)
    if b_class == "subnormal":
        exp_b_eff = []
        k = 0
        while k < _EXP_WIDTH:
            exp_b_eff.append(0)
            k = k + 1
        exp_b_eff[0] = 1

    # Sum exponents: exp_a_eff + exp_b_eff
    exp_sum, _ = ripple_carry_adder(exp_a_eff, exp_b_eff)
    exp_sum = _normalize_bits_to_width(exp_sum, _EXP_WIDTH)

    # Subtract bias: exp_sum - 127
    neg_bias = negate_twos_complement(_EXP_BIAS_BITS_127)
    exp_tmp, _ = ripple_carry_adder(exp_sum, neg_bias)
    exp_tmp = _normalize_bits_to_width(exp_tmp, _EXP_WIDTH)

    trace.append(
        {
            "stage": "exponent_combined",
            "exp_a_eff": exp_a_eff[:],
            "exp_b_eff": exp_b_eff[:],
            "exp_sum": exp_sum[:],
            "exp_minus_bias": exp_tmp[:],
        }
    )

    # -----------------------
    # Multiply mantissas via shift-add
    # -----------------------
    product_width = 48
    product: list[int] = []
    idx = 0
    while idx < product_width:
        product.append(0)
        idx = idx + 1

    # Track any discarded low bits for inexact flag later
    inexact_flag = False

    bit_index = 0
    while bit_index < _MANT_WIDTH:
        if mant_b[bit_index] & 1:
            term = _normalize_bits_to_width(mant_a, product_width)

            # left shift term by bit_index using sll
            shift_count = 0
            while shift_count < bit_index:
                term = sll(term, 1)
                term = _normalize_bits_to_width(term, product_width)
                shift_count = shift_count + 1

            # product += term
            product, _ = ripple_carry_adder(product, term)
            product = _normalize_bits_to_width(product, product_width)

        bit_index = bit_index + 1

    # Any non-zero bits in the lower 23 bits imply inexact when we truncate
    low = 0
    while low < 23:
        if product[low] & 1:
            inexact_flag = True
            break
        low = low + 1

    trace.append(
        {
            "stage": "mantissa_product",
            "mant_a": mant_a[:],
            "mant_b": mant_b[:],
            "product": product[:],
        }
    )

    # -----------------------
    # Normalize product to 24-bit mantissa with an extra guard bit
    # We form a 25-bit mantissa as product >> 23.
    # -----------------------
    mant_ext: list[int] = []
    idx = 0
    while idx < (_MANT_WIDTH + 1):  # 25 bits
        src_pos = idx + 23
        if src_pos < product_width:
            mant_ext.append(product[src_pos] & 1)
        else:
            mant_ext.append(0)
        idx = idx + 1

    # Now mant_ext[0..24] corresponds to product bits [23..47].
    # If the top bit (24) is set, shift right once more and bump exponent.
    if mant_ext[_MANT_WIDTH] & 1:  # index 24
        mant_ext = srl(mant_ext, 1)
        mant_ext = _normalize_bits_to_width(mant_ext, _MANT_WIDTH + 1)
        exp_tmp = _increment_bits(exp_tmp)

    # Check exponent overflow after normalization
    overflow_flag = False
    underflow_flag = False

    if _all_ones(exp_tmp):
        overflow_flag = True
        # Saturate to infinity
        exp_inf: list[int] = []
        i = 0
        while i < _EXP_WIDTH:
            exp_inf.append(1)
            i = i + 1
        frac_zero: list[int] = []
        j = 0
        while j < _FRAC_WIDTH:
            frac_zero.append(0)
            j = j + 1
        result_inf = _assemble_ieee(res_sign, exp_inf, frac_zero)
        return {
            "result": result_inf,
            "flags": {
                "overflow": True,
                "underflow": False,
                "invalid": False,
                "inexact": True,
            },
            "trace": trace,
        }

    # If exponent is all zero but mantissa non-zero, treat as subnormal.
    if _all_zero(exp_tmp) and (not _mantissa_is_zero(mant_ext)):
        underflow_flag = True
        # Keep exponent = 0, drop implicit bit; just truncate mantissa ext.
        # (This is a simplification; we aren't fully denormalizing by shifting repeatedly.)
        exp_res = exp_tmp
        mant_for_pack = mant_ext
    else:
        exp_res = exp_tmp
        mant_for_pack = mant_ext

    # -----------------------
    # Drop implicit leading bit and pack fraction bits 0..22
    # -----------------------
    fraction_result: list[int] = []
    idx = 0
    while idx < _FRAC_WIDTH:
        fraction_result.append(mant_for_pack[idx] & 1)
        idx = idx + 1

    exponent_result = _normalize_bits_to_width(exp_res, _EXP_WIDTH)
    result_bits = _assemble_ieee(res_sign, exponent_result, fraction_result)

    flags = {
        "overflow": overflow_flag,
        "underflow": underflow_flag,
        "invalid": False,
        "inexact": inexact_flag,
    }

    return {
        "result": result_bits,
        "flags": flags,
        "trace": trace,
    }
