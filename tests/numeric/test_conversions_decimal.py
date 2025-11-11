import pytest

from src.numeric_core.conversions import (
    bits32_to_decimal_string,
    decimal_string_to_bits32,
)


@pytest.mark.parametrize(
    "value",
    [0, 1, -1, 13, -13, 2147483647, -2147483648],
)
def test_signed_round_trip(value: int) -> None:
    bits = decimal_string_to_bits32(str(value), signed=True)
    assert bits32_to_decimal_string(bits, signed=True) == str(value)


def test_leading_signs_and_zero_handling() -> None:
    assert decimal_string_to_bits32("+13", signed=True) == decimal_string_to_bits32(
        "13", signed=True
    )

    zero_bits = decimal_string_to_bits32("-0", signed=True)
    assert bits32_to_decimal_string(zero_bits, signed=True) == "0"


def test_unsigned_large_value_round_trip() -> None:
    bits = decimal_string_to_bits32("2147483648", signed=False)
    assert bits32_to_decimal_string(bits, signed=False) == "2147483648"
