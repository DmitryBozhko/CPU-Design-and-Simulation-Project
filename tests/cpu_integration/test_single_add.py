from __future__ import annotations
from src.cpu.state import CPUState
from src.cpu.interpreter import step
from src.numeric_core.conversions import hex_to_bits32, bits32_to_hex


def test_single_add_instruction_updates_register_and_pc():
    state = CPUState()
    state.reset(pc=0)
    state.regs.write(1, hex_to_bits32("00000005"))
    state.regs.write(2, hex_to_bits32("0000000A"))
    instr_bits = hex_to_bits32("002081B3")
    step(state, instr_bits)
    x3_bits = state.regs.read(3)
    x3_hex = bits32_to_hex(x3_bits).upper()
    assert x3_hex == "0000000F"
    x0_bits = state.regs.read(0)
    x0_hex = bits32_to_hex(x0_bits).upper()
    assert x0_hex == "00000000"
    assert state.pc == 4
