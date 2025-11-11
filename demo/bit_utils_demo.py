#!/usr/bin/env python3
"""Demonstration of bit_utils functionality."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.numeric_core.bit_utils import (
    bit_to_char,
    print_bits_formatted,
    char_to_bit,
    string_to_bits,
    bits_to_string,
)


def main() -> None:
    print("=" * 60)
    print("BIT UTILITIES DEMONSTRATION")
    print("=" * 60)

    print("\n1. Single Bit Conversions")
    print("-" * 40)
    print(f"bit_to_char(0) = {bit_to_char(0)!r}")
    print(f"bit_to_char(1) = {bit_to_char(1)!r}")
    print(f"bit_to_char(False) = {bit_to_char(False)!r}")
    print(f"bit_to_char(True) = {bit_to_char(True)!r}")
    print(f"char_to_bit('0') = {char_to_bit('0')!r}")
    print(f"char_to_bit('1') = {char_to_bit('1')!r}")

    print("\n2. Bit Lists to Strings")
    print("-" * 40)
    bits1 = [1, 0, 1, 0]
    print(f"bits_to_string({bits1}) = {bits_to_string(bits1)!r}")

    bits2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1]
    print(f"bits_to_string({bits2})")
    print(f"  = {bits_to_string(bits2)!r}")

    print("\n3. Strings to Bit Lists")
    print("-" * 40)
    s1 = "1010"
    print(f"string_to_bits({s1!r}) = {string_to_bits(s1)}")

    s2 = "0000000000000101"
    print(f"string_to_bits({s2!r})")
    print(f"  = {string_to_bits(s2)}")

    print("\n4. Round-Trip Conversions")
    print("-" * 40)
    original_string = "11001010"
    print(f"Original string: {original_string!r}")
    bits = string_to_bits(original_string)
    print(f"  → bits: {bits}")
    result_string = bits_to_string(bits)
    print(f"  → string: {result_string!r}")
    print(f"  Match: {original_string == result_string}")

    print("\n5. Formatted Bit Strings (grouped by 4)")
    print("-" * 40)

    bits_16 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1]
    formatted = print_bits_formatted(bits_16, 16)
    print(f"16-bit example: {formatted}")
    print("  Expected: '0000_0000_0000_0101'")
    print("  Match: {formatted == '0000_0000_0000_0101'}")

    print("\nOther formatting examples:")
    print(
        f"  8-bit [1,0,1,0,1,0,1,0]: "
        f"{print_bits_formatted([1, 0, 1, 0, 1, 0, 1, 0], 8)}"
    )
    print(
        f"  4-bit [1,1,1,1]: "
        f"{print_bits_formatted([1, 1, 1, 1], 4)}"
    )
    print(
        f"  5-bit [1,0,1,0,1] (no padding): "
        f"{print_bits_formatted([1, 0, 1, 0, 1], 0)}"
    )
    print(
        f"  3-bit [1,0,1] padded to 8: "
        f"{print_bits_formatted([1, 0, 1], 8)}"
    )
    print(
        "  10-bit partial group: "
        f"{print_bits_formatted([1, 1, 1, 0, 1, 0, 1, 0, 1, 0], 0)}"
    )


if __name__ == "__main__":
    main()
