from __future__ import annotations


def bit_to_char(bit: bool) -> str:
    if bit not in (0, 1, True, False):
        raise ValueError(f"Invalid bit value: {bit!r}")
    return "1" if bool(bit) else "0"


def char_to_bit(c: str) -> bool:
    if c not in ("0", "1"):
        raise ValueError(f"Invalid bit character: {c!r}")
    return c == "1"


def bits_to_string(bits: list[int]) -> str:
    chars: list[str] = []
    for bit in bits:
        chars.append(bit_to_char(bool(bit)))
    return "".join(chars)


def string_to_bits(s: str) -> list[int]:
    bits: list[int] = []
    for char in s:
        bit_value = char_to_bit(char)
        bits.append(1 if bit_value else 0)
    return bits


def print_bits_formatted(bits: list[int], width: int) -> str:
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
