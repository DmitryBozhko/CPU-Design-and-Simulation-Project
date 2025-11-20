from __future__ import annotations
from typing import List, Tuple


_WORD_WIDTH = 32
_NUM_REGS = 32


#AI-BEGIN
def _zero_word() -> List[int]:
    """Return a fresh 32-bit 0 word."""
    bits: List[int] = []
    i = 0
    while i < _WORD_WIDTH:
        bits.append(0)
        i = i + 1
    return bits
#AI-END


def _normalize_word(value: List[int]) -> List[int]:
    #AI-BEGIN
    """Normalize an arbitrary bit list into a 32-bit word (LSB-first)."""
    #AI-END
    normalized: List[int] = []
    length = len(value)
    i = 0
    while i < _WORD_WIDTH:
        if i < length:
            normalized.append(value[i] & 1)
        else:
            normalized.append(0)
        i = i + 1
    return normalized


class RegisterFile:
    #AI-BEGIN
    """32 x 32-bit register file for RV32, with x0 hard-wired to zero."""
    #AI-END
    def __init__(self) -> None:
        regs: List[List[int]] = []
        idx = 0
        while idx < _NUM_REGS:
            regs.append(_zero_word())
            idx = idx + 1
        self._regs = regs
    def read(self, rs: int) -> List[int]:
        #AI-BEGIN
        """Read a single register as a 32-bit bit-vector (copy).

        x0 (rs == 0) is always all zeros.
        """
        #AI-END
        if rs <= 0:
            return _zero_word()
        if rs >= _NUM_REGS:
            raise ValueError("register index out of range")
        word = self._regs[rs]
        copy: List[int] = []
        i = 0
        while i < _WORD_WIDTH:
            copy.append(word[i] & 1)
            i = i + 1
        return copy
    #AI-BEGIN
    def read_pair(self, rs1: int, rs2: int) -> Tuple[List[int], List[int]]:
        """Convenience method: read two registers at once."""
        return self.read(rs1), self.read(rs2)
    #AI-BEGIN

    def write(self, rd: int, value: List[int], write_enable: bool = True) -> None:
        #AI-BEGIN
        """Write a value into rd if write_enable is True and rd != 0.

        Value is normalized to 32 bits. Writes to x0 are ignored.
        """
        #AI-END
        if not write_enable:
            return
        if rd <= 0:
            return
        if rd >= _NUM_REGS:
            raise ValueError("register index out of range")
        self._regs[rd] = _normalize_word(value)

    def dump(self) -> List[List[int]]:
        #AI-BEGIN
        """Return a deep-ish copy of all registers (for debugging / tracing)."""
        #AI-END
        snapshot: List[List[int]] = []
        idx = 0
        while idx < _NUM_REGS:
            row = self._regs[idx]
            copy_row: List[int] = []
            j = 0
            while j < _WORD_WIDTH:
                copy_row.append(row[j] & 1)
                j = j + 1
            snapshot.append(copy_row)
            idx = idx + 1
        return snapshot
