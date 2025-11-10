from __future__ import annotations

from src.numeric_core.alu import ALU


def _int_to_bits(value: int, width: int) -> list[int]:
    mask = (1 << width) - 1
    masked = value & mask
    return [(masked >> index) & 1 for index in range(width)]


def _bits_to_int(bits: list[int]) -> int:
    total = 0
    for index, bit in enumerate(bits):
        if bit & 1:
            total |= 1 << index
    return total


def _execute(op: str, a: int, b: int) -> dict:
    width = 32
    alu = ALU()
    a_bits = _int_to_bits(a, width)
    b_bits = _int_to_bits(b, width)
    return alu.execute(op, a_bits, b_bits)


def test_add_overflow_sets_flags() -> None:
    result = _execute("ADD", 0x7FFFFFFF, 0x00000001)

    assert _bits_to_int(result["result"]) == 0x80000000
    assert result["N"] == 1
    assert result["Z"] == 0
    assert result["C"] == 0
    assert result["V"] == 1


def test_subtract_with_borrow_sets_flags() -> None:
    result = _execute("SUB", 0x80000000, 0x00000001)

    assert _bits_to_int(result["result"]) == 0x7FFFFFFF
    assert result["N"] == 0
    assert result["Z"] == 0
    assert result["C"] == 1
    assert result["V"] == 1


def test_add_negative_values_sets_expected_flags() -> None:
    result = _execute("ADD", -1, -1)

    assert _bits_to_int(result["result"]) == 0xFFFFFFFE
    assert result["N"] == 1
    assert result["Z"] == 0
    assert result["C"] == 1
    assert result["V"] == 0