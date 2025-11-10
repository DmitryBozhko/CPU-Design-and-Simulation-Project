from __future__ import annotations

from .adders import ripple_carry_adder
from .comparators import compare_signed, compare_unsigned, is_zero
from .shifter import sll, sra, srl
from .twos_complement import negate_twos_complement


def _normalize_bits(bits: list[int]) -> list[int]:

    normalized: list[int] = []

    for bit in bits:
        normalized.append(bit & 1)

    return normalized


def _sign_bit(bits: list[int]) -> int:

    if bits:
        return bits[-1] & 1

    return 0


def _sign_extend(bits: list[int], width: int) -> list[int]:

    if width <= 0:
        return [0]

    normalized = _normalize_bits(bits)
    length = len(normalized)
    sign = _sign_bit(normalized)

    extended: list[int] = []

    for index in range(width):
        if index < length:
            extended.append(normalized[index])
        else:
            extended.append(sign)

    return extended


class ALU:
    _ADD_OPS = {"ADD", "SUB"}
    _LOGIC_OPS = {"AND", "OR", "XOR", "NOT"}
    _SHIFT_OPS = {"SLL", "SRL", "SRA"}
    _COMPARE_OPS = {"SLT", "SLTU"}
    _SHIFT_WEIGHTS = (1, 2, 4, 8, 16)

    def execute(self, op: str, a_bits: list[int], b_bits: list[int]) -> dict:

        if op in self._ADD_OPS:
            return self._execute_add_sub(op, a_bits, b_bits)
        if op in self._LOGIC_OPS:
            return self._execute_logic(op, a_bits, b_bits)
        if op in self._SHIFT_OPS:
            return self._execute_shift(op, a_bits, b_bits)
        if op in self._COMPARE_OPS:
            return self._execute_compare(op, a_bits, b_bits)

        raise ValueError(f"Unsupported ALU operation: {op!r}")

    def _execute_add_sub(self, op: str, a_bits: list[int], b_bits: list[int]) -> dict:

        width = len(a_bits)
        b_length = len(b_bits)
        if b_length > width:
            width = b_length
        if width <= 0:
            width = 1

        a_aligned = _sign_extend(a_bits, width)
        b_aligned = _sign_extend(b_bits, width)

        if op == "ADD":
            b_operand = b_aligned
        else:
            b_operand = negate_twos_complement(b_aligned)

        result_bits, carry_out = ripple_carry_adder(a_aligned, b_operand)

        result: list[int] = []
        length = len(result_bits)
        for index in range(width):
            if index < length:
                result.append(result_bits[index] & 1)
            else:
                result.append(0)

        a_sign = _sign_bit(a_aligned)
        b_sign = _sign_bit(b_operand)
        result_sign = _sign_bit(result)

        same_sign = (a_sign ^ b_sign) ^ 1
        sign_changed = result_sign ^ a_sign
        overflow = same_sign & sign_changed

        return {
            "result": result,
            "N": result_sign,
            "Z": 1 if is_zero(result) else 0,
            "C": carry_out & 1,
            "V": overflow & 1,
        }

    def _execute_logic(self, op: str, a_bits: list[int], b_bits: list[int]) -> dict:

        width = len(a_bits)
        b_length = len(b_bits)
        if b_length > width and op != "NOT":
            width = b_length
        if width <= 0:
            width = 1

        a_aligned = _sign_extend(a_bits, width)
        if op == "NOT":
            b_aligned: list[int] | None = None
        else:
            b_aligned = _sign_extend(b_bits, width)

        result: list[int] = []

        for index in range(width):
            a_bit = a_aligned[index] & 1

            if op == "NOT":
                bit = (a_bit ^ 1) & 1
            else:
                b_bit = 0
                if b_aligned:
                    b_bit = b_aligned[index] & 1

                if op == "AND":
                    bit = a_bit & b_bit
                elif op == "OR":
                    bit = a_bit | b_bit
                else:  # XOR
                    bit = (a_bit ^ b_bit) & 1

            result.append(bit)

        return {
            "result": result,
            "N": _sign_bit(result),
            "Z": 1 if is_zero(result) else 0,
            "C": 0,
            "V": 0,
        }
    
    def _execute_shift(self, op: str, a_bits: list[int], b_bits: list[int]) -> dict:

        width = len(a_bits)
        if width <= 0:
            width = 1

        operand = _sign_extend(a_bits, width)
        shamt_bits = _normalize_bits(b_bits)[:5]

        while len(shamt_bits) < 5:
            shamt_bits.append(0)

        shamt = self._shift_amount_from_bits(shamt_bits)

        if op == "SLL":
            shifted = sll(operand, shamt)
        elif op == "SRL":
            shifted = srl(operand, shamt)
        else:
            shifted = sra(operand, shamt)

        result = shifted[:width]

        return {
            "result": result,
            "N": _sign_bit(result),
            "Z": 1 if is_zero(result) else 0,
            "C": 0,
            "V": 0,
        }

    def _shift_amount_from_bits(self, bits: list[int]) -> int:

        amount = 0
        limit = len(self._SHIFT_WEIGHTS)

        for index in range(limit):
            if index >= len(bits):
                break

            bit = bits[index]
            if bit:
                amount += self._SHIFT_WEIGHTS[index]

        return amount

    def _execute_compare(self, op: str, a_bits: list[int], b_bits: list[int]) -> dict:

        if op == "SLT":
            relation = compare_signed(a_bits, b_bits)
        else:
            relation = compare_unsigned(a_bits, b_bits)

        less_bit = 0
        if relation == -1:
            less_bit = 1

        width = self._COMPARE_RESULT_WIDTH
        result: list[int] = []

        for index in range(width):
            if index == 0:
                result.append(less_bit)
            else:
                result.append(0)

        return {
            "result": result,
            "N": _sign_bit(result),
            "Z": 1 if is_zero(result) else 0,
            "C": 0,
            "V": 0,
        }