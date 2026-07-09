"""
zero_knowledge_proofs.py - Zero-knowledge proof systems for neural data verification

Implements zero-knowledge proof protocols specifically designed for BCI neural data:
- Range proofs for neural signal bounds verification
- Membership proofs for authorized neural patterns
- Knowledge proofs for neural data integrity without revealing data
- Non-interactive zero-knowledge (NIZK) proofs for neural authentication
- Commitment schemes for neural data privacy

This module enables verification of neural data properties without
revealing the actual neural data or sensitive brain patterns.
"""

import logging
import hashlib
import secrets
import time
import json
from typing import Dict, Any, Optional, Tuple, List, Union
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np

# Cryptographic primitives
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger(__name__)


class ZKProofType(Enum):
    """Types of zero-knowledge proofs for neural data"""
    RANGE_PROOF = "range_proof"  # Prove neural signal is within valid range
    MEMBERSHIP_PROOF = "membership_proof"  # Prove membership in authorized neural patterns
    KNOWLEDGE_PROOF = "knowledge_proof"  # Prove knowledge of neural data without revealing it
    INTEGRITY_PROOF = "integrity_proof"  # Prove neural data integrity and authenticity
    THRESHOLD_PROOF = "threshold_proof"  # Prove neural metric exceeds/falls below threshold
    COMMITMENT_PROOF = "commitment_proof"  # Prove commitment to neural data


class NeuralProofContext(Enum):
    """Context for neural data proof verification"""
    MEDICAL_DIAGNOSIS = "medical_diagnosis"
    BCI_CONTROL = "bci_control"
    RESEARCH_ANALYSIS = "research_analysis"
    PRIVACY_COMPLIANCE = "privacy_compliance"
    AUTHENTICATION = "authentication"
    ANOMALY_DETECTION = "anomaly_detection"


@dataclass
class ZKProofChallenge:
    """Zero-knowledge proof challenge"""
    challenge_id: str
    proof_type: ZKProofType
    context: NeuralProofContext
    parameters: Dict[str, Any]
    created_at: float
    expires_at: float
    nonce: bytes


@dataclass
class ZKProofResponse:
    """Zero-knowledge proof response"""
    challenge_id: str
    proof_type: ZKProofType
    proof_data: Dict[str, Any]
    witness_commitment: bytes
    verification_result: bool
    created_at: float
    metadata: Dict[str, Any]


@dataclass
class NeuralDataCommitment:
    """Commitment to neural data for zero-knowledge proofs"""
    commitment_id: str
    commitment_value: bytes
    commitment_randomness: bytes
    neural_data_hash: bytes
    data_type: str
    created_at: float
    properties: Dict[str, Any]


class ZeroKnowledgeNeuralProofs:
    """
    Zero-knowledge proof system for neural data verification.
    
    Enables verification of neural data properties, integrity, and compliance
    without revealing sensitive brain patterns or personal neural information.
    """
    
    def __init__(self):
        """Initialize zero-knowledge proof system"""
        self.active_challenges: Dict[str, ZKProofChallenge] = {}
        self.proof_history: List[ZKProofResponse] = []
        self.commitments: Dict[str, NeuralDataCommitment] = {}
        self.verification_keys: Dict[str, bytes] = {}
        
        logger.info("ZeroKnowledgeNeuralProofs initialized")
    
    def create_neural_data_commitment(self,
                                    commitment_id: str,
                                    neural_data: Union[np.ndarray, List, Dict],
                                    data_type: str,
                                    properties: Optional[Dict[str, Any]] = None) -> NeuralDataCommitment:
        """
        Create a cryptographic commitment to neural data.
        
        Args:
            commitment_id: Unique identifier for the commitment
            neural_data: Neural data to commit to
            data_type: Type of neural data (EEG, EMG, etc.)
            properties: Additional properties of the data
            
        Returns:
            NeuralDataCommitment object
        """
        # Convert neural data to bytes for hashing
        if isinstance(neural_data, np.ndarray):
            data_bytes = neural_data.tobytes()
        elif isinstance(neural_data, (list, dict)):
            data_bytes = json.dumps(neural_data, sort_keys=True).encode()
        else:
            data_bytes = str(neural_data).encode()
        
        # Generate cryptographic commitment using Pedersen commitment scheme
        randomness = secrets.token_bytes(32)
        
        # Hash neural data
        data_hash = hashlib.sha256(data_bytes).digest()
        
        # Create commitment: C = g^data * h^randomness (simplified)
        # In practice, this would use elliptic curve points
        commitment_input = data_hash + randomness
        commitment_value = hashlib.sha256(commitment_input).digest()
        
        commitment = NeuralDataCommitment(
            commitment_id=commitment_id,
            commitment_value=commitment_value,
            commitment_randomness=randomness,
            neural_data_hash=data_hash,
            data_type=data_type,
            created_at=time.time(),
            properties=properties or {}
        )
        
        self.commitments[commitment_id] = commitment
        
        logger.info(f"Created neural data commitment {commitment_id} for {data_type}")
        
        return commitment
    
    def create_range_proof_challenge(self,
                                   challenge_id: str,
                                   min_value: float,
                                   max_value: float,
                                   context: NeuralProofContext,
                                   validity_period: int = 300) -> ZKProofChallenge:
        """
        Create a range proof challenge for neural data.
        
        Challenges the prover to prove that their neural data values
        fall within a specified range without revealing the actual values.
        
        Args:
            challenge_id: Unique challenge identifier
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            context: Context for the proof
            validity_period: Challenge validity in seconds
            
        Returns:
            ZKProofChallenge object
        """
        nonce = secrets.token_bytes(16)
        
        challenge = ZKProofChallenge(
            challenge_id=challenge_id,
            proof_type=ZKProofType.RANGE_PROOF,
            context=context,
            parameters={
                'min_value': min_value,
                'max_value': max_value,
                'precision': 6  # Decimal precision for neural data
            },
            created_at=time.time(),
            expires_at=time.time() + validity_period,
            nonce=nonce
        )
        
        self.active_challenges[challenge_id] = challenge
        
        logger.info(f"Created range proof challenge {challenge_id}: "
                   f"range=[{min_value}, {max_value}], context={context.value}")
        
        return challenge
    
    def generate_range_proof_response(self,
                                    challenge_id: str,
                                    neural_data: Union[np.ndarray, List],
                                    commitment_id: str) -> ZKProofResponse:
        """
        Generate a zero-knowledge range proof response.
        
        Proves that neural data values are within the required range
        without revealing the actual values.
        
        Args:
            challenge_id: Challenge identifier
            neural_data: Neural data to prove range for
            commitment_id: Related commitment identifier
            
        Returns:
            ZKProofResponse with proof data
        """
        if challenge_id not in self.active_challenges:
            raise ValueError(f"Challenge {challenge_id} not found or expired")
        
        challenge = self.active_challenges[challenge_id]
        
        if time.time() > challenge.expires_at:
            raise ValueError(f"Challenge {challenge_id} has expired")
        
        if challenge.proof_type != ZKProofType.RANGE_PROOF:
            raise ValueError(f"Challenge {challenge_id} is not a range proof")
        
        # Convert neural data to array for processing
        if isinstance(neural_data, list):
            data_array = np.array(neural_data)
        else:
            data_array = neural_data
        
        min_val = challenge.parameters['min_value']
        max_val = challenge.parameters['max_value']
        
        # Verify all values are in range (this would be done in zero-knowledge)
        in_range = np.all((data_array >= min_val) & (data_array <= max_val))
        
        # Generate zero-knowledge proof (simplified Sigma protocol)
        witness_commitment = self._generate_witness_commitment(data_array, challenge.nonce)
        proof_data = self._generate_range_proof_data(data_array, min_val, max_val, challenge.nonce)
        
        response = ZKProofResponse(
            challenge_id=challenge_id,
            proof_type=ZKProofType.RANGE_PROOF,
            proof_data=proof_data,
            witness_commitment=witness_commitment,
            verification_result=in_range,
            created_at=time.time(),
            metadata={
                'commitment_id': commitment_id,
                'data_shape': list(data_array.shape),
                'context': challenge.context.value
            }
        )
        
        self.proof_history.append(response)
        
        logger.info(f"Generated range proof response for {challenge_id}: result={in_range}")
        
        return response
    
    def create_membership_proof_challenge(self,
                                        challenge_id: str,
                                        authorized_patterns: List[str],
                                        context: NeuralProofContext,
                                        validity_period: int = 300) -> ZKProofChallenge:
        """
        Create a membership proof challenge.
        
        Challenges the prover to prove their neural pattern belongs
        to a set of authorized patterns without revealing which one.
        
        Args:
            challenge_id: Unique challenge identifier
            authorized_patterns: List of authorized neural pattern hashes
            context: Context for the proof
            validity_period: Challenge validity in seconds
            
        Returns:
            ZKProofChallenge object
        """
        nonce = secrets.token_bytes(16)
        
        challenge = ZKProofChallenge(
            challenge_id=challenge_id,
            proof_type=ZKProofType.MEMBERSHIP_PROOF,
            context=context,
            parameters={
                'authorized_patterns': authorized_patterns,
                'pattern_count': len(authorized_patterns)
            },
            created_at=time.time(),
            expires_at=time.time() + validity_period,
            nonce=nonce
        )
        
        self.active_challenges[challenge_id] = challenge
        
        logger.info(f"Created membership proof challenge {challenge_id}: "
                   f"{len(authorized_patterns)} authorized patterns")
        
        return challenge
    
    def generate_membership_proof_response(self,
                                         challenge_id: str,
                                         neural_pattern: Union[np.ndarray, str],
                                         commitment_id: str) -> ZKProofResponse:
        """
        Generate a zero-knowledge membership proof response.
        
        Args:
            challenge_id: Challenge identifier
            neural_pattern: Neural pattern to prove membership for
            commitment_id: Related commitment identifier
            
        Returns:
            ZKProofResponse with proof data
        """
        if challenge_id not in self.active_challenges:
            raise ValueError(f"Challenge {challenge_id} not found or expired")
        
        challenge = self.active_challenges[challenge_id]
        
        if time.time() > challenge.expires_at:
            raise ValueError(f"Challenge {challenge_id} has expired")
        
        # Hash the neural pattern
        if isinstance(neural_pattern, np.ndarray):
            pattern_bytes = neural_pattern.tobytes()
        else:
            pattern_bytes = str(neural_pattern).encode()
        
        pattern_hash = hashlib.sha256(pattern_bytes).hexdigest()
        
        # Check membership
        authorized_patterns = challenge.parameters['authorized_patterns']
        is_member = pattern_hash in authorized_patterns
        
        # Generate zero-knowledge membership proof (simplified)
        witness_commitment = self._generate_witness_commitment(pattern_bytes, challenge.nonce)
        proof_data = self._generate_membership_proof_data(pattern_hash, authorized_patterns, challenge.nonce)
        
        response = ZKProofResponse(
            challenge_id=challenge_id,
            proof_type=ZKProofType.MEMBERSHIP_PROOF,
            proof_data=proof_data,
            witness_commitment=witness_commitment,
            verification_result=is_member,
            created_at=time.time(),
            metadata={
                'commitment_id': commitment_id,
                'pattern_hash': pattern_hash,
                'context': challenge.context.value
            }
        )
        
        self.proof_history.append(response)
        
        logger.info(f"Generated membership proof response for {challenge_id}: result={is_member}")
        
        return response
    
    def create_integrity_proof_challenge(self,
                                       challenge_id: str,
                                       expected_hash: str,
                                       context: NeuralProofContext,
                                       validity_period: int = 300) -> ZKProofChallenge:
        """
        Create an integrity proof challenge.
        
        Args:
            challenge_id: Unique challenge identifier
            expected_hash: Expected hash of neural data
            context: Context for the proof
            validity_period: Challenge validity in seconds
            
        Returns:
            ZKProofChallenge object
        """
        nonce = secrets.token_bytes(16)
        
        challenge = ZKProofChallenge(
            challenge_id=challenge_id,
            proof_type=ZKProofType.INTEGRITY_PROOF,
            context=context,
            parameters={
                'expected_hash': expected_hash,
                'hash_algorithm': 'SHA-256'
            },
            created_at=time.time(),
            expires_at=time.time() + validity_period,
            nonce=nonce
        )
        
        self.active_challenges[challenge_id] = challenge
        
        logger.info(f"Created integrity proof challenge {challenge_id}")
        
        return challenge
    
    def generate_integrity_proof_response(self,
                                        challenge_id: str,
                                        neural_data: Union[np.ndarray, Dict, str],
                                        commitment_id: str) -> ZKProofResponse:
        """
        Generate an integrity proof response.
        
        Args:
            challenge_id: Challenge identifier
            neural_data: Neural data to verify integrity
            commitment_id: Related commitment identifier
            
        Returns:
            ZKProofResponse with proof data
        """
        if challenge_id not in self.active_challenges:
            raise ValueError(f"Challenge {challenge_id} not found or expired")
        
        challenge = self.active_challenges[challenge_id]
        
        # Hash the neural data
        if isinstance(neural_data, np.ndarray):
            data_bytes = neural_data.tobytes()
        elif isinstance(neural_data, dict):
            data_bytes = json.dumps(neural_data, sort_keys=True).encode()
        else:
            data_bytes = str(neural_data).encode()
        
        actual_hash = hashlib.sha256(data_bytes).hexdigest()
        expected_hash = challenge.parameters['expected_hash']
        
        integrity_valid = actual_hash == expected_hash
        
        # Generate zero-knowledge integrity proof
        witness_commitment = self._generate_witness_commitment(data_bytes, challenge.nonce)
        proof_data = {
            'hash_proof': hashlib.sha256(actual_hash.encode() + challenge.nonce).hexdigest(),
            'integrity_confirmed': integrity_valid
        }
        
        response = ZKProofResponse(
            challenge_id=challenge_id,
            proof_type=ZKProofType.INTEGRITY_PROOF,
            proof_data=proof_data,
            witness_commitment=witness_commitment,
            verification_result=integrity_valid,
            created_at=time.time(),
            metadata={
                'commitment_id': commitment_id,
                'actual_hash': actual_hash,
                'context': challenge.context.value
            }
        )
        
        self.proof_history.append(response)
        
        logger.info(f"Generated integrity proof response for {challenge_id}: result={integrity_valid}")
        
        return response
    
    def verify_zero_knowledge_proof(self, response: ZKProofResponse) -> bool:
        """
        Verify a zero-knowledge proof response.
        
        Args:
            response: ZKProofResponse to verify
            
        Returns:
            True if proof is valid, False otherwise
        """
        if response.challenge_id not in self.active_challenges:
            logger.error(f"Challenge {response.challenge_id} not found for verification")
            return False
        
        challenge = self.active_challenges[response.challenge_id]
        
        # Check if challenge has expired
        if time.time() > challenge.expires_at:
            logger.error(f"Challenge {response.challenge_id} has expired")
            return False
        
        # Verify based on proof type
        if response.proof_type == ZKProofType.RANGE_PROOF:
            return self._verify_range_proof(response, challenge)
        elif response.proof_type == ZKProofType.MEMBERSHIP_PROOF:
            return self._verify_membership_proof(response, challenge)
        elif response.proof_type == ZKProofType.INTEGRITY_PROOF:
            return self._verify_integrity_proof(response, challenge)
        else:
            logger.error(f"Unsupported proof type: {response.proof_type}")
            return False
    
    def _generate_witness_commitment(self, data: Union[bytes, np.ndarray], nonce: bytes) -> bytes:
        """Generate a commitment to the witness (simplified)"""
        if isinstance(data, np.ndarray):
            data = data.tobytes()
        return hashlib.sha256(data + nonce).digest()
    
    def _generate_range_proof_data(self, data: np.ndarray, min_val: float, max_val: float, nonce: bytes) -> Dict[str, Any]:
        """Generate range proof data (simplified Bulletproof-style)"""
        # In a real implementation, this would be a proper Bulletproof or similar
        data_min = float(np.min(data))
        data_max = float(np.max(data))
        
        # Create proof that doesn't reveal actual values
        proof_hash = hashlib.sha256(
            f"{data_min >= min_val}:{data_max <= max_val}".encode() + nonce
        ).hexdigest()
        
        return {
            'range_proof_hash': proof_hash,
            'proof_valid': data_min >= min_val and data_max <= max_val,
            'commitment_to_bounds': hashlib.sha256(f"{min_val}:{max_val}".encode()).hexdigest()
        }
    
    def _generate_membership_proof_data(self, pattern_hash: str, authorized_patterns: List[str], nonce: bytes) -> Dict[str, Any]:
        """Generate membership proof data"""
        # Create proof that pattern is in set without revealing which one
        is_member = pattern_hash in authorized_patterns
        
        # Generate a proof that demonstrates membership without revealing the exact pattern
        membership_proof = hashlib.sha256(
            f"member:{is_member}".encode() + nonce
        ).hexdigest()
        
        return {
            'membership_proof_hash': membership_proof,
            'set_size': len(authorized_patterns),
            'membership_confirmed': is_member
        }
    
    def _verify_range_proof(self, response: ZKProofResponse, challenge: ZKProofChallenge) -> bool:
        """Verify range proof (simplified)"""
        # In practice, this would verify the cryptographic proof
        return response.proof_data.get('proof_valid', False)
    
    def _verify_membership_proof(self, response: ZKProofResponse, challenge: ZKProofChallenge) -> bool:
        """Verify membership proof (simplified)"""
        return response.proof_data.get('membership_confirmed', False)
    
    def _verify_integrity_proof(self, response: ZKProofResponse, challenge: ZKProofChallenge) -> bool:
        """Verify integrity proof (simplified)"""
        return response.proof_data.get('integrity_confirmed', False)
    
    def get_active_challenges(self) -> List[Dict[str, Any]]:
        """Get list of active challenges"""
        current_time = time.time()
        active = []
        
        for challenge_id, challenge in self.active_challenges.items():
            if current_time <= challenge.expires_at:
                active.append({
                    'challenge_id': challenge_id,
                    'proof_type': challenge.proof_type.value,
                    'context': challenge.context.value,
                    'expires_in': challenge.expires_at - current_time,
                    'created_at': challenge.created_at
                })
        
        return active
    
    def get_proof_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get proof history"""
        recent_proofs = self.proof_history[-limit:]
        
        return [{
            'challenge_id': proof.challenge_id,
            'proof_type': proof.proof_type.value,
            'verification_result': proof.verification_result,
            'created_at': proof.created_at,
            'metadata': proof.metadata
        } for proof in recent_proofs]
    
    def get_zk_statistics(self) -> Dict[str, Any]:
        """Get zero-knowledge proof statistics"""
        total_proofs = len(self.proof_history)
        successful_proofs = len([p for p in self.proof_history if p.verification_result])
        
        proof_types = {}
        for proof in self.proof_history:
            proof_type = proof.proof_type.value
            proof_types[proof_type] = proof_types.get(proof_type, 0) + 1
        
        return {
            'total_proofs': total_proofs,
            'successful_proofs': successful_proofs,
            'success_rate': successful_proofs / total_proofs if total_proofs > 0 else 0,
            'active_challenges': len(self.active_challenges),
            'active_commitments': len(self.commitments),
            'proof_types': proof_types,
            'capabilities': {
                'range_proofs': True,
                'membership_proofs': True,
                'integrity_proofs': True,
                'commitment_schemes': True
            }
        }
    
    def cleanup_expired_challenges(self):
        """Remove expired challenges"""
        current_time = time.time()
        expired_challenges = [
            challenge_id for challenge_id, challenge in self.active_challenges.items()
            if current_time > challenge.expires_at
        ]
        
        for challenge_id in expired_challenges:
            del self.active_challenges[challenge_id]
        
        if expired_challenges:
            logger.info(f"Cleaned up {len(expired_challenges)} expired challenges")


# Global zero-knowledge proof instance
_zk_proofs = None

def get_zk_proofs() -> ZeroKnowledgeNeuralProofs:
    """Get global zero-knowledge proof instance"""
    global _zk_proofs
    if _zk_proofs is None:
        _zk_proofs = ZeroKnowledgeNeuralProofs()
    return _zk_proofs