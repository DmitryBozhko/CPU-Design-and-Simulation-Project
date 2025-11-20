# src/cpu/interpreter.py
from __future__ import annotations
from typing import List
from src.cpu.alu import alu
from src.cpu.state import CPUState
from src.numeric_core.conversions import hex_to_bits32, bits32_to_hex
from src.numeric_core.mdu import (
    mul,
    mulh,
    mulhsu,
    mulhu,
    div,
    divu,
    rem,
    remu,
)


def _cpu_bits_to_mdu_bits(bits32: List[int]) -> List[int]:
    #AI-BEGIN
    """Convert CPU canonical bits32 -> MDU LSB-first bits32."""
    #AI-END
    hex_str = bits32_to_hex(bits32)
    value = int(hex_str, 16) & 0xFFFFFFFF
    out: List[int] = []
    i = 0
    while i < 32:
        out.append((value >> i) & 1)
        i = i + 1
    return out


def _mdu_bits_to_cpu_bits(bits32_lsb: List[int]) -> List[int]:
    #AI-BEGIN
    """Convert MDU LSB-first bits32 -> CPU canonical bits32."""
    #AI-END
    value = 0
    i = 0
    while i < 32:
        if i < len(bits32_lsb) and (bits32_lsb[i] & 1):
            value |= 1 << i
        i = i + 1
    hex_str = f"{value:08X}"
    return hex_to_bits32(hex_str)


def _bits_to_uint(bits: List[int]) -> int:
    #AI-BEGIN
    """Convert a 32-bit instruction bit vector into an integer.

    Supports both:
      * canonical hex_to_bits32 layout
      * plain little-endian layout where bits[i] is bit i.
    """
    #AI-END
    if len(bits) != 32:
        raise ValueError("instr_bits must contain exactly 32 bits")
    hex_str = bits32_to_hex(bits)
    word1 = int(hex_str, 16)
    word2 = 0
    i = 0
    while i < 32:
        if bits[i] & 1:
            word2 |= 1 << i
        i = i + 1
    valid_opcodes = (0x33, 0x13, 0x03, 0x23, 0x63)
    op1 = word1 & 0x7F
    op2 = word2 & 0x7F
    if op1 in valid_opcodes:
        return word1
    if op2 in valid_opcodes:
        return word2
    return word1


def _sign_extend(value: int, bit_width: int) -> int:
    # AI-BEGIN
    """Sign-extend a value with given bit width to Python int."""
    # AI-END
    sign_bit = 1 << (bit_width - 1)
    mask = (1 << bit_width) - 1
    value = value & mask
    if value & sign_bit:
        return value - (1 << bit_width)
    return value


def _int_to_bits32(value: int) -> List[int]:
    #AI-BEGIN
    """Convert Python int to project bits32 (via hex string)."""
    #AI-END
    value &= 0xFFFFFFFF
    hex_str = f"{value:08X}"
    return hex_to_bits32(hex_str)


def step(state: CPUState, instr_bits: List[int]) -> None:
    #AI-BEGIN
    """Execute a single RV32I instruction.

    Currently:
      * R-type: ADD (opcode=0x33, funct3=0, funct7=0x00)
      * I-type (OP-IMM / opcode=0x13):
          - ADDI  (funct3=0x0)
          - ANDI  (funct3=0x7)
          - ORI   (funct3=0x6)
          - XORI  (funct3=0x4)
          - SLTI  (funct3=0x2)
          - SLTIU (funct3=0x3)
    """
    #AI-END
    if len(instr_bits) != 32:
        raise ValueError("instr_bits must contain exactly 32 bits")
    word = _bits_to_uint(instr_bits)
    opcode = word & 0x7F
    rd = (word >> 7) & 0x1F
    funct3 = (word >> 12) & 0x7
    rs1 = (word >> 15) & 0x1F
    rs2 = (word >> 20) & 0x1F
    funct7 = (word >> 25) & 0x7F
    imm_i = _sign_extend((word >> 20) & 0xFFF, 12)

    #AI-BEGIN
    if opcode == 0x33:
        if funct7 == 0x01:
            # --- M-extension R-type ---
            # CPU regs use canonical nibble layout; MDU expects LSB-first.
            a_cpu = state.regs.read(rs1)
            b_cpu = state.regs.read(rs2)

            a_mdu = _cpu_bits_to_mdu_bits(a_cpu)
            b_mdu = _cpu_bits_to_mdu_bits(b_cpu)

            if funct3 == 0x0:  # MUL (low 32 signed)
                res_mdu, _overflow, _trace = mul(a_mdu, b_mdu)
                result_bits = _mdu_bits_to_cpu_bits(res_mdu)

            elif funct3 == 0x1:  # MULH (high 32 signed*signed)
                res_mdu, _overflow, _trace = mulh(a_mdu, b_mdu)
                result_bits = _mdu_bits_to_cpu_bits(res_mdu)

            elif funct3 == 0x2:  # MULHSU (high 32 signed*unsigned)
                res_mdu, _overflow, _trace = mulhsu(a_mdu, b_mdu)
                result_bits = _mdu_bits_to_cpu_bits(res_mdu)

            elif funct3 == 0x3:  # MULHU (high 32 unsigned*unsigned)
                res_mdu, _overflow, _trace = mulhu(a_mdu, b_mdu)
                result_bits = _mdu_bits_to_cpu_bits(res_mdu)

            elif funct3 == 0x4:  # DIV (signed)
                q_mdu, _r_mdu, _overflow, _trace = div(a_mdu, b_mdu)
                result_bits = _mdu_bits_to_cpu_bits(q_mdu)

            elif funct3 == 0x5:  # DIVU (unsigned)
                q_mdu, _r_mdu, _overflow, _trace = divu(a_mdu, b_mdu)
                result_bits = _mdu_bits_to_cpu_bits(q_mdu)

            elif funct3 == 0x6:  # REM (signed)
                r_mdu, _overflow, _trace = rem(a_mdu, b_mdu)
                result_bits = _mdu_bits_to_cpu_bits(r_mdu)

            elif funct3 == 0x7:  # REMU (unsigned)
                r_mdu, _overflow, _trace = remu(a_mdu, b_mdu)
                result_bits = _mdu_bits_to_cpu_bits(r_mdu)

            else:
                raise NotImplementedError(
                    f"Unsupported M-extension R-type: opcode=0x{opcode:02X}, "
                    f"funct3=0x{funct3:X}, funct7=0x{funct7:02X}"
                )
    #AI-END

            state.regs.write(rd, result_bits)
            state.pc = (state.pc + 4) & 0xFFFFFFFF
            return

        a_bits = state.regs.read(rs1)
        b_bits = state.regs.read(rs2)
        #AI-BEGIN
        rtype_map = {
            (0x0, 0x00): "ADD",
            (0x0, 0x20): "SUB",
            (0x7, 0x00): "AND",
            (0x6, 0x00): "OR",
            (0x4, 0x00): "XOR",
            (0x1, 0x00): "SLL",
            (0x5, 0x00): "SRL",
            (0x5, 0x20): "SRA",
            (0x2, 0x00): "SLT",
            (0x3, 0x00): "SLTU",
        }
        #AI-END
        op = rtype_map.get((funct3, funct7))
        if op is None:
            raise NotImplementedError(
                f"Unsupported R-type: opcode=0x{opcode:02X}, "
                f"funct3=0x{funct3:X}, funct7=0x{funct7:02X}"
            )

        alu_info = alu(a_bits, b_bits, op)
        result_bits = alu_info["result"]

        state.regs.write(rd, result_bits)
        state.pc = (state.pc + 4) & 0xFFFFFFFF
        return
    if opcode == 0x13:
        imm_bits32 = _int_to_bits32(imm_i)
        a_bits = state.regs.read(rs1)
        #AI-BEGIN
        if funct3 == 0x0:  # ADDI
            op = "ADD"
        elif funct3 == 0x7:  # ANDI
            op = "AND"
        elif funct3 == 0x6:  # ORI
            op = "OR"
        elif funct3 == 0x4:  # XORI
            op = "XOR"
        elif funct3 == 0x2:  # SLTI (signed)
            op = "SLT"
        elif funct3 == 0x3:  # SLTIU (unsigned)
            op = "SLTU"
        else:
            raise NotImplementedError(
                f"Unsupported OP-IMM funct3: opcode=0x{opcode:02X}, funct3=0x{funct3:X}"
            )
        #AI-END

        alu_info = alu(a_bits, imm_bits32, op)
        result_bits = alu_info["result"]
        state.regs.write(rd, result_bits)
        state.pc = (state.pc + 4) & 0xFFFFFFFF
        return
    

    if opcode == 0x03:
        if funct3 != 0x2:
            raise NotImplementedError(
                f"Unsupported LOAD funct3: opcode=0x{opcode:02X}, funct3=0x{funct3:X}"
            )
        base_bits = state.regs.read(rs1)
        base = _bits_to_uint(base_bits)
        addr = (base + imm_i) & 0xFFFFFFFF
        result_bits = state.data_mem.load_word(addr)
        state.regs.write(rd, result_bits)
        state.pc = (state.pc + 4) & 0xFFFFFFFF
        return
    

    if opcode == 0x23:
        if funct3 != 0x2:
            raise NotImplementedError(
                f"Unsupported STORE funct3: opcode=0x{opcode:02X}, funct3=0x{funct3:X}"
            )
        imm_s = ((word >> 7) & 0x1F) | (((word >> 25) & 0x7F) << 5)
        offset = _sign_extend(imm_s, 12)
        base_bits = state.regs.read(rs1)
        base = _bits_to_uint(base_bits)
        addr = (base + offset) & 0xFFFFFFFF
        value_bits = state.regs.read(rs2)
        state.data_mem.store_word(addr, value_bits)
        state.pc = (state.pc + 4) & 0xFFFFFFFF
        return


    if opcode == 0x63:
        imm_11 = (word >> 7) & 0x1
        imm_4_1 = (word >> 8) & 0xF
        imm_10_5 = (word >> 25) & 0x3F
        imm_12 = (word >> 31) & 0x1
        imm_b = (imm_4_1 << 1) | (imm_10_5 << 5) | (imm_11 << 11) | (imm_12 << 12)
        offset = _sign_extend(imm_b, 13) << 1
        rs1_bits = state.regs.read(rs1)
        rs2_bits = state.regs.read(rs2)
        v1 = _bits_to_uint(rs1_bits)
        v2 = _bits_to_uint(rs2_bits)
        if funct3 == 0x0:
            taken = v1 == v2
        elif funct3 == 0x1:
            taken = v1 != v2
        else:
            raise NotImplementedError(
                f"Unsupported BRANCH funct3: opcode=0x{opcode:02X}, funct3=0x{funct3:X}"
            )
        if taken:
            state.pc = (state.pc + offset) & 0xFFFFFFFF
        else:
            state.pc = (state.pc + 4) & 0xFFFFFFFF
        return


    raise NotImplementedError(
        f"Unsupported opcode/funct combination: "
        f"opcode=0x{opcode:02X}, funct3=0x{funct3:X}, funct7=0x{funct7:02X}"
    )
