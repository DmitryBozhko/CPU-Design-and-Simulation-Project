from __future__ import annotations
from typing import TYPE_CHECKING
from .adders import ripple_carry_adder
from .small_ops import _fixed_width
from .comparators import compare_signed, compare_unsigned

# AI-BEGIN
if TYPE_CHECKING:  # pragma: no cover - typing helper
    from .conversions import (
        bits32_to_decimal_string,
        bits32_to_hex,
        decimal_string_to_bits32,
        _is_zero_compare,
        _is_positive_compare,
    )


def _import_decimal_string_to_bits32() -> "decimal_string_to_bits32":
    from .conversions import decimal_string_to_bits32

    return decimal_string_to_bits32


def _import_bits32_to_hex() -> "bits32_to_hex":
    from .conversions import bits32_to_hex

    return bits32_to_hex


def _import_bits32_to_decimal_string() -> "bits32_to_decimal_string":
    from .conversions import bits32_to_decimal_string

    return bits32_to_decimal_string


def _import_compare_helpers() -> tuple["_is_zero_compare", "_is_positive_compare"]:
    from .conversions import _is_zero_compare, _is_positive_compare

    return _is_zero_compare, _is_positive_compare


# AI-END


def _zero_bits(width: int) -> list[int]:
    zeros: list[int] = []
    for _ in range(width):
        zeros.append(0 & 1)
    return zeros


def _normalize_slice(bits: list[int], width: int) -> list[int]:
    normalized: list[int] = []
    it = iter(bits)
    for _ in range(width):
        try:
            value = next(it)
        except StopIteration:
            value = 0
        normalized.append(value & 1)
    return normalized


def _reorder_little_endian_word(bits32: list[int]) -> list[int]:
    normalized = _normalize_slice(bits32, 32)
    nibbles: list[list[int]] = []
    it = iter(normalized)
    for _ in range(8):
        nibble: list[int] = []
        for _ in range(4):
            try:
                bit = next(it)
            except StopIteration:
                bit = 0
            nibble.append(bit & 1)
        nibbles.append(nibble)
    nibbles.reverse()
    reordered: list[int] = []
    for nibble in nibbles:
        for bit in nibble:
            reordered.append(bit & 1)
    return reordered


def _split_sign(value_str: str) -> tuple[str, bool]:
    if not value_str:
        return "0", False
    first = value_str[0]
    negative = False
    start_index = 0
    if first == "+":
        start_index = 1
    elif first == "-":
        negative = True
        start_index = 1
    digits = value_str[start_index:]
    if not digits:
        digits = "0"
    return digits, negative


def invert_bits(bits: list[int]) -> list[int]:
    inverted: list[int] = []
    for bit in bits:
        inverted.append((bit ^ 1) & 1)
    return inverted


def negate_twos_complement(bits: list[int]) -> list[int]:
    if not bits:
        return []
    inverted = invert_bits(bits)
    incremented, _ = ripple_carry_adder(inverted, [1])
    width = len(bits)
    result: list[int] = []
    it = iter(incremented)
    for _ in range(width):
        try:
            bit = next(it)
        except StopIteration:
            bit = 0
        result.append(bit & 1)
    return result


def sign_extend(bits: list[int], from_width: int, to_width: int) -> list[int]:
    from_str = str(from_width)
    to_str = str(to_width)
    if from_str[0] == "-":
        raise ValueError("from_width must be non-negative")
    if to_str[0] == "-":
        raise ValueError("to_width must be greater than or equal to from_width")
    decimal_to_bits32 = _import_decimal_string_to_bits32()
    is_zero_compare, is_positive_compare = _import_compare_helpers()
    from_width_bits = decimal_to_bits32(from_str, False)
    to_width_bits = decimal_to_bits32(to_str, False)
    cmp_to_from = compare_unsigned(to_width_bits, from_width_bits)
    if (not is_zero_compare(cmp_to_from)) and (not is_positive_compare(cmp_to_from)):
        raise ValueError("to_width must be greater than or equal to from_width")
    base = _normalize_slice(bits, from_width)
    if is_zero_compare(cmp_to_from):
        return base
    sign_bit = 0
    if base:
        sign_bit = base[-1] & 1
    result: list[int] = []
    for _ in range(to_width):
        result.append(sign_bit & 1)
    it = iter(base)
    for index in range(from_width):
        try:
            value = next(it)
        except StopIteration:
            value = 0
        result[index] = value & 1
    return result


def zero_extend(bits: list[int], from_width: int, to_width: int) -> list[int]:
    from_str = str(from_width)
    to_str = str(to_width)

    if from_str and from_str[0] == "-":
        raise ValueError("from_width must be non-negative")
    if to_str and to_str[0] == "-":
        raise ValueError("to_width must be greater than or equal to from_width")

    decimal_to_bits32 = _import_decimal_string_to_bits32()
    is_zero_compare, is_positive_compare = _import_compare_helpers()
    from_width_bits = decimal_to_bits32(from_str, False)
    to_width_bits = decimal_to_bits32(to_str, False)
    cmp_to_from = compare_unsigned(to_width_bits, from_width_bits)
    if (not is_zero_compare(cmp_to_from)) and (not is_positive_compare(cmp_to_from)):
        raise ValueError("to_width must be greater than or equal to from_width")

    base = _normalize_slice(bits, from_width)
    result = _fixed_width(base, to_width)
    return result


def _convert_value_to_bits32(value_str: str) -> tuple[list[int], bool]:
    decimal_to_bits32 = _import_decimal_string_to_bits32()
    overflow = False
    try:
        return decimal_to_bits32(value_str, True), overflow
    except ValueError:
        overflow = True
        digits, negative = _split_sign(value_str)
        try:
            magnitude = decimal_to_bits32(digits, False)
        except ValueError:
            magnitude = _zero_bits(32)
        if negative:
            return negate_twos_complement(magnitude), overflow
        return magnitude, overflow


def encode_twos_complement(value: int, width: int = 32) -> tuple[list[int], str, bool]:
    width_str = str(width)
    if (not width) or (width_str[0] == "-"):
        raise ValueError("width must be positive")

    string_value = str(value)
    bits32, overflow = _convert_value_to_bits32(string_value)

    bits32_to_hex_fn = _import_bits32_to_hex()
    hex_string = bits32_to_hex_fn(_reorder_little_endian_word(bits32))

    is_32 = 0
    is_less_than_32 = 0

    if width_str == "32":
        is_32 = 1
    else:
        is_single_digit = 0
        is_two_digits = 0
        try:
            _ = width_str[1]
        except IndexError:
            is_single_digit = 1
        if not is_single_digit:
            try:
                _ = width_str[2]
            except IndexError:
                is_two_digits = 1
        if is_single_digit:
            is_less_than_32 = 1
        elif is_two_digits:
            first = width_str[0]
            if first == "1":
                is_less_than_32 = 1
            elif width_str in (
                "20",
                "21",
                "22",
                "23",
                "24",
                "25",
                "26",
                "27",
                "28",
                "29",
                "30",
                "31",
            ):
                is_less_than_32 = 1

    is_zero_compare, _ = _import_compare_helpers()

    if is_32:
        result_bits = _fixed_width(bits32, width)
    elif is_less_than_32:
        result_bits = _fixed_width(bits32, width)
        extended_back = sign_extend(result_bits, width, 32)
        if not is_zero_compare(compare_signed(extended_back, bits32)):
            overflow = True
    else:
        result_bits = sign_extend(bits32, 32, width)

    return result_bits, hex_string, overflow


#AI-BEGIN
def decode_twos_complement(bits: list[int]) -> str:
    #AI-END
    if not bits:
        #AI-BEGIN
        return "0"
        #AI-END
    try:
        _ = bits[31]
        normalized = _normalize_slice(bits, 32)
    except IndexError:
        normalized = sign_extend(bits, len(bits), 32)
    decimal_converter = _import_bits32_to_decimal_string()
    #AI-BEGIN
    return decimal_converter(normalized, True)
    #AI-END
