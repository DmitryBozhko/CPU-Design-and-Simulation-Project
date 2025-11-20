from __future__ import annotations
from src.numeric_core.alu import ALU


def int_to_bits(value: int, width: int) -> list[int]:
    bits: list[int] = []
    for idx in range(width):
        bits.append((value >> idx) & 1)
    return bits


def bits_to_int(bits: list[int]) -> int:
    value = 0
    for idx, bit in enumerate(bits):
        if bit & 1:
            value |= 1 << idx
    return value


def test_sll_matches_manual_shifter() -> None:
    alu = ALU()
    a_bits = int_to_bits(0x00000001, 32)
    b_bits = int_to_bits(0x00000004, 32)
    result = alu.execute("SLL", a_bits, b_bits)
    assert bits_to_int(result["result"]) == 0x00000010
    assert len(result["result"]) == 32


def test_srl_matches_manual_shifter() -> None:
    alu = ALU()
    a_bits = int_to_bits(0x80000000, 32)
    b_bits = int_to_bits(0x00000001, 32)
    result = alu.execute("SRL", a_bits, b_bits)
    assert bits_to_int(result["result"]) == 0x40000000
    assert len(result["result"]) == 32


def test_sra_matches_manual_shifter() -> None:
    alu = ALU()
    a_bits = int_to_bits(0x80000000, 32)
    b_bits = int_to_bits(0x00000001, 32)
    result = alu.execute("SRA", a_bits, b_bits)
    assert bits_to_int(result["result"]) == 0xC0000000
    assert len(result["result"]) == 32


def test_shift_amount_uses_lower_five_bits_only() -> None:
    alu = ALU()
    a_bits = int_to_bits(0x00000001, 32)
    b_bits = int_to_bits(0b100100, 32)
    result = alu.execute("SLL", a_bits, b_bits)
    assert bits_to_int(result["result"]) == 0x00000010
    assert len(result["result"]) == 32
