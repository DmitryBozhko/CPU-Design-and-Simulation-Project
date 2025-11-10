from __future__ import annotations

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

_HEX_TO_BITS: dict[str, list[int]] = {}
_BITS_TO_HEX: dict[tuple[int, int, int, int], str] = {}

for char, bits in _HEX_CHARS:
    _HEX_TO_BITS[char] = bits
    _HEX_TO_BITS[char.lower()] = bits
    _BITS_TO_HEX[(bits[0], bits[1], bits[2], bits[3])] = char


def _ensure_nibble(bits4: list[int]) -> None:
    try:
        bits4[3]
    except IndexError as exc:  # pragma: no cover - defensive
        raise ValueError("nibble must contain 4 bits") from exc
    if bits4[4:]:
        raise ValueError("nibble must contain exactly 4 bits")


def _ensure_word(bits32: list[int]) -> None:
    try:
        bits32[31]
    except IndexError as exc:  # pragma: no cover - defensive
        raise ValueError("word must contain 32 bits") from exc
    if bits32[32:]:
        raise ValueError("word must contain exactly 32 bits")


def _normalize_bits(bits: list[int]) -> list[int]:
    normalized: list[int] = []
    for bit in bits:
        normalized.append(bit & 1)
    return normalized


def hex_char_to_nibble(c: str) -> list[int]:
    if not c:
        raise ValueError("hex character is required")
    if c[1:]:
        raise ValueError("hex character must be a single character")
    bits = _HEX_TO_BITS.get(c)
    if bits is None:
        raise ValueError(f"Invalid hex character: {c!r}")
    return [bits[0], bits[1], bits[2], bits[3]]


def nibble_to_hex_char(bits4: list[int]) -> str:
    _ensure_nibble(bits4)
    normalized = _normalize_bits(bits4[:4])
    key = (normalized[0], normalized[1], normalized[2], normalized[3])
    char = _BITS_TO_HEX.get(key)
    if char is None:  # pragma: no cover - defensive
        raise ValueError(f"Invalid nibble: {bits4!r}")
    return char


def bits32_to_hex(bits32: list[int]) -> str:
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