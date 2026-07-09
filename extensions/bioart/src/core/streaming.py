#!/usr/bin/env python3
"""
Streaming and Chunking Support for Large DNA Sequences
Allows processing of very large sequences without holding entire data in memory
"""

import io
import os
import tempfile
import time
from typing import Iterator, Optional, Union, BinaryIO, TextIO, Generator
from dataclasses import dataclass
import gc

# Import our encoding systems
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.encoding import DNAEncoder
from core.flexible_encoding import FlexibleDNAEncoder

@dataclass
class StreamingConfig:
    """Configuration for streaming operations"""
    chunk_size: int = 1024 * 1024  # 1MB chunks by default
    buffer_size: int = 8192        # 8KB buffer for I/O
    use_temp_files: bool = True    # Use temp files for large operations
    temp_dir: Optional[str] = None # Temporary directory
    max_memory_usage: int = 50 * 1024 * 1024  # 50MB max in memory
    
class DNAStreamer:
    """Streaming DNA encoder/decoder for large sequences"""
    
    def __init__(self, config: StreamingConfig = None, encoder: Union[DNAEncoder, FlexibleDNAEncoder] = None):
        self.config = config or StreamingConfig()
        self.encoder = encoder or DNAEncoder()
        self.temp_files = []  # Track temp files for cleanup
    
    def encode_stream(self, input_stream: BinaryIO, output_stream: TextIO) -> int:
        """
        Encode binary data stream to DNA sequence stream
        Returns the number of bytes processed
        """
        total_bytes = 0
        buffer = bytearray()
        
        try:
            while True:
                # Read chunk from input
                chunk = input_stream.read(self.config.chunk_size)
                if not chunk:
                    break
                
                buffer.extend(chunk)
                total_bytes += len(chunk)
                
                # Process complete 4-byte groups (since each group becomes 4 nucleotides)
                while len(buffer) >= 4:
                    # Take 4 bytes
                    four_bytes = bytes(buffer[:4])
                    buffer = buffer[4:]
                    
                    # Encode to DNA
                    if hasattr(self.encoder, 'encode_bytes'):
                        dna_chunk = self.encoder.encode_bytes(four_bytes)
                    else:
                        # Fallback for basic DNAEncoder
                        dna_chunk = ''.join(self.encoder.byte_to_dna(b) for b in four_bytes)
                    
                    # Write to output
                    output_stream.write(dna_chunk)
                
                # Periodic garbage collection for very large files
                if total_bytes % (10 * self.config.chunk_size) == 0:
                    gc.collect()
            
            # Handle remaining bytes (pad with zeros if necessary)
            if buffer:
                while len(buffer) % 4 != 0:
                    buffer.append(0)  # Pad with zeros
                
                final_bytes = bytes(buffer)
                if hasattr(self.encoder, 'encode_bytes'):
                    final_dna = self.encoder.encode_bytes(final_bytes)
                else:
                    final_dna = ''.join(self.encoder.byte_to_dna(b) for b in final_bytes)
                
                output_stream.write(final_dna)
        
        except Exception as e:
            raise RuntimeError(f"Error during streaming encode: {e}")
        
        return total_bytes
    
    def decode_stream(self, input_stream: TextIO, output_stream: BinaryIO) -> int:
        """
        Decode DNA sequence stream to binary data stream
        Returns the number of nucleotides processed
        """
        total_nucleotides = 0
        buffer = ""
        
        try:
            while True:
                # Read chunk from input
                chunk = input_stream.read(self.config.buffer_size)
                if not chunk:
                    break
                
                # Clean chunk (remove whitespace)
                clean_chunk = ''.join(chunk.split()).upper()
                buffer += clean_chunk
                total_nucleotides += len(clean_chunk)
                
                # Process complete 4-nucleotide groups
                while len(buffer) >= 4:
                    # Take 4 nucleotides
                    four_nucleotides = buffer[:4]
                    buffer = buffer[4:]
                    
                    # Decode to bytes
                    if hasattr(self.encoder, 'decode_dna'):
                        byte_data = self.encoder.decode_dna(four_nucleotides)
                    else:
                        # Fallback for basic DNAEncoder
                        byte_val = self.encoder.dna_to_byte(four_nucleotides)
                        byte_data = bytes([byte_val])
                    
                    # Write to output
                    output_stream.write(byte_data)
                
                # Periodic garbage collection
                if total_nucleotides % (10 * self.config.buffer_size) == 0:
                    gc.collect()
            
            # Handle remaining nucleotides
            if buffer:
                # Pad buffer to multiple of 4 if necessary
                while len(buffer) % 4 != 0:
                    buffer += 'A'  # Pad with A (00)
                
                if hasattr(self.encoder, 'decode_dna'):
                    byte_data = self.encoder.decode_dna(buffer)
                else:
                    byte_data = bytes([self.encoder.dna_to_byte(buffer)])
                
                output_stream.write(byte_data)
        
        except Exception as e:
            raise RuntimeError(f"Error during streaming decode: {e}")
        
        return total_nucleotides
    
    def encode_file(self, input_filename: str, output_filename: str) -> dict:
        """
        Encode a file to DNA format with streaming
        Returns encoding statistics
        """
        import time
        start_time = time.time()
        
        with open(input_filename, 'rb') as input_file, \
             open(output_filename, 'w') as output_file:
            
            bytes_processed = self.encode_stream(input_file, output_file)
        
        end_time = time.time()
        
        # Calculate statistics
        input_size = os.path.getsize(input_filename)
        output_size = os.path.getsize(output_filename)
        elapsed_time = end_time - start_time
        
        return {
            "input_file": input_filename,
            "output_file": output_filename,
            "input_size_bytes": input_size,
            "output_size_bytes": output_size,
            "expansion_ratio": output_size / input_size if input_size > 0 else 0,
            "bytes_processed": bytes_processed,
            "processing_time_seconds": elapsed_time,
            "throughput_mb_per_sec": (input_size / (1024 * 1024)) / elapsed_time if elapsed_time > 0 else 0
        }
    
    def decode_file(self, input_filename: str, output_filename: str) -> dict:
        """
        Decode a DNA file to binary format with streaming
        Returns decoding statistics
        """
        import time
        start_time = time.time()
        
        with open(input_filename, 'r') as input_file, \
             open(output_filename, 'wb') as output_file:
            
            nucleotides_processed = self.decode_stream(input_file, output_file)
        
        end_time = time.time()
        
        # Calculate statistics
        input_size = os.path.getsize(input_filename)
        output_size = os.path.getsize(output_filename)
        elapsed_time = end_time - start_time
        
        return {
            "input_file": input_filename,
            "output_file": output_filename,
            "input_size_bytes": input_size,
            "output_size_bytes": output_size,
            "compression_ratio": input_size / output_size if output_size > 0 else 0,
            "nucleotides_processed": nucleotides_processed,
            "processing_time_seconds": elapsed_time,
            "throughput_mb_per_sec": (output_size / (1024 * 1024)) / elapsed_time if elapsed_time > 0 else 0
        }
    
    def create_chunked_iterator(self, data: Union[bytes, str], chunk_size: Optional[int] = None) -> Generator:
        """
        Create an iterator that yields chunks of data
        Useful for processing large sequences in memory-efficient way
        """
        chunk_size = chunk_size or self.config.chunk_size
        
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]
    
    def process_large_sequence(self, sequence: Union[bytes, str], 
                             operation: str = "encode") -> Iterator[str]:
        """
        Process a large sequence in chunks, yielding results incrementally
        """
        if operation == "encode" and isinstance(sequence, bytes):
            # Encode bytes to DNA
            for chunk in self.create_chunked_iterator(sequence, self.config.chunk_size):
                if hasattr(self.encoder, 'encode_bytes'):
                    yield self.encoder.encode_bytes(chunk)
                else:
                    yield ''.join(self.encoder.byte_to_dna(b) for b in chunk)
        
        elif operation == "decode" and isinstance(sequence, str):
            # Decode DNA to bytes, but yield as hex strings for readability
            clean_sequence = ''.join(sequence.split()).upper()
            
            # Process in 4-nucleotide chunks (since each represents 1 byte)
            for i in range(0, len(clean_sequence), self.config.chunk_size):
                chunk = clean_sequence[i:i + self.config.chunk_size]
                
                # Ensure chunk length is multiple of 4
                while len(chunk) % 4 != 0:
                    chunk += 'A'  # Pad with A
                
                if hasattr(self.encoder, 'decode_dna'):
                    byte_data = self.encoder.decode_dna(chunk)
                else:
                    byte_data = bytes([self.encoder.dna_to_byte(chunk[j:j+4]) 
                                     for j in range(0, len(chunk), 4)])
                
                # Yield as hex string for readability
                yield byte_data.hex()
        
        else:
            raise ValueError(f"Invalid operation '{operation}' or data type mismatch")
    
    def get_memory_usage_estimate(self, data_size: int, operation: str = "encode") -> dict:
        """
        Estimate memory usage for processing given data size
        """
        if operation == "encode":
            # Encoding: input bytes -> DNA (4x expansion)
            input_memory = data_size
            output_memory = data_size * 4  # 4 nucleotides per byte
            working_memory = self.config.chunk_size * 2  # Input + output buffers
        
        else:  # decode
            # Decoding: DNA -> bytes (4:1 compression)
            input_memory = data_size
            output_memory = data_size // 4
            working_memory = self.config.chunk_size * 2
        
        total_estimated = input_memory + output_memory + working_memory
        
        return {
            "input_memory_bytes": input_memory,
            "output_memory_bytes": output_memory,
            "working_memory_bytes": working_memory,
            "total_estimated_bytes": total_estimated,
            "recommended_chunk_size": min(self.config.chunk_size, 
                                        self.config.max_memory_usage // 6),
            "will_use_temp_files": total_estimated > self.config.max_memory_usage
        }
    
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass  # Ignore cleanup errors
        self.temp_files.clear()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()

def main():
    """Demo of streaming DNA processing"""
    import time
    
    print("🧬 DNA STREAMING & CHUNKING DEMO")
    print("=" * 40)
    
    # Create streamer
    config = StreamingConfig(chunk_size=1024, buffer_size=512)
    streamer = DNAStreamer(config)
    
    # Create test data
    test_data = b"This is a test of streaming DNA encoding and decoding. " * 100
    print(f"Test data size: {len(test_data)} bytes")
    
    # Memory usage estimate
    memory_est = streamer.get_memory_usage_estimate(len(test_data), "encode")
    print(f"Estimated memory usage: {memory_est['total_estimated_bytes']} bytes")
    
    # Test chunked processing
    print("\n--- Chunked Encoding Test ---")
    encoded_chunks = list(streamer.process_large_sequence(test_data, "encode"))
    print(f"Generated {len(encoded_chunks)} chunks")
    
    # Reconstruct full sequence
    full_dna_sequence = ''.join(encoded_chunks)
    print(f"Total DNA length: {len(full_dna_sequence)} nucleotides")
    
    # Test chunked decoding
    print("\n--- Chunked Decoding Test ---")
    decoded_chunks = list(streamer.process_large_sequence(full_dna_sequence, "decode"))
    print(f"Generated {len(decoded_chunks)} decoded chunks")
    
    # Reconstruct original data
    full_hex = ''.join(decoded_chunks)
    reconstructed_data = bytes.fromhex(full_hex)
    print(f"Reconstructed size: {len(reconstructed_data)} bytes")
    print(f"Roundtrip: {'✅ PASS' if reconstructed_data == test_data else '❌ FAIL'}")
    
    # Test file streaming
    print("\n--- File Streaming Test ---")
    
    # Create temporary test file
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_input:
        temp_input.write(test_data)
        input_filename = temp_input.name
    
    try:
        # Encode file
        dna_filename = input_filename + ".dna"
        output_filename = input_filename + ".decoded"  # Define early
        
        encode_stats = streamer.encode_file(input_filename, dna_filename)
        print(f"Encoding: {encode_stats['throughput_mb_per_sec']:.2f} MB/s")
        
        # Decode file
        decode_stats = streamer.decode_file(dna_filename, output_filename)
        print(f"Decoding: {decode_stats['throughput_mb_per_sec']:.2f} MB/s")
        
        # Verify file integrity
        with open(output_filename, 'rb') as f:
            decoded_file_data = f.read()
        
        print(f"File roundtrip: {'✅ PASS' if decoded_file_data == test_data else '❌ FAIL'}")
        
    finally:
        # Cleanup
        for filename in [input_filename, dna_filename, output_filename]:
            if os.path.exists(filename):
                os.remove(filename)
        
        streamer.cleanup()
    
    print("\n✅ Streaming demo completed!")

if __name__ == "__main__":
    main()