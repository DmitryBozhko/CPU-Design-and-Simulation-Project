#AI-BEGIN
"""Numeric core - Spec-compliant public API."""

# Import internal implementations
from . import twos_complement as _tc
from . import alu as _alu_mod
from . import shifter as _shifter_mod
from . import mdu as _mdu_mod
from . import float32 as _float_mod

from typing import Union, List, Dict, Any


def encode_twos_complement(value: int) -> Dict[str, Any]:
    """Spec-compliant: returns dict with bin/hex/overflow_flag."""
    from .bit_utils import print_bits_formatted
    bits, hex_str, overflow = _tc.encode_twos_complement(value, 32)
    bits_msb = list(reversed(bits))
    bin_str = print_bits_formatted(bits_msb, 32)
    return {"bin": bin_str, "hex": hex_str, "overflow_flag": overflow}


def decode_twos_complement(bits: Union[str, int]) -> Dict[str, int]:
    """Spec-compliant: accepts str|int, returns dict with value."""
    from .bit_utils import string_to_bits
    if isinstance(bits, str):
        cleaned = bits.replace("_", "").replace(" ", "")
        bit_list = list(reversed(string_to_bits(cleaned)))
    elif isinstance(bits, int):
        bit_list = []
        temp = bits & 0xFFFFFFFF
        for _ in range(32):
            bit_list.append(temp & 1)
            temp >>= 1
    else:
        bit_list = bits
    value_str = _tc.decode_twos_complement(bit_list)
    return {"value": int(value_str)}


def alu(bitsA: List[int], bitsB: List[int], op: str) -> Dict[str, Any]:
    """Spec-compliant: flat dict with N,Z,C,V at top level."""
    alu_obj = _alu_mod.ALU()
    result = alu_obj.execute(op, bitsA, bitsB)
    return {
        "result": result["result"],
        "N": result["N"],
        "Z": result["Z"],
        "C": result["C"],
        "V": result["V"]
    }


def shifter(bits: List[int], shamt: int, op: str) -> List[int]:
    """Spec-compliant: unified shifter interface."""
    if op == "SLL":
        return _shifter_mod.sll(bits, shamt)
    elif op == "SRL":
        return _shifter_mod.srl(bits, shamt)
    elif op == "SRA":
        return _shifter_mod.sra(bits, shamt)
    raise ValueError(f"Unknown shift op: {op}")


def mdu_mul(op: str, rs1_bits: List[int], rs2_bits: List[int]) -> Dict[str, Any]:
    """Spec-compliant: MDU multiply with op parameter."""
    if op == "MUL":
        rd, ovf, tr = _mdu_mod.mul(rs1_bits, rs2_bits)
        return {"rd_bits": rd, "hi_bits": None, "flags": {"overflow": ovf}, "trace": tr}
    elif op == "MULH":
        hi, ovf, tr = _mdu_mod.mulh(rs1_bits, rs2_bits)
        return {"rd_bits": hi, "hi_bits": hi, "flags": {"overflow": ovf}, "trace": tr}
    elif op == "MULHU":
        hi, ovf, tr = _mdu_mod.mulhu(rs1_bits, rs2_bits)
        return {"rd_bits": hi, "hi_bits": hi, "flags": {"overflow": ovf}, "trace": tr}
    elif op == "MULHSU":
        hi, ovf, tr = _mdu_mod.mulhsu(rs1_bits, rs2_bits)
        return {"rd_bits": hi, "hi_bits": hi, "flags": {"overflow": ovf}, "trace": tr}
    raise ValueError(f"Unknown mul op: {op}")


def mdu_div(op: str, rs1_bits: List[int], rs2_bits: List[int]) -> Dict[str, Any]:
    """Spec-compliant: MDU divide with op parameter."""
    if op == "DIV":
        q, r, ovf, tr = _mdu_mod.div(rs1_bits, rs2_bits)
        return {"q_bits": q, "r_bits": r, "flags": {"overflow": ovf}, "trace": tr}
    elif op == "DIVU":
        q, r, ovf, tr = _mdu_mod.divu(rs1_bits, rs2_bits)
        return {"q_bits": q, "r_bits": r, "flags": {"overflow": ovf}, "trace": tr}
    elif op == "REM":
        r, ovf, tr = _mdu_mod.rem(rs1_bits, rs2_bits)
        return {"q_bits": None, "r_bits": r, "flags": {"overflow": ovf}, "trace": tr}
    elif op == "REMU":
        r, ovf, tr = _mdu_mod.remu(rs1_bits, rs2_bits)
        return {"q_bits": None, "r_bits": r, "flags": {"overflow": ovf}, "trace": tr}
    raise ValueError(f"Unknown div op: {op}")


def fpu_add(a_bits: List[int], b_bits: List[int]) -> Dict[str, Any]:
    """Spec-compliant: returns res_bits not result."""
    result = _float_mod.fadd_f32(a_bits, b_bits)
    return {"res_bits": result["result"], "flags": result["flags"], "trace": result["trace"]}


def fpu_sub(a_bits: List[int], b_bits: List[int]) -> Dict[str, Any]:
    """Spec-compliant: returns res_bits not result."""
    result = _float_mod.fsub_f32(a_bits, b_bits)
    return {"res_bits": result["result"], "flags": result["flags"], "trace": result["trace"]}


def fpu_mul(a_bits: List[int], b_bits: List[int]) -> Dict[str, Any]:
    """Spec-compliant: returns res_bits not result."""
    result = _float_mod.fmul_f32(a_bits, b_bits)
    return {"res_bits": result["result"], "flags": result["flags"], "trace": result["trace"]}


def pack_f32(value) -> List[int]:
    """Spec-compliant: pack float32."""
    return _float_mod.pack_f32(value)


def unpack_f32(bits: List[int]):
    """Spec-compliant: unpack float32."""
    return _float_mod.unpack_f32(bits)


__all__ = [
    "encode_twos_complement",
    "decode_twos_complement",
    "alu",
    "shifter",
    "mdu_mul",
    "mdu_div",
    "fpu_add",
    "fpu_sub",
    "fpu_mul",
    "pack_f32",
    "unpack_f32",
]
#AI-END