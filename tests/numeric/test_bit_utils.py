import pytest
from src.numeric_core.bit_utils import (
    bit_to_char,
    print_bits_formatted,
    char_to_bit,
    string_to_bits,
    bits_to_string,
)


class TestBitToChar:
    def test_zero_to_char(self):
        assert bit_to_char(0) == "0"

    def test_one_to_char(self):
        assert bit_to_char(1) == "1"

    def test_false_to_char(self):
        assert bit_to_char(False) == "0"

    def test_true_to_char(self):
        assert bit_to_char(True) == "1"

    def test_invalid_bit_raises(self):
        with pytest.raises(ValueError, match="Invalid bit value"):
            bit_to_char(2)
        with pytest.raises(ValueError, match="Invalid bit value"):
            bit_to_char(-1)
        with pytest.raises(ValueError, match="Invalid bit value"):
            bit_to_char("1")


class TestCharToBit:
    def test_char_zero_to_bit(self):
        assert char_to_bit("0") is False
        assert char_to_bit("0") == 0

    def test_char_one_to_bit(self):
        assert char_to_bit("1") is True
        assert char_to_bit("1") == 1

    def test_invalid_char_raises(self):
        with pytest.raises(ValueError, match="Invalid bit character"):
            char_to_bit("2")
        with pytest.raises(ValueError, match="Invalid bit character"):
            char_to_bit("a")
        with pytest.raises(ValueError, match="Invalid bit character"):
            char_to_bit("")


class TestBitsToString:
    def test_empty_list(self):
        assert bits_to_string([]) == ""

    def test_single_zero(self):
        assert bits_to_string([0]) == "0"

    def test_single_one(self):
        assert bits_to_string([1]) == "1"

    def test_multiple_bits(self):
        assert bits_to_string([1, 0, 1, 0]) == "1010"

    def test_all_zeros(self):
        assert bits_to_string([0, 0, 0, 0]) == "0000"

    def test_all_ones(self):
        assert bits_to_string([1, 1, 1, 1]) == "1111"

    def test_sixteen_bits(self):
        bits = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1]
        assert bits_to_string(bits) == "0000000000000101"


class TestStringToBits:
    def test_empty_string(self):
        assert string_to_bits("") == []

    def test_single_zero(self):
        assert string_to_bits("0") == [0]

    def test_single_one(self):
        assert string_to_bits("1") == [1]

    def test_multiple_bits(self):
        assert string_to_bits("1010") == [1, 0, 1, 0]

    def test_all_zeros(self):
        assert string_to_bits("0000") == [0, 0, 0, 0]

    def test_all_ones(self):
        assert string_to_bits("1111") == [1, 1, 1, 1]

    def test_sixteen_bits(self):
        s = "0000000000000101"
        expected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1]
        assert string_to_bits(s) == expected


class TestRoundTrip:
    def test_string_to_bits_to_string(self):
        original = "10101010"
        bits = string_to_bits(original)
        result = bits_to_string(bits)
        assert result == original

    def test_bits_to_string_to_bits(self):
        original = [1, 0, 1, 0, 1, 0, 1, 0]
        s = bits_to_string(original)
        result = string_to_bits(s)
        assert result == original

    def test_empty_round_trip(self):
        assert bits_to_string(string_to_bits("")) == ""
        assert string_to_bits(bits_to_string([])) == []

    def test_sixteen_bit_round_trip(self):
        original = "0000000000000101"
        bits = string_to_bits(original)
        result = bits_to_string(bits)
        assert result == original


class TestPrintBitsFormatted:
    def test_sixteen_bits_example(self):
        bits = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1]
        result = print_bits_formatted(bits, 16)
        assert result == "0000_0000_0000_0101"

    def test_eight_bits(self):
        bits = [1, 0, 1, 0, 1, 0, 1, 0]
        result = print_bits_formatted(bits, 8)
        assert result == "1010_1010"

    def test_four_bits(self):
        bits = [1, 0, 1, 0]
        result = print_bits_formatted(bits, 4)
        assert result == "1010"

    def test_twelve_bits(self):
        bits = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        result = print_bits_formatted(bits, 12)
        assert result == "1010_1010_1010"

    def test_padding_short_bits(self):
        bits = [1, 0, 1, 0, 1]
        result = print_bits_formatted(bits, 8)
        assert result == "0001_0101"

    def test_padding_to_sixteen(self):
        bits = [1, 0, 1]
        result = print_bits_formatted(bits, 16)
        assert result == "0000_0000_0000_0101"

    def test_no_padding(self):
        bits = [1, 0, 1, 0, 1]
        result = print_bits_formatted(bits, 0)
        assert result == "1_0101"

    def test_width_smaller_than_bits(self):
        bits = [1, 0, 1, 0, 1, 0, 1, 0]
        result = print_bits_formatted(bits, 4)
        assert result == "1010_1010"

    def test_empty_bits_with_width(self):
        result = print_bits_formatted([], 8)
        assert result == "0000_0000"

    def test_empty_bits_no_width(self):
        result = print_bits_formatted([], 0)
        assert result == ""

    def test_negative_width_raises(self):
        with pytest.raises(ValueError, match="width must be non-negative"):
            print_bits_formatted([1, 0], -1)

    def test_grouping_partial_leading_group(self):
        bits = [1, 1, 1, 0, 1, 0, 1, 0, 1, 0]
        result = print_bits_formatted(bits, 0)
        assert result == "11_1010_1010"

    def test_grouping_odd_length(self):
        bits = [1, 0, 1, 0, 1]
        result = print_bits_formatted(bits, 0)
        assert result == "1_0101"

    def test_grouping_exact_multiple_of_four(self):
        bits = [1, 1, 1, 1, 0, 0, 0, 0]
        result = print_bits_formatted(bits, 0)
        assert result == "1111_0000"


class TestNoIntOrBinUsed:
    def test_no_int_base_2_conversion(self):
        bits = [1, 0, 1, 0]
        s = bits_to_string(bits)
        assert s == "1010"
        assert string_to_bits(s) == bits

    def test_no_bin_conversion(self):
        for i in range(16):
            bits = []
            val = i
            for _ in range(4):
                bits.insert(0, val % 2)
                val //= 2

            s = bits_to_string(bits)
            assert len(s) == 4
            assert all(c in "01" for c in s)
            assert string_to_bits(s) == bits


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
