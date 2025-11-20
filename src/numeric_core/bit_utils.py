from __future__ import annotations


def bit_to_char(bit: bool) -> str:
    # AI-BEGIN
    """Convert a single bit into its '0'/'1' character form."""
    # AI-END
    if bit not in (0, 1, True, False):
        raise ValueError(f"Invalid bit value: {bit!r}")
    return "1" if bool(bit) else "0"


def char_to_bit(c: str) -> bool:
    # AI-BEGIN
    """Convert a '0' or '1' character into a boolean bit."""
    # AI-END
    if c not in ("0", "1"):
        raise ValueError(f"Invalid bit character: {c!r}")
    return c == "1"


def bits_to_string(bits: list[int]) -> str:
    # AI-BEGIN
    """Render a list of bits as a concatenated 0/1 string."""
    # AI-END
    chars: list[str] = []
    for bit in bits:
        chars.append(bit_to_char(bool(bit)))
    return "".join(chars)


def string_to_bits(s: str) -> list[int]:
    # AI-BEGIN
    """Convert a string of 0/1 characters into a list of ints."""
    # AI-END
    bits: list[int] = []
    for char in s:
        bit_value = char_to_bit(char)
        bits.append(1 if bit_value else 0)
    return bits


def print_bits_formatted(bits: list[int], width: int) -> str:
    # AI-BEGIN
    """Pretty-print bits with zero-padding and nibble underscores."""
    # AI-END
    width_str = str(width)
    if width_str and width_str[0] == "-":
        raise ValueError("width must be non-negative")
    raw = bits_to_string(bits)
    if width:
        raw = raw.rjust(width, "0")
    if not raw:
        if width:
            return "0".rjust(width, "0")
        return ""
    group_size = 4
    groups: list[str] = []
    current = ""
    for ch in reversed(raw):
        current = ch + current
        if len(current) == group_size:
            groups.insert(0, current)
            current = ""
    if current:
        groups.insert(0, current)
    return "_".join(groups)
