#!/usr/bin/env python3
"""
Binary DNA Format (.dna) with metadata header
Supports serialization and deserialization of compiled DNA programs
"""

import struct
import json
import time
import hashlib
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import IntEnum

class DNAFormatVersion(IntEnum):
    """DNA format versions"""
    V1_0 = 1
    V2_0 = 2

@dataclass
class DNAMetadata:
    """Metadata for DNA programs"""
    format_version: int = DNAFormatVersion.V2_0
    created_timestamp: float = 0.0
    modified_timestamp: float = 0.0
    compiler_version: str = "2.0.0"
    source_language: str = "DNA Assembly"
    error_correction_scheme: str = "Reed-Solomon"
    compression_type: str = "None"
    checksum: str = ""
    description: str = ""
    author: str = ""
    custom_fields: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_timestamp == 0.0:
            self.created_timestamp = time.time()
        if self.modified_timestamp == 0.0:
            self.modified_timestamp = self.created_timestamp
        if self.custom_fields is None:
            self.custom_fields = {}

class DNABinaryFormat:
    """Binary format handler for .dna files"""
    
    # Magic number for DNA files (DNA encoded as hex)
    MAGIC_NUMBER = b'DNA\x01'  # 4 bytes
    HEADER_SIZE_OFFSET = 4     # Offset where header size is stored
    HEADER_SIZE_BYTES = 4      # Size of header size field
    
    def __init__(self):
        self.supported_versions = [DNAFormatVersion.V1_0, DNAFormatVersion.V2_0]
    
    def create_dna_file(self, program_data: bytes, metadata: DNAMetadata = None,
                       filename: str = None) -> bytes:
        """Create a binary .dna file with metadata header"""
        if metadata is None:
            metadata = DNAMetadata()
        
        # Update timestamps
        metadata.modified_timestamp = time.time()
        
        # Calculate checksum of program data
        metadata.checksum = hashlib.sha256(program_data).hexdigest()
        
        # Serialize metadata to JSON
        metadata_dict = asdict(metadata)
        metadata_json = json.dumps(metadata_dict, indent=None, separators=(',', ':')).encode('utf-8')
        
        # Create file structure
        file_data = bytearray()
        
        # Magic number (4 bytes)
        file_data.extend(self.MAGIC_NUMBER)
        
        # Header size (4 bytes, little endian)
        header_size = len(metadata_json)
        file_data.extend(struct.pack('<I', header_size))
        
        # Metadata header
        file_data.extend(metadata_json)
        
        # Program data
        file_data.extend(program_data)
        
        # Save to file if filename provided
        if filename:
            with open(filename, 'wb') as f:
                f.write(file_data)
        
        return bytes(file_data)
    
    def read_dna_file(self, filename: str = None, data: bytes = None) -> Tuple[bytes, DNAMetadata]:
        """Read a binary .dna file and extract program data and metadata"""
        if filename:
            with open(filename, 'rb') as f:
                file_data = f.read()
        elif data:
            file_data = data
        else:
            raise ValueError("Either filename or data must be provided")
        
        if len(file_data) < 8:
            raise ValueError("Invalid DNA file: too short")
        
        # Check magic number
        magic = file_data[:4]
        if magic != self.MAGIC_NUMBER:
            raise ValueError(f"Invalid DNA file: bad magic number (got {magic!r})")
        
        # Read header size
        header_size = struct.unpack('<I', file_data[4:8])[0]
        
        if len(file_data) < 8 + header_size:
            raise ValueError("Invalid DNA file: incomplete header")
        
        # Read metadata
        metadata_bytes = file_data[8:8 + header_size]
        try:
            metadata_dict = json.loads(metadata_bytes.decode('utf-8'))
            metadata = DNAMetadata(**metadata_dict)
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Invalid DNA file: corrupted metadata ({e})")
        
        # Check format version
        if metadata.format_version not in self.supported_versions:
            raise ValueError(f"Unsupported DNA format version: {metadata.format_version}")
        
        # Read program data
        program_data = file_data[8 + header_size:]
        
        # Verify checksum if present
        if metadata.checksum:
            calculated_checksum = hashlib.sha256(program_data).hexdigest()
            if calculated_checksum != metadata.checksum:
                raise ValueError("DNA file checksum mismatch: file may be corrupted")
        
        return program_data, metadata
    
    def update_metadata(self, filename: str, new_metadata: Dict[str, Any]):
        """Update metadata in an existing .dna file"""
        program_data, metadata = self.read_dna_file(filename)
        
        # Update metadata fields
        for key, value in new_metadata.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)
            else:
                metadata.custom_fields[key] = value
        
        # Update modified timestamp
        metadata.modified_timestamp = time.time()
        
        # Recreate file
        self.create_dna_file(program_data, metadata, filename)
    
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """Get information about a .dna file without loading program data"""
        try:
            _, metadata = self.read_dna_file(filename)
            
            # Calculate file size
            import os
            file_size = os.path.getsize(filename)
            
            info = {
                "filename": filename,
                "file_size": file_size,
                "format_version": metadata.format_version,
                "created": time.ctime(metadata.created_timestamp),
                "modified": time.ctime(metadata.modified_timestamp),
                "compiler_version": metadata.compiler_version,
                "error_correction": metadata.error_correction_scheme,
                "description": metadata.description,
                "author": metadata.author,
                "checksum": metadata.checksum[:16] + "..." if metadata.checksum else "None"
            }
            
            return info
            
        except Exception as e:
            return {"filename": filename, "error": str(e)}
    
    def create_empty_dna_file(self, filename: str, description: str = "Empty DNA program"):
        """Create an empty .dna file with just metadata"""
        metadata = DNAMetadata(description=description)
        empty_program = b''
        self.create_dna_file(empty_program, metadata, filename)
    
    def validate_dna_file(self, filename: str) -> Dict[str, Any]:
        """Validate a .dna file and return validation results"""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "info": {}
        }
        
        try:
            program_data, metadata = self.read_dna_file(filename)
            
            # Basic validation
            result["valid"] = True
            result["info"]["program_size"] = len(program_data)
            result["info"]["metadata"] = asdict(metadata)
            
            # Check for warnings
            if not metadata.description:
                result["warnings"].append("No description provided")
            
            if not metadata.author:
                result["warnings"].append("No author specified")
            
            if metadata.error_correction_scheme == "None":
                result["warnings"].append("No error correction enabled")
            
            # Check program data
            if len(program_data) == 0:
                result["warnings"].append("Empty program")
            elif len(program_data) % 4 != 0:
                result["warnings"].append("Program size not aligned to 4-byte boundaries")
            
        except Exception as e:
            result["errors"].append(str(e))
        
        return result

class DNADisassembler:
    """Disassembler for .dna files"""
    
    def __init__(self):
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from bioart import Bioart
        self.bioart = Bioart()
        self.format_handler = DNABinaryFormat()
    
    def disassemble_file(self, filename: str, output_file: str = None) -> str:
        """Disassemble a .dna file to human-readable format"""
        program_data, metadata = self.format_handler.read_dna_file(filename)
        
        output = []
        output.append("DNA PROGRAM DISASSEMBLY")
        output.append("=" * 50)
        
        # Metadata section
        output.append("\nMETADATA:")
        output.append(f"  Format Version: {metadata.format_version}")
        output.append(f"  Created: {time.ctime(metadata.created_timestamp)}")
        output.append(f"  Modified: {time.ctime(metadata.modified_timestamp)}")
        output.append(f"  Compiler: {metadata.compiler_version}")
        output.append(f"  Error Correction: {metadata.error_correction_scheme}")
        output.append(f"  Description: {metadata.description}")
        output.append(f"  Author: {metadata.author}")
        output.append(f"  Checksum: {metadata.checksum}")
        
        # Program section
        output.append(f"\nPROGRAM DATA ({len(program_data)} bytes):")
        output.append("-" * 30)
        
        if len(program_data) == 0:
            output.append("  (empty program)")
        else:
            # Disassemble bytecode
            disassembly = self.bioart.disassemble(program_data)
            output.append(disassembly)
        
        result = '\n'.join(output)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(result)
        
        return result

def main():
    """Demo of DNA binary format"""
    print("🧬 DNA BINARY FORMAT DEMO")
    print("=" * 30)
    
    # Create format handler
    fmt = DNABinaryFormat()
    
    # Sample program data (Load 42, Add 8, Print, Halt)
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from bioart import Bioart
    bioart = Bioart()
    program = "AAAU AACA AAAG AAAC AAUG AAGA"
    program_data = bioart.compile_dna_to_bytecode(program)
    
    print(f"Sample program: {program}")
    print(f"Compiled size: {len(program_data)} bytes")
    
    # Create metadata
    metadata = DNAMetadata(
        description="Simple arithmetic program",
        author="DNA Programmer",
        error_correction_scheme="Reed-Solomon"
    )
    
    # Create .dna file
    dna_filename = "sample_program.dna"
    fmt.create_dna_file(program_data, metadata, dna_filename)
    print(f"\nCreated {dna_filename}")
    
    # Read it back
    loaded_data, loaded_metadata = fmt.read_dna_file(dna_filename)
    print(f"Loaded program: {len(loaded_data)} bytes")
    print(f"Metadata: {loaded_metadata.description}")
    
    # Get file info
    info = fmt.get_file_info(dna_filename)
    print(f"\nFile info: {info}")
    
    # Validate file
    validation = fmt.validate_dna_file(dna_filename)
    print(f"Validation: {'PASS' if validation['valid'] else 'FAIL'}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")
    
    # Disassemble
    disasm = DNADisassembler()
    disassembly = disasm.disassemble_file(dna_filename)
    print(f"\nDisassembly:\n{disassembly}")
    
    # Clean up
    import os
    if os.path.exists(dna_filename):
        os.remove(dna_filename)
        print(f"\nCleaned up {dna_filename}")

if __name__ == "__main__":
    main()