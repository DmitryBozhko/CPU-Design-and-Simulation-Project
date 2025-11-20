#AI-BEGIN
#!/usr/bin/env python3
"""Run the test_base.hex program."""

from src.cpu.state import CPUState
from src.cpu.runner import load_hex_file, run_program


def main():
    # Create CPU state
    state = CPUState()
    state.reset(pc=0)
    
    # Load program into instruction memory at address 0
    hex_file = "test_base.hex"  # Make sure this file is in your project root
    print(f"Loading program from {hex_file}...")
    hex_words = load_hex_file(hex_file)
    state.instr_mem.load_program_from_hex_words(0, hex_words)
    
    print(f"Loaded {len(hex_words)} instructions")
    
    # Run the program
    run_program(state, max_steps=100)


if __name__ == "__main__":
    main()
#AI-END