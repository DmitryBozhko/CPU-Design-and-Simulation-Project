from __future__ import annotations
from typing import List
import pytest
from src.cpu.register_file import RegisterFile
from src.numeric_core.conversions import hex_to_bits32, bits32_to_hex


def _zeros32() -> List[int]:
    bits: List[int] = []
    i = 0
    while i < 32:
        bits.append(0)
        i = i + 1
    return bits


def test_x0_is_always_zero_even_after_writes():
    rf = RegisterFile()
    x0_before = rf.read(0)
    assert x0_before == _zeros32()
    pattern = hex_to_bits32("DEADBEEF")
    rf.write(0, pattern, write_enable=True)
    x0_after = rf.read(0)
    assert x0_after == _zeros32()
    rf.write(1, pattern, write_enable=False)
    assert rf.read(1) == _zeros32()


def test_write_and_read_general_register():
    rf = RegisterFile()
    value = hex_to_bits32("1234ABCD")
    rf.write(5, value)
    read_back = rf.read(5)
    assert bits32_to_hex(read_back).upper() == "1234ABCD"
    read_back[0] = read_back[0] ^ 1  # Flip LSB
    again = rf.read(5)
    assert bits32_to_hex(again).upper() == "1234ABCD"


def test_registers_are_independent():
    rf = RegisterFile()
    v1 = hex_to_bits32("00000001")
    v2 = hex_to_bits32("80000000")
    rf.write(1, v1)
    rf.write(2, v2)
    r1 = bits32_to_hex(rf.read(1)).upper()
    r2 = bits32_to_hex(rf.read(2)).upper()
    assert r1 == "00000001"
    assert r2 == "80000000"


def test_register_index_out_of_range_raises():
    rf = RegisterFile()
    with pytest.raises(ValueError):
        rf.read(32)
    with pytest.raises(ValueError):
        rf.write(32, _zeros32())
