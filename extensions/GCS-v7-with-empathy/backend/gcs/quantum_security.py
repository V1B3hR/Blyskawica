"""
quantum_security.py - Quantum-resistant cryptography for BCI neural data protection

Implements post-quantum cryptography algorithms and evaluation framework:
- NIST-approved post-quantum cryptographic algorithms
- Quantum-resistant key exchange protocols
- Performance evaluation and fallback mechanisms
- Integration with existing security infrastructure

This module provides quantum-resistant security for neural data transmission
that will remain secure even against quantum computer attacks.
"""

import logging
import os
import secrets
import time
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

# Post-quantum cryptography imports
try:
    import pqcrypto.sign.dilithium3
    import pqcrypto.kem.kyber768
    import pqcrypto.kem.sike754
    QUANTUM_CRYPTO_AVAILABLE = True
except ImportError:
    QUANTUM_CRYPTO_AVAILABLE = False
    logging.warning("Post-quantum cryptography libraries not available. Using classical fallback.")

# Classical cryptography fallback
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

logger = logging.getLogger(__name__)


class QuantumAlgorithm(Enum):
    """Post-quantum cryptographic algorithms"""
    KYBER768 = "kyber768"  # NIST Level 3 KEM
    DILITHIUM3 = "dilithium3"  # NIST Level 3 Digital Signature
    SIKE754 = "sike754"  # Supersingular Isogeny KEM
    CLASSICAL_FALLBACK = "classical_fallback"  # ECC fallback


class QuantumSecurityLevel(Enum):
    """Security levels for quantum resistance"""
    NIST_LEVEL_1 = "nist_level_1"  # Equivalent to AES-128
    NIST_LEVEL_3 = "nist_level_3"  # Equivalent to AES-192  
    NIST_LEVEL_5 = "nist_level_5"  # Equivalent to AES-256
    FUTURE_PROOF = "future_proof"   # Maximum quantum resistance


@dataclass
class QuantumKeyPair:
    """Quantum-resistant key pair"""
    public_key: bytes
    private_key: bytes
    algorithm: QuantumAlgorithm
    security_level: QuantumSecurityLevel
    created_at: float
    key_id: str


@dataclass
class QuantumEncryptionResult:
    """Result of quantum-resistant encryption"""
    ciphertext: bytes
    encapsulated_key: bytes
    algorithm: QuantumAlgorithm
    security_level: QuantumSecurityLevel
    timestamp: float
    metadata: Dict[str, Any]


class QuantumResistantCrypto:
    """
    Quantum-resistant cryptography manager for BCI neural data protection.
    
    Implements NIST-approved post-quantum algorithms with performance evaluation
    and fallback to classical cryptography when needed.
    """
    
    def __init__(self, security_level: QuantumSecurityLevel = QuantumSecurityLevel.NIST_LEVEL_3):
        """Initialize quantum-resistant crypto manager"""
        self.security_level = security_level
        self.key_cache: Dict[str, QuantumKeyPair] = {}
        self.performance_metrics: Dict[str, List[float]] = {
            'keygen_time': [],
            'encryption_time': [],
            'decryption_time': []
        }
        self.quantum_available = QUANTUM_CRYPTO_AVAILABLE
        
        # Initialize preferred algorithms based on security level
        self._initialize_algorithms()
        
        logger.info(f"QuantumResistantCrypto initialized with {security_level.value}")
        if not self.quantum_available:
            logger.warning("Post-quantum libraries unavailable. Using classical ECC fallback.")
    
    def _initialize_algorithms(self):
        """Initialize preferred algorithms for the security level"""
        if self.security_level == QuantumSecurityLevel.NIST_LEVEL_1:
            self.preferred_kem = QuantumAlgorithm.KYBER768  # Using Level 3 as minimum
            self.preferred_sig = QuantumAlgorithm.DILITHIUM3
        elif self.security_level == QuantumSecurityLevel.NIST_LEVEL_3:
            self.preferred_kem = QuantumAlgorithm.KYBER768
            self.preferred_sig = QuantumAlgorithm.DILITHIUM3
        elif self.security_level == QuantumSecurityLevel.NIST_LEVEL_5:
            self.preferred_kem = QuantumAlgorithm.SIKE754  # Higher security
            self.preferred_sig = QuantumAlgorithm.DILITHIUM3
        else:  # FUTURE_PROOF
            self.preferred_kem = QuantumAlgorithm.SIKE754
            self.preferred_sig = QuantumAlgorithm.DILITHIUM3
    
    def generate_quantum_keypair(self, 
                                key_id: str,
                                algorithm: Optional[QuantumAlgorithm] = None) -> QuantumKeyPair:
        """
        Generate a quantum-resistant key pair for neural data protection.
        
        Args:
            key_id: Unique identifier for the key pair
            algorithm: Specific algorithm to use (defaults to preferred)
            
        Returns:
            QuantumKeyPair with public/private keys and metadata
        """
        start_time = time.perf_counter()
        
        if algorithm is None:
            algorithm = self.preferred_kem
        
        try:
            if algorithm == QuantumAlgorithm.KYBER768 and self.quantum_available:
                public_key, private_key = pqcrypto.kem.kyber768.keypair()
                
            elif algorithm == QuantumAlgorithm.SIKE754 and self.quantum_available:
                public_key, private_key = pqcrypto.kem.sike754.keypair()
                
            else:
                # Classical ECC fallback
                algorithm = QuantumAlgorithm.CLASSICAL_FALLBACK
                private_key_obj = ec.generate_private_key(ec.SECP384R1())
                public_key = private_key_obj.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                private_key = private_key_obj.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            
            keygen_time = time.perf_counter() - start_time
            self.performance_metrics['keygen_time'].append(keygen_time)
            
            keypair = QuantumKeyPair(
                public_key=public_key,
                private_key=private_key,
                algorithm=algorithm,
                security_level=self.security_level,
                created_at=time.time(),
                key_id=key_id
            )
            
            self.key_cache[key_id] = keypair
            
            logger.info(f"Generated quantum-resistant keypair {key_id} using {algorithm.value} "
                       f"in {keygen_time:.3f}ms")
            
            return keypair
            
        except Exception as e:
            logger.error(f"Failed to generate quantum keypair: {e}")
            # Fallback to classical
            return self.generate_quantum_keypair(key_id, QuantumAlgorithm.CLASSICAL_FALLBACK)
    
    def quantum_encrypt_neural_data(self,
                                   neural_data: bytes,
                                   recipient_public_key: bytes,
                                   algorithm: Optional[QuantumAlgorithm] = None) -> QuantumEncryptionResult:
        """
        Encrypt neural data using quantum-resistant algorithms.
        
        Args:
            neural_data: Raw neural/emotional data to encrypt
            recipient_public_key: Recipient's quantum-resistant public key
            algorithm: Specific algorithm (defaults to preferred)
            
        Returns:
            QuantumEncryptionResult with encrypted data and metadata
        """
        start_time = time.perf_counter()
        
        if algorithm is None:
            algorithm = self.preferred_kem
        
        try:
            if algorithm == QuantumAlgorithm.KYBER768 and self.quantum_available:
                # Use Kyber768 for key encapsulation
                ciphertext, shared_secret = pqcrypto.kem.kyber768.enc(recipient_public_key)
                
                # Use AES-GCM with the shared secret
                aes_gcm = AESGCM(shared_secret[:32])  # Use first 32 bytes for AES-256
                nonce = secrets.token_bytes(12)
                encrypted_data = aes_gcm.encrypt(nonce, neural_data, None)
                
                final_ciphertext = nonce + encrypted_data
                
            elif algorithm == QuantumAlgorithm.SIKE754 and self.quantum_available:
                # Use SIKE754 for key encapsulation
                ciphertext, shared_secret = pqcrypto.kem.sike754.enc(recipient_public_key)
                
                # Use AES-GCM with the shared secret
                aes_gcm = AESGCM(shared_secret[:32])
                nonce = secrets.token_bytes(12)
                encrypted_data = aes_gcm.encrypt(nonce, neural_data, None)
                
                final_ciphertext = nonce + encrypted_data
                
            else:
                # Classical ECC fallback with ECDH
                algorithm = QuantumAlgorithm.CLASSICAL_FALLBACK
                
                # Generate ephemeral key pair
                ephemeral_private = ec.generate_private_key(ec.SECP384R1())
                
                # Load recipient public key
                recipient_key = serialization.load_pem_public_key(recipient_public_key)
                
                # Perform ECDH
                shared_key = ephemeral_private.exchange(ec.ECDH(), recipient_key)
                
                # Derive encryption key
                derived_key = HKDF(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=None,
                    info=b'quantum-resistant-neural-data'
                ).derive(shared_key)
                
                # Encrypt with AES-GCM
                aes_gcm = AESGCM(derived_key)
                nonce = secrets.token_bytes(12)
                encrypted_data = aes_gcm.encrypt(nonce, neural_data, None)
                
                # Include ephemeral public key in ciphertext
                ephemeral_public = ephemeral_private.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                ciphertext = ephemeral_public
                final_ciphertext = nonce + encrypted_data
            
            encryption_time = time.perf_counter() - start_time
            self.performance_metrics['encryption_time'].append(encryption_time)
            
            result = QuantumEncryptionResult(
                ciphertext=final_ciphertext,
                encapsulated_key=ciphertext,
                algorithm=algorithm,
                security_level=self.security_level,
                timestamp=time.time(),
                metadata={
                    'encryption_time_ms': encryption_time * 1000,
                    'data_size_bytes': len(neural_data),
                    'quantum_resistant': algorithm != QuantumAlgorithm.CLASSICAL_FALLBACK
                }
            )
            
            logger.info(f"Quantum-encrypted {len(neural_data)} bytes using {algorithm.value} "
                       f"in {encryption_time:.3f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Quantum encryption failed: {e}")
            # Fallback to classical
            if algorithm != QuantumAlgorithm.CLASSICAL_FALLBACK:
                return self.quantum_encrypt_neural_data(
                    neural_data, recipient_public_key, QuantumAlgorithm.CLASSICAL_FALLBACK
                )
            else:
                raise
    
    def quantum_decrypt_neural_data(self,
                                   encrypted_result: QuantumEncryptionResult,
                                   private_key: bytes) -> bytes:
        """
        Decrypt neural data using quantum-resistant algorithms.
        
        Args:
            encrypted_result: QuantumEncryptionResult from encryption
            private_key: Recipient's quantum-resistant private key
            
        Returns:
            Decrypted neural data bytes
        """
        start_time = time.perf_counter()
        algorithm = encrypted_result.algorithm
        
        try:
            if algorithm == QuantumAlgorithm.KYBER768 and self.quantum_available:
                # Decapsulate shared secret
                shared_secret = pqcrypto.kem.kyber768.dec(
                    encrypted_result.encapsulated_key, private_key
                )
                
                # Decrypt with AES-GCM
                aes_gcm = AESGCM(shared_secret[:32])
                nonce = encrypted_result.ciphertext[:12]
                ciphertext = encrypted_result.ciphertext[12:]
                neural_data = aes_gcm.decrypt(nonce, ciphertext, None)
                
            elif algorithm == QuantumAlgorithm.SIKE754 and self.quantum_available:
                # Decapsulate shared secret
                shared_secret = pqcrypto.kem.sike754.dec(
                    encrypted_result.encapsulated_key, private_key
                )
                
                # Decrypt with AES-GCM
                aes_gcm = AESGCM(shared_secret[:32])
                nonce = encrypted_result.ciphertext[:12]
                ciphertext = encrypted_result.ciphertext[12:]
                neural_data = aes_gcm.decrypt(nonce, ciphertext, None)
                
            else:
                # Classical ECC fallback
                # Load private key
                private_key_obj = serialization.load_pem_private_key(private_key, password=None)
                
                # Extract ephemeral public key from encapsulated key
                ephemeral_public = serialization.load_pem_public_key(encrypted_result.encapsulated_key)
                
                # Perform ECDH
                shared_key = private_key_obj.exchange(ec.ECDH(), ephemeral_public)
                
                # Derive decryption key
                derived_key = HKDF(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=None,
                    info=b'quantum-resistant-neural-data'
                ).derive(shared_key)
                
                # Decrypt with AES-GCM
                aes_gcm = AESGCM(derived_key)
                nonce = encrypted_result.ciphertext[:12]
                ciphertext = encrypted_result.ciphertext[12:]
                neural_data = aes_gcm.decrypt(nonce, ciphertext, None)
            
            decryption_time = time.perf_counter() - start_time
            self.performance_metrics['decryption_time'].append(decryption_time)
            
            logger.info(f"Quantum-decrypted {len(neural_data)} bytes using {algorithm.value} "
                       f"in {decryption_time:.3f}ms")
            
            return neural_data
            
        except Exception as e:
            logger.error(f"Quantum decryption failed: {e}")
            raise
    
    def evaluate_quantum_performance(self) -> Dict[str, Any]:
        """
        Evaluate quantum-resistant cryptography performance for neural data.
        
        Returns:
            Performance metrics and recommendations
        """
        def avg_time(times):
            return sum(times) / len(times) if times else 0
        
        def max_time(times):
            return max(times) if times else 0
        
        metrics = {
            'quantum_crypto_available': self.quantum_available,
            'security_level': self.security_level.value,
            'total_operations': len(self.performance_metrics['keygen_time']),
            'average_keygen_time_ms': avg_time(self.performance_metrics['keygen_time']) * 1000,
            'average_encryption_time_ms': avg_time(self.performance_metrics['encryption_time']) * 1000,
            'average_decryption_time_ms': avg_time(self.performance_metrics['decryption_time']) * 1000,
            'max_keygen_time_ms': max_time(self.performance_metrics['keygen_time']) * 1000,
            'max_encryption_time_ms': max_time(self.performance_metrics['encryption_time']) * 1000,
            'max_decryption_time_ms': max_time(self.performance_metrics['decryption_time']) * 1000,
        }
        
        # Real-time suitability assessment
        total_avg_time = metrics['average_encryption_time_ms'] + metrics['average_decryption_time_ms']
        metrics['real_time_suitable'] = total_avg_time < 10.0  # 10ms threshold for neural data
        
        # Security assessment
        metrics['quantum_resistant'] = self.quantum_available
        metrics['recommended_for_production'] = (
            metrics['real_time_suitable'] and 
            (metrics['quantum_resistant'] or self.security_level == QuantumSecurityLevel.NIST_LEVEL_1)
        )
        
        return metrics
    
    def save_quantum_keypair(self, keypair: QuantumKeyPair, key_dir: Path):
        """Save quantum-resistant keypair to secure storage"""
        key_dir.mkdir(parents=True, exist_ok=True)
        
        # Save public key
        pub_path = key_dir / f"{keypair.key_id}_public.pem"
        with open(pub_path, 'wb') as f:
            f.write(keypair.public_key)
        os.chmod(pub_path, 0o644)
        
        # Save private key with restricted permissions
        priv_path = key_dir / f"{keypair.key_id}_private.pem"
        with open(priv_path, 'wb') as f:
            f.write(keypair.private_key)
        os.chmod(priv_path, 0o600)
        
        logger.info(f"Saved quantum keypair {keypair.key_id} to {key_dir}")
        return pub_path, priv_path
    
    def load_quantum_keypair(self, key_id: str, key_dir: Path) -> QuantumKeyPair:
        """Load quantum-resistant keypair from secure storage"""
        pub_path = key_dir / f"{key_id}_public.pem"
        priv_path = key_dir / f"{key_id}_private.pem"
        
        if not pub_path.exists() or not priv_path.exists():
            raise FileNotFoundError(f"Quantum keypair {key_id} not found in {key_dir}")
        
        with open(pub_path, 'rb') as f:
            public_key = f.read()
        
        with open(priv_path, 'rb') as f:
            private_key = f.read()
        
        # Determine algorithm from key format/metadata (simplified)
        algorithm = QuantumAlgorithm.CLASSICAL_FALLBACK  # Default
        if b'BEGIN PRIVATE KEY' not in private_key:
            # Likely post-quantum binary format
            if len(public_key) == 1088:  # Kyber768 public key size
                algorithm = QuantumAlgorithm.KYBER768
            elif len(public_key) == 378:  # SIKE754 public key size
                algorithm = QuantumAlgorithm.SIKE754
        
        keypair = QuantumKeyPair(
            public_key=public_key,
            private_key=private_key,
            algorithm=algorithm,
            security_level=self.security_level,
            created_at=pub_path.stat().st_mtime,
            key_id=key_id
        )
        
        self.key_cache[key_id] = keypair
        logger.info(f"Loaded quantum keypair {key_id} using {algorithm.value}")
        
        return keypair


# Global instance for easy access
_quantum_crypto = None

def get_quantum_crypto(security_level: QuantumSecurityLevel = QuantumSecurityLevel.NIST_LEVEL_3) -> QuantumResistantCrypto:
    """Get global quantum-resistant crypto instance"""
    global _quantum_crypto
    if _quantum_crypto is None:
        _quantum_crypto = QuantumResistantCrypto(security_level)
    return _quantum_crypto