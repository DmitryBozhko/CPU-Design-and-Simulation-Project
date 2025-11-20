from __future__ import annotations
from typing import List
from src.cpu.state import CPUState
from src.cpu.interpreter import step
from src.numeric_core.conversions import hex_to_bits32, bits32_to_hex


def _encode_rtype(
    opcode: int, rd: int, funct3: int, rs1: int, rs2: int, funct7: int
) -> List[int]:
    word = (
        ((funct7 & 0x7F) << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | ((rd & 0x1F) << 7)
        | (opcode & 0x7F)
    )
    return hex_to_bits32(f"{word:08X}")


def _hex_reg(state: CPUState, reg: int) -> str:
    return bits32_to_hex(state.regs.read(reg)).upper()


def test_sub_basic():
    state = CPUState()
    state.reset(pc=0)
    state.regs.write(1, hex_to_bits32("0000000A"))
    state.regs.write(2, hex_to_bits32("00000003"))
    instr = _encode_rtype(opcode=0x33, rd=3, funct3=0x0, rs1=1, rs2=2, funct7=0x20)
    step(state, instr)
    assert _hex_reg(state, 3) == "00000007"
    assert state.pc == 4


# AI-BEGIN
def test_and_or_xor():
    state = CPUState()
    state.reset(pc=0)
    state.regs.write(1, hex_to_bits32("0F0F0F0F"))
    state.regs.write(2, hex_to_bits32("00FF00FF"))

    # AND
    instr = _encode_rtype(opcode=0x33, rd=3, funct3=0x7, rs1=1, rs2=2, funct7=0x00)
    step(state, instr)
    assert _hex_reg(state, 3) == "000F000F"

    # OR
    instr = _encode_rtype(opcode=0x33, rd=4, funct3=0x6, rs1=1, rs2=2, funct7=0x00)
    step(state, instr)
    assert _hex_reg(state, 4) == "0FFF0FFF"

    # XOR
    instr = _encode_rtype(opcode=0x33, rd=5, funct3=0x4, rs1=1, rs2=2, funct7=0x00)
    step(state, instr)
    assert _hex_reg(state, 5) == "0FF00FF0"


def test_shift_ops():
    state = CPUState()
    state.reset(pc=0)
    state.regs.write(1, hex_to_bits32("00000001"))
    state.regs.write(2, hex_to_bits32("00000002"))

    # SLL x3, x1, x2 (1 << 2 == 4)
    instr = _encode_rtype(opcode=0x33, rd=3, funct3=0x1, rs1=1, rs2=2, funct7=0x00)
    step(state, instr)
    assert _hex_reg(state, 3) == "00000004"

    # Prepare values for right shifts
    state.regs.write(4, hex_to_bits32("F0000000"))
    state.regs.write(5, hex_to_bits32("00000004"))

    # SRL x6, x4, x5 -> logical shift
    instr = _encode_rtype(opcode=0x33, rd=6, funct3=0x5, rs1=4, rs2=5, funct7=0x00)
    step(state, instr)
    assert _hex_reg(state, 6) == "0F000000"

    # SRA x7, x4, x5 -> arithmetic shift preserves sign bits
    instr = _encode_rtype(opcode=0x33, rd=7, funct3=0x5, rs1=4, rs2=5, funct7=0x20)
    step(state, instr)
    assert _hex_reg(state, 7) == "FF000000"


def test_slt_signed_and_unsigned():
    state = CPUState()
    state.reset(pc=0)

    # Signed: -1 < 1 => 1
    state.regs.write(1, hex_to_bits32("FFFFFFFF"))
    state.regs.write(2, hex_to_bits32("00000001"))
    instr = _encode_rtype(opcode=0x33, rd=3, funct3=0x2, rs1=1, rs2=2, funct7=0x00)
    step(state, instr)
    assert _hex_reg(state, 3) == "00000001"

    # Unsigned: 0xFFFFFFFF < 1 => 0
    instr = _encode_rtype(opcode=0x33, rd=4, funct3=0x3, rs1=1, rs2=2, funct7=0x00)
    step(state, instr)
    assert _hex_reg(state, 4) == "00000000"

    # Unsigned: 1 < 0xFFFFFFFF => 1
    instr = _encode_rtype(opcode=0x33, rd=5, funct3=0x3, rs1=2, rs2=1, funct7=0x00)
    step(state, instr)
    assert _hex_reg(state, 5) == "00000001"


# AI-END
