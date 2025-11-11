from __future__ import annotations

from src.numeric_core.mdu import Multiplier


def _bits_from_string(bit_string: str) -> list[int]:
    cleaned = bit_string.replace("_", "")
    return [1 if char == "1" else 0 for char in cleaned]


def _int_to_bits32_le(value: int) -> list[int]:
    """Convert a Python int to 32-bit little-endian two's-complement bits."""
    value &= 0xFFFFFFFF
    bits: list[int] = []
    for i in range(32):
        bits.append((value >> i) & 1)
    return bits


def _bits_to_int_le(bits: list[int]) -> int:
    """Convert little-endian bits (any width) to an unsigned Python int."""
    value = 0
    for i, bit in enumerate(bits):
        if bit & 1:
            value |= 1 << i
    return value


def _int_to_bits64_le(value: int) -> list[int]:
    """Convert a Python int to 64-bit little-endian bits."""
    value &= (1 << 64) - 1
    bits: list[int] = []
    for i in range(64):
        bits.append((value >> i) & 1)
    return bits


def test_load_operands_initializes_registers() -> None:
    multiplier = Multiplier()
    a_bits = _bits_from_string("1010" * 8)
    b_bits = _bits_from_string("0101" * 8)

    multiplier.load_operands(a_bits, b_bits)

    assert multiplier.state == "RUN"
    assert multiplier.step_counter == 0
    assert len(multiplier.multiplicand) == 64
    # low 32 bits of multiplicand come from a_bits exactly
    assert multiplier.multiplicand[:32] == a_bits
    assert multiplier.multiplier == b_bits
    assert multiplier.accumulator == [0] * 64


def test_step_advances_state_machine() -> None:
    multiplier = Multiplier()
    all_ones = [1] * 32
    multiplier.load_operands(all_ones, all_ones)

    for iteration in range(32):
        assert multiplier.state == "RUN"
        multiplier.step()
        assert multiplier.step_counter == iteration + 1

    assert multiplier.is_done()
    assert multiplier.state == "DONE"


def test_step_after_done_has_no_effect() -> None:
    multiplier = Multiplier()
    zeros = [0] * 32
    multiplier.load_operands(zeros, zeros)

    for _ in range(32):
        multiplier.step()

    assert multiplier.is_done()
    final_count = multiplier.step_counter
    final_product = multiplier.get_product()[:]

    # Extra step should not change anything
    multiplier.step()
    assert multiplier.step_counter == final_count
    assert multiplier.state == "DONE"
    assert multiplier.get_product() == final_product


def test_unsigned_multiply_simple_values() -> None:
    """Check a few simple 32×32→64 unsigned products."""
    cases = [
        (0, 0),
        (0, 123),
        (1, 1),
        (1, 123456),
        (5, 7),
        (0xFFFFFFFF, 1),
        (0xFFFFFFFF, 2),
    ]

    for a, b in cases:
        m = Multiplier()
        a_bits = _int_to_bits32_le(a)
        b_bits = _int_to_bits32_le(b)
        m.load_operands(a_bits, b_bits)

        while not m.is_done():
            m.step()

        product_bits = m.get_product()
        product_int = _bits_to_int_le(product_bits)
        expected = (a * b) & ((1 << 64) - 1)

        assert product_int == expected, f"{a} * {b} != product from Multiplier"


def test_unsigned_multiply_all_ones_matches_python() -> None:
    """Stress a big case: 0xFFFFFFFF * 0xFFFFFFFF."""
    a = 0xFFFFFFFF
    b = 0xFFFFFFFF

    m = Multiplier()
    a_bits = _int_to_bits32_le(a)
    b_bits = _int_to_bits32_le(b)
    m.load_operands(a_bits, b_bits)

    while not m.is_done():
        m.step()

    product_bits = m.get_product()
    product_int = _bits_to_int_le(product_bits)
    expected = (a * b) & ((1 << 64) - 1)

    assert product_int == expected
    # Optional sanity: full 64-bit pattern equality check
    assert product_bits == _int_to_bits64_le(expected)
