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


def test_slt_sets_one_when_less_than() -> None:
    result = _execute("SLT", 5, 10)

    assert _bits_to_int(result["result"]) == 1
    assert result["N"] == 0
    assert result["Z"] == 0


def test_slt_clears_result_when_not_less() -> None:
    result = _execute("SLT", 10, 5)

    assert _bits_to_int(result["result"]) == 0
    assert result["Z"] == 1


def test_slt_handles_negative_operands() -> None:
    result = _execute("SLT", -1, 0)

    assert _bits_to_int(result["result"]) == 1
    assert result["N"] == 0


def test_sltu_handles_no_wrap_around() -> None:
    result = _execute("SLTU", 0xFFFFFFFF, 1)

    assert _bits_to_int(result["result"]) == 0
    assert result["Z"] == 1


def test_sltu_handles_unsigned_wraparound() -> None:
    result = _execute("SLTU", 1, 0xFFFFFFFF)

    assert _bits_to_int(result["result"]) == 1
    assert result["N"] == 0