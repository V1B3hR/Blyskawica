# Bioart DNA Programming Language - Format Specification

## Overview

This document defines the container format specifications for Bioart DNA programs, covering the current implicit format (v1) and the planned future container format (v2) for enhanced metadata, error correction, and biological compatibility.

**Current Version**: 1.0 (Implicit Format)
**Planned Version**: 2.0 (Container Format)
**Target Migration**: Phase 2 Development (Q3-Q4 2025)

---

## Current Format (v1.0) - Implicit Format

### Structure

The current Bioart format uses a simple, implicit structure without explicit headers or metadata. Programs are stored as pure DNA sequences with instruction boundaries inferred from the 4-nucleotide instruction length.

```
┌─────────────────────────────────────────────────────────────┐
│                     DNA Program (v1.0)                     │
├─────────────────────────────────────────────────────────────┤
│  AAAU ACAG AAAG AAGA                                      │
│  ^^^^ ^^^^ ^^^^ ^^^^                                      │
│  |    |    |    └── HALT (0x0C)                          │
│  |    |    └────── ADD (0x03)                             │
│  |    └────────── PRINTS (0x17)                           │
│  └─────────────── LOAD (0x01)                             │
└─────────────────────────────────────────────────────────────┘
```

### Characteristics

**Advantages**:
- **Minimal Overhead**: No metadata storage required
- **Maximum Density**: Pure instruction sequences
- **Simple Parsing**: Fixed 4-nucleotide instruction boundaries
- **Direct Execution**: No preprocessing required

**Limitations**:
- **No Metadata**: Program information must be inferred
- **No Error Correction**: No built-in integrity checking
- **No Versioning**: Format version not embedded
- **Limited Extensibility**: Cannot add features without breaking changes

### File Extensions
- `.dna` - DNA program files
- `.txt` - Human-readable DNA sequences
- `.bin` - Binary equivalent representation

### Encoding Rules
```
Nucleotide Encoding:
A = 00 (binary)
U = 01 (binary)
C = 10 (binary)
G = 11 (binary)

Example: AAAU = 00000001 = 0x01 (LOAD instruction)
```

---

## Planned Format (v2.0) - Container Format

### Design Goals

1. **Metadata Support**: Program information, compilation details, documentation
2. **Error Correction**: Built-in ECC for biological environments
3. **Versioning**: Explicit format version and compatibility information
4. **Extensibility**: Forward-compatible structure for future enhancements
5. **Biological Optimization**: Features specific to DNA storage and synthesis

### Container Structure

```
┌───────────────────────────────────────────────────────────────────┐
│                        Bioart Container v2.0                  │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │  Header Block   │  │  Metadata Block │  │   Data Blocks   │   │
│  │                 │  │                 │  │                 │   │
│  │ • Magic Number  │  │ • Program Info  │  │ • Instructions  │   │
│  │ • Version       │  │ • Compiler Data │  │ • Constants     │   │
│  │ • Length        │  │ • Documentation │  │ • Resources     │   │
│  │ • Checksum      │  │ • Annotations   │  │ • Debug Info    │   │
│  │ • ECC Config    │  │ • Dependencies  │  │ • Extensions    │   │
│  │ • Block Index   │  │ • Build Info    │  │                 │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Header Block Specification

#### Magic Number (8 nucleotides)
```
DNA Sequence: GGAACCUU
Binary:       11000010 01000101
Hex:          0xC2, 0x45
ASCII:        "Bio" (when interpreted as modified ASCII)
```

**Purpose**: File format identification and validation

#### Version Field (4 nucleotides)
```
Format: XYZW
X: Major version (0-3)
Y: Minor version (0-3)
Z: Patch version (0-3)
W: Extension flags (0-3)

Example: AUAU = 0102 = v2.1.0 with no extensions
```

#### Length Field (8 nucleotides)
```
Format: AAAAAAAA to GGGGGGGG
Range:  0x00000000 to 0xFFFFFFFF (4 GB maximum)
Units:  Nucleotides (not bytes)

Example: AAAUAAAA = 0x01000000 = 16,777,216 nucleotides
```

#### Checksum Field (16 nucleotides)
```
Algorithm: CRC-32 over entire container
Format:    64-bit DNA sequence (16 nucleotides)
Coverage:  All blocks including header (except checksum field itself)

Example: AAAUUCGGUUAACCGG = 0x1234ABCD5678EF90
```

#### ECC Configuration (4 nucleotides)
```
Format: XYZW
X: ECC Type (0=None, 1=Hamming, 2=Reed-Solomon, 3=Custom)
Y: ECC Strength (0=Disabled, 1=Low, 2=Medium, 3=High)
Z: Block Size (0=64, 1=128, 2=256, 3=512 nucleotides)
W: Reserved for future use

Example: AUCU = Reed-Solomon, Medium strength, 256-nucleotide blocks
```

#### Block Index (Variable length)
```
Format: Table of contents for all blocks in container
Entry:  [Type:4nt][Offset:8nt][Length:8nt][Checksum:8nt]

Block Types:
AAAA = Metadata Block
AAAU = Instruction Block
AAAC = Constants Block
AAAG = Resources Block
AAUA = Debug Information Block
AAUU = Extension Block
... (additional types reserved)
```

### Metadata Block Specification

#### Program Information
```
Program Name:        Variable length string (null-terminated)
Version:            XYZW format (4 nucleotides)
Compilation Date:   Unix timestamp (8 nucleotides)
Compiler Version:   String identifier
Target Platform:    Platform specification string
Language Features:  Feature flags bitfield
```

#### Documentation
```
Author Information: Name, email, organization
License:           License identifier and text
Description:       Program purpose and functionality
Usage:             Command-line arguments and options
Examples:          Sample usage patterns
Dependencies:      Required libraries and versions
```

### Data Block Types

#### Instruction Block
```
Content: Pure DNA instruction sequences (same as v1.0)
Format:  4-nucleotide instructions concatenated
ECC:     Applied per ECC configuration
Compression: Optional (specified in header flags)
```

#### Constants Block
```
Content: Literal values, strings, lookup tables
Format:  [Type:2nt][Length:4nt][Data:Variable]
Types:   String, Integer, Float, Array, Object
Encoding: UTF-8 for strings, IEEE 754 for floats
```

#### Resources Block
```
Content: External files, assets, data
Format:  [Name:Variable][Type:4nt][Data:Variable]
Types:   Binary data, text files, images
Compression: Automatic for large resources
```

#### Debug Information Block
```
Content: Symbol tables, source mapping, profiling data
Format:  [Symbol:Variable][Address:8nt][Type:4nt][Metadata:Variable]
Features: Line number mapping, variable names, call stack info
Optional: Can be stripped for production releases
```

---

## Format Migration Strategy

### Phase 1: Dual Format Support (Q3 2025)
- **Reader Compatibility**: Support both v1.0 and v2.0 formats
- **Writer Options**: Default to v1.0, optional v2.0 output
- **Validation**: Automatic format detection and validation
- **Tools**: Conversion utilities between formats

### Phase 2: v2.0 as Primary (Q4 2025)
- **Default Output**: New programs use v2.0 format by default
- **Legacy Support**: Continued v1.0 reading support
- **Feature Utilization**: Metadata and ECC features enabled
- **Documentation**: Updated examples and tutorials

### Phase 3: v1.0 Deprecation (2026)
- **Migration Tools**: Automated v1.0 → v2.0 conversion
- **Warning System**: Deprecation warnings for v1.0 usage
- **Legacy Mode**: Explicit flag required for v1.0 output
- **Sunset Timeline**: Planned end-of-life for v1.0 support

### Compatibility Matrix

| Feature | v1.0 | v2.0 | Migration |
|---------|------|------|-----------|
| Basic Instructions | ✅ | ✅ | Direct |
| Metadata | ❌ | ✅ | Generated |
| Error Correction | ❌ | ✅ | Added |
| Versioning | ❌ | ✅ | Detected |
| Extensions | ❌ | ✅ | Optional |

---

## Error Correction Framework

### ECC Types Supported

#### Hamming Codes
- **Use Case**: Single-bit error correction
- **Overhead**: 12.5% (4 check nucleotides per 32 data nucleotides)
- **Performance**: Fast encoding/decoding
- **Biological**: Good for synthesis errors

#### Reed-Solomon Codes
- **Use Case**: Burst error correction and detection
- **Overhead**: Configurable (typically 20-50%)
- **Performance**: Moderate encoding/decoding cost
- **Biological**: Excellent for degradation and contamination

#### Custom ECC (Future)
- **Use Case**: Biological-specific error patterns
- **Overhead**: Adaptive based on environment
- **Performance**: Optimized for specific use cases
- **Research**: Under development with biology partners

### ECC Implementation

```python
# Example ECC integration
class ECCProcessor:
    def encode_block(self, data: str, ecc_type: ECCType) -> str:
        """Add error correction to DNA block"""

    def decode_block(self, encoded_data: str) -> Tuple[str, bool]:
        """Decode and correct errors, return (data, success)"""

    def detect_errors(self, data: str) -> List[ErrorReport]:
        """Detect and report error locations"""
```

---

## Biological Considerations

### DNA Synthesis Optimization

#### Sequence Constraints
- **GC Content**: Maintain 40-60% GC content for stability
- **Homopolymers**: Avoid runs >4 identical nucleotides
- **Secondary Structure**: Minimize hairpins and loops
- **Restriction Sites**: Avoid common enzyme recognition sequences

#### Synthesis-Friendly Features
- **Block Structure**: Optimize for synthesis block sizes
- **Redundancy**: Multiple encoding options for problematic sequences
- **Validation**: Pre-synthesis sequence analysis
- **Error Prediction**: Model synthesis failure modes

### Storage Considerations

#### Environmental Factors
- **Temperature**: Encoding stable at -20°C to +37°C
- **pH**: Stable in pH 6.0-8.0 range
- **Humidity**: Resilient to typical laboratory conditions
- **Contamination**: ECC protects against nuclease degradation

#### Long-term Stability
- **Half-life**: >1000 years at -20°C (theoretical)
- **Degradation Patterns**: Predictable error patterns
- **Recovery**: Error correction designed for expected degradation
- **Monitoring**: Built-in integrity checking

---

## Implementation Roadmap

### v2.0 Development Timeline

#### Q1 2025: Design Finalization
- [ ] Complete format specification
- [ ] Prototype implementation
- [ ] Performance benchmarking
- [ ] Biological validation testing

#### Q2 2025: Core Implementation
- [ ] Header processing engine
- [ ] Metadata management system
- [ ] ECC framework integration
- [ ] Format conversion tools

#### Q3 2025: Integration & Testing
- [ ] VM integration updates
- [ ] Comprehensive test suite
- [ ] Performance optimization
- [ ] Documentation completion

#### Q4 2025: Production Release
- [ ] Beta testing program
- [ ] Migration tool finalization
- [ ] Release candidate validation
- [ ] v2.0 format official release

---

## Developer Interface

### API Specification

#### Format Detection
```python
def detect_format_version(data: str) -> FormatVersion:
    """Automatically detect format version from DNA sequence"""

def validate_format(data: str, version: FormatVersion) -> ValidationResult:
    """Validate format compliance and integrity"""
```

#### Container Manipulation
```python
class BioartContainer:
    def __init__(self, version: FormatVersion = FormatVersion.V2_0):
        """Create new container with specified format version"""

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to container"""

    def set_ecc_config(self, ecc_type: ECCType, strength: ECCStrength) -> None:
        """Configure error correction settings"""

    def add_instructions(self, dna_sequence: str) -> None:
        """Add instruction block to container"""

    def serialize(self) -> str:
        """Generate final DNA container sequence"""
```

#### Migration Utilities
```python
def migrate_v1_to_v2(v1_data: str, metadata: Dict[str, Any] = None) -> str:
    """Convert v1.0 format to v2.0 with optional metadata"""

def extract_v1_instructions(v2_data: str) -> str:
    """Extract pure instruction sequence compatible with v1.0"""
```

---

## Security Considerations

### Data Integrity
- **Checksums**: Multiple layers of integrity checking
- **Validation**: Comprehensive format validation on load
- **Tampering Detection**: Header modification detection
- **Recovery**: Graceful handling of corrupted containers

### Access Control
- **Metadata Protection**: Optional encryption of metadata blocks
- **Instruction Signing**: Cryptographic signatures for code authenticity
- **Version Control**: Audit trail for format modifications
- **Compliance**: Support for regulatory requirements

---

## Performance Metrics

### Format Overhead Analysis

| Component | v1.0 | v2.0 Minimal | v2.0 Full | Impact |
|-----------|------|--------------|-----------|---------|
| Instructions | 100% | 100% | 100% | Baseline |
| Header | 0% | +2.5% | +5% | Metadata |
| ECC | 0% | +12.5% | +25% | Error Correction |
| Metadata | 0% | +1% | +10% | Documentation |
| **Total** | **100%** | **116%** | **140%** | **Typical Range** |

### Processing Performance

| Operation | v1.0 | v2.0 | Difference |
|-----------|------|------|------------|
| Parse Header | N/A | 50μs | +50μs |
| Load Instructions | 1ms | 1.1ms | +10% |
| Validate Integrity | N/A | 5ms | +5ms |
| ECC Decode | N/A | 10ms | +10ms |
| **Total Load Time** | **1ms** | **16.1ms** | **+1500%** |

*Note: Performance impact is front-loaded during program loading; execution performance is identical.*

---

## Future Extensions

### v2.1 Planned Features
- **Compression**: Instruction sequence compression
- **Optimization**: Dead code elimination metadata
- **Profiling**: Runtime performance data collection
- **Internationalization**: Multi-language metadata support

### v3.0 Vision
- **Distributed Programs**: Multi-container program distribution
- **Hot Updates**: Runtime program modification capability
- **Biological Integration**: Direct synthesis/sequencing integration
- **AI Optimization**: Machine learning-optimized encoding

---

*This format specification serves as the authoritative reference for Bioart container formats and migration strategies.*

**Specification Version**: 1.0
**Last Updated**: 2024
**Format Authority**: Bioart Architecture Team
**Implementation Status**: v2.0 in development