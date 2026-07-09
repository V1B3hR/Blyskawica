# Bioart Translator Guide

## Overview

The Bioart Translator is a comprehensive, production-ready tool for converting between text, binary data, and DNA sequences using the Bioart 2-bit encoding system (A=00, U=01, C=10, G=11).

## Key Features

✅ **Complete Translator**: Convert text, binary, and files to DNA and back
✅ **DNA Modifier**: Modify DNA sequences with insert, delete, replace operations
✅ **100% Reversible**: Perfect round-trip conversion with validation
✅ **Real-World Ready**: Command-line interface and Python API
✅ **Well-Tested**: 35+ comprehensive tests with 100% pass rate

## Quick Start

### Command Line Interface

#### Encode Text to DNA
```bash
python bioart_cli.py encode --text "Hello, World!"
```
Output: `UACAUCUUUCGAUCGAUCGGACGAACAAUUUGUCGGUGACUCGAUCUAACAU`

#### Decode DNA to Text
```bash
python bioart_cli.py decode --dna "UACAUCUUUCGAUCGAUCGGACGAACAAUUUGUCGGUGACUCGAUCUAACAU"
```
Output: `Hello, World!`

#### Encode File to DNA
```bash
python bioart_cli.py encode --file input.txt --output dna.txt
```

#### Decode DNA File Back
```bash
python bioart_cli.py decode --file dna.txt --output restored.txt
```

#### Verify Reversibility
```bash
python bioart_cli.py verify --text "Test data"
```

#### Get Sequence Information
```bash
python bioart_cli.py info --dna "AUCGAUCGAUCGAUCG"
```

#### Modify DNA Sequences
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

#### Interactive Mode
```bash
python bioart_cli.py interactive
```

### Python API

#### Basic Translation

```python
from src.translator import BioartTranslator

# Initialize translator
translator = BioartTranslator()

# Text to DNA
dna = translator.text_to_dna("Hello, World!")
print(dna)  # UACAUCUUUCGAUCGAUCGGACGAACAAUUUGUCGGUGACUCGAUCUAACAU

# DNA to text
text = translator.dna_to_text(dna)
print(text)  # Hello, World!
```

#### Binary Data Translation

```python
# Binary to DNA
data = b"Hello"
dna = translator.binary_to_dna(data)

# DNA to binary
restored = translator.dna_to_binary(dna)
assert data == restored
```

#### File Operations

```python
# Convert file to DNA
dna = translator.file_to_dna("input.txt")

# Save DNA to file
translator.dna_to_file(dna, "output.txt")
```

#### DNA Sequence Modification

```python
dna = "AAAAUUUU"

# Modify single nucleotide
modified = translator.modify_nucleotide(dna, 0, 'G')
print(modified)  # GAAAUUUU

# Insert sequence
modified = translator.insert_sequence(dna, 4, "CCCC")
print(modified)  # AAAACCCCUUUU

# Delete sequence
modified = translator.delete_sequence(dna, 2, 4)
print(modified)  # AAUU

# Replace sequence
modified = translator.replace_sequence(dna, 0, 4, "GGGG")
print(modified)  # GGGGUUUU
```

#### Validation and Verification

```python
# Validate DNA sequence
is_valid = translator.validate_dna("AUCGAUCG")
print(is_valid)  # True

# Verify reversibility
result = translator.verify_reversibility("Test data")
print(f"Reversible: {result['success']}")
print(f"Match: {result['match']}")
```

#### Sequence Information

```python
# Get sequence information
info = translator.get_sequence_info("AUCGAUCGAUCGAUCG")
print(f"Length: {info['length']} nucleotides")
print(f"Byte capacity: {info['byte_capacity']} bytes")
print(f"GC content: {info['gc_content']}%")
print(f"Nucleotide counts: {info['nucleotide_counts']}")
```

#### Formatting and Statistics

```python
# Format DNA for display
dna = "AAAUUUCCGGGAAAUUUCCGGG"
formatted = translator.format_dna(dna, width=20, group_size=4)
print(formatted)

# Get usage statistics
stats = translator.get_stats()
print(f"Translations: {stats['translations']}")
print(f"Reversals: {stats['reversals']}")
print(f"Modifications: {stats['modifications']}")
```

### Convenience Functions

For quick one-off operations:

```python
from src.translator import (
    translate_text_to_dna,
    translate_dna_to_text,
    translate_binary_to_dna,
    translate_dna_to_binary
)

# Quick text translation
dna = translate_text_to_dna("Hello")
text = translate_dna_to_text(dna)

# Quick binary translation
dna = translate_binary_to_dna(b"Hello")
data = translate_dna_to_binary(dna)
```

## Real-World Use Cases

### 1. Document Storage

```python
translator = BioartTranslator()

# Store important document
document = """
Important Document
==================
This document is stored in DNA format.
"""

dna = translator.text_to_dna(document)
# Store 'dna' in database or file

# Later, retrieve and decode
restored = translator.dna_to_text(dna)
assert restored == document
```

### 2. JSON Data Storage

```python
import json

data = {"name": "John", "age": 30, "items": [1, 2, 3]}
json_str = json.dumps(data)

# Encode to DNA
dna = translator.text_to_dna(json_str)

# Decode from DNA
restored_json = translator.dna_to_text(dna)
restored_data = json.loads(restored_json)
assert restored_data == data
```

### 3. Program Code Storage

```python
# Store source code in DNA
code = """
def hello_world():
    print("Hello, World!")
    return 42
"""

dna = translator.text_to_dna(code)
restored_code = translator.dna_to_text(dna)
# Execute restored code
exec(restored_code)
```

### 4. Binary File Storage

```python
# Store any binary file
dna = translator.file_to_dna("image.png")

# Later restore
translator.dna_to_file(dna, "restored_image.png")
```

## Technical Specifications

### Encoding System

- **Base Encoding**: 2-bit per nucleotide
  - A = 00
  - U = 01
  - C = 10
  - G = 11
- **Efficiency**: 4 nucleotides per byte (optimal)
- **Compatibility**: All 256 byte values (0-255)
- **Reversibility**: 100% lossless round-trip

### Performance

- **Encoding Speed**: ~1-10 million bytes/second
- **Memory Efficiency**: O(n) where n is input size
- **Storage Efficiency**: 4:1 ratio (4 nucleotides per byte)

### Validation

All operations ensure:
- Valid nucleotide sequences (A, U, C, G only)
- Complete sequences (multiples of 4 nucleotides)
- Perfect reversibility (validated by tests)
- Error handling with informative messages

## Testing

The translator includes 35 comprehensive tests covering:

- Text to DNA conversion
- DNA to text conversion
- Binary data translation
- File operations
- DNA modification operations
- Validation and verification
- Edge cases (all 256 byte values, large texts, unicode)
- Real-world scenarios

Run tests:
```bash
python tests/test_translator.py
```

Expected output:
```
Tests run:     35
Successes:     35
Failures:      0
Errors:        0
Success rate:  100.0%
```

## Error Handling

The translator provides clear error messages:

```python
# Invalid nucleotide
translator.modify_nucleotide("AAAA", 0, 'X')
# ValueError: Invalid nucleotide: X

# Out of range position
translator.modify_nucleotide("AAAA", 10, 'A')
# ValueError: Position 10 out of range for sequence of length 4

# Invalid DNA sequence
translator.validate_dna("ATCG")  # T instead of U
# Returns: False

# Non-UTF-8 DNA
translator.dna_to_text("GGGGGGGG")
# ValueError: DNA sequence does not represent valid UTF-8 text
```

## Best Practices

1. **Always verify reversibility** for critical data:
   ```python
   result = translator.verify_reversibility(data)
   if not result['success']:
       print(f"Error: {result['error']}")
   ```

2. **Use file operations** for large data:
   ```python
   # More efficient than reading entire file into memory
   dna = translator.file_to_dna("large_file.bin")
   ```

3. **Validate DNA sequences** before processing:
   ```python
   if translator.validate_dna(dna_sequence):
       text = translator.dna_to_text(dna_sequence)
   ```

4. **Track statistics** for monitoring:
   ```python
   stats = translator.get_stats()
   print(f"Total translations: {stats['translations']}")
   ```

## Integration Examples

### Web API

```python
from flask import Flask, request, jsonify
from src.translator import BioartTranslator

app = Flask(__name__)
translator = BioartTranslator()

@app.route('/encode', methods=['POST'])
def encode():
    text = request.json['text']
    dna = translator.text_to_dna(text)
    return jsonify({'dna': dna})

@app.route('/decode', methods=['POST'])
def decode():
    dna = request.json['dna']
    text = translator.dna_to_text(dna)
    return jsonify({'text': text})
```

### Database Storage

```python
import sqlite3

# Store data as DNA
conn = sqlite3.connect('dna_storage.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS dna_data (
        id INTEGER PRIMARY KEY,
        dna_sequence TEXT,
        metadata TEXT
    )
''')

# Insert data
data = "Important information"
dna = translator.text_to_dna(data)
cursor.execute('INSERT INTO dna_data (dna_sequence, metadata) VALUES (?, ?)',
               (dna, 'document-1'))

# Retrieve and decode
cursor.execute('SELECT dna_sequence FROM dna_data WHERE id = ?', (1,))
dna = cursor.fetchone()[0]
restored = translator.dna_to_text(dna)
```

## Troubleshooting

### Issue: Import Error

```python
# If you get ImportError, add src to path
import sys
sys.path.insert(0, 'src')
from translator import BioartTranslator
```

### Issue: Unicode Decode Error

This happens when trying to decode DNA that doesn't represent valid UTF-8 text:
```python
# Use binary_to_dna/dna_to_binary for arbitrary binary data
data = bytes([255, 254, 253])  # Invalid UTF-8
dna = translator.binary_to_dna(data)  # Works fine
binary = translator.dna_to_binary(dna)  # Works fine
text = translator.dna_to_text(dna)  # Would fail - not valid UTF-8
```

### Issue: Incomplete Sequence

DNA sequences must be multiples of 4 nucleotides:
```python
info = translator.get_sequence_info("AUCGAU")  # 6 nucleotides
print(info['is_complete'])  # False - needs padding
```

## License

This translator is part of the Bioart project and is distributed under GNU GPLv3.

## Support

For issues, questions, or contributions, please refer to the main Bioart repository.
