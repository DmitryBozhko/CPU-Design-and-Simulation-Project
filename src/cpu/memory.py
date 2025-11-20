from __future__ import annotations

from src.numeric_core.conversions import hex_to_bits32


class DataMemory:
    #AI-BEGIN
    """Simple byte-addressed memory with 32-bit word loads/stores."""
    #AI-END
    def __init__(self) -> None:
        self._bytes: dict[int, int] = {}


    def reset(self) -> None:
        self._bytes = {}


    def load_program_from_hex_words(
        self,
        base_addr: int,
        hex_words: list[str],
    ) -> None:
        #AI-BEGIN
        """Helper: load a list of 8-char hex words into memory at base_addr."""
        #AI-END
        addr = base_addr
        for word_hex in hex_words:
            word_bits = hex_to_bits32(word_hex)
            value = 0
            for i in range(32):
                if word_bits[i] & 1:
                    value |= 1 << i
            for offset in range(4):
                byte_val = (value >> (8 * offset)) & 0xFF
                self._bytes[addr + offset] = byte_val
            addr += 4

    def load_word(self, addr: int) -> list[int]:
        #AI-BEGIN
        """LW semantics: 32-bit little-endian word from byte address."""
        #AI-END
        value = 0
        for offset in range(4):
            byte_val = self._bytes.get(addr + offset, 0) & 0xFF
            value |= byte_val << (8 * offset)
        bits: list[int] = []
        for i in range(32):
            bits.append((value >> i) & 1)
        return bits

    def store_word(self, addr: int, bits32: list[int]) -> None:
        #AI-BEGIN
        """SW semantics: store 32-bit word to byte address (little-endian)."""
        #AI-END
        value = 0
        for i in range(32):
            if i < len(bits32) and (bits32[i] & 1):
                value |= 1 << i
        for offset in range(4):
            byte_val = (value >> (8 * offset)) & 0xFF
            self._bytes[addr + offset] = byte_val
