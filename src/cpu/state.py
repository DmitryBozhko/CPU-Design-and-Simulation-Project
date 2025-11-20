from __future__ import annotations

from src.cpu.register_file import RegisterFile
from src.cpu.memory import DataMemory


class CPUState:
    def __init__(self):
        self.pc = 0
        self.regs = RegisterFile()
        self.data_mem = DataMemory()
        self.instr_mem = DataMemory()
    
    def load_program(self, hex_file_path: str):
        with open(hex_file_path) as f:
            hex_words = [line.strip() for line in f if line.strip()]
        self.instr_mem.load_program_from_hex_words(0, hex_words)

    def reset(self, pc: int = 0) -> None:
        self.pc = pc
        self.regs = RegisterFile()
        self.data_mem.reset()
        self.instr_mem.reset()
