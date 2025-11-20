# AI-BEGIN
# tests/cpu_integration/test_m_extension.py
from __future__ import annotations
from src.cpu.state import CPUState
from src.cpu.interpreter import step
from src.numeric_core.conversions import hex_to_bits32, bits32_to_hex


def _word_to_bits32(word: int) -> list[int]:
    return hex_to_bits32(f"{word:08X}")


def _encode_r_type(
    funct7: int,
    rs2: int,
    rs1: int,
    funct3: int,
    rd: int,
    opcode: int = 0x33,
) -> list[int]:
    word = (
        ((funct7 & 0x7F) << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | ((rd & 0x1F) << 7)
        | (opcode & 0x7F)
    )
    return _word_to_bits32(word)


def _reg_hex(state: CPUState, reg_idx: int) -> str:
    """Read a register and convert to canonical 8-hex-digit word."""
    bits = state.regs.read(reg_idx)
    return bits32_to_hex(bits)


def test_cpu_mul_signed_basic():
    """MUL x3, x1, x2: low 32 bits of signed product."""
    state = CPUState()

    # x1 = 3
    state.regs.write(1, hex_to_bits32("00000003"))
    # x2 = -2 (0xFFFFFFFE)
    state.regs.write(2, hex_to_bits32("FFFFFFFE"))

    instr_bits = _encode_r_type(
        funct7=0x01,  # M-extension
        rs2=2,
        rs1=1,
        funct3=0x0,  # MUL
        rd=3,
    )

    step(state, instr_bits)

    # 3 * -2 = -6 -> 0xFFFFFFFA
    assert _reg_hex(state, 3) == "FFFFFFFA"
    assert state.pc == 4


def test_cpu_mulh_signed_high_half():
    """MULH x3, x1, x2: high 32 bits of signed product."""
    state = CPUState()

    # Choose values where high half is non-trivial.
    # x1 = 0x40000000 (2^30)
    # x2 = 0x40000000 (2^30)
    state.regs.write(1, hex_to_bits32("40000000"))
    state.regs.write(2, hex_to_bits32("40000000"))

    instr_bits = _encode_r_type(
        funct7=0x01,  # M-extension
        rs2=2,
        rs1=1,
        funct3=0x1,  # MULH
        rd=3,
    )

    step(state, instr_bits)

    # (2^30 * 2^30) = 2^60
    # 64-bit product = 0x0000000F00000000; high half = 0x0000000F
    assert _reg_hex(state, 3) == "10000000"
    assert state.pc == 4


def test_cpu_div_basic_signed():
    """DIV x3, x1, x2: signed division."""
    state = CPUState()

    # x1 = -7, x2 = 2
    state.regs.write(1, hex_to_bits32("FFFFFFF9"))  # -7
    state.regs.write(2, hex_to_bits32("00000002"))  # 2

    instr_bits = _encode_r_type(
        funct7=0x01,
        rs2=2,
        rs1=1,
        funct3=0x4,  # DIV
        rd=3,
    )

    step(state, instr_bits)

    # -7 / 2 = -3 (trunc toward zero in RISC-V)
    assert _reg_hex(state, 3) == "FFFFFFFD"
    assert state.pc == 4


def test_cpu_div_by_zero_and_rem_by_zero():
    # DIV: quotient = -1, remainder = dividend
    state = CPUState()
    state.regs.write(1, hex_to_bits32("00000007"))  # dividend = 7
    state.regs.write(2, hex_to_bits32("00000000"))  # divisor = 0

    div_instr = _encode_r_type(
        funct7=0x01,
        rs2=2,
        rs1=1,
        funct3=0x4,  # DIV
        rd=3,
    )
    step(state, div_instr)

    assert _reg_hex(state, 3) == "FFFFFFFF"  # -1
    assert state.pc == 4

    # REM: remainder = dividend (quotient is ignored here)
    rem_instr = _encode_r_type(
        funct7=0x01,
        rs2=2,
        rs1=1,
        funct3=0x6,  # REM
        rd=4,
    )
    step(state, rem_instr)

    assert _reg_hex(state, 4) == "00000007"
    assert state.pc == 8


def test_cpu_div_int_min_edge_case():
    state = CPUState()

    # x1 = INT_MIN (0x80000000), x2 = -1 (0xFFFFFFFF)
    state.regs.write(1, hex_to_bits32("80000000"))
    state.regs.write(2, hex_to_bits32("FFFFFFFF"))

    instr_bits = _encode_r_type(
        funct7=0x01,
        rs2=2,
        rs1=1,
        funct3=0x4,  # DIV
        rd=3,
    )

    step(state, instr_bits)

    # Result should be INT_MIN again, per your MDU semantics
    assert _reg_hex(state, 3) == "80000000"
    assert state.pc == 4


def test_cpu_divu_unsigned():
    """DIVU x3, x1, x2: unsigned division."""
    state = CPUState()

    # x1 = 0xFFFFFFFE (4294967294), x2 = 2
    state.regs.write(1, hex_to_bits32("FFFFFFFE"))
    state.regs.write(2, hex_to_bits32("00000002"))

    instr_bits = _encode_r_type(
        funct7=0x01,
        rs2=2,
        rs1=1,
        funct3=0x5,  # DIVU
        rd=3,
    )

    step(state, instr_bits)

    # 0xFFFFFFFE / 2 = 0x7FFFFFFF in unsigned arithmetic
    assert _reg_hex(state, 3) == "7FFFFFFF"
    assert state.pc == 4


def test_cpu_remu_unsigned():
    state = CPUState()

    # x1 = 0xFFFFFFFF (4294967295), x2 = 10
    state.regs.write(1, hex_to_bits32("FFFFFFFF"))
    state.regs.write(2, hex_to_bits32("0000000A"))

    instr_bits = _encode_r_type(
        funct7=0x01,
        rs2=2,
        rs1=1,
        funct3=0x7,  # REMU
        rd=3,
    )

    step(state, instr_bits)

    # 4294967295 % 10 = 5 -> 0x00000005
    assert _reg_hex(state, 3) == "00000005"
    assert state.pc == 4


# AI-END
