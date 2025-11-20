from typing import Union, List, Dict, Any


def encode_twos_complement(value: int) -> Dict[str, Any]:
    from .twos_complement import encode_twos_complement as _encode_impl
    from .bit_utils import print_bits_formatted
    bits, hex_str, overflow = _encode_impl(value, width=32)
    bits_msb_first = list(reversed(bits))
    bin_str = print_bits_formatted(bits_msb_first, 32)
    return {
        "bin": bin_str,
        "hex": hex_str,
        "overflow_flag": overflow
    }


def decode_twos_complement(bits: Union[str, int]) -> Dict[str, int]:
    from .twos_complement import decode_twos_complement as _decode_impl
    from .bit_utils import string_to_bits
    
    if isinstance(bits, str):
        cleaned = bits.replace("_", "").replace(" ", "")
        bit_list = string_to_bits(cleaned)
    elif isinstance(bits, int):
        bit_list = []
        temp = bits & 0xFFFFFFFF
        for _ in range(32):
            bit_list.append(temp & 1)
            temp >>= 1
    else:
        raise TypeError(f"bits must be str or int, got {type(bits)}")
    
    value_str = _decode_impl(bit_list)
    return {"value": int(value_str)}


def alu(bitsA: List[int], bitsB: List[int], op: str) -> Dict[str, Any]:
    from .alu import ALU
    
    alu_obj = ALU()
    result = alu_obj.execute(op, bitsA, bitsB)
    
    return {
        "result": result["result"],
        "N": result["N"],
        "Z": result["Z"],
        "C": result["C"],
        "V": result["V"]
    }


def shifter(bits: List[int], shamt: int, op: str) -> List[int]:
    from .shifter import sll, srl, sra
    
    if op == "SLL":
        return sll(bits, shamt)
    elif op == "SRL":
        return srl(bits, shamt)
    elif op == "SRA":
        return sra(bits, shamt)
    else:
        raise ValueError(f"Unknown shift operation: {op}")


def mdu_mul(op: str, rs1_bits: List[int], rs2_bits: List[int]) -> Dict[str, Any]:
    from .mdu import mul, mulh, mulhu, mulhsu
    
    if op == "MUL":
        rd_bits, overflow, trace = mul(rs1_bits, rs2_bits)
        return {
            "rd_bits": rd_bits,
            "hi_bits": None,
            "flags": {"overflow": overflow},
            "trace": trace
        }
    elif op == "MULH":
        hi_bits, overflow, trace = mulh(rs1_bits, rs2_bits)
        return {
            "rd_bits": hi_bits,
            "hi_bits": hi_bits,
            "flags": {"overflow": overflow},
            "trace": trace
        }
    elif op == "MULHU":
        hi_bits, overflow, trace = mulhu(rs1_bits, rs2_bits)
        return {
            "rd_bits": hi_bits,
            "hi_bits": hi_bits,
            "flags": {"overflow": overflow},
            "trace": trace
        }
    elif op == "MULHSU":
        hi_bits, overflow, trace = mulhsu(rs1_bits, rs2_bits)
        return {
            "rd_bits": hi_bits,
            "hi_bits": hi_bits,
            "flags": {"overflow": overflow},
            "trace": trace
        }
    else:
        raise ValueError(f"Unknown multiply operation: {op}")


def mdu_div(op: str, rs1_bits: List[int], rs2_bits: List[int]) -> Dict[str, Any]:
    from .mdu import div, divu, rem, remu
    
    if op == "DIV":
        q_bits, r_bits, overflow, trace = div(rs1_bits, rs2_bits)
        return {
            "q_bits": q_bits,
            "r_bits": r_bits,
            "flags": {"overflow": overflow},
            "trace": trace
        }
    elif op == "DIVU":
        q_bits, r_bits, overflow, trace = divu(rs1_bits, rs2_bits)
        return {
            "q_bits": q_bits,
            "r_bits": r_bits,
            "flags": {"overflow": overflow},
            "trace": trace
        }
    elif op == "REM":
        r_bits, overflow, trace = rem(rs1_bits, rs2_bits)
        return {
            "q_bits": None,
            "r_bits": r_bits,
            "flags": {"overflow": overflow},
            "trace": trace
        }
    elif op == "REMU":
        r_bits, overflow, trace = remu(rs1_bits, rs2_bits)
        return {
            "q_bits": None,
            "r_bits": r_bits,
            "flags": {"overflow": overflow},
            "trace": trace
        }
    else:
        raise ValueError(f"Unknown divide operation: {op}")


def fpu_add(a_bits: List[int], b_bits: List[int]) -> Dict[str, Any]:
    from .float32 import fadd_f32
    result = fadd_f32(a_bits, b_bits)
    return {
        "res_bits": result["result"],
        "flags": result["flags"],
        "trace": result["trace"]
    }


def fpu_sub(a_bits: List[int], b_bits: List[int]) -> Dict[str, Any]:
    from .float32 import fsub_f32
    result = fsub_f32(a_bits, b_bits)
    return {
        "res_bits": result["result"],
        "flags": result["flags"],
        "trace": result["trace"]
    }


def fpu_mul(a_bits: List[int], b_bits: List[int]) -> Dict[str, Any]:
    from .float32 import fmul_f32
    result = fmul_f32(a_bits, b_bits)
    return {
        "res_bits": result["result"],
        "flags": result["flags"],
        "trace": result["trace"]
    }


def pack_f32(value) -> List[int]:
    from .float32 import pack_f32 as _pack_impl
    return _pack_impl(value)


def unpack_f32(bits: List[int]):
    from .float32 import unpack_f32 as _unpack_impl
    return _unpack_impl(bits)