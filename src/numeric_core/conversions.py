from __future__ import annotations
from .adders import ripple_carry_adder
from .comparators import compare_unsigned, is_zero
from .twos_complement import negate_twos_complement

#AI-BEGIN
_HEX_CHARS = (
    ("0", [0, 0, 0, 0]),
    ("1", [1, 0, 0, 0]),
    ("2", [0, 1, 0, 0]),
    ("3", [1, 1, 0, 0]),
    ("4", [0, 0, 1, 0]),
    ("5", [1, 0, 1, 0]),
    ("6", [0, 1, 1, 0]),
    ("7", [1, 1, 1, 0]),
    ("8", [0, 0, 0, 1]),
    ("9", [1, 0, 0, 1]),
    ("A", [0, 1, 0, 1]),
    ("B", [1, 1, 0, 1]),
    ("C", [0, 0, 1, 1]),
    ("D", [1, 0, 1, 1]),
    ("E", [0, 1, 1, 1]),
    ("F", [1, 1, 1, 1]),
)
#AI-END

_HEX_TO_BITS: dict[str, list[int]] = {}
_BITS_TO_HEX: dict[tuple[int, int, int, int], str] = {}

for char, bits in _HEX_CHARS:
    _HEX_TO_BITS[char] = bits
    _HEX_TO_BITS[char.lower()] = bits
    _BITS_TO_HEX[(bits[0], bits[1], bits[2], bits[3])] = char


def _ensure_nibble(bits4: list[int]) -> None:
    # AI-BEGIN
    """Validate that a list contains exactly 4 bits."""
    # AI-END
    try:
        bits4[3]
    except IndexError as exc:  #AI-BEGIN # pragma: no cover - defensive #AI-END
        raise ValueError("nibble must contain 4 bits") from exc
    if bits4[4:]:
        raise ValueError("nibble must contain exactly 4 bits")


def _ensure_word(bits32: list[int]) -> None:
    # AI-BEGIN
    """Validate that a list contains exactly 32 bits."""
    # AI-END
    try:
        bits32[31]
    except IndexError as exc:  #AI-BEGIN # pragma: no cover - defensive #AI-END
        raise ValueError("word must contain 32 bits") from exc
    if bits32[32:]:
        raise ValueError("word must contain exactly 32 bits")


def _normalize_bits(bits: list[int]) -> list[int]:
    # AI-BEGIN
    """Normalize arbitrary integers into 0/1 bit values."""
    # AI-END
    normalized: list[int] = []
    for bit in bits:
        normalized.append(bit & 1)
    return normalized


def hex_char_to_nibble(c: str) -> list[int]:
    # AI-BEGIN
    """Decode a single hex character into a 4-bit list."""
    # AI-END
    if not c:
        raise ValueError("hex character is required")
    if c[1:]:
        raise ValueError("hex character must be a single character")
    bits = _HEX_TO_BITS.get(c)
    if bits is None:
        raise ValueError(f"Invalid hex character: {c!r}")
    return [bits[0], bits[1], bits[2], bits[3]]


def nibble_to_hex_char(bits4: list[int]) -> str:
    # AI-BEGIN
    """Convert a 4-bit list into its hex character."""
    # AI-END
    _ensure_nibble(bits4)
    normalized = _normalize_bits(bits4[:4])
    key = (normalized[0], normalized[1], normalized[2], normalized[3])
    char = _BITS_TO_HEX.get(key)
    if char is None:  #AI-BEGIN # pragma: no cover - defensive #AI-END
        raise ValueError(f"Invalid nibble: {bits4!r}")
    return char


def bits32_to_hex(bits32: list[int]) -> str:
    # AI-BEGIN
    """Encode a 32-bit vector into an 8-character hex string."""
    # AI-END
    _ensure_word(bits32)
    nibbles = (
        bits32[0:4],
        bits32[4:8],
        bits32[8:12],
        bits32[12:16],
        bits32[16:20],
        bits32[20:24],
        bits32[24:28],
        bits32[28:32],
    )
    chars: list[str] = []
    for nibble in nibbles:
        chars.append(nibble_to_hex_char(nibble))
    return "".join(chars)


def hex_to_bits32(hex_str: str) -> list[int]:
    # AI-BEGIN
    """Parse an up-to-8-digit hex string into 32 bits."""
    # AI-END
    if hex_str is None:
        raise ValueError("hex string is required")
    cleaned = hex_str.strip()
    if cleaned[8:]:
        raise ValueError("hex string must be at most 8 characters")
    padded = cleaned.rjust(8, "0")
    bits: list[int] = []
    for char in padded:
        bits.extend(hex_char_to_nibble(char))
    return bits


_DECIMAL_DIGITS = tuple("0123456789")

_DECIMAL_DIGIT_BITS: dict[str, list[int]] = {}

for digit_char in _DECIMAL_DIGITS:
    nibble = _HEX_TO_BITS[digit_char]
    normalized: list[int] = []
    for bit in nibble:
        normalized.append(bit & 1)
    tmp_rev: list[int] = []
    seen_one = 0
    for bit in reversed(normalized):
        b = bit & 1
        if b & 1:
            seen_one = 1
        if seen_one & 1:
            tmp_rev.append(b)
    if seen_one & 1:
        trimmed: list[int] = []
        for bit in reversed(tmp_rev):
            trimmed.append(bit & 1)
    else:
        trimmed = [0]
    _DECIMAL_DIGIT_BITS[digit_char] = trimmed


_TEN_BITS = [0, 1, 0, 1]
_SIGNED_MIN_MAG_BITS: list[int] = []
for _ in range(31):
    _SIGNED_MIN_MAG_BITS.append(0)
_SIGNED_MIN_MAG_BITS.append(1)
_COMPARISON_NON_NEGATIVE: dict[int, int] = {-1: 0, 0: 1, 1: 1}
_COMPARISON_POSITIVE: dict[int, int] = {-1: 0, 0: 0, 1: 1}
_COMPARISON_ZERO: dict[int, int] = {-1: 0, 0: 1, 1: 0}


def _is_non_negative_compare(result: int) -> bool:
    # AI-BEGIN
    """Return True if a comparator result is >= 0."""
    # AI-END
    return bool(_COMPARISON_NON_NEGATIVE[result])


def _is_positive_compare(result: int) -> bool:
    # AI-BEGIN
    """Return True if a comparator result is > 0."""
    # AI-END
    return bool(_COMPARISON_POSITIVE[result])


def _is_zero_compare(result: int) -> bool:
    # AI-BEGIN
    """Return True if a comparator result is == 0."""
    # AI-END
    return bool(_COMPARISON_ZERO[result])


def _normalize_word(bits32: list[int]) -> list[int]:
    # AI-BEGIN
    """Normalize a 32-bit input ensuring only 0/1 values."""
    # AI-END
    _ensure_word(bits32)
    normalized: list[int] = []
    for index in range(32):
        normalized.append(bits32[index] & 1)
    return normalized


def _normalize_bits_nonempty(bits: list[int]) -> list[int]:
    # AI-BEGIN
    """Normalize bits and guarantee at least one element."""
    # AI-END
    normalized = _normalize_bits(bits)
    if not normalized:
        normalized.append(0)
    return normalized


def _fixed_width(bits: list[int], width: int) -> list[int]:
    # AI-BEGIN
    """Pad or truncate a bit list to a fixed width."""
    # AI-END
    fixed: list[int] = []
    it = iter(bits)
    for _ in range(width):
        try:
            bit = next(it)
        except StopIteration:
            bit = 0
        fixed.append(bit & 1)
    return fixed


def _highest_bit_index(bits: list[int]) -> int:
    # AI-BEGIN
    """Return the highest index containing a 1 bit, or -1 if none."""
    # AI-END
    highest = ~0
    for index, value in enumerate(bits):
        if value & 1:
            highest = index
    return highest


def _shift_left(bits: list[int], amount: int) -> list[int]:
    # AI-BEGIN
    """Shift a bit vector left by inserting zeros on the LSB side."""
    # AI-END
    shifted: list[int] = []
    for _ in range(amount):
        shifted.append(0)
    for bit in bits:
        shifted.append(bit & 1)
    return shifted


def _subtract_unsigned(a_bits: list[int], b_bits: list[int]) -> list[int]:
    # AI-BEGIN
    """Unsigned subtraction of equal-width bit vectors."""
    # AI-END
    padded_a: list[int] = []
    padded_b: list[int] = []
    it_a = iter(a_bits)
    it_b = iter(b_bits)
    while True:
        a_has = 1
        b_has = 1
        try:
            a_val = next(it_a)
        except StopIteration:
            a_val = 0
            a_has = 0
        try:
            b_val = next(it_b)
        except StopIteration:
            b_val = 0
            b_has = 0
        if not ((a_has | b_has) & 1):
            break
        padded_a.append(a_val)
        padded_b.append(b_val)
    width = len(padded_a)
    inverted: list[int] = []
    for bit in padded_b:
        inverted.append((bit ^ 1) & 1)
    difference, _ = ripple_carry_adder(padded_a, inverted, cin=1)
    return _fixed_width(difference, width)


def _unsigned_divide(
    dividend_bits: list[int], divisor_bits: list[int]
) -> tuple[list[int], list[int]]:
    # AI-BEGIN
    """Divide two unsigned bit vectors, returning quotient and remainder."""
    # AI-END
    normalized_dividend = _fixed_width(dividend_bits, len(dividend_bits))
    normalized_divisor = _normalize_bits_nonempty(divisor_bits)
    if is_zero(normalized_divisor):
        raise ValueError("divisor must be non-zero")
    quotient = [0 for _ in normalized_dividend]
    remainder = list(normalized_dividend)
    if is_zero(remainder):
        return quotient, [0]
    shifts: list[int] = []
    for shift in range(len(normalized_dividend)):
        candidate = _shift_left(normalized_divisor, shift)
        if not _is_non_negative_compare(
            compare_unsigned(normalized_dividend, candidate)
        ):
            break
        shifts.append(shift)
    while shifts:
        shift = shifts.pop()
        candidate = _shift_left(normalized_divisor, shift)
        if _is_non_negative_compare(compare_unsigned(remainder, candidate)):
            remainder = _subtract_unsigned(remainder, candidate)
            quotient[shift] = 1
    return quotient, remainder


def _digit_bits_from_char(char: str) -> list[int]:
    # AI-BEGIN
    """Lookup bit pattern representing a decimal digit."""
    # AI-END
    bits = _DECIMAL_DIGIT_BITS.get(char)
    if bits is None:
        raise ValueError(f"Invalid decimal digit: {char!r}")
    return list(bits)


def _digit_char_from_bits(bits: list[int]) -> str:
    # AI-BEGIN
    """Convert a bit pattern back into a decimal digit character."""
    # AI-END
    for char in _DECIMAL_DIGITS:
        reference = _DECIMAL_DIGIT_BITS[char]
        if _is_zero_compare(compare_unsigned(bits, reference)):
            return char
    raise ValueError("remainder out of decimal digit range")


def _parse_decimal_string(s: str) -> tuple[str, bool]:
    # AI-BEGIN
    """Strip and validate a decimal string, returning digits and sign."""
    # AI-END
    if s is None:
        raise ValueError("decimal string is required")
    stripped = s.strip()
    if not stripped:
        raise ValueError("decimal string is required")
    negative = False
    start_index = 0
    first_char = stripped[0]
    if first_char == "+":
        start_index = 1
    elif first_char == "-":
        negative = True
        start_index = 1
    digits = stripped[start_index:]
    if not digits:
        raise ValueError("decimal digits are required")
    for char in digits:
        if char not in _DECIMAL_DIGITS:
            raise ValueError(f"Invalid decimal digit: {char!r}")
    trimmed = digits.lstrip("0")
    if not trimmed:
        trimmed = "0"
    return trimmed, negative


def _add_within_width(
    a_bits: list[int], b_bits: list[int], width: int
) -> tuple[list[int], int]:
    # AI-BEGIN
    """Add two bit vectors with fixed width, returning result and overflow."""
    # AI-END
    padded_a = _fixed_width(a_bits, width)
    padded_b = _fixed_width(b_bits, width)
    summed, carry = ripple_carry_adder(padded_a, padded_b)
    result = _fixed_width(summed, width)
    overflow = 1 if carry else 0
    return result, overflow


def _multiply_bits_by_ten(bits: list[int], width: int) -> tuple[list[int], int]:
    # AI-BEGIN
    """Multiply a bit vector by ten using repeated addition."""
    # AI-END
    result: list[int] = []
    for _ in range(width):
        result.append(0 & 1)
    overflow = 0
    addend = _fixed_width(bits, width)
    for _ in range(10):
        result, add_overflow = _add_within_width(result, addend, width)
        if add_overflow & 1:
            overflow = 1
    return result, overflow & 1


def _unsigned_bits_to_decimal_string(bits: list[int]) -> str:
    # AI-BEGIN
    """Convert an unsigned bit vector into its decimal string."""
    # AI-END
    current = _fixed_width(bits, len(bits))
    if is_zero(current):
        return "0"
    digits: list[str] = []
    while not is_zero(current):
        quotient, remainder = _unsigned_divide(current, _TEN_BITS)
        digits.append(_digit_char_from_bits(remainder))
        current = quotient
    digits.reverse()
    return "".join(digits)


def bits32_to_decimal_string(bits32: list[int], signed: bool) -> str:
    # AI-BEGIN
    """Render a 32-bit word as decimal, respecting signedness."""
    # AI-END
    normalized = _normalize_word(bits32)
    if signed and normalized[31]:
        magnitude = negate_twos_complement(normalized)
        digits = _unsigned_bits_to_decimal_string(magnitude)
        return "-" + digits
    return _unsigned_bits_to_decimal_string(normalized)


def decimal_string_to_bits32(s: str, signed: bool) -> list[int]:
    # AI-BEGIN
    """Parse a decimal string into 32-bit two's-complement bits."""
    # AI-END
    digits, negative_input = _parse_decimal_string(s)
    width = 32
    accumulator: list[int] = []
    for _ in range(width):
        accumulator.append(0 & 1)
    for char in digits:
        accumulator, mul_overflow = _multiply_bits_by_ten(accumulator, width)
        if mul_overflow:
            raise ValueError("value out of range")
        digit_bits = _digit_bits_from_char(char)
        accumulator, add_overflow = _add_within_width(accumulator, digit_bits, width)
        if add_overflow:
            raise ValueError("value out of range")
    if negative_input:
        if not signed:
            raise ValueError("unsigned conversion cannot accept negative values")
        if is_zero(accumulator):
            return accumulator
        if _is_positive_compare(compare_unsigned(accumulator, _SIGNED_MIN_MAG_BITS)):
            raise ValueError("value out of range")
        return negate_twos_complement(accumulator)
    if signed and accumulator[31]:
        raise ValueError("value out of range")
    return accumulator
