from __future__ import annotations
from typing import Callable, Literal
from .adders import ripple_carry_adder
from .comparators import compare_unsigned, is_zero
from .shifter import srl, sll
from .twos_complement import negate_twos_complement
from src.numeric_core.conversions import hex_to_bits32

FloatClass = Literal["zero", "subnormal", "normal", "infinity", "nan"]
_EXP_WIDTH = 8
_FRAC_WIDTH = 23
_MANT_WIDTH = 24
_WORD_WIDTH = 32
_EXP_BIAS_BITS_127 = [1, 1, 1, 1, 1, 1, 1, 0]
#AI-BEGIN
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
#AI-END

#AI-BEGIN
def _import_decimal_string_to_bits32() -> Callable[[str], list[int]]:

    """Late-bind decimal_string_to_bits32 to avoid circular imports."""

    from .conversions import decimal_string_to_bits32
    return decimal_string_to_bits32


def _import_bits32_to_decimal_string() -> Callable[[list[int]], str]:
    """Late-bind bits32_to_decimal_string to avoid circular imports."""
    from .conversions import bits32_to_decimal_string
    return bits32_to_decimal_string


def _import_bits32_to_hex() -> Callable[[list[int]], str]:

    """Late-bind bits32_to_hex to avoid circular imports."""

    from .conversions import bits32_to_hex
    return bits32_to_hex



def _bits_from_hex(hex_str: str) -> list[int]:
    return hex_to_bits32(hex_str)


def _import_hex_to_bits32() -> Callable[[str], list[int]]:
    """Late-bind hex_to_bits32 to avoid circular imports."""

    from .conversions import hex_to_bits32
    return hex_to_bits32
#AI-END


def _ensure_word32(bits32: list[int]) -> list[int]:
    #AI-BEGIN
    """Normalize and validate a 32-bit float word."""
    #AI-END
    normalized: list[int] = []
    for bit in bits32[:_WORD_WIDTH]:
        normalized.append(bit & 1)
    try:
        _ = bits32[31]
    except IndexError as exc: #AI-BEGIN # pragma: no cover - defensive #AI-END
        raise ValueError("float32 value must contain 32 bits") from exc
    if bits32[32:]:
        raise ValueError("float32 value must contain exactly 32 bits")
    return normalized

#AI-BEGIN
def _all_zero(bits: list[int]) -> bool:
    """Return True if all bits in the vector are zero."""
    for bit in bits:
        if bit & 1:
            return False
    return True
#AI-END


def _all_ones(bits: list[int]) -> bool:
    # AI-BEGIN
    """Return True if all bits in the vector are ones."""
    # AI-END
    if not bits:
        return False
    for bit in bits:
        if (bit & 1) ^ 1:
            return False
    return True


def _normalize_bits_to_width(bits: list[int], width: int) -> list[int]:
    # AI-BEGIN
    """Clamp or zero-extend a bit vector to the requested width."""
    # AI-END
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

# AI-BEGIN
def _split_fields_no_plus(bits32: list[int]) -> tuple[int, list[int], list[int]]:
    """Decode sign, exponent, and fraction from a 32-bit float pattern."""
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
# AI-END


# AI-BEGIN
def _assemble_fields(sign: int, exponent: list[int], fraction: list[int]) -> list[int]:
    """Assemble sign, exponent, and fraction into a canonical float32 pattern.

    This is now just a thin wrapper around _assemble_ieee, kept for
    compatibility with existing callers.
    """
    exp_norm = _normalize_bits_to_width(exponent, _EXP_WIDTH)
    frac_norm = _normalize_bits_to_width(fraction, _FRAC_WIDTH)
    return _assemble_ieee(sign, exp_norm, frac_norm)
# AI-EN


def _classify(exponent: list[int], fraction: list[int]) -> FloatClass:
    # AI-BEGIN
    """Classify a float32 pattern as zero, subnormal, normal, infinity, or NaN."""
    # AI-END
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
    # AI-BEGIN
    """Split a raw 32-bit pattern into sign, exponent, and fraction fields."""
    # AI-END
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
    # AI-BEGIN
    """Assemble IEEE-754 float32 fields into a 32-bit bit vector."""
    # AI-END
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
    # AI-BEGIN
    """Increment a bit vector by one using the ripple-carry adder."""
    # AI-END
    one: list[int] = [1]
    inc, _ = ripple_carry_adder(bits, one)
    return _normalize_bits_to_width(inc, len(bits))


def _decrement_bits(bits: list[int]) -> list[int]:
    # AI-BEGIN
    """Decrement a bit vector by one in two’s complement form."""
    # AI-END
    width = len(bits)
    negative_one: list[int] = []
    c = 0
    while c < width:
        negative_one.append(1)
        c = c + 1
    dec, _ = ripple_carry_adder(bits, negative_one)
    return _normalize_bits_to_width(dec, width)


def _compare_magnitude(mant_a: list[int], mant_b: list[int]) -> int:
    """Compare mantissa magnitudes as unsigned bit vectors."""
    return compare_unsigned(mant_a, mant_b)


def _build_mantissa(fclass: FloatClass, fraction: list[int]) -> list[int]:
    # AI-BEGIN
    """Construct a 24-bit mantissa, adding the hidden bit for normal values."""
    # AI-END
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
    # AI-BEGIN
    """Return True if the mantissa has no non-zero bits."""
    # AI-END
    return is_zero(mant)


def _round_rne_mantissa(
    mant: list[int],
    guard_bit: int,
    sticky_bit: int,
) -> tuple[list[int], int, bool]:
    mant_norm = _normalize_bits_to_width(mant, len(mant))
    exp_carry = 0
    inexact = False
    g = guard_bit & 1
    s = sticky_bit & 1
    if g == 0 and s == 0:
        return mant_norm, exp_carry, False
    inexact = True
    round_up = 0
    if g == 1:
        if s == 1:
            round_up = 1
        else:
            lsb = mant_norm[0] & 1
            if lsb == 1:
                round_up = 1
    else:
        round_up = 0
    if round_up:
        one: list[int] = [1]
        inc, carry = ripple_carry_adder(mant_norm, one)
        mant_norm = _normalize_bits_to_width(inc, len(mant_norm))
        if carry:
            exp_carry = 1
    return mant_norm, exp_carry, inexact


def pack_f32_from_fields(
    sign: int,
    exponent_bits: list[int],
    fraction_bits: list[int],
) -> list[int]:
    #AI-BEGIN
    """Pack sign, exponent, and fraction fields into float32 bits."""
    #AI-END
    exp_norm = _normalize_bits_to_width(exponent_bits, _EXP_WIDTH)
    frac_norm = _normalize_bits_to_width(fraction_bits, _FRAC_WIDTH)
    return _assemble_ieee(sign, exp_norm, frac_norm)


def unpack_f32_fields(bits32: list[int]) -> dict:
    #AI-BEGIN
    """Unpack float32 bits into sign, exponent, fraction, and class metadata."""
    #AI-END
    norm = _ensure_word32(bits32)
    sign, exponent, fraction = _split_fields_ieee(norm)
    fclass = _classify(exponent, fraction)
    return {
        "sign": sign,
        "exponent": exponent,
        "fraction": fraction,
        "class": fclass,
    }


def pack_f32_raw(bits32: list[int]) -> list[int]:
    # AI-BEGIN
    """Normalize a raw 32-bit pattern into canonical float32 bits."""
    # AI-END
    return _ensure_word32(bits32)


def pack_f32(value: float | str) -> list[int]:
    decimal_to_bits32 = _import_decimal_string_to_bits32()
    if isinstance(value, str):
        value_str = value
    else:
        value_str = repr(value)
    bits32 = decimal_to_bits32(value_str)
    return _ensure_word32(bits32)


def unpack_f32(bits32: list[int]) -> str:
    #AI-BEGIN
    """Convert float32 bits back into a decimal string value."""
    #AI-END
    bits32_to_decimal = _import_bits32_to_decimal_string()
    normalized = _ensure_word32(bits32)
    decimal_str = bits32_to_decimal(normalized)
    return decimal_str

#AI-BEGIN
def _make_quiet_nan() -> list[int]:
    """Return a canonical quiet NaN bit pattern in IEEE bit layout."""
    return _make_quiet_nan_ieee()
#AI-END


def _make_quiet_nan_ieee(sign: int = 0) -> list[int]:
    # AI-BEGIN
    """Construct a quiet NaN directly from IEEE-754 fields."""
    # AI-END
    exponent: list[int] = []
    i = 0
    while i < _EXP_WIDTH:
        exponent.append(1)
        i = i + 1
    fraction: list[int] = []
    fraction.append(1)
    while len(fraction) < _FRAC_WIDTH:
        fraction.append(0)
    return _assemble_ieee(sign, exponent, fraction)


def fadd_f32(a_bits: list[int], b_bits: list[int]) -> dict:
    #AI-BEGIN
    """Perform IEEE-754 float32 addition with trace and flags."""
    #AI-END
    trace: list[dict[str, object]] = []
    a_sign, a_exp, a_frac = _split_fields_ieee(a_bits)
    b_sign, b_exp, b_frac = _split_fields_ieee(b_bits)
    a_class = _classify(a_exp, a_frac)
    b_class = _classify(b_exp, b_frac)
    trace.append(
        {
            "stage": "unpacked",
            "a_sign": a_sign,
            "a_exp": a_exp[:],
            "a_frac": a_frac[:],
            "a_class": a_class,
            "b_sign": b_sign,
            "b_exp": b_exp[:],
            "b_frac": b_frac[:],
            "b_class": b_class,
        }
    )
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
            "result": _assemble_ieee(a_sign, a_exp, a_frac),
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
            "result": _assemble_ieee(b_sign, b_exp, b_frac),
            "flags": {
                "overflow": False,
                "underflow": False,
                "invalid": False,
                "inexact": False,
            },
            "trace": trace,
        }
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
            "result": _assemble_ieee(a_sign, a_exp, a_frac),
            "flags": {
                "overflow": False,
                "underflow": False,
                "invalid": False,
                "inexact": False,
            },
            "trace": trace,
        }
    mant_a = _build_mantissa(a_class, a_frac)
    mant_b = _build_mantissa(b_class, b_frac)
    exp_a = _normalize_bits_to_width(a_exp, _EXP_WIDTH)
    exp_b = _normalize_bits_to_width(b_exp, _EXP_WIDTH)
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
    inexact_flag = False
    alignment_shifts = 0
    guard_bit = 0
    sticky_bit = 0
    while True:
        cmp_exp = compare_unsigned(exp_a, exp_b)
        if cmp_exp == 0:
            break
        lsb = mant_b[0] & 1
        if lsb:
            inexact_flag = True
        if guard_bit & 1:
            sticky_bit = 1
        guard_bit = lsb & 1
        mant_b = srl(mant_b, 1)
        exp_b = _increment_bits(exp_b)
        alignment_shifts = alignment_shifts + 1
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
            "alignment_shifts": alignment_shifts,
        }
    )
    result_sign = a_sign
    overflow_flag = False
    underflow_flag = False
    if a_sign == b_sign:
        mant_sum, carry = ripple_carry_adder(mant_a, mant_b)
        if carry:
            dropped_lsb = mant_sum[0] & 1
            if dropped_lsb:
                inexact_flag = True
            if guard_bit & 1:
                sticky_bit = 1
            guard_bit = dropped_lsb & 1
            mant_shifted = srl(mant_sum, 1)
            mant_result = _normalize_bits_to_width(mant_shifted, _MANT_WIDTH)
            exp_a = _increment_bits(exp_a)
            if _all_ones(exp_a):
                overflow_flag = True
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
                result_inf = _assemble_ieee(result_sign, exp_inf, frac_zero)
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
            tmp_m = mant_a
            mant_a = mant_b
            mant_b = tmp_m
            result_sign = b_sign
        neg_b = negate_twos_complement(mant_b)
        mant_diff, _ = ripple_carry_adder(mant_a, neg_b)
        mant_result = _normalize_bits_to_width(mant_diff, _MANT_WIDTH)
        msb_index = _MANT_WIDTH - 1
        normalization_shifts = 0
        if not _mantissa_is_zero(mant_result):
            while ((mant_result[msb_index] & 1) ^ 1) & 1:
                mant_result = sll(mant_result, 1)
                mant_result = _normalize_bits_to_width(mant_result, _MANT_WIDTH)
                normalization_shifts = normalization_shifts + 1
                if _all_zero(exp_a):
                    underflow_flag = True
                    break
                exp_a = _decrement_bits(exp_a)
        else:
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
    mant_main = _normalize_bits_to_width(mant_result, _MANT_WIDTH)
    mant_rounded, exp_carry, inexact_from_round = _round_rne_mantissa(
        mant_main,
        guard_bit,
        sticky_bit,
    )
    exp_res = _normalize_bits_to_width(exp_a, _EXP_WIDTH)
    if exp_carry:
        exp_res = _increment_bits(exp_res)
    exponent_result = _normalize_bits_to_width(exp_res, _EXP_WIDTH)
    if _all_ones(exponent_result):
        overflow_flag = True
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
        result_inf = _assemble_ieee(result_sign, exp_inf, frac_zero)
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

    fraction_result: list[int] = []
    idx = 0
    while idx < _FRAC_WIDTH:
        fraction_result.append(mant_rounded[idx] & 1)
        idx = idx + 1

    result_bits = _assemble_ieee(result_sign, exponent_result, fraction_result)
    if _all_zero(exponent_result) and (not _all_zero(fraction_result)):
        underflow_flag = True
    inexact_flag = inexact_flag or inexact_from_round
    if overflow_flag or underflow_flag:
        inexact_flag = True
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


def fsub_f32(a_bits: list[int], b_bits: list[int]) -> dict:
    # AI-BEGIN
    """Implement a − b as a + (−b) in float32 form."""
    # AI-END
    b_norm: list[int] = []
    idx = 0
    while idx < _WORD_WIDTH:
        bit = b_bits[idx] & 1
        if idx == 31:
            bit = bit ^ 1
        b_norm.append(bit)
        idx = idx + 1
    return fadd_f32(a_bits, b_norm)


def fmul_f32(a_bits: list[int], b_bits: list[int]) -> dict:
    # AI-BEGIN
    """Perform IEEE-754 float32 multiplication with trace and flags."""
    # AI-END

    trace: list[dict[str, object]] = []
    a_sign, a_exp, a_frac = _split_fields_ieee(a_bits)
    b_sign, b_exp, b_frac = _split_fields_ieee(b_bits)
    a_class = _classify(a_exp, a_frac)
    b_class = _classify(b_exp, b_frac)
    trace.append(
        {
            "stage": "unpacked",
            "a_sign": a_sign,
            "a_exp": a_exp[:],
            "a_frac": a_frac[:],
            "a_class": a_class,
            "b_sign": b_sign,
            "b_exp": b_exp[:],
            "b_frac": b_frac[:],
            "b_class": b_class,
        }
    )
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
    is_a_zero = a_class == "zero"
    is_b_zero = b_class == "zero"
    is_a_inf = a_class == "infinity"
    is_b_inf = b_class == "infinity"
    if (is_a_zero and is_b_inf) or (is_b_zero and is_a_inf):
        return {
            "result": _make_quiet_nan_ieee(),
            "flags": {
                "overflow": False,
                "underflow": False,
                "invalid": True,
                "inexact": True,
            },
            "trace": trace,
        }
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
                "overflow": False,
                "underflow": False,
                "invalid": False,
                "inexact": False,
            },
            "trace": trace,
        }
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
    res_sign = (a_sign ^ b_sign) & 1
    mant_a = _build_mantissa(a_class, a_frac)
    mant_b = _build_mantissa(b_class, b_frac)
    exp_a_eff = _normalize_bits_to_width(a_exp, _EXP_WIDTH)
    if a_class == "subnormal":
        exp_a_eff = []
        k = 0
        while k < _EXP_WIDTH:
            exp_a_eff.append(0)
            k = k + 1
        exp_a_eff[0] = 1
    exp_b_eff = _normalize_bits_to_width(b_exp, _EXP_WIDTH)
    if b_class == "subnormal":
        exp_b_eff = []
        k = 0
        while k < _EXP_WIDTH:
            exp_b_eff.append(0)
            k = k + 1
        exp_b_eff[0] = 1
    exp_sum, _ = ripple_carry_adder(exp_a_eff, exp_b_eff)
    exp_sum = _normalize_bits_to_width(exp_sum, _EXP_WIDTH)
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
    product_width = 48
    product: list[int] = []
    idx = 0
    while idx < product_width:
        product.append(0)
        idx = idx + 1
        product_width = 48
    product: list[int] = []
    idx = 0
    while idx < product_width:
        product.append(0)
        idx = idx + 1
    bit_index = 0
    while bit_index < _MANT_WIDTH:
        if mant_b[bit_index] & 1:
            term = _normalize_bits_to_width(mant_a, product_width)
            shift_count = 0
            while shift_count < bit_index:
                term = sll(term, 1)
                term = _normalize_bits_to_width(term, product_width)
                shift_count = shift_count + 1
            product, _ = ripple_carry_adder(product, term)
            product = _normalize_bits_to_width(product, product_width)
        bit_index = bit_index + 1
    sticky_bit = 0
    low = 0
    while low < 23:
        if product[low] & 1:
            sticky_bit = 1
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
    mant_ext: list[int] = []
    idx = 0
    while idx < (_MANT_WIDTH + 1):
        src_pos = idx + 23
        if src_pos < product_width:
            mant_ext.append(product[src_pos] & 1)
        else:
            mant_ext.append(0)
        idx = idx + 1
    if mant_ext[_MANT_WIDTH] & 1:
        lost_lsb = mant_ext[0] & 1
        mant_ext = srl(mant_ext, 1)
        mant_ext = _normalize_bits_to_width(mant_ext, _MANT_WIDTH + 1)
        exp_tmp = _increment_bits(exp_tmp)
        if lost_lsb:
            sticky_bit = 1
    overflow_flag = False
    underflow_flag = False
    if _all_ones(exp_tmp):
        overflow_flag = True
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
    mant_main: list[int] = []
    idx = 0
    while idx < _MANT_WIDTH:
        mant_main.append(mant_ext[idx] & 1)
        idx = idx + 1
    guard_bit = mant_ext[_MANT_WIDTH] & 1
    mant_rounded, exp_carry, inexact_from_round = _round_rne_mantissa(
        mant_main,
        guard_bit,
        sticky_bit,
    )
    exp_res = _normalize_bits_to_width(exp_tmp, _EXP_WIDTH)
    if exp_carry:
        exp_res = _increment_bits(exp_res)
    if _all_ones(exp_res):
        overflow_flag = True
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
    fraction_result: list[int] = []
    idx = 0
    while idx < _FRAC_WIDTH:
        fraction_result.append(mant_rounded[idx] & 1)
        idx = idx + 1

    exponent_result = _normalize_bits_to_width(exp_res, _EXP_WIDTH)
    #AI-BEGIN
    if (
        _all_zero(exponent_result)
        and _all_zero(fraction_result)
        and (not _mantissa_is_zero(product))
    ):
        fraction_result[0] = 1
        underflow_flag = True
        inexact_from_round = True
    if _all_zero(exponent_result) and (not _all_zero(fraction_result)):
        underflow_flag = True
        #AI-END
    result_bits = _assemble_ieee(res_sign, exponent_result, fraction_result)
    inexact_flag = inexact_from_round
    if overflow_flag or underflow_flag:
        inexact_flag = True
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
