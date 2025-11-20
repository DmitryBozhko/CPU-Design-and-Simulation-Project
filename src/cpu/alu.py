from __future__ import annotations
from typing import Dict, List, Literal, TypedDict
from src.numeric_core.conversions import bits32_to_hex, hex_to_bits32

_MASK_32 = 0xFFFFFFFF

ALUOp = Literal[
    "ADD",
    "SUB",
    "AND",
    "OR",
    "XOR",
    "SLL",
    "SRL",
    "SRA",
    "SLT",
    "SLTU",
]


class ALUResult(TypedDict):
    result: List[int]
    flags: Dict[str, bool]


def _bits_to_int(bits: List[int]) -> int:
    hex_str = bits32_to_hex(bits)
    return int(hex_str, 16)


def _int_to_bits(value: int) -> List[int]:
    value &= _MASK_32
    hex_str = f"{value:08X}"
    return hex_to_bits32(hex_str)


def _to_signed32(x: int) -> int:
    x &= _MASK_32
    if x & 0x80000000:
        return x - 0x100000000
    return x


def _compute_flags(res32: int, carry: bool, overflow: bool) -> Dict[str, bool]:
    res32 &= _MASK_32
    n_flag = bool((res32 >> 31) & 1)
    z_flag = (res32 & _MASK_32) == 0
    c_flag = bool(carry)
    v_flag = bool(overflow)
    return {"N": n_flag, "Z": z_flag, "C": c_flag, "V": v_flag}


def alu(bits_a: List[int], bits_b: List[int], op: ALUOp) -> ALUResult:
    a = _bits_to_int(bits_a) & _MASK_32
    b = _bits_to_int(bits_b) & _MASK_32
    carry_out = False
    overflow = False
    if op == "ADD":
        full = a + b
        res32 = full & _MASK_32
        carry_out = full > _MASK_32
        sign_a = (a >> 31) & 1
        sign_b = (b >> 31) & 1
        sign_r = (res32 >> 31) & 1
        overflow = (sign_a == sign_b) and (sign_r != sign_a)
    elif op == "SUB":
        full = a + ((~b + 1) & _MASK_32)
        res32 = full & _MASK_32
        carry_out = a >= b
        sign_a = (a >> 31) & 1
        sign_b = (b >> 31) & 1
        sign_r = (res32 >> 31) & 1
        overflow = (sign_a != sign_b) and (sign_r != sign_a)
    elif op == "AND":
        res32 = a & b
    elif op == "OR":
        res32 = a | b
    elif op == "XOR":
        res32 = a ^ b
    elif op in ("SLL", "SRL", "SRA"):
        shamt = b & 0x1F
        if op == "SLL":
            res32 = (a << shamt) & _MASK_32
        elif op == "SRL":
            res32 = (a >> shamt) & _MASK_32
        else:
            sa = _to_signed32(a)
            res_signed = sa >> shamt
            res32 = res_signed & _MASK_32
    elif op == "SLT":
        sa = _to_signed32(a)
        sb = _to_signed32(b)
        res32 = 1 if sa < sb else 0
    elif op == "SLTU":
        ua = a & _MASK_32
        ub = b & _MASK_32
        res32 = 1 if ua < ub else 0
    else:
        raise ValueError(f"Unsupported ALU op: {op}")
    flags = _compute_flags(res32, carry_out, overflow)
    result_bits = _int_to_bits(res32)
    return {"result": result_bits, "flags": flags}
