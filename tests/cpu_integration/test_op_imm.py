# AI-BEGIN
from __future__ import annotations

from typing import List

from src.cpu.state import CPUState
from src.cpu.interpreter import step
from src.numeric_core.conversions import hex_to_bits32, bits32_to_hex


def _encode_itype(opcode: int, rd: int, funct3: int, rs1: int, imm: int) -> List[int]:
    """Encode an I-type instruction word (RV32I) and return bits32 via hex_to_bits32.

    Layout:
      [31:20] imm[11:0] (two's complement)
      [19:15] rs1
      [14:12] funct3
      [11:7]  rd
      [6:0]   opcode
    """
    imm12 = imm & 0xFFF
    word = (
        (imm12 << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | ((rd & 0x1F) << 7)
        | (opcode & 0x7F)
    )
    hex_str = f"{word:08X}"
    return hex_to_bits32(hex_str)


def _hex_reg(state: CPUState, reg: int) -> str:
    return bits32_to_hex(state.regs.read(reg)).upper()


def test_addi_positive_imm():
    state = CPUState()
    state.reset(pc=0)

    # x1 = 5
    state.regs.write(1, hex_to_bits32("00000005"))

    # ADDI x2, x1, 3   => x2 = 8
    instr_bits = _encode_itype(opcode=0x13, rd=2, funct3=0x0, rs1=1, imm=3)
    step(state, instr_bits)

    assert _hex_reg(state, 2) == "00000008"
    assert state.pc == 4


def test_addi_negative_imm():
    state = CPUState()
    state.reset(pc=0)

    # x1 = 5
    state.regs.write(1, hex_to_bits32("00000005"))

    # ADDI x2, x1, -8  => x2 = -3 (0xFFFFFFFD)
    instr_bits = _encode_itype(opcode=0x13, rd=2, funct3=0x0, rs1=1, imm=-8)
    step(state, instr_bits)

    assert _hex_reg(state, 2) == "FFFFFFFD"
    assert state.pc == 4


def test_andi_basic():
    state = CPUState()
    state.reset(pc=0)

    # x1 = 0x00FF00FF
    state.regs.write(1, hex_to_bits32("00FF00FF"))

    # ANDI x2, x1, 0x0F0   => x2 = 0x000000F0 (mask low byte's upper nibble)
    instr_bits = _encode_itype(opcode=0x13, rd=2, funct3=0x7, rs1=1, imm=0x0F0)
    step(state, instr_bits)

    assert _hex_reg(state, 2) == "000000F0"
    assert state.pc == 4


def test_ori_basic():
    state = CPUState()
    state.reset(pc=0)

    # x1 = 0x0000FF00
    state.regs.write(1, hex_to_bits32("0000FF00"))

    # ORI x2, x1, 0x00FF   => x2 = 0x0000FFFF
    instr_bits = _encode_itype(opcode=0x13, rd=2, funct3=0x6, rs1=1, imm=0x00FF)
    step(state, instr_bits)

    assert _hex_reg(state, 2) == "0000FFFF"
    assert state.pc == 4


def test_xori_basic():
    state = CPUState()
    state.reset(pc=0)

    # x1 = 0xAAAAAAAA
    state.regs.write(1, hex_to_bits32("AAAAAAAA"))

    # XORI x2, x1, 0x0FFF  => x2 = 0x55555555 (because imm = -1, so xor with all 1s)
    instr_bits = _encode_itype(opcode=0x13, rd=2, funct3=0x4, rs1=1, imm=0x0FFF)
    step(state, instr_bits)

    assert _hex_reg(state, 2) == "55555555"
    assert state.pc == 4


def test_slti_signed():
    state = CPUState()
    state.reset(pc=0)

    # x1 = -1 (0xFFFFFFFF)
    state.regs.write(1, hex_to_bits32("FFFFFFFF"))

    # SLTI x2, x1, 1   => (-1 < 1) signed => x2 = 1
    instr_bits = _encode_itype(opcode=0x13, rd=2, funct3=0x2, rs1=1, imm=1)
    step(state, instr_bits)

    assert _hex_reg(state, 2) == "00000001"
    assert state.pc == 4


def test_sltiu_unsigned():
    state = CPUState()
    state.reset(pc=0)

    # x1 = 0xFFFFFFFF (unsigned: very large)
    state.regs.write(1, hex_to_bits32("FFFFFFFF"))

    # SLTIU x2, x1, 1  => (0xFFFFFFFF < 1) unsigned => 0
    instr_bits = _encode_itype(opcode=0x13, rd=2, funct3=0x3, rs1=1, imm=1)
    step(state, instr_bits)

    assert _hex_reg(state, 2) == "00000000"
    assert state.pc == 4


# AI-END
