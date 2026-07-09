#!/usr/bin/env python3
"""
Security and Robustness Utilities for Bioart DNA Programming Language
Enhanced error handling, input validation, security measures, and AI ethics integration
"""

import os
import sys
import hashlib
import hmac
import secrets
import re
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from functools import wraps
from dataclasses import dataclass
from enum import Enum
import traceback

# Import our core modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class SecurityLevel(Enum):
    """Security levels for operations"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_input: Any = None

class DNASecurityError(Exception):
    """Custom exception for DNA security issues"""
    pass

class DNAValidationError(Exception):
    """Custom exception for DNA validation issues"""
    pass

class InputValidator:
    """Comprehensive input validator for DNA operations"""
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.MEDIUM):
        self.security_level = security_level
        self.max_sequence_length = self._get_max_sequence_length()
        self.allowed_nucleotides = {'A', 'U', 'C', 'G', 'T'}  # Include T for DNA
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _get_max_sequence_length(self) -> int:
        """Get maximum sequence length based on security level"""
        limits = {
            SecurityLevel.LOW: 1000000,      # 1M nucleotides
            SecurityLevel.MEDIUM: 100000,   # 100K nucleotides
            SecurityLevel.HIGH: 10000,      # 10K nucleotides
            SecurityLevel.CRITICAL: 1000    # 1K nucleotides
        }
        return limits.get(self.security_level, 100000)
    
    def validate_dna_sequence(self, sequence: str, 
                            allow_whitespace: bool = True,
                            allow_lowercase: bool = True) -> ValidationResult:
        """Validate a DNA sequence string"""
        errors = []
        warnings = []
        
        if not isinstance(sequence, str):
            errors.append(f"Sequence must be a string, got {type(sequence)}")
            return ValidationResult(False, errors, warnings)
        
        # Check for null or empty
        if not sequence:
            errors.append("Sequence cannot be empty")
            return ValidationResult(False, errors, warnings)
        
        # Check length limits
        clean_sequence = ''.join(sequence.split()) if allow_whitespace else sequence
        if len(clean_sequence) > self.max_sequence_length:
            errors.append(f"Sequence too long: {len(clean_sequence)} > {self.max_sequence_length}")
            return ValidationResult(False, errors, warnings)
        
        # Sanitize input
        sanitized = clean_sequence.upper() if allow_lowercase else clean_sequence
        
        # Check for invalid characters
        invalid_chars = set(sanitized) - self.allowed_nucleotides
        if invalid_chars:
            errors.append(f"Invalid nucleotides found: {sorted(invalid_chars)}")
        
        # Check for suspicious patterns (potential security issues)
        if self.security_level.value >= SecurityLevel.HIGH.value:
            suspicious_patterns = self._check_suspicious_patterns(sanitized)
            if suspicious_patterns:
                warnings.extend(suspicious_patterns)
        
        # Check sequence structure
        if len(sanitized) % 4 != 0:
            warnings.append(f"Sequence length {len(sanitized)} is not multiple of 4")
        
        # Check for extremely repetitive sequences (potential DoS)
        if self._is_overly_repetitive(sanitized):
            warnings.append("Sequence appears highly repetitive")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, sanitized)
    
    def validate_file_path(self, file_path: str, 
                         allowed_extensions: List[str] = None,
                         check_existence: bool = True) -> ValidationResult:
        """Validate file path for security"""
        errors = []
        warnings = []
        
        if not isinstance(file_path, str):
            errors.append(f"File path must be string, got {type(file_path)}")
            return ValidationResult(False, errors, warnings)
        
        # Check for path traversal attempts
        if '..' in file_path or file_path.startswith('/'):
            errors.append("Path traversal detected")
        
        # Check for null bytes (security issue)
        if '\x00' in file_path:
            errors.append("Null byte in file path")
        
        # Check file extension
        if allowed_extensions:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in allowed_extensions:
                errors.append(f"File extension {file_ext} not allowed")
        
        # Check path length
        if len(file_path) > 255:  # Most filesystems limit
            errors.append("File path too long")
        
        # Check existence if required
        if check_existence and not os.path.exists(file_path):
            warnings.append("File does not exist")
        
        # Sanitize path
        sanitized = os.path.normpath(file_path)
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, sanitized)
    
    def validate_program_size(self, program_data: bytes) -> ValidationResult:
        """Validate program size and content"""
        errors = []
        warnings = []
        
        if not isinstance(program_data, (bytes, bytearray)):
            errors.append(f"Program must be bytes, got {type(program_data)}")
            return ValidationResult(False, errors, warnings)
        
        # Size limits based on security level
        max_sizes = {
            SecurityLevel.LOW: 10 * 1024 * 1024,    # 10MB
            SecurityLevel.MEDIUM: 1024 * 1024,      # 1MB
            SecurityLevel.HIGH: 64 * 1024,          # 64KB
            SecurityLevel.CRITICAL: 1024            # 1KB
        }
        
        max_size = max_sizes.get(self.security_level, 1024 * 1024)
        if len(program_data) > max_size:
            errors.append(f"Program too large: {len(program_data)} > {max_size}")
        
        # Check for suspicious byte patterns
        if self.security_level.value >= SecurityLevel.HIGH.value:
            if self._has_suspicious_bytes(program_data):
                warnings.append("Program contains suspicious byte patterns")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, program_data)
    
    def _check_suspicious_patterns(self, sequence: str) -> List[str]:
        """Check for suspicious patterns in DNA sequence"""
        warnings = []
        
        # Check for overly long runs of same nucleotide
        for nucleotide in self.allowed_nucleotides:
            if nucleotide * 20 in sequence:  # 20 consecutive same nucleotides
                warnings.append(f"Long run of {nucleotide} detected")
        
        # Check for potential buffer overflow patterns
        if 'AAAA' * 10 in sequence:  # Many NOPs
            warnings.append("Excessive NOP instructions detected")
        
        return warnings
    
    def _is_overly_repetitive(self, sequence: str, threshold: float = 0.8) -> bool:
        """Check if sequence is overly repetitive"""
        if len(sequence) < 16:
            return False
        
        # Check for repeated 4-nucleotide patterns
        patterns = {}
        for i in range(0, len(sequence) - 3, 4):
            pattern = sequence[i:i+4]
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        if patterns:
            max_pattern_count = max(patterns.values())
            total_patterns = len(sequence) // 4
            repetition_ratio = max_pattern_count / total_patterns
            return repetition_ratio > threshold
        
        return False
    
    def _has_suspicious_bytes(self, data: bytes) -> bool:
        """Check for suspicious byte patterns"""
        # Check for excessive runs of same byte
        for i in range(256):
            if bytes([i]) * 50 in data:  # 50 consecutive same bytes
                return True
        
        return False

class SecureOperationManager:
    """Manager for secure DNA operations with integrated AI ethics framework"""
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.MEDIUM, enable_ethics: bool = True):
        self.security_level = security_level
        self.validator = InputValidator(security_level)
        self.operation_log = []
        self.enable_ethics = enable_ethics
        
        # Set up secure random
        self.secure_random = secrets.SystemRandom()
        
        # Initialize ethics framework if enabled
        self.ethics_framework = None
        if enable_ethics:
            try:
                from ethics.ai_ethics_framework import EthicsFramework, EthicsLevel
                # Map security level to ethics level
                ethics_level_map = {
                    SecurityLevel.LOW: EthicsLevel.BASIC,
                    SecurityLevel.MEDIUM: EthicsLevel.STANDARD,
                    SecurityLevel.HIGH: EthicsLevel.STRICT,
                    SecurityLevel.CRITICAL: EthicsLevel.CRITICAL
                }
                ethics_level = ethics_level_map.get(security_level, EthicsLevel.STANDARD)
                self.ethics_framework = EthicsFramework(ethics_level)
            except ImportError:
                # Ethics framework not available, continue without it
                self.enable_ethics = False
    
    def secure_operation_wrapper(self, operation_name: str):
        """Decorator for secure operations with ethics validation"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    # Ethics validation if enabled
                    if self.enable_ethics and self.ethics_framework:
                        context = {
                            "operation_name": operation_name,
                            "significant_action": True,
                            "verification_completed": True,
                            "biological_operation": "dna" in operation_name.lower() or "bio" in operation_name.lower(),
                            "safety_validated": True
                        }
                        
                        action_description = f"Execute secure operation: {operation_name}"
                        ethics_result = self.ethics_framework.validate_action(action_description, context)
                        
                        if not ethics_result.is_ethical:
                            # Log ethics violation
                            self.operation_log.append({
                                'operation': operation_name,
                                'timestamp': time.time(),
                                'status': 'ethics_violation',
                                'violations': ethics_result.violations
                            })
                            raise DNASecurityError(f"Ethics violation in operation '{operation_name}': {'; '.join(ethics_result.violations)}")
                    
                    # Log operation start
                    self.operation_log.append({
                        'operation': operation_name,
                        'timestamp': time.time(),
                        'status': 'started'
                    })
                    
                    # Execute operation
                    result = func(*args, **kwargs)
                    
                    # Log success
                    self.operation_log[-1]['status'] = 'completed'
                    return result
                    
                except Exception as e:
                    # Log error
                    self.operation_log[-1]['status'] = 'failed'
                    self.operation_log[-1]['error'] = str(e)
                    
                    # Handle error based on security level
                    if self.security_level.value >= SecurityLevel.HIGH.value:
                        # Don't leak error details in high security mode
                        raise DNASecurityError("Operation failed for security reasons")
                    else:
                        raise
            
            return wrapper
        return decorator
    
    def create_secure_hash(self, data: Union[str, bytes], salt: bytes = None) -> str:
        """Create secure hash of data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if salt is None:
            salt = secrets.token_bytes(32)
        
        # Use SHA-256 with salt
        hash_obj = hashlib.sha256()
        hash_obj.update(salt)
        hash_obj.update(data)
        
        return salt.hex() + hash_obj.hexdigest()
    
    def verify_secure_hash(self, data: Union[str, bytes], hash_with_salt: str) -> bool:
        """Verify secure hash"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Extract salt (first 64 hex chars = 32 bytes)
            salt_hex = hash_with_salt[:64]
            expected_hash = hash_with_salt[64:]
            
            salt = bytes.fromhex(salt_hex)
            
            # Recreate hash
            hash_obj = hashlib.sha256()
            hash_obj.update(salt)
            hash_obj.update(data)
            calculated_hash = hash_obj.hexdigest()
            
            # Use constant-time comparison
            return hmac.compare_digest(calculated_hash, expected_hash)
            
        except Exception:
            return False
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for security"""
        # Remove dangerous characters
        sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Prevent hidden files
        if sanitized.startswith('.'):
            sanitized = '_' + sanitized[1:]
        
        # Limit length
        if len(sanitized) > 100:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:90] + ext
        
        return sanitized
    
    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Get operation log for audit"""
        return self.operation_log.copy()
    
    def get_ethics_compliance_report(self) -> Dict[str, Any]:
        """Get ethics compliance report if ethics framework is enabled"""
        if not self.enable_ethics or not self.ethics_framework:
            return {"status": "ethics_disabled", "message": "Ethics framework not enabled"}
        
        return self.ethics_framework.get_compliance_report()

class RobustErrorHandler:
    """Robust error handling for DNA operations"""
    
    def __init__(self, log_errors: bool = True):
        self.log_errors = log_errors
        self.error_counts = {}
        
        # Set up logging
        if log_errors:
            logging.basicConfig(
                level=logging.ERROR,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error: Exception, context: str = "", 
                    reraise: bool = True) -> Optional[str]:
        """Handle errors with logging and counting"""
        error_type = type(error).__name__
        
        # Count errors
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Create error message
        error_msg = f"{context}: {error_type}: {str(error)}"
        
        # Log error
        if self.log_errors:
            self.logger.error(error_msg)
            if hasattr(error, '__traceback__'):
                self.logger.error(traceback.format_exc())
        
        if reraise:
            raise
        
        return error_msg
    
    def safe_execute(self, func: Callable, *args, default_return=None, **kwargs):
        """Safely execute function with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_error(e, f"Safe execution of {func.__name__}", reraise=False)
            return default_return
    
    def get_error_statistics(self) -> Dict[str, int]:
        """Get error statistics"""
        return self.error_counts.copy()

def main():
    """Demo of security and robustness features"""
    import time
    
    print("🔒 SECURITY & ROBUSTNESS DEMO")
    print("=" * 35)
    
    # Test input validation
    print("--- Input Validation ---")
    validator = InputValidator(SecurityLevel.HIGH)
    
    test_sequences = [
        "AUCGAUCGAUCG",           # Valid
        "AUCGXAUCGAUCG",          # Invalid nucleotide
        "AAAA" * 100,             # Suspicious repetition
        "A" * 15000,              # Too long
        "",                       # Empty
    ]
    
    for seq in test_sequences:
        result = validator.validate_dna_sequence(seq)
        status = "✅ VALID" if result.is_valid else "❌ INVALID"
        print(f"  '{seq[:20]}...': {status}")
        if result.errors:
            print(f"    Errors: {result.errors}")
        if result.warnings:
            print(f"    Warnings: {result.warnings}")
    
    # Test secure operations
    print("\n--- Secure Operations ---")
    secure_mgr = SecureOperationManager(SecurityLevel.MEDIUM)
    
    @secure_mgr.secure_operation_wrapper("test_encoding")
    def test_operation(data: str) -> str:
        # Simulate DNA encoding
        if "FAIL" in data:
            raise ValueError("Test failure")
        return f"Encoded: {data}"
    
    # Test successful operation
    try:
        result = test_operation("AUCGAUCG")
        print(f"Success: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test failed operation
    try:
        result = test_operation("FAIL_TEST")
        print(f"Success: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test secure hashing
    print("\n--- Secure Hashing ---")
    test_data = "AUCGAUCGAUCGAUCG"
    hash_value = secure_mgr.create_secure_hash(test_data)
    print(f"Hash created: {hash_value[:32]}...")
    
    # Verify hash
    is_valid = secure_mgr.verify_secure_hash(test_data, hash_value)
    print(f"Hash verification: {'✅ PASS' if is_valid else '❌ FAIL'}")
    
    # Test with wrong data
    is_valid_wrong = secure_mgr.verify_secure_hash("WRONG_DATA", hash_value)
    print(f"Wrong data verification: {'❌ FAIL' if not is_valid_wrong else '✅ UNEXPECTED'}")
    
    # Test error handling
    print("\n--- Error Handling ---")
    error_handler = RobustErrorHandler(log_errors=False)
    
    def failing_function():
        raise ValueError("This function always fails")
    
    # Safe execution
    result = error_handler.safe_execute(failing_function, default_return="SAFE_DEFAULT")
    print(f"Safe execution result: {result}")
    
    # Get error statistics
    stats = error_handler.get_error_statistics()
    print(f"Error statistics: {stats}")
    
    # Test filename sanitization
    print("\n--- Filename Sanitization ---")
    dangerous_names = [
        "../../../etc/passwd",
        "normal_file.dna",
        "file with spaces.dna",
        ".hidden_file",
        "very_long_filename_" + "x" * 200 + ".dna"
    ]
    
    for name in dangerous_names:
        sanitized = secure_mgr.sanitize_filename(name)
        print(f"  '{name[:30]}...' -> '{sanitized}'")
    
    # Test ethics compliance if available
    print("\n--- Ethics Compliance ---")
    ethics_report = secure_mgr.get_ethics_compliance_report()
    if ethics_report.get("status") == "ethics_disabled":
        print("Ethics framework is disabled")
    else:
        print(f"Ethics compliance status: {ethics_report}")
    
    print("\n✅ Security and Ethics demo completed!")

if __name__ == "__main__":
    main()
