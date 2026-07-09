# Bioart Translator - Quick Start Guide

## What is it?

The Bioart Translator is a **complete, reversible, and real-world ready** tool for converting between:
- Text ↔ DNA sequences
- Binary data ↔ DNA sequences
- Files ↔ DNA sequences

All conversions are **100% reversible** with perfect data integrity.

## Quick Examples

### Command Line

```bash
# Encode text to DNA
python bioart_cli.py encode --text "Hello, World!"
# Output: UACAUCUUUCGAUCGAUCGGACGAACAAUUUGUCGGUGACUCGAUCUAACAU

# Decode DNA back to text
python bioart_cli.py decode --dna "UACAUCUUUCGAUCGAUCGGACGAACAAUUUGUCGGUGACUCGAUCUAACAU"
# Output: Hello, World!

# Verify data is reversible
python bioart_cli.py verify --text "Important data"
# Shows full verification report

# Get DNA sequence information
python bioart_cli.py info --dna "AUCGAUCGAUCGAUCG"
# Shows length, composition, GC content, etc.
```

### Python API

```python
from src.translator import BioartTranslator

# Create translator
translator = BioartTranslator()

# Text to DNA and back
dna = translator.text_to_dna("Hello, World!")
text = translator.dna_to_text(dna)
# text == "Hello, World!"  ✓

# Binary to DNA and back
data = b"Binary data"
dna = translator.binary_to_dna(data)
restored = translator.dna_to_binary(dna)
# restored == data  ✓

# File to DNA and back
dna = translator.file_to_dna("input.txt")
translator.dna_to_file(dna, "output.txt")
# Files are identical  ✓
```

## Features

### ✅ Translation
- Text to DNA and back
- Binary data to DNA and back
- Files to DNA and back
- All 256 byte values supported
- UTF-8 text encoding support

### ✅ Modification
- Modify individual nucleotides
- Insert DNA sequences
- Delete DNA sequences
- Replace DNA sequences

### ✅ Validation
- Validate DNA sequences
- Verify reversibility
- Get sequence information
- Check data integrity

### ✅ Real-World Ready
- Command-line interface
- Interactive mode
- Comprehensive error handling
- Usage statistics tracking
- Formatted output

## Installation

No installation required! Just Python 3.8+

```bash
# Clone the repository
git clone <repository-url>
cd bioart

# Run immediately
python bioart_cli.py --help
```

## CLI Commands

### Encode
```bash
# Encode text
python bioart_cli.py encode --text "Your text here"

# Encode file
python bioart_cli.py encode --file input.txt --output dna.txt

# Format output for readability
python bioart_cli.py encode --text "Hello" --format
```

### Decode
```bash
# Decode to text
python bioart_cli.py decode --dna "AUCGAUCG..."

# Decode file
python bioart_cli.py decode --file dna.txt --output restored.txt

# Decode to binary
python bioart_cli.py decode --dna "AUCGAUCG..." --binary
```

### Modify
```bash
# Replace nucleotides
python bioart_cli.py modify --dna "AAAAUUUU" --replace 0 4 "GGGG"

# Insert sequence
python bioart_cli.py modify --dna "AAAAUUUU" --insert 4 "CCCC"

# Delete sequence
python bioart_cli.py modify --dna "AAAAUUUU" --delete 2 4

# Mutate single nucleotide
python bioart_cli.py modify --dna "AAAAUUUU" --mutate 0 G
```

### Verify
```bash
# Verify text reversibility
python bioart_cli.py verify --text "Test data"

# Verify file reversibility
python bioart_cli.py verify --file input.txt
```

### Info
```bash
# Get sequence information
python bioart_cli.py info --dna "AUCGAUCGAUCGAUCG"

# Get info from file
python bioart_cli.py info --file dna.txt
```

### Interactive
```bash
# Start interactive mode
python bioart_cli.py interactive

# Then use commands:
bioart> encode Hello, World!
bioart> decode UACAUCUUUCGA...
bioart> verify Test data
bioart> stats
bioart> quit
```

## Python API Examples

### Basic Usage

```python
from src.translator import BioartTranslator

translator = BioartTranslator()

# Translate text
dna = translator.text_to_dna("Hello")
text = translator.dna_to_text(dna)
```

### Modify DNA

```python
# Start with a DNA sequence
dna = "AAAAUUUU"

# Modify it
modified = translator.modify_nucleotide(dna, 0, 'G')
# Result: GAAAUUUU

modified = translator.insert_sequence(dna, 4, "CCCC")
# Result: AAAACCCCUUUU

modified = translator.delete_sequence(dna, 2, 4)
# Result: AAUU

modified = translator.replace_sequence(dna, 0, 4, "GGGG")
# Result: GGGGUUUU
```

### Validate and Verify

```python
# Validate DNA
is_valid = translator.validate_dna("AUCGAUCG")
# Returns: True

# Verify reversibility
result = translator.verify_reversibility("Important data")
print(f"Success: {result['success']}")
print(f"Match: {result['match']}")
print(f"Original size: {result['original_size']} bytes")
print(f"DNA size: {result['dna_size']} nucleotides")
```

### Get Information

```python
# Get sequence info
info = translator.get_sequence_info("AUCGAUCGAUCGAUCG")

print(f"Length: {info['length']} nucleotides")
print(f"Byte capacity: {info['byte_capacity']} bytes")
print(f"Valid: {info['is_valid']}")
print(f"Complete: {info['is_complete']}")
print(f"GC content: {info['gc_content']}%")
print(f"Nucleotide counts: {info['nucleotide_counts']}")
```

### Format DNA

```python
# Format for display
dna = translator.text_to_dna("This is a longer text")
formatted = translator.format_dna(dna, width=60, group_size=4)
print(formatted)
```

## Real-World Examples

### Store JSON Data

```python
import json

data = {"name": "John", "age": 30}
json_str = json.dumps(data)

# Store as DNA
dna = translator.text_to_dna(json_str)

# Retrieve and use
restored_json = translator.dna_to_text(dna)
restored_data = json.loads(restored_json)
# restored_data == data  ✓
```

### Store Program Code

```python
code = """
def hello():
    print("Hello from DNA!")
"""

# Store code as DNA
dna = translator.text_to_dna(code)

# Retrieve and execute
restored_code = translator.dna_to_text(dna)
exec(restored_code)
```

### Store Binary Files

```python
# Store any file (images, executables, etc.)
dna = translator.file_to_dna("image.png")

# Restore later
translator.dna_to_file(dna, "restored_image.png")
# Files are identical  ✓
```

## Testing

Run comprehensive tests:

```bash
# Test the translator
python tests/test_translator.py

# Expected output:
# Tests run:     35
# Successes:     35
# Failures:      0
# Success rate:  100.0%
```

## Performance

- **Encoding Speed**: 1-10 million bytes/second
- **Storage Ratio**: 4 nucleotides per byte (optimal)
- **Reversibility**: 100% for all 256 byte values
- **Memory**: O(n) where n is input size

## Documentation

- **[Full Guide](docs/TRANSLATOR_GUIDE.md)** - Complete documentation with all features
- **[Demo Script](examples/translator_demo.py)** - Comprehensive demonstration
- **[Main README](README.md)** - Project overview

## Demo

Run the comprehensive demo:

```bash
python examples/translator_demo.py
```

This shows:
1. Basic text to DNA translation
2. Binary data translation
3. DNA sequence modification
4. Validation and verification
5. Sequence information analysis
6. Real-world scenario (JSON storage)
7. DNA formatting
8. Usage statistics
9. All byte values test (0-255)

## Technical Details

### Encoding System

- **Base Encoding**: 2-bit per nucleotide
  - A = 00
  - U = 01  
  - C = 10
  - G = 11

- **Efficiency**: 4 nucleotides per byte (optimal)
- **Compatibility**: All 256 byte values
- **Reversibility**: 100% lossless

### File Format

DNA sequences are stored as text files containing only the characters A, U, C, G:
```
AUCGAUCGAUCGAUCG...
```

Can be formatted with spaces and newlines for readability:
```
AUCG AUCG AUCG AUCG
AUCG AUCG AUCG AUCG
```

## Troubleshooting

### Import Error

If you get an import error, add src to your Python path:

```python
import sys
sys.path.insert(0, 'src')
from translator import BioartTranslator
```

### Unicode Decode Error

This happens when trying to decode DNA that doesn't represent valid UTF-8 text. Use binary methods instead:

```python
# For arbitrary binary data
dna = translator.binary_to_dna(data)
restored = translator.dna_to_binary(dna)  # Use binary, not text
```

### Incomplete Sequence

DNA sequences must be multiples of 4 nucleotides. Check with:

```python
info = translator.get_sequence_info(dna)
if not info['is_complete']:
    print("Sequence needs padding")
```

## Support

For questions or issues, please refer to the main Bioart repository.

## License

GNU GPLv3 - See LICENSE file for details.
