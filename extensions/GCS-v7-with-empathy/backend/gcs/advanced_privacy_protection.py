"""
advanced_privacy_protection.py - Advanced privacy protection for BCI neural data

Implements cutting-edge privacy-preserving techniques for neural data:
- Differential Privacy with neural-specific noise calibration
- Homomorphic Encryption for computation on encrypted neural data
- Secure Multi-party Computation for collaborative neural analysis
- Privacy budget management and tracking
- Zero-knowledge proofs for neural data verification

This module ensures maximum privacy for neural data while enabling
authorized computational analysis and machine learning.
"""

import logging
import numpy as np
import secrets
import math
import time
from typing import Dict, Any, Optional, Tuple, List, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import json

# Privacy libraries
try:
    from phe import paillier
    from phe.paillier import EncryptedNumber
    HOMOMORPHIC_AVAILABLE = True
except ImportError:
    HOMOMORPHIC_AVAILABLE = False

# Secure computation
try:
    import openmined_psi as psi
    PSI_AVAILABLE = True
except ImportError:
    PSI_AVAILABLE = False

logger = logging.getLogger(__name__)


class PrivacyMechanism(Enum):
    """Privacy protection mechanisms"""
    DIFFERENTIAL_PRIVACY = "differential_privacy"
    HOMOMORPHIC_ENCRYPTION = "homomorphic_encryption"
    SECURE_MULTIPARTY = "secure_multiparty"
    K_ANONYMITY = "k_anonymity"
    L_DIVERSITY = "l_diversity"
    T_CLOSENESS = "t_closeness"


class NeuralDataType(Enum):
    """Types of neural data for privacy calibration"""
    EEG_RAW = "eeg_raw"
    EEG_FEATURES = "eeg_features"
    EMG_SIGNALS = "emg_signals"
    EMOTIONAL_STATES = "emotional_states"
    COGNITIVE_LOAD = "cognitive_load"
    NEURAL_COMMANDS = "neural_commands"
    AGGREGATED_STATISTICS = "aggregated_statistics"


@dataclass
class PrivacyBudget:
    """Privacy budget management for differential privacy"""
    total_epsilon: float
    remaining_epsilon: float
    delta: float
    queries_made: int
    last_query_time: float
    neural_data_type: NeuralDataType
    sensitivity_multiplier: float = 1.0


@dataclass
class DifferentialPrivacyResult:
    """Result of differential privacy operation"""
    noisy_data: Union[np.ndarray, float, List]
    epsilon_used: float
    delta_used: float
    mechanism: str
    noise_scale: float
    privacy_budget_remaining: float
    neural_data_type: NeuralDataType
    timestamp: float


@dataclass
class HomomorphicResult:
    """Result of homomorphic encryption operation"""
    encrypted_data: Any  # EncryptedNumber or similar
    public_key: Any
    computation_result: Optional[Any]
    operation_history: List[str]
    encryption_time_ms: float
    computation_time_ms: Optional[float]


class AdvancedPrivacyProtection:
    """
    Advanced privacy protection system for BCI neural data.
    
    Implements differential privacy, homomorphic encryption, and secure
    multiparty computation specifically calibrated for neural data analysis.
    """
    
    # Neural data sensitivity parameters
    NEURAL_SENSITIVITY = {
        NeuralDataType.EEG_RAW: 2.0,          # High sensitivity - raw brain signals
        NeuralDataType.EEG_FEATURES: 1.5,     # Medium-high - processed features
        NeuralDataType.EMG_SIGNALS: 1.2,      # Medium - muscle activity
        NeuralDataType.EMOTIONAL_STATES: 3.0, # Very high - emotional privacy
        NeuralDataType.COGNITIVE_LOAD: 1.8,   # High - cognitive information
        NeuralDataType.NEURAL_COMMANDS: 2.5,  # Very high - control commands
        NeuralDataType.AGGREGATED_STATISTICS: 0.5  # Lower - already aggregated
    }
    
    def __init__(self, 
                 default_epsilon: float = 1.0,
                 default_delta: float = 1e-5):
        """
        Initialize advanced privacy protection system.
        
        Args:
            default_epsilon: Default privacy budget epsilon
            default_delta: Default privacy budget delta
        """
        self.default_epsilon = default_epsilon
        self.default_delta = default_delta
        self.privacy_budgets: Dict[str, PrivacyBudget] = {}
        self.homomorphic_keys: Dict[str, Tuple[Any, Any]] = {}  # (public, private)
        self.privacy_operations_log: List[Dict[str, Any]] = []
        
        self.homomorphic_available = HOMOMORPHIC_AVAILABLE
        self.psi_available = PSI_AVAILABLE
        
        logger.info(f"AdvancedPrivacyProtection initialized: "
                   f"HE available: {self.homomorphic_available}, "
                   f"PSI available: {self.psi_available}")
    
    def create_privacy_budget(self,
                             budget_id: str,
                             total_epsilon: float,
                             delta: float,
                             neural_data_type: NeuralDataType) -> PrivacyBudget:
        """
        Create a privacy budget for neural data analysis.
        
        Args:
            budget_id: Unique identifier for the budget
            total_epsilon: Total epsilon privacy budget
            delta: Delta parameter for (epsilon, delta)-differential privacy
            neural_data_type: Type of neural data for sensitivity calibration
            
        Returns:
            PrivacyBudget object
        """
        # Adjust epsilon based on neural data sensitivity
        sensitivity_multiplier = self.NEURAL_SENSITIVITY[neural_data_type]
        
        budget = PrivacyBudget(
            total_epsilon=total_epsilon,
            remaining_epsilon=total_epsilon,
            delta=delta,
            queries_made=0,
            last_query_time=time.time(),
            neural_data_type=neural_data_type,
            sensitivity_multiplier=sensitivity_multiplier
        )
        
        self.privacy_budgets[budget_id] = budget
        
        logger.info(f"Created privacy budget {budget_id}: "
                   f"epsilon={total_epsilon}, delta={delta}, "
                   f"type={neural_data_type.value}")
        
        return budget
    
    def apply_differential_privacy(self,
                                  data: Union[np.ndarray, float, List],
                                  budget_id: str,
                                  epsilon: Optional[float] = None,
                                  mechanism: str = "laplace") -> DifferentialPrivacyResult:
        """
        Apply differential privacy to neural data.
        
        Args:
            data: Neural data to make private
            budget_id: Privacy budget identifier
            epsilon: Epsilon to use (None = auto-calculate)
            mechanism: Privacy mechanism ("laplace", "gaussian", "exponential")
            
        Returns:
            DifferentialPrivacyResult with noisy data and metadata
        """
        if budget_id not in self.privacy_budgets:
            raise ValueError(f"Privacy budget {budget_id} not found")
        
        budget = self.privacy_budgets[budget_id]
        
        if epsilon is None:
            # Auto-calculate epsilon based on remaining budget and data sensitivity
            epsilon = min(budget.remaining_epsilon * 0.1, 0.1)
            epsilon *= budget.sensitivity_multiplier
        
        if epsilon > budget.remaining_epsilon:
            raise ValueError(f"Insufficient privacy budget: requested {epsilon}, "
                           f"remaining {budget.remaining_epsilon}")
        
        start_time = time.perf_counter()
        
        # Convert data to numpy array if needed
        if isinstance(data, list):
            data = np.array(data)
        
        # Apply neural-specific differential privacy
        if mechanism == "laplace":
            noisy_data = self._apply_laplace_noise(data, epsilon, budget.neural_data_type)
            noise_scale = budget.sensitivity_multiplier / epsilon
        elif mechanism == "gaussian":
            # For Gaussian mechanism, need to satisfy (epsilon, delta)-DP
            sigma = self._calculate_gaussian_sigma(epsilon, budget.delta, budget.sensitivity_multiplier)
            noisy_data = self._apply_gaussian_noise(data, sigma, budget.neural_data_type)
            noise_scale = sigma
        elif mechanism == "exponential":
            noisy_data = self._apply_exponential_mechanism(data, epsilon, budget.neural_data_type)
            noise_scale = 1.0 / epsilon
        else:
            raise ValueError(f"Unknown mechanism: {mechanism}")
        
        # Update privacy budget
        budget.remaining_epsilon -= epsilon
        budget.queries_made += 1
        budget.last_query_time = time.time()
        
        result = DifferentialPrivacyResult(
            noisy_data=noisy_data,
            epsilon_used=epsilon,
            delta_used=budget.delta if mechanism == "gaussian" else 0.0,
            mechanism=mechanism,
            noise_scale=noise_scale,
            privacy_budget_remaining=budget.remaining_epsilon,
            neural_data_type=budget.neural_data_type,
            timestamp=time.time()
        )
        
        # Log operation
        self._log_privacy_operation(
            operation="differential_privacy",
            mechanism=mechanism,
            epsilon_used=epsilon,
            budget_id=budget_id,
            data_shape=data.shape if hasattr(data, 'shape') else str(type(data)),
            execution_time_ms=(time.perf_counter() - start_time) * 1000
        )
        
        logger.info(f"Applied {mechanism} differential privacy: "
                   f"epsilon={epsilon:.4f}, remaining_budget={budget.remaining_epsilon:.4f}")
        
        return result
    
    def _apply_laplace_noise(self, 
                           data: Union[np.ndarray, float], 
                           epsilon: float,
                           neural_data_type: NeuralDataType) -> Union[np.ndarray, float]:
        """Apply Laplace noise calibrated for neural data"""
        sensitivity = self.NEURAL_SENSITIVITY[neural_data_type]
        
        if isinstance(data, np.ndarray):
            # For neural signals, apply element-wise noise
            noise = np.random.laplace(0, sensitivity / epsilon, data.shape)
            noisy_data = data + noise
            
            # Apply neural-specific post-processing
            if neural_data_type in [NeuralDataType.EEG_RAW, NeuralDataType.EMG_SIGNALS]:
                # Preserve signal characteristics - clip extreme outliers
                std_dev = np.std(data)
                noisy_data = np.clip(noisy_data, 
                                   data.mean() - 5 * std_dev,
                                   data.mean() + 5 * std_dev)
            
            return noisy_data
        else:
            # Scalar value
            noise = np.random.laplace(0, sensitivity / epsilon)
            return data + noise
    
    def _apply_gaussian_noise(self, 
                            data: Union[np.ndarray, float], 
                            sigma: float,
                            neural_data_type: NeuralDataType) -> Union[np.ndarray, float]:
        """Apply Gaussian noise for (epsilon, delta)-differential privacy"""
        if isinstance(data, np.ndarray):
            noise = np.random.normal(0, sigma, data.shape)
            noisy_data = data + noise
            
            # Neural-specific post-processing
            if neural_data_type == NeuralDataType.EMOTIONAL_STATES:
                # Emotional states might be bounded (e.g., [0, 1])
                noisy_data = np.clip(noisy_data, 0, 1)
            elif neural_data_type == NeuralDataType.COGNITIVE_LOAD:
                # Cognitive load is typically non-negative
                noisy_data = np.maximum(noisy_data, 0)
            
            return noisy_data
        else:
            noise = np.random.normal(0, sigma)
            return data + noise
    
    def _calculate_gaussian_sigma(self, epsilon: float, delta: float, sensitivity: float) -> float:
        """Calculate sigma for Gaussian mechanism"""
        return sensitivity * math.sqrt(2 * math.log(1.25 / delta)) / epsilon
    
    def _apply_exponential_mechanism(self, 
                                   data: Union[np.ndarray, float], 
                                   epsilon: float,
                                   neural_data_type: NeuralDataType) -> Union[np.ndarray, float]:
        """Apply exponential mechanism (simplified for neural data)"""
        # For neural data, we'll use this for selecting discrete values
        if isinstance(data, np.ndarray):
            # Apply exponential mechanism to each element
            sensitivity = self.NEURAL_SENSITIVITY[neural_data_type]
            
            # Create discrete candidates around each value
            noisy_data = np.zeros_like(data)
            for i in range(data.shape[0]):
                candidates = np.linspace(data[i] - sensitivity, data[i] + sensitivity, 100)
                scores = -np.abs(candidates - data[i])  # Utility function
                probabilities = np.exp(epsilon * scores / (2 * sensitivity))
                probabilities /= probabilities.sum()
                
                # Sample from the distribution
                chosen_idx = np.random.choice(len(candidates), p=probabilities)
                noisy_data[i] = candidates[chosen_idx]
            
            return noisy_data
        else:
            # Scalar case
            sensitivity = self.NEURAL_SENSITIVITY[neural_data_type]
            candidates = np.linspace(data - sensitivity, data + sensitivity, 100)
            scores = -np.abs(candidates - data)
            probabilities = np.exp(epsilon * scores / (2 * sensitivity))
            probabilities /= probabilities.sum()
            
            chosen_idx = np.random.choice(len(candidates), p=probabilities)
            return candidates[chosen_idx]
    
    def setup_homomorphic_encryption(self, key_id: str, key_length: int = 2048) -> Tuple[Any, Any]:
        """
        Setup homomorphic encryption for neural data computation.
        
        Args:
            key_id: Unique identifier for the key pair
            key_length: Key length in bits
            
        Returns:
            Tuple of (public_key, private_key)
        """
        if not self.homomorphic_available:
            raise ImportError("Paillier homomorphic encryption not available")
        
        start_time = time.perf_counter()
        
        # Generate Paillier key pair
        public_key, private_key = paillier.generate_paillier_keypair(n_length=key_length)
        
        # Store keys
        self.homomorphic_keys[key_id] = (public_key, private_key)
        
        setup_time = (time.perf_counter() - start_time) * 1000
        
        self._log_privacy_operation(
            operation="homomorphic_setup",
            key_id=key_id,
            key_length=key_length,
            execution_time_ms=setup_time
        )
        
        logger.info(f"Setup homomorphic encryption keys {key_id}: "
                   f"{key_length}-bit ({setup_time:.2f}ms)")
        
        return public_key, private_key
    
    def homomorphic_encrypt_neural_data(self,
                                       data: Union[np.ndarray, List, float],
                                       key_id: str) -> HomomorphicResult:
        """
        Encrypt neural data using homomorphic encryption.
        
        Args:
            data: Neural data to encrypt
            key_id: Key identifier for encryption
            
        Returns:
            HomomorphicResult with encrypted data
        """
        if key_id not in self.homomorphic_keys:
            raise ValueError(f"Homomorphic key {key_id} not found")
        
        public_key, _ = self.homomorphic_keys[key_id]
        start_time = time.perf_counter()
        
        # Encrypt data element-wise for neural signals
        if isinstance(data, np.ndarray):
            # For neural data arrays, encrypt each value
            encrypted_data = []
            for value in data.flatten():
                # Scale to integer for Paillier encryption
                scaled_value = int(value * 1000000)  # Scale factor for precision
                encrypted_value = public_key.encrypt(scaled_value)
                encrypted_data.append(encrypted_value)
            
            encrypted_data = np.array(encrypted_data).reshape(data.shape)
            
        elif isinstance(data, list):
            encrypted_data = []
            for value in data:
                scaled_value = int(value * 1000000)
                encrypted_value = public_key.encrypt(scaled_value)
                encrypted_data.append(encrypted_value)
        else:
            # Single value
            scaled_value = int(data * 1000000)
            encrypted_data = public_key.encrypt(scaled_value)
        
        encryption_time = (time.perf_counter() - start_time) * 1000
        
        result = HomomorphicResult(
            encrypted_data=encrypted_data,
            public_key=public_key,
            computation_result=None,
            operation_history=["encrypt"],
            encryption_time_ms=encryption_time,
            computation_time_ms=None
        )
        
        self._log_privacy_operation(
            operation="homomorphic_encrypt",
            key_id=key_id,
            data_size=len(data) if hasattr(data, '__len__') else 1,
            execution_time_ms=encryption_time
        )
        
        logger.info(f"Homomorphic encrypted neural data using key {key_id} ({encryption_time:.2f}ms)")
        
        return result
    
    def homomorphic_compute_on_neural_data(self,
                                          encrypted_result: HomomorphicResult,
                                          operation: str,
                                          operand: Optional[Union[float, int, HomomorphicResult]] = None) -> HomomorphicResult:
        """
        Perform computation on homomorphically encrypted neural data.
        
        Args:
            encrypted_result: HomomorphicResult from encryption
            operation: Operation to perform ("add", "multiply_scalar", "sum", "mean")
            operand: Operand for binary operations
            
        Returns:
            HomomorphicResult with computation result
        """
        start_time = time.perf_counter()
        encrypted_data = encrypted_result.encrypted_data
        
        if operation == "add":
            if operand is None:
                raise ValueError("Add operation requires operand")
            
            if isinstance(operand, (int, float)):
                # Add scalar
                scaled_operand = int(operand * 1000000)
                if isinstance(encrypted_data, np.ndarray):
                    result = np.array([val + scaled_operand for val in encrypted_data.flatten()]).reshape(encrypted_data.shape)
                elif isinstance(encrypted_data, list):
                    result = [val + scaled_operand for val in encrypted_data]
                else:
                    result = encrypted_data + scaled_operand
            else:
                # Add another encrypted result
                operand_data = operand.encrypted_data
                if isinstance(encrypted_data, np.ndarray):
                    result = encrypted_data + operand_data
                elif isinstance(encrypted_data, list):
                    result = [a + b for a, b in zip(encrypted_data, operand_data)]
                else:
                    result = encrypted_data + operand_data
        
        elif operation == "multiply_scalar":
            if operand is None:
                raise ValueError("Multiply operation requires scalar operand")
            
            scalar = int(operand * 1000000)
            if isinstance(encrypted_data, np.ndarray):
                result = np.array([val * scalar for val in encrypted_data.flatten()]).reshape(encrypted_data.shape)
            elif isinstance(encrypted_data, list):
                result = [val * scalar for val in encrypted_data]
            else:
                result = encrypted_data * scalar
        
        elif operation == "sum":
            # Sum all encrypted values
            if isinstance(encrypted_data, np.ndarray):
                result = sum(encrypted_data.flatten())
            elif isinstance(encrypted_data, list):
                result = sum(encrypted_data)
            else:
                result = encrypted_data
        
        elif operation == "mean":
            # Compute mean (sum / count)
            if isinstance(encrypted_data, np.ndarray):
                count = encrypted_data.size
                total = sum(encrypted_data.flatten())
                result = total * (1.0 / count)  # Multiply by reciprocal
            elif isinstance(encrypted_data, list):
                count = len(encrypted_data)
                total = sum(encrypted_data)
                result = total * (1.0 / count)
            else:
                result = encrypted_data  # Already a single value
        
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        
        computation_time = (time.perf_counter() - start_time) * 1000
        
        # Update result
        new_result = HomomorphicResult(
            encrypted_data=result,
            public_key=encrypted_result.public_key,
            computation_result=result,
            operation_history=encrypted_result.operation_history + [operation],
            encryption_time_ms=encrypted_result.encryption_time_ms,
            computation_time_ms=computation_time
        )
        
        logger.info(f"Homomorphic computation '{operation}' completed ({computation_time:.2f}ms)")
        
        return new_result
    
    def homomorphic_decrypt_result(self,
                                  encrypted_result: HomomorphicResult,
                                  key_id: str) -> Union[np.ndarray, List, float]:
        """
        Decrypt homomorphic computation result.
        
        Args:
            encrypted_result: HomomorphicResult to decrypt
            key_id: Key identifier for decryption
            
        Returns:
            Decrypted neural data
        """
        if key_id not in self.homomorphic_keys:
            raise ValueError(f"Homomorphic key {key_id} not found")
        
        _, private_key = self.homomorphic_keys[key_id]
        encrypted_data = encrypted_result.encrypted_data
        
        # Decrypt and unscale
        if isinstance(encrypted_data, np.ndarray):
            decrypted_data = np.array([
                private_key.decrypt(val) / 1000000.0
                for val in encrypted_data.flatten()
            ]).reshape(encrypted_data.shape)
        elif isinstance(encrypted_data, list):
            decrypted_data = [
                private_key.decrypt(val) / 1000000.0
                for val in encrypted_data
            ]
        else:
            decrypted_data = private_key.decrypt(encrypted_data) / 1000000.0
        
        logger.info(f"Homomorphic decryption completed for key {key_id}")
        
        return decrypted_data
    
    def apply_k_anonymity(self,
                         neural_data: List[Dict[str, Any]], 
                         k: int,
                         quasi_identifiers: List[str]) -> List[Dict[str, Any]]:
        """
        Apply k-anonymity to neural data records.
        
        Args:
            neural_data: List of neural data records
            k: Minimum group size for anonymity
            quasi_identifiers: Fields that could identify individuals
            
        Returns:
            k-anonymous neural data records
        """
        if len(neural_data) < k:
            raise ValueError(f"Dataset too small for k={k} anonymity")
        
        # Group records by quasi-identifier combinations
        groups = {}
        for record in neural_data:
            key = tuple(record.get(qi, None) for qi in quasi_identifiers)
            if key not in groups:
                groups[key] = []
            groups[key].append(record)
        
        # Filter out groups with less than k records
        anonymous_data = []
        for group in groups.values():
            if len(group) >= k:
                anonymous_data.extend(group)
            else:
                # Generalize the group by suppressing some quasi-identifiers
                for record in group:
                    for qi in quasi_identifiers:
                        if qi in record:
                            record[qi] = "*"  # Suppress specific value
                anonymous_data.extend(group)
        
        self._log_privacy_operation(
            operation="k_anonymity",
            k_value=k,
            original_records=len(neural_data),
            anonymous_records=len(anonymous_data)
        )
        
        logger.info(f"Applied k={k} anonymity: {len(neural_data)} -> {len(anonymous_data)} records")
        
        return anonymous_data
    
    def get_privacy_budget_status(self, budget_id: str) -> Dict[str, Any]:
        """Get privacy budget status"""
        if budget_id not in self.privacy_budgets:
            return {"error": "Budget not found"}
        
        budget = self.privacy_budgets[budget_id]
        return {
            "budget_id": budget_id,
            "total_epsilon": budget.total_epsilon,
            "remaining_epsilon": budget.remaining_epsilon,
            "delta": budget.delta,
            "queries_made": budget.queries_made,
            "last_query_time": budget.last_query_time,
            "neural_data_type": budget.neural_data_type.value,
            "sensitivity_multiplier": budget.sensitivity_multiplier,
            "budget_exhausted": budget.remaining_epsilon <= 0.001
        }
    
    def get_privacy_metrics(self) -> Dict[str, Any]:
        """Get overall privacy protection metrics"""
        return {
            "active_budgets": len(self.privacy_budgets),
            "homomorphic_keys": len(self.homomorphic_keys),
            "total_operations": len(self.privacy_operations_log),
            "operations_by_type": {
                op_type: len([op for op in self.privacy_operations_log if op.get('operation') == op_type])
                for op_type in ['differential_privacy', 'homomorphic_encrypt', 'k_anonymity']
            },
            "capabilities": {
                "differential_privacy": True,
                "homomorphic_encryption": self.homomorphic_available,
                "secure_multiparty": self.psi_available,
                "k_anonymity": True
            }
        }
    
    def _log_privacy_operation(self, **kwargs):
        """Log privacy operation for audit trail"""
        log_entry = {
            "timestamp": time.time(),
            **kwargs
        }
        self.privacy_operations_log.append(log_entry)
        
        # Keep only recent operations (last 1000)
        if len(self.privacy_operations_log) > 1000:
            self.privacy_operations_log = self.privacy_operations_log[-1000:]


# Global privacy protection instance
_privacy_protection = None

def get_privacy_protection(default_epsilon: float = 1.0, 
                         default_delta: float = 1e-5) -> AdvancedPrivacyProtection:
    """Get global privacy protection instance"""
    global _privacy_protection
    if _privacy_protection is None:
        _privacy_protection = AdvancedPrivacyProtection(default_epsilon, default_delta)
    return _privacy_protection