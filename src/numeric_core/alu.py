from __future__ import annotations
from .adders import ripple_carry_adder
from .comparators import compare_signed, compare_unsigned, is_zero
from .shifter import sll, sra, srl
from .twos_complement import negate_twos_complement


_WORD_WIDTH = 32


def _normalize_bits(bits: list[int]) -> list[int]:
    # AI-BEGIN
    """Normalize a bit list so every entry is 0 or 1."""
    # AI-END
    normalized: list[int] = []
    for bit in bits:
        normalized.append(bit & 1)
    return normalized


def _sign_bit(bits: list[int]) -> int:
    # AI-BEGIN
    """Return the MSB of the provided bit vector."""
    # AI-END
    if bits:
        return bits[-1] & 1
    return 0


def _resolved_width(width: int) -> int:
    # AI-BEGIN
    """Ensure zero width defaults to 1 for downstream helpers."""
    # AI-END
    if width:
        return width
    return 1


def _sign_extend(bits: list[int], width: int) -> list[int]:
    # AI-BEGIN
    """Sign-extend a bit vector to the requested width."""
    # AI-END
    target_width = _resolved_width(width)
    normalized = _normalize_bits(bits)
    sign = _sign_bit(normalized)
    extended: list[int] = []
    it = iter(normalized)
    for _ in range(target_width):
        try:
            value = next(it)
        except StopIteration:
            value = sign
        extended.append(value & 1)
    return extended


_COMPARISON_LESS: dict[int, int] = {-1: 1, 0: 0, 1: 0}


class ALU:
    # AI-BEGIN
    """Bit-vector ALU that wraps numeric_core primitives."""

    # AI-END

    _COMPARE_RESULT_WIDTH = 32
    _ADD_OPS = {"ADD", "SUB"}
    _LOGIC_OPS = {"AND", "OR", "XOR", "NOT"}
    _SHIFT_OPS = {"SLL", "SRL", "SRA"}
    _COMPARE_OPS = {"SLT", "SLTU"}
    _SHIFT_WEIGHTS = (1, 2, 4, 8, 16)

    def execute(self, op: str, a_bits: list[int], b_bits: list[int]) -> dict:
        # AI-BEGIN
        """Dispatch an ALU operation by name."""
        # AI-END
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
        # AI-BEGIN
        """Perform signed ADD or SUB operations."""
        # AI-END
        width = _WORD_WIDTH
        a_aligned = _sign_extend(a_bits, width)
        b_aligned = _sign_extend(b_bits, width)
        if op == "ADD":
            b_operand = b_aligned
        else:
            b_operand = negate_twos_complement(b_aligned)
        result_bits, carry_out = ripple_carry_adder(a_aligned, b_operand)
        result: list[int] = []
        it = iter(result_bits)
        for _ in range(width):
            try:
                bit = next(it)
            except StopIteration:
                bit = 0
            result.append(bit & 1)
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
        # AI-BEGIN
        """Perform AND/OR/XOR/NOT on the inputs."""
        # AI-END
        width = _WORD_WIDTH
        a_aligned = _sign_extend(a_bits, width)
        if op == "NOT":
            b_aligned: list[int] | None = None
        else:
            b_aligned = _sign_extend(b_bits, width)
        result: list[int] = []
        idx = 0
        for _ in range(width):
            a_bit = a_aligned[idx] & 1
            if op == "NOT":
                bit = (a_bit ^ 1) & 1
            else:
                b_bit = 0
                if b_aligned:
                    b_bit = b_aligned[idx] & 1
                if op == "AND":
                    bit = a_bit & b_bit
                elif op == "OR":
                    bit = a_bit | b_bit
                else:
                    bit = (a_bit ^ b_bit) & 1
            result.append(bit)
            idx += 1
        return {
            "result": result,
            "N": _sign_bit(result),
            "Z": 1 if is_zero(result) else 0,
            "C": 0,
            "V": 0,
        }

    def _execute_shift(self, op: str, a_bits: list[int], b_bits: list[int]) -> dict:
        # AI-BEGIN
        """Execute logical or arithmetic shifts using the shifter module."""
        # AI-END
        width = _WORD_WIDTH
        operand = _sign_extend(a_bits, width)
        shamt = self._shift_amount_from_bits(_normalize_bits(b_bits))
        if op == "SLL":
            shifted = sll(operand, shamt)
        elif op == "SRL":
            shifted = srl(operand, shamt)
        else:
            shifted = sra(operand, shamt)
        result: list[int] = []
        it = iter(shifted)
        for _ in range(width):
            try:
                bit = next(it)
            except StopIteration:
                bit = 0
            result.append(bit & 1)

        return {
            "result": result,
            "N": _sign_bit(result),
            "Z": 1 if is_zero(result) else 0,
            "C": 0,
            "V": 0,
        }

    def _execute_compare(self, op: str, a_bits: list[int], b_bits: list[int]) -> dict:
        # AI-BEGIN
        """Produce SLT/SLTU comparison results."""
        # AI-END
        if op == "SLT":
            relation = compare_signed(a_bits, b_bits)
        else:
            relation = compare_unsigned(a_bits, b_bits)
        less_bit = _COMPARISON_LESS[relation]

        width = self._COMPARE_RESULT_WIDTH
        result: list[int] = []
        result.append(less_bit)
        for _ in range(1, width):
            result.append(0)

        return {
            "result": result,
            "N": _sign_bit(result),
            "Z": 1 if is_zero(result) else 0,
            "C": 0,
            "V": 0,
        }

    def _shift_amount_from_bits(self, bits: list[int]) -> int:
        # AI-BEGIN
        """Decode a five-bit little-endian shift amount."""
        # AI-END
        amount = 0
        it = iter(bits)
        for weight in self._SHIFT_WEIGHTS:
            try:
                bit = next(it)
            except StopIteration:
                bit = 0
            if bit & 1:
                amount |= weight
        return amount
