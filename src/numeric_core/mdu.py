from __future__ import annotations
from .conversions import (
    decimal_string_to_bits32,
    compare_unsigned,
    _is_non_negative_compare,
)


def _ensure_word(bits32: list[int]) -> list[int]:
    normalized: list[int] = []
    for bit in bits32[:32]:
        normalized.append(bit & 1)
    try:
        bits32[31]
    except IndexError as exc:  # pragma: no cover - defensive
        raise ValueError("operand must contain 32 bits") from exc
    if bits32[32:]:
        raise ValueError("operand must contain exactly 32 bits")
    return normalized


def _zero_list(length: int) -> list[int]:
    zeros: list[int] = []
    for _ in range(length):
        zeros.append(0)
    return zeros


def _add_bits(a_bits: list[int], b_bits: list[int]) -> list[int]:
    result: list[int] = []
    carry = 0
    it_a = iter(a_bits)
    it_b = iter(b_bits)
    while True:
        a_has = 1
        b_has = 1
        try:
            a_val = next(it_a)
        except StopIteration:
            a_val = 0
            a_has = 0
        try:
            b_val = next(it_b)
        except StopIteration:
            b_val = 0
            b_has = 0
        if not ((a_has | b_has) & 1):
            break
        if (a_has ^ b_has) & 1:
            raise ValueError("bit vectors must have same width")
        a_bit = a_val & 1
        b_bit = b_val & 1
        sum_bit = a_bit ^ b_bit ^ carry
        carry_out = (a_bit & b_bit) | (a_bit & carry) | (b_bit & carry)
        result.append(sum_bit)
        carry = carry_out
    return result


def _negate_twos_complement(bits: list[int]) -> list[int]:
    width = len(bits)
    inverted: list[int] = []
    for bit in bits:
        b = bit & 1
        inverted.append(b ^ 1)
    one = _zero_list(width)
    if width:
        one[0] = 1
    return _add_bits(inverted, one)


def _is_zero_bits(bits: list[int]) -> bool:
    for bit in bits:
        if bit & 1:
            return False
    return True


_INT_MIN_BITS32: list[int] = []
for _ in range(31):
    _INT_MIN_BITS32.append(0)
_INT_MIN_BITS32.append(1)


_INT_MINUS_ONE_BITS32: list[int] = []
for _ in range(32):
    _INT_MINUS_ONE_BITS32.append(1)


class Multiplier:
    multiplicand: list[int]
    multiplier: list[int]
    accumulator: list[int]
    step_counter: int
    state: str
    def __init__(self) -> None:
        self.multiplicand = _zero_list(64)
        self.multiplier = _zero_list(32)
        self.accumulator = _zero_list(64)
        self.state = "IDLE"
        self.step_counter = 0
        self._step_history: list[dict[str, object]] = []
    def load_operands(self, a_bits32: list[int], b_bits32: list[int]) -> None:
        """Load 32-bit operands for an unsigned 32×32 → 64 multiply."""
        multiplicand32 = _ensure_word(a_bits32)
        multiplier32 = _ensure_word(b_bits32)
        new_multiplicand = _zero_list(64)
        for idx in range(32):
            new_multiplicand[idx] = multiplicand32[idx] & 1
        self.multiplicand = new_multiplicand
        self.multiplier = multiplier32
        self.accumulator = _zero_list(64)
        self._step_history = []
        self.step_counter = 0
        self.state = "RUN"


    def step(self) -> None:
        if self.state != "RUN":
            return
        if self.multiplier and (self.multiplier[0] & 1):
            self.accumulator = _add_bits(self.accumulator, self.multiplicand)
        self.multiplicand = [0] + self.multiplicand[:-1]
        new_multiplier: list[int] = []
        if self.multiplier:
            for idx in range(1, len(self.multiplier)):
                new_multiplier.append(self.multiplier[idx] & 1)
            new_multiplier.append(0)
        else:
            new_multiplier = _zero_list(32)
        self.multiplier = new_multiplier
        snapshot = {
            "step": self.step_counter,
            "accumulator": self.accumulator[:],
            "multiplicand": self.multiplicand[:],
            "multiplier": self.multiplier[:],
        }
        self._step_history.append(snapshot)
        self.step_counter = len(self._step_history)
        count_bits = decimal_string_to_bits32(str(self.step_counter), False)
        max_steps_bits = decimal_string_to_bits32("32", False)
        cmp_result = compare_unsigned(count_bits, max_steps_bits)
        if _is_non_negative_compare(cmp_result):
            self.state = "DONE"


    def is_done(self) -> bool:
        return self.state == "DONE"


    def get_product(self) -> list[int]:
        return self.accumulator[:]


def _multiply_unsigned_32x32(a_bits32: list[int], b_bits32: list[int]) -> list[int]:
    m = Multiplier()
    m.load_operands(a_bits32, b_bits32)
    while not m.is_done():
        m.step()
    return m.get_product()


def _signed_product_64(a_bits32: list[int], b_bits32: list[int]) -> list[int]:
    a_word = _ensure_word(a_bits32)
    b_word = _ensure_word(b_bits32)
    sign_a = a_word[31] & 1
    sign_b = b_word[31] & 1
    if sign_a & 1:
        abs_a = _negate_twos_complement(a_word)
    else:
        abs_a = a_word[:]
    if sign_b & 1:
        abs_b = _negate_twos_complement(b_word)
    else:
        abs_b = b_word[:]
    unsigned_product = _multiply_unsigned_32x32(abs_a, abs_b)
    sign_result = sign_a ^ sign_b
    if sign_result & 1:
        return _negate_twos_complement(unsigned_product)
    return unsigned_product


def mul(a_bits32: list[int], b_bits32: list[int]) -> dict:
    full_product = _signed_product_64(a_bits32, b_bits32)
    low32: list[int] = []
    for idx in range(32):
        low32.append(full_product[idx] & 1)
    sign_bit = low32[31] & 1
    overflow_flag = 0
    for idx in range(32, 64):
        bit = full_product[idx] & 1
        if bit ^ sign_bit:
            overflow_flag = 1
            break
    return {"result": low32, "overflow": bool(overflow_flag)}


def mulh(a_bits32: list[int], b_bits32: list[int]) -> dict:
    full_product = _signed_product_64(a_bits32, b_bits32)
    high32: list[int] = []
    for idx in range(32, 64):
        high32.append(full_product[idx] & 1)
    return {"result": high32}


def mulhu(a_bits32: list[int], b_bits32: list[int]) -> dict:
    a_word = _ensure_word(a_bits32)
    b_word = _ensure_word(b_bits32)
    full_product = _multiply_unsigned_32x32(a_word, b_word)
    high32: list[int] = []
    for idx in range(32, 64):
        high32.append(full_product[idx] & 1)
    return {"result": high32}


def mulhsu(a_bits32: list[int], b_bits32: list[int]) -> dict:
    a_word = _ensure_word(a_bits32)
    sign_a = a_word[31] & 1
    if sign_a & 1:
        abs_a = _negate_twos_complement(a_word)
    else:
        abs_a = a_word[:]
    abs_b = _ensure_word(b_bits32)
    unsigned_product = _multiply_unsigned_32x32(abs_a, abs_b)
    if sign_a & 1:
        full_product = _negate_twos_complement(unsigned_product)
    else:
        full_product = unsigned_product
    high32: list[int] = []
    for idx in range(32, 64):
        high32.append(full_product[idx] & 1)
    return {"result": high32}


class Divider:
    dividend: list[int]
    divisor: list[int]
    remainder: list[int]
    _pending_bits: list[int]
    _quotient_msb_first: list[int]
    step_counter: int
    state: str


    def __init__(self) -> None:
        self.dividend = _zero_list(32)
        self.divisor = _zero_list(32)
        self.remainder = _zero_list(32)
        self._pending_bits = []
        self._quotient_msb_first = []
        self.step_counter = 0
        self.state = "IDLE"
        self._step_history: list[dict[str, object]] = []


    def load_operands(self, dividend_bits32: list[int], divisor_bits32: list[int]) -> None:
        dividend = _ensure_word(dividend_bits32)
        divisor = _ensure_word(divisor_bits32)
        self.dividend = dividend
        self.divisor = divisor
        self.remainder = _zero_list(32)
        self._pending_bits = []
        for bit in reversed(dividend):
            self._pending_bits.append(bit & 1)
        self._quotient_msb_first = []
        self._step_history = []
        self.step_counter = 0
        self.state = "RUN"


    def step(self) -> None:
        if self.state != "RUN":
            return
        if self._pending_bits:
            incoming = self._pending_bits.pop(0) & 1
        else:
            incoming = 0
        shifted: list[int] = [0] + self.remainder[:-1]
        shifted[0] = incoming & 1
        self.remainder = shifted
        cmp_result = compare_unsigned(self.remainder, self.divisor)
        if _is_non_negative_compare(cmp_result):
            neg_divisor = _negate_twos_complement(self.divisor)
            self.remainder = _add_bits(self.remainder, neg_divisor)
            q_bit = 1
        else:
            q_bit = 0
        self._quotient_msb_first.append(q_bit)
        snapshot = {
            "step": self.step_counter,
            "remainder": self.remainder[:],
            "divisor": self.divisor[:],
            "pending_remaining": len(self._pending_bits),
            "q_bit": q_bit,
        }
        self._step_history.append(snapshot)
        self.step_counter = len(self._step_history)
        count_bits = decimal_string_to_bits32(str(self.step_counter), False)
        max_steps_bits = decimal_string_to_bits32("32", False)
        cmp_steps = compare_unsigned(count_bits, max_steps_bits)
        if _is_non_negative_compare(cmp_steps):
            self.state = "DONE"

    def is_done(self) -> bool:
        return self.state == "DONE"

    def get_quotient(self) -> list[int]:
        bits_le_src = list(reversed(self._quotient_msb_first))
        it = iter(bits_le_src)
        padded: list[int] = []
        for _ in range(32):
            try:
                value = next(it)
            except StopIteration:
                value = 0
            padded.append(value & 1)
        return padded

    def get_remainder(self) -> list[int]:
        return self.remainder[:]


def _unsigned_div_rem_32(
    a_bits32: list[int],
    b_bits32: list[int],
) -> tuple[list[int], list[int]]:
    dividend = _ensure_word(a_bits32)
    divisor = _ensure_word(b_bits32)
    if _is_zero_bits(divisor):
        raise ValueError("divisor must be non zero")
    d = Divider()
    d.load_operands(dividend, divisor)
    while not d.is_done():
        d.step()
    return d.get_quotient(), d.get_remainder()


def _signed_div_rem_32(
    a_bits32: list[int],
    b_bits32: list[int],
) -> dict:
    dividend = _ensure_word(a_bits32)
    divisor = _ensure_word(b_bits32)
    if (dividend == _INT_MIN_BITS32) and (divisor == _INT_MINUS_ONE_BITS32):
        result_remainder = _zero_list(32)
        return {
            "quotient": dividend[:],
            "remainder": result_remainder,
            "overflow": True,
        }
    if _is_zero_bits(divisor):
        return {
            "quotient": _INT_MINUS_ONE_BITS32[:],
            "remainder": dividend[:],
            "overflow": False,
        }
    sign_a = dividend[31] & 1
    sign_b = divisor[31] & 1
    if sign_a & 1:
        abs_a = _negate_twos_complement(dividend)
    else:
        abs_a = dividend[:]

    if sign_b & 1:
        abs_b = _negate_twos_complement(divisor)
    else:
        abs_b = divisor[:]
    quot_u, rem_u = _unsigned_div_rem_32(abs_a, abs_b)
    sign_q = sign_a ^ sign_b
    if sign_q & 1:
        quotient_bits = _negate_twos_complement(quot_u)
    else:
        quotient_bits = quot_u
    if sign_a & 1:
        remainder_bits = _negate_twos_complement(rem_u)
    else:
        remainder_bits = rem_u

    return {
        "quotient": quotient_bits,
        "remainder": remainder_bits,
        "overflow": False,
    }


def div(a_bits32: list[int], b_bits32: list[int]) -> dict:
    dividend = _ensure_word(a_bits32)
    divisor = _ensure_word(b_bits32)

    if _is_zero_bits(divisor):
        return {
            "quotient": _INT_MINUS_ONE_BITS32[:],
            "remainder": dividend,
            "overflow": False,
        }

    return _signed_div_rem_32(dividend, divisor)


def divu(a_bits32: list[int], b_bits32: list[int]) -> dict:
    dividend = _ensure_word(a_bits32)
    divisor = _ensure_word(b_bits32)

    if _is_zero_bits(divisor):
        return {
            "quotient": _INT_MINUS_ONE_BITS32[:],
            "remainder": dividend,
        }

    quotient_bits, remainder_bits = _unsigned_div_rem_32(dividend, divisor)
    return {"quotient": quotient_bits, "remainder": remainder_bits}


def rem(a_bits32: list[int], b_bits32: list[int]) -> dict:
    dividend = _ensure_word(a_bits32)
    divisor = _ensure_word(b_bits32)

    if _is_zero_bits(divisor):
        return {"result": dividend}
    div_result = _signed_div_rem_32(dividend, divisor)
    return {"result": div_result["remainder"]}


def remu(a_bits32: list[int], b_bits32: list[int]) -> dict:
    dividend = _ensure_word(a_bits32)
    divisor = _ensure_word(b_bits32)
    if _is_zero_bits(divisor):
        return {"result": dividend}
    _, remainder_bits = _unsigned_div_rem_32(dividend, divisor)
    return {"result": remainder_bits}