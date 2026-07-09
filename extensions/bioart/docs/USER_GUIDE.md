# Bioart DNA Programming Language - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Features](#core-features)
5. [Advanced Features](#advanced-features)
6. [Tools and Utilities](#tools-and-utilities)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Introduction

Bioart is a revolutionary programming language that uses biological DNA sequences as code, implementing 2-bit encoding for maximum efficiency and direct binary compatibility. This guide covers all features from basic usage to advanced biological computing.

## Installation

### Prerequisites
- Python 3.6 or higher
- No external dependencies required (uses standard library only)

### Quick Installation
```bash
git clone <repository-url>
cd bioart
```

That's it! No pip install needed.

## Quick Start

### Your First DNA Program

```python
from src.bioart import Bioart

# Create interpreter
bioart = Bioart()

# Write a simple program: Load 42, Add 8, Print result, Halt
program = "AAAU AACA AAAG AAAC AAUG AAGA"

# Compile and run
bytecode = bioart.compile_dna_to_bytecode(program)
bioart.execute_bytecode(bytecode)
# Output: 50
```

### Basic DNA Encoding

```python
from src.core.encoding import DNAEncoder

encoder = DNAEncoder()

# Encode text to DNA
text = "Hello, DNA!"
dna_sequence = encoder.encode_string(text)
print(f"DNA: {dna_sequence}")

# Decode back to text
decoded = encoder.decode_to_string(dna_sequence)
print(f"Decoded: {decoded}")
```

## Core Features

### 1. DNA Encoding System

The core 2-bit encoding maps nucleotides to binary:
- **A (Adenine)** = `00`
- **U (Uracil)** = `01`  
- **C (Cytosine)** = `10`
- **G (Guanine)** = `11`

### 2. Instruction Set

| DNA Sequence | Binary | Instruction | Description |
|--------------|--------|-------------|-------------|
| AAAA | 00000000 | NOP | No Operation |
| AAAU | 00000001 | LOAD | Load Value |
| AAAC | 00000010 | STORE | Store Value |
| AAAG | 00000011 | ADD | Add |
| AAUA | 00000100 | SUB | Subtract |
| AAUU | 00000101 | MUL | Multiply |
| AAUC | 00000110 | DIV | Divide |
| AAUG | 00000111 | PRINT | Print Output |
| AACA | 00001000 | INPUT | Input Value |
| AACU | 00001001 | JMP | Jump |
| AACC | 00001010 | JEQ | Jump if Equal |
| AACG | 00001011 | JNE | Jump if Not Equal |
| AAGA | 00001100 | HALT | Halt Program |

### 3. Virtual Machine

The DNA Virtual Machine includes:
- **Memory**: 256 bytes
- **Registers**: 4 (A, B, C, D)
- **Instruction Pointer**: Program counter
- **Stack**: For function calls (enhanced versions)

## Advanced Features

### 1. Error Correction Plugins

Multiple error correction schemes available:

```python
from src.biological.error_correction_plugins import get_error_correction_manager

# Get plugin manager
manager = get_error_correction_manager()

# List available plugins
print("Available plugins:", manager.list_plugins())

# Use different error correction schemes
test_sequence = "AUCGAUCGAUCGAUCG"

# Simple redundancy
encoded = manager.encode_with_plugin(test_sequence, "Simple Redundancy")
decoded, errors = manager.decode_with_plugin(encoded, "Simple Redundancy")

# Hamming codes
encoded = manager.encode_with_plugin(test_sequence, "Hamming Code")
decoded, errors = manager.decode_with_plugin(encoded, "Hamming Code")

# Advanced biological
encoded = manager.encode_with_plugin(test_sequence, "Advanced Biological")
decoded, errors = manager.decode_with_plugin(encoded, "Advanced Biological")
```

### 2. Flexible Alphabets

Support for different nucleotide alphabets:

```python
from src.core.flexible_encoding import FlexibleDNAEncoder

encoder = FlexibleDNAEncoder()

# Use RNA alphabet (default: A, U, C, G)
encoder.set_alphabet("RNA")
rna_encoded = encoder.encode_bytes(b"Hello")

# Use DNA alphabet (A, T, C, G)
encoder.set_alphabet("DNA") 
dna_encoded = encoder.encode_bytes(b"Hello")

# Convert between alphabets
converted = encoder.convert_between_alphabets(rna_encoded, "RNA", "DNA")
```

### 3. Streaming for Large Data

Process large sequences without memory issues:

```python
from src.core.streaming import DNAStreamer

streamer = DNAStreamer()

# Stream encode large file
stats = streamer.encode_file("large_file.bin", "large_file.dna")
print(f"Throughput: {stats['throughput_mb_per_sec']} MB/s")

# Stream decode
stats = streamer.decode_file("large_file.dna", "decoded_file.bin")
```

### 4. Binary Format (.dna files)

Store compiled DNA programs with metadata:

```python
from src.utils.dna_format import DNABinaryFormat, DNAMetadata

fmt = DNABinaryFormat()

# Create metadata
metadata = DNAMetadata(
    description="My DNA program",
    author="DNA Programmer",
    error_correction_scheme="Reed-Solomon"
)

# Save program with metadata
program_data = bioart.compile_dna_to_bytecode("AAAU AAUG AAGA")
fmt.create_dna_file(program_data, metadata, "program.dna")

# Load program
loaded_data, loaded_metadata = fmt.read_dna_file("program.dna")
```

### 5. Bioinformatics Integration

FASTA format support for interoperability:

```python
from src.utils.bioinformatics import BioinformaticsConverter

converter = BioinformaticsConverter()

# Convert DNA program to FASTA
program_data = bioart.compile_dna_to_bytecode("AAAU AAUG AAGA")
converter.bioart_to_fasta(
    program_data, 
    "hello_world", 
    "hello.fasta",
    "Simple hello world program"
)

# Convert FASTA back to program
recovered_data = converter.fasta_to_bioart("hello.fasta")
```

## Tools and Utilities

### 1. Visualization Tool

```bash
python tools/dna_visualizer.py
```

Visualizes DNA programs with:
- Color-coded nucleotides
- Instruction breakdown
- Program flow charts

### 2. Benchmark Suite

```bash
python benchmarks/benchmark_suite.py
```

Performance testing with:
- Encoding/decoding speed
- Memory usage analysis
- Large data processing
- CI/CD integration

### 3. Security Validation

```python
from src.utils.security import InputValidator, SecurityLevel

validator = InputValidator(SecurityLevel.HIGH)
result = validator.validate_dna_sequence("AUCGAUCG")

if result.is_valid:
    print("Sequence is valid")
else:
    print("Errors:", result.errors)
```

## Best Practices

### 1. Program Structure

```python
# Good: Clear program structure
program = """
AAAU AACA    # Load value, input
AAAG AAAC    # Add, store result  
AAUG AAGA    # Print, halt
"""

# Compile and run
bytecode = bioart.compile_dna_to_bytecode(program)
bioart.execute_bytecode(bytecode)
```

### 2. Error Handling

```python
from src.utils.security import RobustErrorHandler

error_handler = RobustErrorHandler()

def safe_dna_operation():
    try:
        # Your DNA operations here
        result = encoder.decode_dna("INVALID")
        return result
    except Exception as e:
        return error_handler.handle_error(e, "DNA decode operation", reraise=False)

result = safe_dna_operation()
```

### 3. Large Data Processing

```python
# For large files, use streaming
config = StreamingConfig(
    chunk_size=1024*1024,  # 1MB chunks
    max_memory_usage=50*1024*1024  # 50MB max
)

streamer = DNAStreamer(config)

# Process large sequence in chunks
for chunk in streamer.process_large_sequence(large_data, "encode"):
    process_chunk(chunk)
```

### 4. Security

```python
# Always validate inputs
validator = InputValidator(SecurityLevel.HIGH)
result = validator.validate_dna_sequence(user_input)

if not result.is_valid:
    print("Invalid input:", result.errors)
    return

# Use sanitized input
safe_sequence = result.sanitized_input
```

## Troubleshooting

### Common Issues

#### 1. "Invalid nucleotide" Error
```python
# Problem: Invalid characters in DNA sequence
# Solution: Use only A, U, C, G (or A, T, C, G for DNA alphabet)
clean_seq = ''.join(c for c in sequence if c in 'AUCG')
```

#### 2. "Sequence length not multiple of 4"
```python
# Problem: DNA sequences must be 4-nucleotide aligned
# Solution: Pad with 'A' nucleotides
while len(sequence) % 4 != 0:
    sequence += 'A'
```

#### 3. Memory Issues with Large Files
```python
# Problem: Running out of memory
# Solution: Use streaming
from src.core.streaming import DNAStreamer

streamer = DNAStreamer()
streamer.encode_file("large_input.bin", "output.dna")
```

#### 4. Slow Performance
```python
# Problem: Slow encoding/decoding
# Solution: Use optimized encoder or adjust chunk size
from src.core.encoding import DNAEncoder  # Optimized version

# Or adjust streaming chunk size
config = StreamingConfig(chunk_size=2*1024*1024)  # 2MB chunks
```

### Error Codes

| Error | Description | Solution |
|-------|-------------|----------|
| DNAValidationError | Invalid DNA sequence | Check nucleotides, length |
| DNASecurityError | Security violation | Review input validation |
| FileNotFoundError | Missing file | Check file paths |
| MemoryError | Out of memory | Use streaming mode |

### Getting Help

1. **Check the logs**: Error handler provides detailed logging
2. **Validate inputs**: Use the security validator
3. **Test with small data**: Start with small sequences
4. **Check examples**: See `examples/` directory
5. **Run benchmarks**: Use benchmark suite to test performance

### Performance Tips

1. **Use appropriate chunk sizes** for your data size
2. **Enable error correction** only when needed
3. **Use streaming** for files > 1MB
4. **Validate inputs** early to catch errors
5. **Monitor memory usage** with large datasets

### Security Guidelines

1. **Always validate inputs** from untrusted sources
2. **Use appropriate security levels** for your use case
3. **Sanitize file paths** to prevent directory traversal
4. **Log operations** for audit trails
5. **Handle errors gracefully** without leaking information

## Examples

See the `examples/` directory for:
- Basic DNA programs
- Error correction examples
- Streaming large files
- Bioinformatics integration
- Security best practices

## API Reference

Detailed API documentation is available in the source code docstrings. Key modules:

- `src.bioart`: Core DNA virtual machine
- `src.core.encoding`: DNA encoding/decoding
- `src.core.flexible_encoding`: Multiple alphabet support
- `src.core.streaming`: Large data processing
- `src.biological.error_correction_plugins`: Error correction
- `src.utils.dna_format`: Binary file format
- `src.utils.bioinformatics`: FASTA support
- `src.utils.security`: Security and validation

## Contributing

See `CONTRIBUTING.md` for guidelines on contributing to the project.

## License

See `LICENSE` for license information.