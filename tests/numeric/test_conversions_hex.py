import pytest

from src.numeric_core.conversions import (
    bits32_to_hex,
    hex_char_to_nibble,
    hex_to_bits32,
    nibble_to_hex_char,
)


def test_round_trip_deadbeef():
    bits = hex_to_bits32("DEADBEEF")
    assert len(bits) == 32
    assert bits32_to_hex(bits) == "DEADBEEF"


def test_round_trip_lowercase():
    bits = hex_to_bits32("deadbeef")
    assert bits32_to_hex(bits) == "DEADBEEF"


def test_nibble_conversions():
    nibble = hex_char_to_nibble("A")
    assert nibble == [0, 1, 0, 1]
    assert nibble_to_hex_char(nibble) == "A"


def test_bits32_to_hex_zero_padding():
    bits = [0] * 28 + [1, 1, 1, 1]
    assert bits32_to_hex(bits) == "0000000F"


def test_hex_to_bits32_padding_and_length():
    bits = hex_to_bits32("1A")
    assert len(bits) == 32
    assert bits32_to_hex(bits) == "0000001A"


def test_invalid_hex_character():
    with pytest.raises(ValueError):
        hex_char_to_nibble("G")


def test_invalid_length_inputs():
    with pytest.raises(ValueError):
        nibble_to_hex_char([1, 0, 0])
    with pytest.raises(ValueError):
        bits32_to_hex([0, 1])
    with pytest.raises(ValueError):
        hex_to_bits32("123456789")
