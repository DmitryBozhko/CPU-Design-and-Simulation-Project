# tests/cpu_unit/test_cpu_alu.py
from __future__ import annotations
from src.cpu.alu import alu
from src.numeric_core.conversions import hex_to_bits32, bits32_to_hex


# AI-BEGIN
def _hex_result(op: str, a_hex: str, b_hex: str) -> tuple[str, dict]:
    a_bits = hex_to_bits32(a_hex)
    b_bits = hex_to_bits32(b_hex)
    info = alu(a_bits, b_bits, op)
    res_hex = bits32_to_hex(info["result"]).upper()
    return res_hex, info["flags"]


# AI-END


def test_add_overflow_positive_to_negative():
    res_hex, flags = _hex_result("ADD", "7FFFFFFF", "00000001")

    assert res_hex == "80000000"
    assert flags["V"] is True
    assert flags["C"] is False
    assert flags["N"] is True
    assert flags["Z"] is False


def test_sub_overflow_negative_to_positive():
    res_hex, flags = _hex_result("SUB", "80000000", "00000001")
    assert res_hex == "7FFFFFFF"
    assert flags["V"] is True
    assert flags["C"] is True
    assert flags["N"] is False
    assert flags["Z"] is False


def test_add_minus_one_plus_minus_one():
    res_hex, flags = _hex_result("ADD", "FFFFFFFF", "FFFFFFFF")

    assert res_hex == "FFFFFFFE"
    assert flags["V"] is False
    assert flags["C"] is True
    assert flags["N"] is True
    assert flags["Z"] is False


def test_add_13_plus_minus_13_zero_result():
    res_hex, flags = _hex_result("ADD", "0000000D", "FFFFFFF3")

    assert res_hex == "00000000"
    assert flags["V"] is False
    assert flags["C"] is True
    assert flags["N"] is False
    assert flags["Z"] is True


def test_and_or_xor_basic():
    a_hex = "0F0F0F0F"
    b_hex = "00FF00FF"
    res_and, flags_and = _hex_result("AND", a_hex, b_hex)
    res_or, flags_or = _hex_result("OR", a_hex, b_hex)
    res_xor, flags_xor = _hex_result("XOR", a_hex, b_hex)

    assert res_and == "000F000F"
    assert flags_and["Z"] is False
    assert res_or == "0FFF0FFF"
    assert flags_or["Z"] is False
    assert res_xor == "0FF00FF0"
    assert flags_xor["Z"] is False


def test_shifts_sll_srl_sra():
    res_hex, flags = _hex_result("SLL", "00000001", "00000001")
    assert res_hex == "00000002"
    assert flags["Z"] is False
    res_hex, flags = _hex_result("SRL", "80000000", "00000001")
    assert res_hex == "40000000"
    res_hex, flags = _hex_result("SRA", "80000000", "00000001")
    assert res_hex == "C0000000"
    assert flags["N"] is True


def test_slt_signed_and_unsigned():
    res_hex, flags = _hex_result("SLT", "FFFFFFFF", "00000001")
    assert res_hex == "00000001"
    assert flags["Z"] is False
    res_hex, flags = _hex_result("SLT", "00000001", "FFFFFFFF")
    assert res_hex == "00000000"
    assert flags["Z"] is True
    res_hex, flags = _hex_result("SLTU", "FFFFFFFF", "00000001")
    assert res_hex == "00000000"
    assert flags["Z"] is True
    res_hex, flags = _hex_result("SLTU", "00000001", "FFFFFFFF")
    assert res_hex == "00000001"
    assert flags["Z"] is False
