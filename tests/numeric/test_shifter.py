from __future__ import annotations

from src.numeric_core.shifter import sll, sra, srl


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


def test_sll_inserts_zeros_on_lsb_side() -> None:
    bits = int_to_bits(0x00000001, 32)
    result = sll(bits, 4)
    assert bits_to_int(result) == 0x00000010
    assert len(result) == 32


def test_srl_drops_lsb_bits_and_fills_with_zero() -> None:
    bits = int_to_bits(0x80000000, 32)
    result = srl(bits, 1)
    assert bits_to_int(result) == 0x40000000
    assert len(result) == 32


def test_sra_preserves_sign_bit() -> None:
    bits = int_to_bits(0x80000000, 32)
    result = sra(bits, 1)
    assert bits_to_int(result) == 0xC0000000
    assert len(result) == 32
