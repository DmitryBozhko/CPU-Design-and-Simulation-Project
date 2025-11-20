from __future__ import annotations
from typing import List
from src.cpu.state import CPUState
from src.cpu.interpreter import step
from src.numeric_core.conversions import hex_to_bits32, bits32_to_hex


def _encode_btype(
    opcode: int, funct3: int, rs1: int, rs2: int, offset: int
) -> List[int]:
    if offset & 0x1:
        raise ValueError("branch offset must be even")
    imm = (offset >> 1) & 0x1FFF
    imm_11 = (imm >> 11) & 0x1
    imm_4_1 = (imm >> 1) & 0xF
    imm_10_5 = (imm >> 5) & 0x3F
    imm_12 = (imm >> 12) & 0x1
    word = (
        (imm_12 << 31)
        | (imm_10_5 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | (imm_4_1 << 8)
        | (imm_11 << 7)
        | (opcode & 0x7F)
    )
    return hex_to_bits32(f"{word:08X}")


def _hex_reg(state: CPUState, reg: int) -> str:
    return bits32_to_hex(state.regs.read(reg)).upper()


def test_beq_taken_skips_next_instruction():
    state = CPUState()
    state.reset(pc=0)
    state.regs.write(1, hex_to_bits32("00000005"))
    state.regs.write(2, hex_to_bits32("00000005"))
    beq_instr = _encode_btype(opcode=0x63, funct3=0x0, rs1=1, rs2=2, offset=8)
    step(state, beq_instr)
    assert state.pc == 8


def test_beq_not_taken_falls_through():
    state = CPUState()
    state.reset(pc=0)
    state.regs.write(1, hex_to_bits32("00000005"))
    state.regs.write(2, hex_to_bits32("00000007"))
    beq_instr = _encode_btype(opcode=0x63, funct3=0x0, rs1=1, rs2=2, offset=8)
    step(state, beq_instr)
    assert state.pc == 4


def test_bne_taken_when_not_equal():
    state = CPUState()
    state.reset(pc=0)
    state.regs.write(1, hex_to_bits32("00000001"))
    state.regs.write(2, hex_to_bits32("00000002"))
    bne_instr = _encode_btype(opcode=0x63, funct3=0x1, rs1=1, rs2=2, offset=8)
    step(state, bne_instr)
    assert state.pc == 8


def test_bne_not_taken_when_equal():
    state = CPUState()
    state.reset(pc=0)
    state.regs.write(1, hex_to_bits32("00000001"))
    state.regs.write(2, hex_to_bits32("00000001"))
    bne_instr = _encode_btype(opcode=0x63, funct3=0x1, rs1=1, rs2=2, offset=8)
    step(state, bne_instr)
    assert state.pc == 4
