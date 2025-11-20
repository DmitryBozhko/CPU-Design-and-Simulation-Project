from __future__ import annotations
from typing import List
from src.cpu.state import CPUState
from src.cpu.interpreter import step
from src.numeric_core.conversions import hex_to_bits32, bits32_to_hex


def _encode_itype(opcode: int, rd: int, funct3: int, rs1: int, imm: int) -> List[int]:
    imm12 = imm & 0xFFF
    word = (
        (imm12 << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | ((rd & 0x1F) << 7)
        | (opcode & 0x7F)
    )
    return hex_to_bits32(f"{word:08X}")


def _encode_stype(opcode: int, funct3: int, rs1: int, rs2: int, imm: int) -> List[int]:
    imm12 = imm & 0xFFF
    imm_low = imm12 & 0x1F
    imm_high = (imm12 >> 5) & 0x7F
    word = (
        (imm_high << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | (imm_low << 7)
        | (opcode & 0x7F)
    )
    return hex_to_bits32(f"{word:08X}")


def _hex_reg(state: CPUState, reg: int) -> str:
    return bits32_to_hex(state.regs.read(reg)).upper()


def test_lw_reads_preloaded_memory():
    state = CPUState()
    state.reset(pc=0)
    base_addr = 0x1000
    state.regs.write(1, hex_to_bits32(f"{base_addr:08X}"))
    state.data_mem.store_word(base_addr, hex_to_bits32("DEADBEEF"))
    instr = _encode_itype(opcode=0x03, rd=2, funct3=0x2, rs1=1, imm=0)
    step(state, instr)
    assert _hex_reg(state, 2) == "DEADBEEF"
    assert state.pc == 4


def test_sw_then_lw_round_trip():
    state = CPUState()
    state.reset(pc=0)
    base_addr = 0x2000
    state.regs.write(1, hex_to_bits32(f"{base_addr:08X}"))
    state.regs.write(2, hex_to_bits32("12345678"))
    sw_instr = _encode_stype(opcode=0x23, funct3=0x2, rs1=1, rs2=2, imm=0)
    step(state, sw_instr)
    assert state.pc == 4
    state.pc = 4
    lw_instr = _encode_itype(opcode=0x03, rd=3, funct3=0x2, rs1=1, imm=0)
    step(state, lw_instr)
    assert _hex_reg(state, 3) == "12345678"
    assert state.pc == 8
