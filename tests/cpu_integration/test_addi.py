from __future__ import annotations
from src.cpu.state import CPUState
from src.cpu.interpreter import step
from src.numeric_core.conversions import hex_to_bits32, bits32_to_hex


def test_addi_basic():
    state = CPUState()
    state.reset(pc=0)
    state.regs.write(1, hex_to_bits32("00000005"))
    instr = hex_to_bits32("00308113")
    step(state, instr)
    assert bits32_to_hex(state.regs.read(2)) == "00000008"
    assert state.pc == 4
