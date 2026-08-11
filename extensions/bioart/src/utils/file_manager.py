#!/usr/bin/env python3
"""
DNA File Manager
Utilities for DNA program file I/O operations with metadata support
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional


class DNAFileManager:
    """
    File manager for DNA programs with metadata and versioning support
    """

    DNA_EXTENSION = '.dna'
    SOURCE_EXTENSION = '.dnas'  # DNA Source
    METADATA_EXTENSION = '.dnameta'  # DNA Metadata

    def __init__(self, base_directory: Optional[str] = None):
        """Initialize file manager with optional base directory"""
        self.base_directory = Path(base_directory) if base_directory else Path.cwd()
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure required directories exist"""
        dirs = ['programs', 'compiled', 'examples', 'backups']
        for dir_name in dirs:
            (self.base_directory / dir_name).mkdir(exist_ok=True)

    def save_dna_program(self, filename: str, dna_source: str, metadata: Optional[Dict] = None):
        """
        Save DNA source program with metadata
        
        Args:
            filename: Program filename (without extension)
            dna_source: DNA source code
            metadata: Optional program metadata
        """  # noqa: W293
        try:
            # Ensure filename has correct extension
            if not filename.endswith(self.SOURCE_EXTENSION):
                filename += self.SOURCE_EXTENSION

            file_path = self.base_directory / 'programs' / filename

            # Create metadata
            program_metadata = {
                'filename': filename,
                'created': time.time(),
                'version': '1.0',
                'size_nucleotides': len(dna_source.replace(' ', '')),
                'size_bytes': len(dna_source.replace(' ', '')) // 4,
                'language_version': '2.0.0-refactored',
                'user_metadata': metadata or {}
            }

            # Save source file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(dna_source)

            # Save metadata
            meta_path = file_path.with_suffix(self.METADATA_EXTENSION)
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(program_metadata, f, indent=2)

            return str(file_path)

        except Exception as e:
            raise RuntimeError(f"Failed to save DNA program: {e}")  # noqa: B904

    def load_dna_program(self, filename: str) -> Dict[str, Any]:
        """
        Load DNA source program with metadata
        
        Args:
            filename: Program filename
            
        Returns:
            Dictionary with source code and metadata
        """  # noqa: W293
        try:
            # Ensure filename has correct extension
            if not filename.endswith(self.SOURCE_EXTENSION):
                filename += self.SOURCE_EXTENSION

            file_path = self.base_directory / 'programs' / filename

            if not file_path.exists():
                raise FileNotFoundError(f"DNA program not found: {filename}")

            # Load source code
            with open(file_path, encoding='utf-8') as f:
                source_code = f.read()

            # Load metadata if available
            meta_path = file_path.with_suffix(self.METADATA_EXTENSION)
            metadata = {}
            if meta_path.exists():
                with open(meta_path, encoding='utf-8') as f:
                    metadata = json.load(f)

            return {
                'source_code': source_code,
                'metadata': metadata,
                'file_path': str(file_path),
                'last_modified': os.path.getmtime(file_path)
            }

        except Exception as e:
            raise RuntimeError(f"Failed to load DNA program: {e}")  # noqa: B904

    def save_compiled_program(self, filename: str, bytecode: bytes, metadata: Optional[Dict] = None):
        """
        Save compiled DNA program bytecode
        
        Args:
            filename: Program filename (without extension)
            bytecode: Compiled bytecode
            metadata: Optional compilation metadata
        """  # noqa: W293
        try:
            # Ensure filename has correct extension
            if not filename.endswith(self.DNA_EXTENSION):
                filename += self.DNA_EXTENSION

            file_path = self.base_directory / 'compiled' / filename

            # Create compilation metadata
            compile_metadata = {
                'filename': filename,
                'compiled': time.time(),
                'bytecode_size': len(bytecode),
                'checksum': hash(bytecode),
                'language_version': '2.0.0-refactored',
                'compilation_metadata': metadata or {}
            }

            # Save bytecode
            with open(file_path, 'wb') as f:
                f.write(bytecode)

            # Save metadata
            meta_path = file_path.with_suffix(self.METADATA_EXTENSION)
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(compile_metadata, f, indent=2)

            return str(file_path)

        except Exception as e:
            raise RuntimeError(f"Failed to save compiled program: {e}")  # noqa: B904

    def load_compiled_program(self, filename: str) -> bytes:
        """
        Load compiled DNA program bytecode
        
        Args:
            filename: Program filename
            
        Returns:
            Compiled bytecode
        """  # noqa: W293
        try:
            # Ensure filename has correct extension
            if not filename.endswith(self.DNA_EXTENSION):
                filename += self.DNA_EXTENSION

            file_path = self.base_directory / 'compiled' / filename

            if not file_path.exists():
                raise FileNotFoundError(f"Compiled program not found: {filename}")

            # Load bytecode
            with open(file_path, 'rb') as f:
                bytecode = f.read()

            # Verify checksum if metadata exists
            meta_path = file_path.with_suffix(self.METADATA_EXTENSION)
            if meta_path.exists():
                with open(meta_path, encoding='utf-8') as f:
                    metadata = json.load(f)

                stored_checksum = metadata.get('checksum')
                if stored_checksum and hash(bytecode) != stored_checksum:
                    raise ValueError("Bytecode checksum mismatch - file may be corrupted")

            return bytecode

        except Exception as e:
            raise RuntimeError(f"Failed to load compiled program: {e}")  # noqa: B904

    def list_programs(self, program_type: str = 'source') -> list:
        """
        List available programs
        
        Args:
            program_type: 'source' or 'compiled'
            
        Returns:
            List of program information dictionaries
        """  # noqa: W293
        try:
            if program_type == 'source':
                directory = self.base_directory / 'programs'
                extension = self.SOURCE_EXTENSION
            elif program_type == 'compiled':
                directory = self.base_directory / 'compiled'
                extension = self.DNA_EXTENSION
            else:
                raise ValueError("program_type must be 'source' or 'compiled'")

            programs = []

            for file_path in directory.glob(f'*{extension}'):
                program_info = {
                    'filename': file_path.name,
                    'basename': file_path.stem,
                    'size': file_path.stat().st_size,
                    'modified': file_path.stat().st_mtime,
                    'path': str(file_path)
                }

                # Load metadata if available
                meta_path = file_path.with_suffix(self.METADATA_EXTENSION)
                if meta_path.exists():
                    with open(meta_path, encoding='utf-8') as f:
                        program_info['metadata'] = json.load(f)

                programs.append(program_info)

            # Sort by modification time (newest first)
            programs.sort(key=lambda x: x['modified'], reverse=True)

            return programs

        except Exception as e:
            raise RuntimeError(f"Failed to list programs: {e}")  # noqa: B904

    def backup_program(self, filename: str, program_type: str = 'source'):
        """
        Create backup of program
        
        Args:
            filename: Program filename
            program_type: 'source' or 'compiled'
        """  # noqa: W293
        try:
            if program_type == 'source':
                source_dir = self.base_directory / 'programs'
                extension = self.SOURCE_EXTENSION
            else:
                source_dir = self.base_directory / 'compiled'
                extension = self.DNA_EXTENSION

            if not filename.endswith(extension):
                filename += extension

            source_path = source_dir / filename
            if not source_path.exists():
                raise FileNotFoundError(f"Program not found: {filename}")

            # Create backup filename with timestamp
            timestamp = int(time.time())
            backup_name = f"{source_path.stem}_{timestamp}{extension}"
            backup_path = self.base_directory / 'backups' / backup_name

            # Copy program file
            import shutil
            shutil.copy2(source_path, backup_path)

            # Copy metadata if exists
            meta_source = source_path.with_suffix(self.METADATA_EXTENSION)
            if meta_source.exists():
                meta_backup = backup_path.with_suffix(self.METADATA_EXTENSION)
                shutil.copy2(meta_source, meta_backup)

            return str(backup_path)

        except Exception as e:
            raise RuntimeError(f"Failed to backup program: {e}")  # noqa: B904

    def delete_program(self, filename: str, program_type: str = 'source', create_backup: bool = True):
        """
        Delete program with optional backup
        
        Args:
            filename: Program filename
            program_type: 'source' or 'compiled'
            create_backup: Create backup before deletion
        """  # noqa: W293
        try:
            # Create backup first if requested
            if create_backup:
                self.backup_program(filename, program_type)

            if program_type == 'source':
                directory = self.base_directory / 'programs'
                extension = self.SOURCE_EXTENSION
            else:
                directory = self.base_directory / 'compiled'
                extension = self.DNA_EXTENSION

            if not filename.endswith(extension):
                filename += extension

            file_path = directory / filename
            meta_path = file_path.with_suffix(self.METADATA_EXTENSION)

            # Delete files
            if file_path.exists():
                file_path.unlink()

            if meta_path.exists():
                meta_path.unlink()

        except Exception as e:
            raise RuntimeError(f"Failed to delete program: {e}")  # noqa: B904

    def export_program(self, filename: str, export_path: str, include_metadata: bool = True):
        """
        Export program to external location
        
        Args:
            filename: Program filename
            export_path: Destination path
            include_metadata: Include metadata files
        """  # noqa: W293
        try:
            import shutil

            # Try both source and compiled directories
            for program_type, directory, extension in [  # noqa: B007
                ('source', self.base_directory / 'programs', self.SOURCE_EXTENSION),
                ('compiled', self.base_directory / 'compiled', self.DNA_EXTENSION)
            ]:
                if not filename.endswith(extension):
                    test_filename = filename + extension
                else:
                    test_filename = filename

                source_path = directory / test_filename
                if source_path.exists():
                    # Copy program file
                    shutil.copy2(source_path, export_path)

                    # Copy metadata if requested and exists
                    if include_metadata:
                        meta_source = source_path.with_suffix(self.METADATA_EXTENSION)
                        if meta_source.exists():
                            meta_dest = Path(export_path) / (source_path.stem + self.METADATA_EXTENSION)
                            shutil.copy2(meta_source, meta_dest)

                    return export_path

            raise FileNotFoundError(f"Program not found: {filename}")

        except Exception as e:
            raise RuntimeError(f"Failed to export program: {e}")  # noqa: B904

    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage usage information"""
        try:
            info = {
                'base_directory': str(self.base_directory),
                'directories': {}
            }

            for dir_name in ['programs', 'compiled', 'examples', 'backups']:
                dir_path = self.base_directory / dir_name
                if dir_path.exists():
                    files = list(dir_path.iterdir())
                    total_size = sum(f.stat().st_size for f in files if f.is_file())

                    info['directories'][dir_name] = {
                        'file_count': len([f for f in files if f.is_file()]),
                        'total_size_bytes': total_size,
                        'total_size_kb': total_size / 1024,
                        'path': str(dir_path)
                    }

            return info

        except Exception as e:
            raise RuntimeError(f"Failed to get storage info: {e}")  # noqa: B904
