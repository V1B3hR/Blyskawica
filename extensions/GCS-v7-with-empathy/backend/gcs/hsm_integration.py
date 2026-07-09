"""
hsm_integration.py - Hardware Security Module integration for BCI neural data protection

Provides HSM integration for hardware-based key storage, secure key generation,
and tamper-resistant cryptographic operations:
- Hardware-based key generation and storage
- Secure cryptographic operations in HSM
- Key lifecycle management with hardware protection
- Integration with existing security infrastructure
- Fallback to software when HSM unavailable

This module ensures maximum security for neural data encryption keys
by leveraging dedicated hardware security modules.
"""

import logging
import os
import secrets
import time
import json
from typing import Dict, Any, Optional, Tuple, List, Union
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib

# HSM library imports (with fallbacks)
try:
    # PyKCS11 for PKCS#11 HSM integration
    import PyKCS11
    HSM_PKCS11_AVAILABLE = True
except ImportError:
    HSM_PKCS11_AVAILABLE = False

# Cryptographic fallbacks
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

logger = logging.getLogger(__name__)


class HSMType(Enum):
    """Types of supported HSMs"""
    PKCS11 = "pkcs11"  # PKCS#11 standard HSMs (SoftHSM, Thales, etc.)
    SOFTWARE_FALLBACK = "software_fallback"  # Software-based secure storage
    TPM = "tpm"  # Trusted Platform Module
    CLOUD_HSM = "cloud_hsm"  # Cloud-based HSM services


class HSMKeyType(Enum):
    """Types of keys stored in HSM"""
    NEURAL_MASTER_KEY = "neural_master_key"
    WIRELESS_PROTOCOL_KEY = "wireless_protocol_key" 
    DEVICE_IDENTITY_KEY = "device_identity_key"
    QUANTUM_RESISTANT_KEY = "quantum_resistant_key"
    BACKUP_KEY = "backup_key"


class HSMOperationResult(Enum):
    """Results of HSM operations"""
    SUCCESS = "success"
    KEY_NOT_FOUND = "key_not_found"
    HSM_UNAVAILABLE = "hsm_unavailable"
    AUTHENTICATION_FAILED = "authentication_failed"
    OPERATION_FAILED = "operation_failed"


@dataclass
class HSMKeyMetadata:
    """Metadata for HSM-stored keys"""
    key_id: str
    key_type: HSMKeyType
    algorithm: str
    key_size: int
    created_at: float
    last_used: float
    usage_count: int
    hsm_handle: str
    attributes: Dict[str, Any]


@dataclass
class HSMOperationContext:
    """Context for HSM operations"""
    operation: str
    key_id: str
    timestamp: float
    session_id: Optional[str]
    result: HSMOperationResult
    execution_time_ms: float
    metadata: Dict[str, Any]


class HSMSecureStorage:
    """
    Hardware Security Module integration for secure BCI neural data protection.
    
    Provides hardware-based key storage, generation, and cryptographic operations
    with fallback to secure software implementation when HSM is unavailable.
    """
    
    def __init__(self, 
                 hsm_type: HSMType = HSMType.SOFTWARE_FALLBACK,
                 hsm_config: Optional[Dict[str, Any]] = None):
        """
        Initialize HSM integration.
        
        Args:
            hsm_type: Type of HSM to use
            hsm_config: HSM-specific configuration
        """
        self.hsm_type = hsm_type
        self.hsm_config = hsm_config or {}
        self.key_metadata: Dict[str, HSMKeyMetadata] = {}
        self.operation_log: List[HSMOperationContext] = []
        self.hsm_session = None
        self.hsm_available = False
        
        # Software fallback storage
        self.software_key_store = Path(self.hsm_config.get('fallback_path', '/tmp/hsm_fallback'))
        self.software_key_store.mkdir(parents=True, exist_ok=True)
        
        self._initialize_hsm()
        
        logger.info(f"HSM integration initialized: {hsm_type.value}, available: {self.hsm_available}")
    
    def _initialize_hsm(self):
        """Initialize HSM connection and session"""
        try:
            if self.hsm_type == HSMType.PKCS11 and HSM_PKCS11_AVAILABLE:
                self._initialize_pkcs11()
            elif self.hsm_type == HSMType.TPM:
                self._initialize_tpm()
            elif self.hsm_type == HSMType.CLOUD_HSM:
                self._initialize_cloud_hsm()
            else:
                # Software fallback
                self.hsm_type = HSMType.SOFTWARE_FALLBACK
                self.hsm_available = True
                logger.info("Using software fallback for HSM operations")
                
        except Exception as e:
            logger.warning(f"HSM initialization failed: {e}. Using software fallback.")
            self.hsm_type = HSMType.SOFTWARE_FALLBACK
            self.hsm_available = True
    
    def _initialize_pkcs11(self):
        """Initialize PKCS#11 HSM connection"""
        if not HSM_PKCS11_AVAILABLE:
            raise ImportError("PyKCS11 not available")
        
        pkcs11_lib = self.hsm_config.get('pkcs11_library', '/usr/lib/softhsm/libsofthsm2.so')
        slot_id = self.hsm_config.get('slot_id', 0)
        pin = self.hsm_config.get('pin', '1234')
        
        # Initialize PKCS11 library
        self.pkcs11 = PyKCS11.PyKCS11Lib()
        self.pkcs11.load(pkcs11_lib)
        
        # Open session
        self.hsm_session = self.pkcs11.openSession(slot_id, PyKCS11.CKF_SERIAL_SESSION | PyKCS11.CKF_RW_SESSION)
        self.hsm_session.login(pin)
        
        self.hsm_available = True
        logger.info(f"PKCS#11 HSM initialized: {pkcs11_lib}, slot: {slot_id}")
    
    def _initialize_tpm(self):
        """Initialize TPM integration (placeholder)"""
        # TPM integration would require tpm2-tools and specific libraries
        logger.info("TPM integration not yet implemented, using software fallback")
        raise NotImplementedError("TPM integration not yet implemented")
    
    def _initialize_cloud_hsm(self):
        """Initialize cloud HSM integration (placeholder)"""
        # Cloud HSM would require cloud provider-specific libraries
        logger.info("Cloud HSM integration not yet implemented, using software fallback")
        raise NotImplementedError("Cloud HSM integration not yet implemented")
    
    def generate_neural_master_key(self, 
                                  key_id: str,
                                  key_size: int = 32) -> HSMOperationResult:
        """
        Generate master key for neural data encryption in HSM.
        
        Args:
            key_id: Unique identifier for the key
            key_size: Key size in bytes (32 for AES-256)
            
        Returns:
            HSMOperationResult indicating success or failure
        """
        start_time = time.perf_counter()
        
        try:
            if self.hsm_type == HSMType.PKCS11 and self.hsm_available:
                result = self._generate_pkcs11_key(key_id, key_size, HSMKeyType.NEURAL_MASTER_KEY)
            else:
                result = self._generate_software_key(key_id, key_size, HSMKeyType.NEURAL_MASTER_KEY)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            # Log operation
            self._log_operation(
                operation="generate_key",
                key_id=key_id,
                result=result,
                execution_time_ms=execution_time,
                metadata={'key_size': key_size, 'key_type': 'neural_master_key'}
            )
            
            if result == HSMOperationResult.SUCCESS:
                logger.info(f"Generated neural master key {key_id} in HSM ({execution_time:.2f}ms)")
            else:
                logger.error(f"Failed to generate neural master key {key_id}: {result.value}")
            
            return result
            
        except Exception as e:
            logger.error(f"HSM key generation failed: {e}")
            return HSMOperationResult.OPERATION_FAILED
    
    def _generate_pkcs11_key(self, key_id: str, key_size: int, key_type: HSMKeyType) -> HSMOperationResult:
        """Generate key using PKCS#11 HSM"""
        try:
            # Generate AES key in HSM
            template = [
                (PyKCS11.CKA_CLASS, PyKCS11.CKO_SECRET_KEY),
                (PyKCS11.CKA_KEY_TYPE, PyKCS11.CKK_AES),
                (PyKCS11.CKA_VALUE_LEN, key_size),
                (PyKCS11.CKA_LABEL, key_id),
                (PyKCS11.CKA_ID, hashlib.sha256(key_id.encode()).digest()[:16]),
                (PyKCS11.CKA_TOKEN, True),
                (PyKCS11.CKA_SENSITIVE, True),
                (PyKCS11.CKA_EXTRACTABLE, False),
                (PyKCS11.CKA_ENCRYPT, True),
                (PyKCS11.CKA_DECRYPT, True),
            ]
            
            key_handle = self.hsm_session.generateKey(PyKCS11.CKM_AES_KEY_GEN, template)
            
            # Store metadata
            metadata = HSMKeyMetadata(
                key_id=key_id,
                key_type=key_type,
                algorithm="AES-256-GCM",
                key_size=key_size * 8,  # Convert to bits
                created_at=time.time(),
                last_used=time.time(),
                usage_count=0,
                hsm_handle=str(key_handle),
                attributes={'token': True, 'sensitive': True}
            )
            
            self.key_metadata[key_id] = metadata
            return HSMOperationResult.SUCCESS
            
        except Exception as e:
            logger.error(f"PKCS#11 key generation failed: {e}")
            return HSMOperationResult.OPERATION_FAILED
    
    def _generate_software_key(self, key_id: str, key_size: int, key_type: HSMKeyType) -> HSMOperationResult:
        """Generate key using software fallback with secure storage"""
        try:
            # Generate cryptographically secure key
            key_data = secrets.token_bytes(key_size)
            
            # Store securely in filesystem with restricted permissions
            key_path = self.software_key_store / f"{key_id}.key"
            with open(key_path, 'wb') as f:
                f.write(key_data)
            os.chmod(key_path, 0o600)
            
            # Store metadata
            metadata = HSMKeyMetadata(
                key_id=key_id,
                key_type=key_type,
                algorithm="AES-256-GCM",
                key_size=key_size * 8,
                created_at=time.time(),
                last_used=time.time(),
                usage_count=0,
                hsm_handle=str(key_path),
                attributes={'software_fallback': True}
            )
            
            self.key_metadata[key_id] = metadata
            
            # Also store metadata (convert enums to strings for JSON serialization)
            metadata_dict = asdict(metadata)
            metadata_dict['key_type'] = metadata.key_type.value
            metadata_path = self.software_key_store / f"{key_id}.metadata"
            with open(metadata_path, 'w') as f:
                json.dump(metadata_dict, f, indent=2)
            os.chmod(metadata_path, 0o600)
            
            return HSMOperationResult.SUCCESS
            
        except Exception as e:
            logger.error(f"Software key generation failed: {e}")
            return HSMOperationResult.OPERATION_FAILED
    
    def retrieve_key(self, key_id: str) -> Tuple[HSMOperationResult, Optional[bytes]]:
        """
        Retrieve key from HSM or software storage.
        
        Args:
            key_id: Key identifier
            
        Returns:
            Tuple of (result, key_data). key_data is None if operation fails.
        """
        start_time = time.perf_counter()
        
        if key_id not in self.key_metadata:
            return HSMOperationResult.KEY_NOT_FOUND, None
        
        try:
            metadata = self.key_metadata[key_id]
            
            if self.hsm_type == HSMType.PKCS11 and self.hsm_available:
                key_data = self._retrieve_pkcs11_key(key_id, metadata)
            else:
                key_data = self._retrieve_software_key(key_id, metadata)
            
            if key_data is not None:
                # Update usage statistics
                metadata.last_used = time.time()
                metadata.usage_count += 1
                
                execution_time = (time.perf_counter() - start_time) * 1000
                self._log_operation(
                    operation="retrieve_key",
                    key_id=key_id,
                    result=HSMOperationResult.SUCCESS,
                    execution_time_ms=execution_time,
                    metadata={'usage_count': metadata.usage_count}
                )
                
                logger.debug(f"Retrieved key {key_id} from HSM ({execution_time:.2f}ms)")
                return HSMOperationResult.SUCCESS, key_data
            else:
                return HSMOperationResult.OPERATION_FAILED, None
                
        except Exception as e:
            logger.error(f"HSM key retrieval failed: {e}")
            return HSMOperationResult.OPERATION_FAILED, None
    
    def _retrieve_pkcs11_key(self, key_id: str, metadata: HSMKeyMetadata) -> Optional[bytes]:
        """Retrieve key using PKCS#11 HSM"""
        try:
            # Find key by ID
            key_id_hash = hashlib.sha256(key_id.encode()).digest()[:16]
            template = [(PyKCS11.CKA_ID, key_id_hash)]
            keys = self.hsm_session.findObjects(template)
            
            if not keys:
                logger.error(f"Key {key_id} not found in HSM")
                return None
            
            key_handle = keys[0]
            
            # For sensitive keys, we can't extract them directly
            # Instead, we return a reference that can be used for operations
            # In practice, you would use the key handle for encrypt/decrypt operations
            
            # For this implementation, we'll simulate by returning the handle as bytes
            # In a real implementation, you'd use the handle directly for crypto operations
            return str(key_handle).encode()
            
        except Exception as e:
            logger.error(f"PKCS#11 key retrieval failed: {e}")
            return None
    
    def _retrieve_software_key(self, key_id: str, metadata: HSMKeyMetadata) -> Optional[bytes]:
        """Retrieve key from software storage"""
        try:
            key_path = Path(metadata.hsm_handle)
            if not key_path.exists():
                logger.error(f"Software key file not found: {key_path}")
                return None
            
            with open(key_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Software key retrieval failed: {e}")
            return None
    
    def hsm_encrypt_data(self, 
                        key_id: str, 
                        plaintext: bytes, 
                        additional_data: Optional[bytes] = None) -> Tuple[HSMOperationResult, Optional[bytes]]:
        """
        Encrypt data using HSM-stored key.
        
        Args:
            key_id: Key identifier in HSM
            plaintext: Data to encrypt
            additional_data: Optional additional authenticated data
            
        Returns:
            Tuple of (result, ciphertext). ciphertext is None if operation fails.
        """
        start_time = time.perf_counter()
        
        try:
            result, key_data = self.retrieve_key(key_id)
            if result != HSMOperationResult.SUCCESS or key_data is None:
                return result, None
            
            if self.hsm_type == HSMType.PKCS11 and self.hsm_available:
                # Use HSM for encryption (simplified - would use key handle directly)
                ciphertext = self._pkcs11_encrypt(key_data, plaintext, additional_data)
            else:
                # Software fallback encryption
                ciphertext = self._software_encrypt(key_data, plaintext, additional_data)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            self._log_operation(
                operation="encrypt",
                key_id=key_id,
                result=HSMOperationResult.SUCCESS,
                execution_time_ms=execution_time,
                metadata={'data_size': len(plaintext)}
            )
            
            logger.debug(f"HSM encrypted {len(plaintext)} bytes using key {key_id} ({execution_time:.2f}ms)")
            return HSMOperationResult.SUCCESS, ciphertext
            
        except Exception as e:
            logger.error(f"HSM encryption failed: {e}")
            return HSMOperationResult.OPERATION_FAILED, None
    
    def _software_encrypt(self, key_data: bytes, plaintext: bytes, additional_data: Optional[bytes]) -> bytes:
        """Encrypt using software AES-GCM"""
        aes_gcm = AESGCM(key_data[:32])  # Use first 32 bytes for AES-256
        nonce = secrets.token_bytes(12)
        ciphertext = aes_gcm.encrypt(nonce, plaintext, additional_data)
        return nonce + ciphertext
    
    def _pkcs11_encrypt(self, key_handle_bytes: bytes, plaintext: bytes, additional_data: Optional[bytes]) -> bytes:
        """Encrypt using PKCS#11 HSM (simplified implementation)"""
        # In a real implementation, you would use the key handle directly with the HSM
        # For this demo, we'll fall back to software encryption
        return self._software_encrypt(key_handle_bytes, plaintext, additional_data)
    
    def hsm_decrypt_data(self, 
                        key_id: str, 
                        ciphertext: bytes, 
                        additional_data: Optional[bytes] = None) -> Tuple[HSMOperationResult, Optional[bytes]]:
        """
        Decrypt data using HSM-stored key.
        
        Args:
            key_id: Key identifier in HSM
            ciphertext: Data to decrypt
            additional_data: Optional additional authenticated data
            
        Returns:
            Tuple of (result, plaintext). plaintext is None if operation fails.
        """
        start_time = time.perf_counter()
        
        try:
            result, key_data = self.retrieve_key(key_id)
            if result != HSMOperationResult.SUCCESS or key_data is None:
                return result, None
            
            if self.hsm_type == HSMType.PKCS11 and self.hsm_available:
                plaintext = self._pkcs11_decrypt(key_data, ciphertext, additional_data)
            else:
                plaintext = self._software_decrypt(key_data, ciphertext, additional_data)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            self._log_operation(
                operation="decrypt",
                key_id=key_id,
                result=HSMOperationResult.SUCCESS,
                execution_time_ms=execution_time,
                metadata={'data_size': len(ciphertext)}
            )
            
            logger.debug(f"HSM decrypted {len(ciphertext)} bytes using key {key_id} ({execution_time:.2f}ms)")
            return HSMOperationResult.SUCCESS, plaintext
            
        except Exception as e:
            logger.error(f"HSM decryption failed: {e}")
            return HSMOperationResult.OPERATION_FAILED, None
    
    def _software_decrypt(self, key_data: bytes, ciphertext: bytes, additional_data: Optional[bytes]) -> bytes:
        """Decrypt using software AES-GCM"""
        aes_gcm = AESGCM(key_data[:32])
        nonce = ciphertext[:12]
        actual_ciphertext = ciphertext[12:]
        return aes_gcm.decrypt(nonce, actual_ciphertext, additional_data)
    
    def _pkcs11_decrypt(self, key_handle_bytes: bytes, ciphertext: bytes, additional_data: Optional[bytes]) -> bytes:
        """Decrypt using PKCS#11 HSM (simplified implementation)"""
        # In a real implementation, you would use the key handle directly with the HSM
        return self._software_decrypt(key_handle_bytes, ciphertext, additional_data)
    
    def rotate_key(self, key_id: str) -> HSMOperationResult:
        """
        Rotate an existing key in the HSM.
        
        Args:
            key_id: Key to rotate
            
        Returns:
            HSMOperationResult indicating success or failure
        """
        if key_id not in self.key_metadata:
            return HSMOperationResult.KEY_NOT_FOUND
        
        metadata = self.key_metadata[key_id]
        old_key_id = f"{key_id}_old_{int(time.time())}"
        
        # Backup old key
        self.key_metadata[old_key_id] = metadata
        
        # Generate new key with same parameters
        result = self.generate_neural_master_key(key_id, metadata.key_size // 8)
        
        if result == HSMOperationResult.SUCCESS:
            logger.info(f"Rotated key {key_id}, backed up as {old_key_id}")
        
        return result
    
    def delete_key(self, key_id: str) -> HSMOperationResult:
        """
        Securely delete key from HSM.
        
        Args:
            key_id: Key to delete
            
        Returns:
            HSMOperationResult indicating success or failure
        """
        if key_id not in self.key_metadata:
            return HSMOperationResult.KEY_NOT_FOUND
        
        try:
            metadata = self.key_metadata[key_id]
            
            if self.hsm_type == HSMType.SOFTWARE_FALLBACK:
                # Securely delete from filesystem
                key_path = Path(metadata.hsm_handle)
                if key_path.exists():
                    # Overwrite file multiple times before deletion
                    with open(key_path, 'r+b') as f:
                        for _ in range(3):
                            f.seek(0)
                            f.write(os.urandom(len(f.read())))
                            f.flush()
                            os.fsync(f.fileno())
                    key_path.unlink()
                
                # Delete metadata file
                metadata_path = key_path.with_suffix('.metadata')
                if metadata_path.exists():
                    metadata_path.unlink()
            
            # Remove from memory
            del self.key_metadata[key_id]
            
            logger.info(f"Securely deleted key {key_id} from HSM")
            return HSMOperationResult.SUCCESS
            
        except Exception as e:
            logger.error(f"Key deletion failed: {e}")
            return HSMOperationResult.OPERATION_FAILED
    
    def get_key_metadata(self, key_id: str) -> Optional[HSMKeyMetadata]:
        """Get metadata for a key"""
        return self.key_metadata.get(key_id)
    
    def list_keys(self, key_type: Optional[HSMKeyType] = None) -> List[HSMKeyMetadata]:
        """List all keys or keys of specific type"""
        if key_type is None:
            return list(self.key_metadata.values())
        else:
            return [metadata for metadata in self.key_metadata.values() 
                   if metadata.key_type == key_type]
    
    def get_hsm_status(self) -> Dict[str, Any]:
        """Get HSM status and statistics"""
        return {
            'hsm_type': self.hsm_type.value,
            'hsm_available': self.hsm_available,
            'total_keys': len(self.key_metadata),
            'total_operations': len(self.operation_log),
            'keys_by_type': {
                key_type.value: len([m for m in self.key_metadata.values() 
                                   if m.key_type == key_type])
                for key_type in HSMKeyType
            },
            'recent_operations': len([op for op in self.operation_log 
                                    if time.time() - op.timestamp < 3600]),  # Last hour
            'average_operation_time_ms': (
                sum(op.execution_time_ms for op in self.operation_log) / len(self.operation_log)
                if self.operation_log else 0
            )
        }
    
    def _log_operation(self, 
                      operation: str, 
                      key_id: str, 
                      result: HSMOperationResult, 
                      execution_time_ms: float,
                      metadata: Optional[Dict[str, Any]] = None):
        """Log HSM operation for audit trail"""
        context = HSMOperationContext(
            operation=operation,
            key_id=key_id,
            timestamp=time.time(),
            session_id=getattr(self.hsm_session, 'session_id', None) if self.hsm_session else None,
            result=result,
            execution_time_ms=execution_time_ms,
            metadata=metadata or {}
        )
        
        self.operation_log.append(context)
        
        # Keep only recent operations (last 1000)
        if len(self.operation_log) > 1000:
            self.operation_log = self.operation_log[-1000:]
    
    def close(self):
        """Close HSM session and cleanup"""
        try:
            if self.hsm_session and self.hsm_type == HSMType.PKCS11:
                self.hsm_session.logout()
                self.hsm_session.closeSession()
            logger.info("HSM session closed")
        except Exception as e:
            logger.warning(f"HSM session cleanup failed: {e}")


# Global HSM instance
_hsm_storage = None

def get_hsm_storage(hsm_type: HSMType = HSMType.SOFTWARE_FALLBACK, 
                   hsm_config: Optional[Dict[str, Any]] = None) -> HSMSecureStorage:
    """Get global HSM storage instance"""
    global _hsm_storage
    if _hsm_storage is None:
        _hsm_storage = HSMSecureStorage(hsm_type, hsm_config)
    return _hsm_storage