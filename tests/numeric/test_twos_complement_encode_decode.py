from __future__ import annotations

from src.numeric_core.twos_complement import (
    decode_twos_complement,
    encode_twos_complement,
    sign_extend,
    zero_extend,
)


def _signed_to_bits(value: int, width: int) -> list[int]:
    return [(value >> index) & 1 for index in range(width)]


def test_encode_positive_value_produces_expected_hex() -> None:
    bits, hex_string, overflow = encode_twos_complement(13)

    assert len(bits) == 32
    assert not overflow
    assert hex_string == "0000000D"
    assert decode_twos_complement(bits) == 13


def test_encode_negative_value_produces_expected_hex() -> None:
    bits, hex_string, overflow = encode_twos_complement(-13)

    assert len(bits) == 32
    assert not overflow
    assert hex_string == "FFFFFFF3"
    assert decode_twos_complement(bits) == -13


def test_encode_reports_overflow_for_out_of_range_value() -> None:
    bits, hex_string, overflow = encode_twos_complement(2**31)

    assert len(bits) == 32
    assert overflow
    assert hex_string == "80000000"


def test_encode_uses_requested_width_when_possible() -> None:
    bits, _, overflow = encode_twos_complement(13, width=8)

    assert len(bits) == 8
    assert not overflow
    assert decode_twos_complement(bits) == 13


def test_encode_reports_overflow_when_width_too_small() -> None:
    _, _, overflow = encode_twos_complement(200, width=8)

    assert overflow


def test_sign_extend_expands_12_bit_immediate_to_32_bits() -> None:
    immediate_bits = _signed_to_bits(-75, 12)

    extended = sign_extend(immediate_bits, 12, 32)

    assert len(extended) == 32
    assert decode_twos_complement(extended) == -75


def test_zero_extend_appends_leading_zeros() -> None:
    base_bits = _signed_to_bits(0x5A3, 12)

    extended = zero_extend(base_bits, 12, 16)

    assert len(extended) == 16
    assert decode_twos_complement(extended) == 0x5A3


def test_decode_empty_bits_defaults_to_zero() -> None:
    assert decode_twos_complement([]) == 0