#!/usr/bin/env python3
"""
Bioart Programming Language Demo Script
Demonstrates Option 1: 2-bit encoding with maximum efficiency
"""

def bioart_encode_demo():
    """Demonstrate bioart encoding/decoding capabilities"""

    # 2-bit DNA encoding
    dna_to_bits = {'A': '00', 'U': '01', 'C': '10', 'G': '11'}
    bits_to_dna = {'00': 'A', '01': 'U', '10': 'C', '11': 'G'}

    def dna_to_byte(dna_seq):
        """Convert 4 DNA nucleotides to 1 byte"""
        binary = ''.join(dna_to_bits[n] for n in dna_seq)
        return int(binary, 2)

    def byte_to_dna(byte_val):
        """Convert 1 byte to 4 DNA nucleotides"""
        binary = format(byte_val, '08b')
        return ''.join(bits_to_dna[binary[i:i+2]] for i in range(0, 8, 2))

    print("🧬 Bioart Programming Language - Option 1 Demo")
    print("=" * 50)

    # Basic encoding demo
    print("\n1. Basic DNA Encoding:")
    examples = ['AAAA', 'AUCG', 'GGGG', 'UCGA']
    for dna in examples:
        byte_val = dna_to_byte(dna)
        binary = format(byte_val, '08b')
        print(f"   {dna} → {binary} → {byte_val:3d}")

    # Reverse encoding demo
    print("\n2. Reverse Encoding:")
    for i in [0, 27, 255, 170]:
        dna = byte_to_dna(i)
        binary = format(i, '08b')
        print(f"   {i:3d} → {binary} → {dna}")

    # Text to DNA conversion
    print("\n3. Text to DNA Conversion:")
    text = "Hi!"
    print(f"   Original text: '{text}'")

    dna_sequence = ""
    for char in text:
        byte_val = ord(char)
        dna_seq = byte_to_dna(byte_val)
        dna_sequence += dna_seq
        print(f"   '{char}' (ASCII {byte_val}) → {dna_seq}")

    print(f"   Complete DNA: {dna_sequence}")

    # DNA back to text
    print("\n4. DNA back to Text:")
    restored_text = ""
    for i in range(0, len(dna_sequence), 4):
        dna_chunk = dna_sequence[i:i+4]
        byte_val = dna_to_byte(dna_chunk)
        char = chr(byte_val)
        restored_text += char
        print(f"   {dna_chunk} → {byte_val} → '{char}'")

    print(f"   Restored text: '{restored_text}'")
    print(f"   Perfect match: {text == restored_text}")

    # File storage demo
    print("\n5. Binary File Storage:")
    data = bytes([72, 101, 108, 108, 111])  # "Hello"
    print(f"   Binary data: {list(data)}")

    # Convert to DNA
    dna_file = ""
    for byte_val in data:
        dna_file += byte_to_dna(byte_val)
    print(f"   As DNA: {dna_file}")

    # Convert back
    restored_data = []
    for i in range(0, len(dna_file), 4):
        dna_chunk = dna_file[i:i+4]
        restored_data.append(dna_to_byte(dna_chunk))

    print(f"   Restored: {restored_data}")
    print(f"   As text: '{bytes(restored_data).decode()}'")

    # Storage efficiency
    print("\n6. Storage Efficiency:")
    print(f"   Original: {len(data)} bytes")
    print(f"   As DNA: {len(dna_file)} nucleotides")
    print(f"   Ratio: {len(dna_file)/len(data)} nucleotides per byte")
    print("   → Maximum density: 4 nucleotides = 1 byte")

def bioart_programming_demo():
    """Demonstrate bioart programming capabilities"""

    print("\n🧬 Bioart Programming Instructions:")
    print("=" * 50)

    # DNA instruction set
    instructions = {
        'AAAA': ('NOP',   0,   'No Operation'),
        'AAAU': ('LOAD',  1,   'Load Value'),
        'AAAC': ('STORE', 2,   'Store Value'),
        'AAAG': ('ADD',   3,   'Add'),
        'AAUA': ('SUB',   4,   'Subtract'),
        'AAUU': ('MUL',   5,   'Multiply'),
        'AAUC': ('DIV',   6,   'Divide'),
        'AAUG': ('PRINT', 7,   'Print Output'),
        'AAGA': ('HALT',  12,  'Halt Program'),
    }

    print("DNA Instruction Set:")
    for dna, (name, code, desc) in instructions.items():
        binary = ''.join(['00' if n=='A' else '01' if n=='U' else '10' if n=='C' else '11' for n in dna])
        print(f"   {dna} → {binary} → {code:2d} → {name:5} ({desc})")

    # Sample program
    print("\nSample DNA Program:")
    program = "AAAU AACA AAAG AAAC AAUG AAGA"  # Load 42, Add 8, Print, Halt
    print(f"   Source: {program}")

    # Convert to bytecode
    bytecode = []
    for dna in program.split():
        if dna in instructions:
            bytecode.append(instructions[dna][1])

    print(f"   Bytecode: {bytecode}")
    print("   → This DNA sequence is a complete program!")

def main():
    """Main demonstration function"""
    bioart_encode_demo()
    bioart_programming_demo()

    print("\n🎯 Key Benefits of Option 1:")
    print("✓ Maximum efficiency: 4 nucleotides per byte")
    print("✓ Direct binary compatibility")
    print("✓ Universal data storage (ANY file type)")
    print("✓ Perfect reversibility (no data loss)")
    print("✓ Fast processing (no translation overhead)")
    print("✓ Memory efficient (smallest representation)")
    print("✓ System integration (works with all tools)")

if __name__ == "__main__":
    main()
