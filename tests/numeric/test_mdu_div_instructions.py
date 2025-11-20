# AI-BEGIN
from __future__ import annotations

import random

from src.numeric_core.mdu import div, divu, rem, remu


def _int_to_bits32(value: int) -> list[int]:
    masked = value & 0xFFFFFFFF
    bits: list[int] = []
    for idx in range(32):
        bits.append((masked >> idx) & 1)
    return bits


def _bits32_to_int_signed(bits32: list[int]) -> int:
    if len(bits32) < 32:
        raise ValueError("expected at least 32 bits")
    masked = 0
    for idx in range(32):
        if bits32[idx] & 1:
            masked |= 1 << idx
    if masked & (1 << 31):
        return masked - (1 << 32)
    return masked


def _bits32_to_int_unsigned(bits32: list[int]) -> int:
    """Decode little-endian 32-bit bits to an unsigned Python int."""
    if len(bits32) < 32:
        raise ValueError("expected at least 32 bits")
    value = 0
    for idx in range(32):
        if bits32[idx] & 1:
            value |= 1 << idx
    return value


def _ref_div_trunc_toward_zero(a: int, b: int) -> tuple[int, int]:
    """Reference signed div/rem with truncation toward zero (excluding a/b edge cases)."""
    if b == 0:
        raise ZeroDivisionError
    # Truncation toward zero, not floor division.
    if (a >= 0 and b > 0) or (a <= 0 and b < 0):
        q = a // b
    else:
        q = -(abs(a) // abs(b))
    r = a - q * b
    return q, r


def _assert_divider_trace(trace: list[dict], allow_empty: bool = False) -> None:
    if not trace:
        assert allow_empty
        return
    entry = trace[0]
    assert set(entry.keys()) == {
        "step",
        "remainder",
        "divisor",
        "pending_remaining",
        "q_bit",
    }


# ---------- Basic deterministic tests ----------


def test_div_basic_positive_negative() -> None:
    a = _int_to_bits32(20)
    b = _int_to_bits32(-3)

    quotient_bits, remainder_bits, overflow, trace = div(a, b)
    q = _bits32_to_int_signed(quotient_bits)
    r = _bits32_to_int_signed(remainder_bits)

    assert q == -6
    assert r == 2
    assert overflow is False
    assert trace
    _assert_divider_trace(trace)


def test_div_rounds_toward_zero() -> None:
    # -7 / 3 => q = -2, r = -1 (truncate toward zero)
    a = _int_to_bits32(-7)
    b = _int_to_bits32(3)

    quotient_bits, remainder_bits, overflow, trace = div(a, b)
    q = _bits32_to_int_signed(quotient_bits)
    r = _bits32_to_int_signed(remainder_bits)

    assert q == -2
    assert r == -1
    assert overflow is False
    assert trace
    _assert_divider_trace(trace)


def test_div_division_by_zero() -> None:
    # DIV x / 0 → quotient = -1 (0xFFFFFFFF), remainder = dividend
    a_val = 123456789
    a_bits = _int_to_bits32(a_val)
    zero_bits = _int_to_bits32(0)

    quotient_bits, remainder_bits, overflow, trace = div(a_bits, zero_bits)
    q = _bits32_to_int_signed(quotient_bits)
    r = _bits32_to_int_signed(remainder_bits)

    assert q == -1
    assert r == a_val
    assert overflow is False
    _assert_divider_trace(trace, allow_empty=True)


def test_div_int_min_div_minus_one_overflow() -> None:
    # DIV INT_MIN / -1 → quotient = INT_MIN, remainder = 0, overflow = True
    int_min = -(2**31)
    a_bits = _int_to_bits32(int_min)
    b_bits = _int_to_bits32(-1)

    quotient_bits, remainder_bits, overflow, trace = div(a_bits, b_bits)
    q = _bits32_to_int_signed(quotient_bits)
    r = _bits32_to_int_signed(remainder_bits)

    assert q == int_min
    assert r == 0
    assert overflow is True
    _assert_divider_trace(trace, allow_empty=True)


def test_divu_basic() -> None:
    # Unsigned: 0x80000000 / 3 → q = 0x2AAAAAAA, r = 0x00000002
    dividend = 0x80000000
    divisor = 3

    a_bits = _int_to_bits32(dividend)
    b_bits = _int_to_bits32(divisor)

    quotient_bits, remainder_bits, overflow, trace = divu(a_bits, b_bits)
    q = _bits32_to_int_unsigned(quotient_bits)
    r = _bits32_to_int_unsigned(remainder_bits)

    assert q == 0x2AAAAAAA
    assert r == 0x00000002
    assert overflow is False
    assert trace
    _assert_divider_trace(trace)


def test_divu_division_by_zero() -> None:
    # DIVU x / 0 → quotient = 0xFFFFFFFF, remainder = dividend
    dividend = 0xDEADBEEF
    a_bits = _int_to_bits32(dividend)
    zero_bits = _int_to_bits32(0)

    quotient_bits, remainder_bits, overflow, trace = divu(a_bits, zero_bits)
    q = _bits32_to_int_unsigned(quotient_bits)
    r = _bits32_to_int_unsigned(remainder_bits)

    assert q == 0xFFFFFFFF
    assert r == dividend
    assert overflow is False
    _assert_divider_trace(trace, allow_empty=True)


def test_rem_matches_dividend_sign() -> None:
    # For REM, remainder has same sign as dividend.
    # -7 / 3 → q = -2, r = -1
    a = _int_to_bits32(-7)
    b = _int_to_bits32(3)

    remainder_bits, overflow, trace = rem(a, b)
    r = _bits32_to_int_signed(remainder_bits)

    assert r == -1
    assert overflow is False
    assert trace
    _assert_divider_trace(trace)

    # 7 / -3 → q = -2, r = 1
    a2 = _int_to_bits32(7)
    b2 = _int_to_bits32(-3)

    remainder_bits2, overflow2, trace2 = rem(a2, b2)
    r2 = _bits32_to_int_signed(remainder_bits2)

    assert r2 == 1
    assert overflow2 is False
    assert trace2
    _assert_divider_trace(trace2)


def test_rem_division_by_zero_returns_dividend() -> None:
    # REM x / 0 → remainder = dividend
    a_val = -42
    a_bits = _int_to_bits32(a_val)
    zero_bits = _int_to_bits32(0)

    remainder_bits, overflow, trace = rem(a_bits, zero_bits)
    r = _bits32_to_int_signed(remainder_bits)

    assert r == a_val
    assert overflow is False
    _assert_divider_trace(trace, allow_empty=True)


def test_remu_basic() -> None:
    dividend = 123456789
    divisor = 97

    a_bits = _int_to_bits32(dividend)
    b_bits = _int_to_bits32(divisor)

    remainder_bits, overflow, trace = remu(a_bits, b_bits)
    r = _bits32_to_int_unsigned(remainder_bits)

    assert r == dividend % divisor
    assert overflow is False
    assert trace
    _assert_divider_trace(trace)


def test_remu_division_by_zero_returns_dividend() -> None:
    dividend = 0xCAFEBABE
    a_bits = _int_to_bits32(dividend)
    zero_bits = _int_to_bits32(0)

    remainder_bits, overflow, trace = remu(a_bits, zero_bits)
    r = _bits32_to_int_unsigned(remainder_bits)

    assert r == dividend
    assert overflow is False
    _assert_divider_trace(trace, allow_empty=True)


# ---------- Randomized consistency tests ----------


def test_div_and_rem_random_consistency() -> None:
    # Exclude b = 0 and INT_MIN / -1 (handled by a dedicated test).
    int_min = -(2**31)
    int_max = 2**31 - 1

    rng = random.Random(12345)
    for _ in range(200):
        a = rng.randint(int_min, int_max)
        b = rng.randint(int_min, int_max)
        if b == 0:
            continue
        if a == int_min and b == -1:
            continue  # overflow case tested separately

        q_ref, r_ref = _ref_div_trunc_toward_zero(a, b)

        a_bits = _int_to_bits32(a)
        b_bits = _int_to_bits32(b)

        quotient_bits, remainder_bits, overflow, trace = div(a_bits, b_bits)
        q = _bits32_to_int_signed(quotient_bits)
        r = _bits32_to_int_signed(remainder_bits)

        assert overflow is False
        assert q == q_ref
        assert r == r_ref
        assert trace
        _assert_divider_trace(trace)

        # rem() should match the remainder from div()
        remainder_bits_only, overflow_rem, trace_rem = rem(a_bits, b_bits)
        r_only = _bits32_to_int_signed(remainder_bits_only)
        assert r_only == r_ref
        assert overflow_rem is False
        assert trace_rem
        _assert_divider_trace(trace_rem)


def test_divu_and_remu_random_consistency() -> None:
    rng = random.Random(54321)
    for _ in range(200):
        a = rng.randint(0, 0xFFFFFFFF)
        b = rng.randint(1, 0xFFFFFFFF)  # avoid zero here; zero case tested separately

        a_bits = _int_to_bits32(a)
        b_bits = _int_to_bits32(b)

        quotient_bits, remainder_bits, overflow, trace = divu(a_bits, b_bits)
        q = _bits32_to_int_unsigned(quotient_bits)
        r = _bits32_to_int_unsigned(remainder_bits)

        assert q == (a // b)
        assert r == (a % b)
        assert overflow is False
        assert trace
        _assert_divider_trace(trace)

        remainder_bits_only, overflow_rem, trace_rem = remu(a_bits, b_bits)
        r_only = _bits32_to_int_unsigned(remainder_bits_only)
        assert r_only == (a % b)
        assert overflow_rem is False
        assert trace_rem
        _assert_divider_trace(trace_rem)


# AI-END
