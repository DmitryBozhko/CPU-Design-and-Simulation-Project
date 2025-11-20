from __future__ import annotations
from typing import List
from src.cpu.state import CPUState
from src.cpu.interpreter import step
from src.numeric_core.conversions import bits32_to_hex


def load_hex_file(filepath: str) -> List[str]:
    hex_words: List[str] = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                hex_words.append(line.upper())
    return hex_words


def run_program(state: CPUState, max_steps: int = 1000) -> None:
    steps = 0
    prev_pc = -1
    halt_count = 0
    print(f"\n{'='*60}")
    print("STARTING PROGRAM EXECUTION")
    print(f"{'='*60}\n")
    while steps < max_steps:
        if state.pc == prev_pc:
            halt_count += 1
            if halt_count >= 2:
                print(f"\nHalted at PC=0x{state.pc:08X} (infinite loop detected)")
                break
        else:
            halt_count = 0
        prev_pc = state.pc
        instr_bits = state.instr_mem.load_word(state.pc)
        instr_hex = bits32_to_hex(instr_bits)
        if instr_hex == "00000000":
            print(f"\nHalted at PC=0x{state.pc:08X} (reached uninitialized memory)")
            break
        print(f"Step {steps:3d}: PC=0x{state.pc:08X}  Instr=0x{instr_hex}")
        try:
            step(state, instr_bits)
        except NotImplementedError as e:
            print(f"\nError at PC=0x{prev_pc:08X}: {e}")
            break
        steps += 1
        print(f"\n{'='*60}")
    print("FINAL CPU STATE")
    print(f"{'='*60}")
    print(f"PC: 0x{state.pc:08X}\n")
    print("Key Registers (test_base.s expectations):")
    reg_names = {
        1: "x1  (should be 5)",
        2: "x2  (should be 10)",
        3: "x3  (should be 15)",
        4: "x4  (should be 15, loaded from mem)",
        5: "x5  (should be 0x00010000 from LUI)",
        6: "x6  (should be 2, branch was taken)"
    }
    for i in [1, 2, 3, 4, 5, 6]:
        reg_bits = state.regs.read(i)
        reg_hex = bits32_to_hex(reg_bits)
        print(f"  {reg_names[i]:<40} = 0x{reg_hex}")
    
    print("\nAll Registers:")
    for i in range(32):
        reg_bits = state.regs.read(i)
        reg_hex = bits32_to_hex(reg_bits)
        if i % 4 == 0:
            print()
        print(f"  x{i:2d}=0x{reg_hex}", end="")
    print("\n")
    print("Memory Check:")
    mem_bits = state.data_mem.load_word(0x00010000)
    mem_hex = bits32_to_hex(mem_bits)
    print(f"  [0x00010000] = 0x{mem_hex} (should be 0x0000000F = 15)")