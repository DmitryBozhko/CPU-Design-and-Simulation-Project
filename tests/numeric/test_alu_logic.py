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


def _execute(op: str, a: int, b: int = 0) -> dict:
    width = 32
    alu = ALU()
    a_bits = _int_to_bits(a, width)
    b_bits = _int_to_bits(b, width)
    return alu.execute(op, a_bits, b_bits)


def test_and_clears_bits() -> None:
    result = _execute("AND", 0xAAAAAAAA, 0x55555555)

    assert _bits_to_int(result["result"]) == 0x00000000
    assert result["N"] == 0
    assert result["Z"] == 1
    assert result["C"] == 0
    assert result["V"] == 0


def test_or_sets_all_bits() -> None:
    result = _execute("OR", 0xAAAAAAAA, 0x55555555)

    assert _bits_to_int(result["result"]) == 0xFFFFFFFF
    assert result["N"] == 1
    assert result["Z"] == 0
    assert result["C"] == 0
    assert result["V"] == 0


def test_xor_with_same_operands_is_zero() -> None:
    result = _execute("XOR", 0xDEADBEEF, 0xDEADBEEF)

    assert _bits_to_int(result["result"]) == 0
    assert result["N"] == 0
    assert result["Z"] == 1
    assert result["C"] == 0
    assert result["V"] == 0


def test_not_inverts_bits() -> None:
    result = _execute("NOT", 0x00000000)

    assert _bits_to_int(result["result"]) == 0xFFFFFFFF
    assert result["N"] == 1
    assert result["Z"] == 0
    assert result["C"] == 0
    assert result["V"] == 0
