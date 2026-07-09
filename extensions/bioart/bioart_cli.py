#!/usr/bin/env python3
"""
Bioart Command Line Interface
Real-world ready translator and modifier for DNA-based encoding
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from translator import BioartTranslator


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Bioart DNA Translator - Convert between text, binary, and DNA sequences',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate text to DNA
  bioart_cli.py encode --text "Hello, World!"
  
  # Translate DNA back to text
  bioart_cli.py decode --dna "UACAUCUUUCGAUCGAUCGA"
  
  # Convert file to DNA
  bioart_cli.py encode --file input.txt --output dna.txt
  
  # Convert DNA file back to original
  bioart_cli.py decode --file dna.txt --output restored.txt
  
  # Modify DNA sequence
  bioart_cli.py modify --dna "AAAUUU" --replace 0 3 "GGG"
  
  # Validate reversibility
  bioart_cli.py verify --text "Test data"
  
  # Get sequence information
  bioart_cli.py info --dna "AUCGAUCG"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # ===== ENCODE command =====
    encode_parser = subparsers.add_parser('encode', help='Encode text/file to DNA')
    encode_group = encode_parser.add_mutually_exclusive_group(required=True)
    encode_group.add_argument('--text', type=str, help='Text to encode')
    encode_group.add_argument('--file', type=str, help='File to encode')
    encode_parser.add_argument('--output', type=str, help='Output file (default: stdout)')
    encode_parser.add_argument('--format', action='store_true', help='Format output for readability')
    
    # ===== DECODE command =====
    decode_parser = subparsers.add_parser('decode', help='Decode DNA to text/file')
    decode_group = decode_parser.add_mutually_exclusive_group(required=True)
    decode_group.add_argument('--dna', type=str, help='DNA sequence to decode')
    decode_group.add_argument('--file', type=str, help='File containing DNA to decode')
    decode_parser.add_argument('--output', type=str, help='Output file (default: stdout)')
    decode_parser.add_argument('--binary', action='store_true', help='Output as binary (for files)')
    
    # ===== MODIFY command =====
    modify_parser = subparsers.add_parser('modify', help='Modify DNA sequence')
    modify_parser.add_argument('--dna', type=str, required=True, help='DNA sequence to modify')
    modify_group = modify_parser.add_mutually_exclusive_group(required=True)
    modify_group.add_argument('--replace', nargs=3, metavar=('START', 'LENGTH', 'NEW_SEQ'),
                             help='Replace sequence at position')
    modify_group.add_argument('--insert', nargs=2, metavar=('POSITION', 'SEQ'),
                             help='Insert sequence at position')
    modify_group.add_argument('--delete', nargs=2, metavar=('START', 'LENGTH'),
                             help='Delete sequence')
    modify_group.add_argument('--mutate', nargs=2, metavar=('POSITION', 'NUCLEOTIDE'),
                             help='Mutate single nucleotide')
    modify_parser.add_argument('--output', type=str, help='Output file (default: stdout)')
    
    # ===== VERIFY command =====
    verify_parser = subparsers.add_parser('verify', help='Verify reversibility')
    verify_group = verify_parser.add_mutually_exclusive_group(required=True)
    verify_group.add_argument('--text', type=str, help='Text to verify')
    verify_group.add_argument('--file', type=str, help='File to verify')
    
    # ===== INFO command =====
    info_parser = subparsers.add_parser('info', help='Get DNA sequence information')
    info_group = info_parser.add_mutually_exclusive_group(required=True)
    info_group.add_argument('--dna', type=str, help='DNA sequence to analyze')
    info_group.add_argument('--file', type=str, help='File containing DNA sequence')
    
    # ===== INTERACTIVE command =====
    interactive_parser = subparsers.add_parser('interactive', help='Interactive mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize translator
    translator = BioartTranslator()
    
    try:
        # Execute command
        if args.command == 'encode':
            return cmd_encode(translator, args)
        elif args.command == 'decode':
            return cmd_decode(translator, args)
        elif args.command == 'modify':
            return cmd_modify(translator, args)
        elif args.command == 'verify':
            return cmd_verify(translator, args)
        elif args.command == 'info':
            return cmd_info(translator, args)
        elif args.command == 'interactive':
            return cmd_interactive(translator)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_encode(translator, args):
    """Handle encode command"""
    if args.text:
        dna = translator.text_to_dna(args.text)
    elif args.file:
        dna = translator.file_to_dna(args.file)
    else:
        print("Error: Either --text or --file required", file=sys.stderr)
        return 1
    
    # Format if requested
    if args.format:
        dna = translator.format_dna(dna)
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(dna)
        print(f"Encoded to: {args.output}")
    else:
        print(dna)
    
    return 0


def cmd_decode(translator, args):
    """Handle decode command"""
    if args.dna:
        dna = args.dna.strip()
    elif args.file:
        with open(args.file, 'r') as f:
            dna = f.read().replace('\n', '').replace(' ', '').strip()
    else:
        print("Error: Either --dna or --file required", file=sys.stderr)
        return 1
    
    # Decode
    if args.binary or args.output:
        # Output as binary
        data = translator.dna_to_binary(dna)
        if args.output:
            with open(args.output, 'wb') as f:
                f.write(data)
            print(f"Decoded to: {args.output}")
        else:
            sys.stdout.buffer.write(data)
    else:
        # Output as text
        text = translator.dna_to_text(dna)
        print(text)
    
    return 0


def cmd_modify(translator, args):
    """Handle modify command"""
    dna = args.dna.strip()
    
    # Validate input
    if not translator.validate_dna(dna):
        print("Error: Invalid DNA sequence", file=sys.stderr)
        return 1
    
    # Apply modification
    if args.replace:
        start, length, new_seq = args.replace
        modified = translator.replace_sequence(dna, int(start), int(length), new_seq)
    elif args.insert:
        position, seq = args.insert
        modified = translator.insert_sequence(dna, int(position), seq)
    elif args.delete:
        start, length = args.delete
        modified = translator.delete_sequence(dna, int(start), int(length))
    elif args.mutate:
        position, nucleotide = args.mutate
        modified = translator.modify_nucleotide(dna, int(position), nucleotide)
    else:
        print("Error: No modification specified", file=sys.stderr)
        return 1
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(modified)
        print(f"Modified DNA saved to: {args.output}")
    else:
        print(modified)
    
    return 0


def cmd_verify(translator, args):
    """Handle verify command"""
    if args.text:
        data = args.text
    elif args.file:
        with open(args.file, 'rb') as f:
            data = f.read()
    else:
        print("Error: Either --text or --file required", file=sys.stderr)
        return 1
    
    # Verify
    result = translator.verify_reversibility(data)
    
    # Print results
    print("=" * 60)
    print("REVERSIBILITY VERIFICATION RESULTS")
    print("=" * 60)
    print(f"Original size:  {result['original_size']} bytes")
    print(f"DNA size:       {result['dna_size']} nucleotides")
    print(f"Restored size:  {result['restored_size']} bytes")
    print(f"Match:          {'✓ YES' if result['match'] else '✗ NO'}")
    print(f"Status:         {'✓ PASSED' if result['success'] else '✗ FAILED'}")
    
    if result['error']:
        print(f"Error:          {result['error']}")
    
    print("=" * 60)
    
    return 0 if result['success'] else 1


def cmd_info(translator, args):
    """Handle info command"""
    if args.dna:
        dna = args.dna.strip()
    elif args.file:
        with open(args.file, 'r') as f:
            dna = f.read().replace('\n', '').replace(' ', '').strip()
    else:
        print("Error: Either --dna or --file required", file=sys.stderr)
        return 1
    
    # Get info
    info = translator.get_sequence_info(dna)
    
    # Print info
    print("=" * 60)
    print("DNA SEQUENCE INFORMATION")
    print("=" * 60)
    print(f"Length:         {info['length']} nucleotides")
    print(f"Byte capacity:  {info['byte_capacity']} bytes")
    print(f"Valid:          {'✓ YES' if info['is_valid'] else '✗ NO'}")
    print(f"Complete:       {'✓ YES' if info['is_complete'] else '✗ NO (padding needed)'}")
    
    if info['is_valid']:
        print("\nNucleotide composition:")
        for nt, count in sorted(info['nucleotide_counts'].items()):
            percentage = (count / info['length'] * 100) if info['length'] > 0 else 0
            print(f"  {nt}: {count:5d} ({percentage:5.1f}%)")
        print(f"\nGC content:     {info['gc_content']:.1f}%")
    
    print("=" * 60)
    
    return 0


def cmd_interactive(translator):
    """Handle interactive mode"""
    print("=" * 60)
    print("BIOART INTERACTIVE TRANSLATOR")
    print("=" * 60)
    print("Commands:")
    print("  encode <text>     - Encode text to DNA")
    print("  decode <dna>      - Decode DNA to text")
    print("  modify <dna>      - Interactive modification")
    print("  verify <text>     - Verify reversibility")
    print("  info <dna>        - Show sequence info")
    print("  stats             - Show usage statistics")
    print("  help              - Show this help")
    print("  quit              - Exit interactive mode")
    print("=" * 60)
    
    while True:
        try:
            command = input("\nbioart> ").strip()
            
            if not command:
                continue
            
            parts = command.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            
            if cmd == 'quit' or cmd == 'exit':
                break
            elif cmd == 'help':
                print("Available commands: encode, decode, modify, verify, info, stats, quit")
            elif cmd == 'encode':
                if arg:
                    dna = translator.text_to_dna(arg)
                    print(f"DNA: {translator.format_dna(dna, width=60)}")
                else:
                    print("Usage: encode <text>")
            elif cmd == 'decode':
                if arg:
                    text = translator.dna_to_text(arg.replace(' ', ''))
                    print(f"Text: {text}")
                else:
                    print("Usage: decode <dna>")
            elif cmd == 'verify':
                if arg:
                    result = translator.verify_reversibility(arg)
                    print(f"Reversible: {'✓ YES' if result['success'] else '✗ NO'}")
                    print(f"Original: {result['original_size']} bytes → DNA: {result['dna_size']} nt → Restored: {result['restored_size']} bytes")
                else:
                    print("Usage: verify <text>")
            elif cmd == 'info':
                if arg:
                    info = translator.get_sequence_info(arg.replace(' ', ''))
                    print(f"Length: {info['length']} nt, Capacity: {info['byte_capacity']} bytes")
                    print(f"Valid: {info['is_valid']}, Complete: {info['is_complete']}")
                    if info['is_valid']:
                        print(f"GC content: {info['gc_content']:.1f}%")
                else:
                    print("Usage: info <dna>")
            elif cmd == 'stats':
                stats = translator.get_stats()
                print("Usage statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
            else:
                print(f"Unknown command: {cmd}. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\nUse 'quit' to exit")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nGoodbye!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
