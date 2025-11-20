from __future__ import annotations

from src.cpu.register_file import RegisterFile
from src.cpu.memory import DataMemory


class CPUState:
    def __init__(self) -> None:
        self.pc: int = 0
        self.regs = RegisterFile()
        self.data_mem = DataMemory()

    def reset(self, pc: int = 0) -> None:
        self.pc = pc
        self.regs = RegisterFile()
        self.data_mem.reset()
