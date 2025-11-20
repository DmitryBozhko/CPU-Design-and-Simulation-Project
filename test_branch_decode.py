#AI-BEGIN
from src.cpu.interpreter import _sign_extend

# The instruction at 0x1C: 0x00418463
word = 0x00418463

# Your code extracts these:
imm_11 = (word >> 7) & 0x1      # bit 7
imm_4_1 = (word >> 8) & 0xF     # bits 8-11
imm_10_5 = (word >> 25) & 0x3F  # bits 25-30
imm_12 = (word >> 31) & 0x1     # bit 31

print(f"imm_11   = {imm_11:01b} (bit 11 of offset)")
print(f"imm_4_1  = {imm_4_1:04b} (bits 4-1 of offset)")
print(f"imm_10_5 = {imm_10_5:06b} (bits 10-5 of offset)")
print(f"imm_12   = {imm_12:01b} (bit 12 of offset)")

# Reassemble
imm_b = (imm_4_1 << 1) | (imm_10_5 << 5) | (imm_11 << 11) | (imm_12 << 12)
print(f"\nimm_b = 0x{imm_b:04X} = {imm_b}")

# Sign extend and shift
offset = _sign_extend(imm_b, 13) << 1
print(f"offset after sign_extend(13) << 1 = {offset}")

# Where should we jump?
pc = 0x1C
target = (pc + offset) & 0xFFFFFFFF
print(f"\nPC=0x{pc:08X} + offset={offset} = 0x{target:08X}")
print(f"Expected: 0x00000024 (skip one 4-byte instruction)")
#AI-END