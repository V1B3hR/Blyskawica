import os
import logging
import hashlib
import hmac
import secrets
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.exceptions import InvalidSignature

# Import new advanced security modules
try:
    from .quantum_security import QuantumResistantCrypto, QuantumSecurityLevel, QuantumAlgorithm
    QUANTUM_SECURITY_AVAILABLE = True
except ImportError:
    QUANTUM_SECURITY_AVAILABLE = False

try:
    from .hsm_integration import HSMSecureStorage, HSMType, HSMKeyType
    HSM_INTEGRATION_AVAILABLE = True
except ImportError:
    HSM_INTEGRATION_AVAILABLE = False

try:
    from .advanced_privacy_protection import AdvancedPrivacyProtection, NeuralDataType
    PRIVACY_PROTECTION_AVAILABLE = True
except ImportError:
    PRIVACY_PROTECTION_AVAILABLE = False

try:
    from .zero_knowledge_proofs import ZeroKnowledgeNeuralProofs, ZKProofType, NeuralProofContext
    ZK_PROOFS_AVAILABLE = True
except ImportError:
    ZK_PROOFS_AVAILABLE = False

# Use a dedicated logger for this module for better traceability
logger = logging.getLogger(__name__)


class DataClassification(Enum):
    """Data sensitivity classification for neural/emotional data"""
    CRITICAL_NEURAL = "critical_neural"  # Real-time brain patterns, neural control
    SENSITIVE_EMOTIONAL = "sensitive_emotional"  # Emotional states, therapy data
    CONFIDENTIAL_HEALTH = "confidential_health"  # Biometric data, health metrics
    INTERNAL_SYSTEM = "internal_system"  # System config, performance data
    PUBLIC = "public"  # Non-sensitive operational data


class WirelessProtocol(Enum):
    """Supported wireless protocols for BCI communications"""
    WIFI_6E = "wifi_6e"
    BLUETOOTH_LE = "bluetooth_le"
    CUSTOM_2_4GHZ = "custom_2_4ghz"
    MESH_NETWORK = "mesh_network"
    CELLULAR_5G = "cellular_5g"


@dataclass
class EncryptionMetadata:
    """Metadata for encrypted wireless transmissions"""
    protocol: WirelessProtocol
    data_classification: DataClassification
    timestamp: float
    key_version: int
    authentication_tag: bytes
    sequence_number: int

class SecurityManager:
    """
    Enhanced security manager for wireless BCI communications with military-grade protection.
    Supports neural/emotional data encryption, wireless protocol security, and threat mitigation.
    Now includes quantum-resistant cryptography, HSM integration, advanced privacy protection,
    and zero-knowledge proofs for next-generation neural data security.
    """
    
    # Key rotation intervals (seconds)
    NEURAL_KEY_ROTATION_INTERVAL = 3600  # 1 hour for critical neural data
    STANDARD_KEY_ROTATION_INTERVAL = 86400  # 24 hours for standard data
    
    # Maximum sequence numbers before key rotation
    MAX_SEQUENCE_NUMBER = 2**32 - 1
    
    def __init__(self, enable_advanced_features: bool = True):
        """Initialize the enhanced security manager with advanced features"""
        self._key_cache = {}
        self._sequence_counters = {}
        self._last_key_rotation = {}
        
        # Initialize advanced security modules if available
        self.quantum_crypto = None
        self.hsm_storage = None
        self.privacy_protection = None
        self.zk_proofs = None
        
        if enable_advanced_features:
            self._initialize_advanced_security()
        
        logger.info(f"SecurityManager initialized with advanced features: "
                   f"Quantum: {self.quantum_crypto is not None}, "
                   f"HSM: {self.hsm_storage is not None}, "
                   f"Privacy: {self.privacy_protection is not None}, "
                   f"ZK: {self.zk_proofs is not None}")
    
    def _initialize_advanced_security(self):
        """Initialize advanced security modules"""
        try:
            if QUANTUM_SECURITY_AVAILABLE:
                self.quantum_crypto = QuantumResistantCrypto(QuantumSecurityLevel.NIST_LEVEL_3)
                logger.info("Quantum-resistant cryptography initialized")
            
            if HSM_INTEGRATION_AVAILABLE:
                self.hsm_storage = HSMSecureStorage(HSMType.SOFTWARE_FALLBACK)
                logger.info("HSM integration initialized")
            
            if PRIVACY_PROTECTION_AVAILABLE:
                self.privacy_protection = AdvancedPrivacyProtection()
                logger.info("Advanced privacy protection initialized")
            
            if ZK_PROOFS_AVAILABLE:
                self.zk_proofs = ZeroKnowledgeNeuralProofs()
                logger.info("Zero-knowledge proofs initialized")
                
        except Exception as e:
            logger.warning(f"Failed to initialize some advanced security features: {e}")
    
    def get_security_capabilities(self) -> Dict[str, Any]:
        """Get current security capabilities"""
        return {
            'quantum_resistant_crypto': self.quantum_crypto is not None,
            'hsm_integration': self.hsm_storage is not None,
            'advanced_privacy': self.privacy_protection is not None,
            'zero_knowledge_proofs': self.zk_proofs is not None,
            'classical_encryption': True,
            'wireless_intrusion_detection': True,
            'differential_privacy': self.privacy_protection is not None,
            'homomorphic_encryption': (
                self.privacy_protection is not None and 
                self.privacy_protection.homomorphic_available
            )
        }
    
    @staticmethod
    def generate_key(key_path: str) -> None:
        """
        Generates a new Fernet key and saves it to a file with secure permissions (600).
        Ensures the parent directory exists before writing.
        """
        try:
            key_file = Path(key_path)
            # Ensure the directory exists to prevent errors
            key_file.parent.mkdir(parents=True, exist_ok=True)

            key = Fernet.generate_key()
            # Atomic write for resilience
            tmp_path = key_file.with_suffix(key_file.suffix + '.tmp')
            with open(tmp_path, "wb") as f:
                f.write(key)
            os.replace(tmp_path, key_file)
            os.chmod(key_file, 0o600)

            logger.info(f"New encryption key generated and saved securely to {key_path}")
        except IOError as e:
            logger.error(f"Failed to write key file to '{key_path}': {e}", exc_info=True)
            raise
    
    @staticmethod
    def generate_wireless_master_key(key_path: str, key_size: int = 32) -> None:
        """
        Generate a master key for wireless neural data encryption using AES-256-GCM.
        
        Args:
            key_path: Path to store the master key
            key_size: Key size in bytes (32 for AES-256)
        """
        try:
            key_file = Path(key_path)
            key_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate cryptographically secure random key
            master_key = secrets.token_bytes(key_size)
            
            # Atomic write with secure permissions
            tmp_path = key_file.with_suffix(key_file.suffix + '.tmp')
            with open(tmp_path, "wb") as f:
                f.write(master_key)
            os.replace(tmp_path, key_file)
            os.chmod(key_file, 0o600)
            
            logger.info(f"Wireless master key generated: {key_path} ({key_size * 8}-bit)")
        except IOError as e:
            logger.error(f"Failed to generate wireless master key: {e}", exc_info=True)
            raise
    
    @staticmethod
    def derive_protocol_key(master_key: bytes, protocol: WirelessProtocol, 
                          classification: DataClassification, 
                          context: Optional[bytes] = None) -> bytes:
        """
        Derive protocol-specific keys using HKDF for different wireless protocols and data types.
        
        Args:
            master_key: The master key for derivation
            protocol: Wireless protocol (WiFi, BLE, etc.)
            classification: Data sensitivity classification
            context: Optional context information for key derivation
            
        Returns:
            Derived 32-byte key for the specific protocol and data type
        """
        try:
            # Create protocol and classification specific salt
            salt = hashlib.sha256(f"{protocol.value}:{classification.value}".encode()).digest()
            
            # Create info parameter with optional context
            info = f"GCS-v7-neural-{protocol.value}-{classification.value}".encode()
            if context:
                info += b":" + context
            
            # Derive key using HKDF-SHA256
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=32,  # 256-bit key
                salt=salt,
                info=info,
            )
            derived_key = hkdf.derive(master_key)
            
            logger.debug(f"Derived key for {protocol.value}:{classification.value}")
            return derived_key
            
        except Exception as e:
            logger.error(f"Key derivation failed: {e}", exc_info=True)
            raise
    
    def encrypt_neural_data(self, data: bytes, protocol: WirelessProtocol,
                          classification: DataClassification = DataClassification.CRITICAL_NEURAL,
                          master_key_path: str = None) -> Tuple[bytes, EncryptionMetadata]:
        """
        Encrypt neural/emotional data for wireless transmission with enhanced protection.
        
        Args:
            data: Raw neural data to encrypt
            protocol: Wireless protocol for transmission
            classification: Data sensitivity classification
            master_key_path: Path to master key file
            
        Returns:
            Tuple of (encrypted_data, metadata)
        """
        try:
            # Load or use cached master key
            if master_key_path and master_key_path not in self._key_cache:
                with open(master_key_path, "rb") as f:
                    self._key_cache[master_key_path] = f.read()
            
            master_key = self._key_cache.get(master_key_path)
            if not master_key:
                raise ValueError("Master key not available")
            
            # Check if key rotation is needed
            rotation_key = f"{protocol.value}:{classification.value}"
            current_time = time.time()
            
            if (rotation_key in self._last_key_rotation and
                current_time - self._last_key_rotation[rotation_key] > 
                self._get_rotation_interval(classification)):
                logger.info(f"Key rotation needed for {rotation_key}")
            
            # Derive protocol-specific key
            context = str(int(current_time)).encode()  # Time-based context
            derived_key = self.derive_protocol_key(master_key, protocol, classification, context)
            
            # Get sequence number
            seq_key = f"{protocol.value}:{classification.value}"
            seq_num = self._sequence_counters.get(seq_key, 0)
            self._sequence_counters[seq_key] = (seq_num + 1) % self.MAX_SEQUENCE_NUMBER
            
            # Create AEAD cipher (AES-256-GCM)
            aesgcm = AESGCM(derived_key)
            
            # Generate nonce (96-bit for GCM)
            nonce = secrets.token_bytes(12)
            
            # Additional authenticated data (AAD)
            aad = f"{protocol.value}:{classification.value}:{seq_num}:{int(current_time)}".encode()
            
            # Encrypt data
            ciphertext = aesgcm.encrypt(nonce, data, aad)
            
            # Create encryption metadata
            metadata = EncryptionMetadata(
                protocol=protocol,
                data_classification=classification,
                timestamp=current_time,
                key_version=1,  # TODO: Implement key versioning
                authentication_tag=ciphertext[-16:],  # Last 16 bytes are auth tag
                sequence_number=seq_num
            )
            
            # Combine nonce + ciphertext for transmission
            encrypted_payload = nonce + ciphertext
            
            logger.debug(f"Neural data encrypted: {len(data)} -> {len(encrypted_payload)} bytes")
            return encrypted_payload, metadata
            
        except Exception as e:
            logger.error(f"Neural data encryption failed: {e}", exc_info=True)
            raise
    
    def decrypt_neural_data(self, encrypted_payload: bytes, metadata: EncryptionMetadata,
                          master_key_path: str) -> bytes:
        """
        Decrypt neural/emotional data received via wireless transmission.
        
        Args:
            encrypted_payload: Encrypted data (nonce + ciphertext)
            metadata: Encryption metadata
            master_key_path: Path to master key file
            
        Returns:
            Decrypted neural data
        """
        try:
            # Load master key
            if master_key_path not in self._key_cache:
                with open(master_key_path, "rb") as f:
                    self._key_cache[master_key_path] = f.read()
            
            master_key = self._key_cache[master_key_path]
            
            # Derive the same key used for encryption
            context = str(int(metadata.timestamp)).encode()
            derived_key = self.derive_protocol_key(
                master_key, metadata.protocol, metadata.data_classification, context
            )
            
            # Extract nonce and ciphertext
            nonce = encrypted_payload[:12]
            ciphertext = encrypted_payload[12:]
            
            # Reconstruct AAD
            aad = (f"{metadata.protocol.value}:{metadata.data_classification.value}:"
                  f"{metadata.sequence_number}:{int(metadata.timestamp)}").encode()
            
            # Decrypt data
            aesgcm = AESGCM(derived_key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, aad)
            
            logger.debug(f"Neural data decrypted: {len(encrypted_payload)} -> {len(plaintext)} bytes")
            return plaintext
            
        except Exception as e:
            logger.error(f"Neural data decryption failed: {e}", exc_info=True)
            raise
    
    def _get_rotation_interval(self, classification: DataClassification) -> int:
        """Get key rotation interval based on data classification"""
        if classification in [DataClassification.CRITICAL_NEURAL, DataClassification.SENSITIVE_EMOTIONAL]:
            return self.NEURAL_KEY_ROTATION_INTERVAL
        return self.STANDARD_KEY_ROTATION_INTERVAL
    
    def verify_wireless_integrity(self, data: bytes, signature: bytes, 
                                public_key_path: str) -> bool:
        """
        Verify integrity of wireless transmission using ECDSA signatures.
        
        Args:
            data: Original data to verify
            signature: Digital signature
            public_key_path: Path to public key file
            
        Returns:
            True if signature is valid
        """
        try:
            # Load public key
            with open(public_key_path, "rb") as f:
                public_key = serialization.load_pem_public_key(f.read())
            
            # Verify signature
            public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
            return True
            
        except InvalidSignature:
            logger.warning("Invalid wireless transmission signature")
            return False
        except Exception as e:
            logger.error(f"Signature verification failed: {e}", exc_info=True)
            return False

    @staticmethod
    def load_key(key_path: str) -> Fernet:
        """
        Loads the encryption key and initializes a Fernet instance for use.
        Verifies length and format for robustness.
        """
        try:
            with open(key_path, "rb") as key_file:
                key = key_file.read()
                # Validate Fernet key length
                if len(key) != 44:
                    raise ValueError("Fernet key must be 44 bytes base64.")
                return Fernet(key)
        except FileNotFoundError:
            logger.error(f"FATAL: Encryption key not found at '{key_path}'. Cannot proceed.")
            raise
        except (ValueError, TypeError) as e:
            logger.error(f"FATAL: Key file at '{key_path}' is corrupt or not a valid Fernet key: {e}", exc_info=True)
            raise

    @staticmethod
    def encrypt_file(file_path: str, key_path: str) -> bool:
        """
        Encrypts a file in place using the provided key.
        Returns True on success, False on failure.
        """
        logger.info(f"Attempting to encrypt file: '{file_path}'")
        try:
            fernet = SecurityManager.load_key(key_path)

            with open(file_path, "rb") as file:
                file_data = file.read()

            encrypted_data = fernet.encrypt(file_data)

            # Atomic write to prevent partial file corruption
            tmp_path = Path(file_path).with_suffix(Path(file_path).suffix + '.enc_tmp')
            with open(tmp_path, "wb") as file:
                file.write(encrypted_data)
            os.replace(tmp_path, file_path)

            logger.info(f"File '{file_path}' has been successfully encrypted.")
            return True
        except Exception as e:
            logger.error(f"An unexpected error occurred during encryption of '{file_path}': {e}", exc_info=True)
            return False

    @staticmethod
    def decrypt_file_safely(file_path: str, key_path: str) -> bool:
        """
        Decrypts a file non-destructively. The original file is only replaced upon
        successful decryption. This prevents data loss on failure.

        Returns:
            True if decryption was successful, False otherwise.
        """
        logger.info(f"Attempting to safely decrypt file: '{file_path}'")
        original_file = Path(file_path)
        decrypted_temp_file = original_file.with_suffix(original_file.suffix + '.decrypted_tmp')

        try:
            fernet = SecurityManager.load_key(key_path)

            with open(original_file, "rb") as file:
                encrypted_data = file.read()

            # Specifically catch the most common crypto error
            decrypted_data = fernet.decrypt(encrypted_data)

            # Non-destructive write to a temporary file first
            with open(decrypted_temp_file, "wb") as file:
                file.write(decrypted_data)

            # Only replace the original if the entire process was successful
            os.replace(decrypted_temp_file, original_file)

            logger.info(f"File '{file_path}' has been successfully decrypted.")
            return True

        except FileNotFoundError:
            logger.error(f"Cannot decrypt: File not found at '{file_path}'.")
            return False
        except InvalidToken:
            logger.error(f"DECRYPTION FAILED for '{file_path}': The key is incorrect or the data is corrupt.")
            if decrypted_temp_file.exists():
                os.remove(decrypted_temp_file)
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during decryption of '{file_path}': {e}", exc_info=True)
            if decrypted_temp_file.exists():
                os.remove(decrypted_temp_file)
            return False


class WirelessIntrusionDetectionSystem:
    """
    Wireless Intrusion Detection System (WIDS) for BCI communications.
    Monitors RF spectrum, protocol anomalies, and device behavior for security threats.
    """
    
    def __init__(self):
        """Initialize WIDS with monitoring capabilities"""
        self.threat_signatures = {}
        self.device_baselines = {}
        self.anomaly_threshold = 0.85  # Anomaly detection threshold
        self.alert_callbacks = []
        
    def register_alert_callback(self, callback):
        """Register callback function for security alerts"""
        self.alert_callbacks.append(callback)
        
    def analyze_rf_spectrum(self, spectrum_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze RF spectrum data for jamming attempts and interference.
        
        Args:
            spectrum_data: Dictionary containing frequency, power, and time data
            
        Returns:
            Analysis results with threat assessment
        """
        try:
            analysis_result = {
                "timestamp": time.time(),
                "threats_detected": [],
                "interference_level": "normal",
                "recommendations": []
            }
            
            # Check for jamming signatures
            if self._detect_jamming(spectrum_data):
                analysis_result["threats_detected"].append({
                    "type": "rf_jamming",
                    "severity": "high",
                    "description": "Potential RF jamming detected",
                    "affected_frequencies": spectrum_data.get("affected_bands", [])
                })
                analysis_result["recommendations"].append("Switch to alternative frequency bands")
                
            # Check for interference levels
            interference_level = self._assess_interference(spectrum_data)
            analysis_result["interference_level"] = interference_level
            
            if interference_level == "high":
                analysis_result["recommendations"].append("Enable adaptive frequency selection")
                
            # Trigger alerts if threats detected
            if analysis_result["threats_detected"]:
                self._trigger_alert("RF_THREAT", analysis_result)
                
            return analysis_result
            
        except Exception as e:
            logger.error(f"RF spectrum analysis failed: {e}", exc_info=True)
            return {"error": str(e)}
    
    def detect_protocol_anomalies(self, protocol: WirelessProtocol, 
                                 traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect anomalies in wireless protocol behavior.
        
        Args:
            protocol: Wireless protocol being monitored
            traffic_data: Protocol traffic analysis data
            
        Returns:
            Anomaly detection results
        """
        try:
            anomalies = []
            
            # Check for unusual packet sizes
            if self._detect_size_anomalies(traffic_data):
                anomalies.append({
                    "type": "packet_size_anomaly",
                    "severity": "medium",
                    "description": "Unusual packet size patterns detected"
                })
            
            # Check for timing anomalies
            if self._detect_timing_anomalies(traffic_data):
                anomalies.append({
                    "type": "timing_anomaly",
                    "severity": "medium",
                    "description": "Abnormal transmission timing patterns"
                })
            
            # Check for unknown devices
            if self._detect_unknown_devices(traffic_data):
                anomalies.append({
                    "type": "unknown_device",
                    "severity": "high",
                    "description": "Unauthorized devices detected in network"
                })
            
            result = {
                "protocol": protocol.value,
                "timestamp": time.time(),
                "anomalies": anomalies,
                "risk_score": self._calculate_risk_score(anomalies)
            }
            
            # Trigger alerts for high-risk anomalies
            if result["risk_score"] > 0.7:
                self._trigger_alert("PROTOCOL_ANOMALY", result)
                
            return result
            
        except Exception as e:
            logger.error(f"Protocol anomaly detection failed: {e}", exc_info=True)
            return {"error": str(e)}
    
    def monitor_device_behavior(self, device_id: str, 
                              behavior_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor individual device behavior for suspicious activity.
        
        Args:
            device_id: Unique device identifier
            behavior_metrics: Device behavior metrics
            
        Returns:
            Behavior analysis results
        """
        try:
            # Establish baseline if first time seeing device
            if device_id not in self.device_baselines:
                self.device_baselines[device_id] = self._establish_baseline(behavior_metrics)
                return {"status": "baseline_established", "device_id": device_id}
            
            baseline = self.device_baselines[device_id]
            deviations = []
            
            # Check for behavior deviations
            for metric, value in behavior_metrics.items():
                if self._is_significant_deviation(baseline.get(metric), value):
                    deviations.append({
                        "metric": metric,
                        "baseline": baseline.get(metric),
                        "current": value,
                        "deviation_score": self._calculate_deviation_score(baseline.get(metric), value)
                    })
            
            result = {
                "device_id": device_id,
                "timestamp": time.time(),
                "deviations": deviations,
                "threat_level": self._assess_threat_level(deviations)
            }
            
            # Update baseline with new data (weighted average)
            self._update_baseline(device_id, behavior_metrics)
            
            # Trigger alerts for suspicious behavior
            if result["threat_level"] == "high":
                self._trigger_alert("SUSPICIOUS_DEVICE", result)
                
            return result
            
        except Exception as e:
            logger.error(f"Device behavior monitoring failed: {e}", exc_info=True)
            return {"error": str(e)}
    
    def _detect_jamming(self, spectrum_data: Dict[str, Any]) -> bool:
        """Detect RF jamming patterns"""
        # Check for sudden power increases across multiple frequencies
        power_levels = spectrum_data.get("power_levels", [])
        if not power_levels:
            return False
            
        # Simple jamming detection: abnormally high power across wide frequency range
        high_power_count = sum(1 for power in power_levels if power > spectrum_data.get("noise_floor", 0) + 20)
        return high_power_count > len(power_levels) * 0.7
    
    def _assess_interference(self, spectrum_data: Dict[str, Any]) -> str:
        """Assess interference level from spectrum data"""
        interference_score = spectrum_data.get("interference_score", 0)
        if interference_score > 0.8:
            return "high"
        elif interference_score > 0.5:
            return "medium"
        return "normal"
    
    def _detect_size_anomalies(self, traffic_data: Dict[str, Any]) -> bool:
        """Detect unusual packet size patterns"""
        packet_sizes = traffic_data.get("packet_sizes", [])
        if not packet_sizes:
            return False
        
        # Simple anomaly detection: check for sizes outside typical neural data range
        avg_size = sum(packet_sizes) / len(packet_sizes)
        return any(abs(size - avg_size) > avg_size * 2 for size in packet_sizes)
    
    def _detect_timing_anomalies(self, traffic_data: Dict[str, Any]) -> bool:
        """Detect abnormal timing patterns"""
        timestamps = traffic_data.get("timestamps", [])
        if len(timestamps) < 2:
            return False
        
        # Check for irregular intervals (potential replay attacks)
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        avg_interval = sum(intervals) / len(intervals)
        return any(abs(interval - avg_interval) > avg_interval * 3 for interval in intervals)
    
    def _detect_unknown_devices(self, traffic_data: Dict[str, Any]) -> bool:
        """Detect unauthorized devices"""
        device_ids = traffic_data.get("device_ids", [])
        known_devices = traffic_data.get("authorized_devices", set())
        return any(device_id not in known_devices for device_id in device_ids)
    
    def _calculate_risk_score(self, anomalies: list) -> float:
        """Calculate overall risk score from detected anomalies"""
        if not anomalies:
            return 0.0
        
        severity_weights = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
        total_score = sum(severity_weights.get(anomaly.get("severity", "medium"), 0.5) 
                         for anomaly in anomalies)
        return min(total_score / len(anomalies), 1.0)
    
    def _establish_baseline(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Establish baseline behavior metrics for a device"""
        return {k: v for k, v in metrics.items() if isinstance(v, (int, float))}
    
    def _is_significant_deviation(self, baseline_value: Any, current_value: Any) -> bool:
        """Check if current value represents significant deviation from baseline"""
        if baseline_value is None or current_value is None:
            return False
        if not isinstance(baseline_value, (int, float)) or not isinstance(current_value, (int, float)):
            return baseline_value != current_value
        
        # 50% deviation threshold
        return abs(current_value - baseline_value) > abs(baseline_value) * 0.5
    
    def _calculate_deviation_score(self, baseline_value: Any, current_value: Any) -> float:
        """Calculate numerical deviation score"""
        if not isinstance(baseline_value, (int, float)) or not isinstance(current_value, (int, float)):
            return 1.0 if baseline_value != current_value else 0.0
        
        if baseline_value == 0:
            return 1.0 if current_value != 0 else 0.0
        
        return min(abs(current_value - baseline_value) / abs(baseline_value), 2.0)
    
    def _assess_threat_level(self, deviations: list) -> str:
        """Assess threat level based on behavior deviations"""
        if not deviations:
            return "normal"
        
        max_deviation = max(dev.get("deviation_score", 0) for dev in deviations)
        if max_deviation > 1.5:
            return "high"
        elif max_deviation > 0.8:
            return "medium"
        return "low"
    
    def _update_baseline(self, device_id: str, new_metrics: Dict[str, Any]) -> None:
        """Update device baseline with new metrics (weighted average)"""
        if device_id not in self.device_baselines:
            return
        
        baseline = self.device_baselines[device_id]
        alpha = 0.1  # Learning rate
        
        for metric, value in new_metrics.items():
            if isinstance(value, (int, float)) and metric in baseline:
                baseline[metric] = (1 - alpha) * baseline[metric] + alpha * value
    
    def _trigger_alert(self, alert_type: str, alert_data: Dict[str, Any]) -> None:
        """Trigger security alert to registered callbacks"""
        alert = {
            "type": alert_type,
            "timestamp": time.time(),
            "data": alert_data,
            "severity": alert_data.get("risk_score", 0.5)
        }
        
        logger.warning(f"Security alert triggered: {alert_type}")
        
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}", exc_info=True)

    @staticmethod
    def load_key(key_path: str) -> Fernet:
        """
        Loads the encryption key and initializes a Fernet instance for use.
        Verifies length and format for robustness.
        """
        try:
            with open(key_path, "rb") as key_file:
                key = key_file.read()
                # Validate Fernet key length
                if len(key) != 44:
                    raise ValueError("Fernet key must be 44 bytes base64.")
                return Fernet(key)
        except FileNotFoundError:
            logger.error(f"FATAL: Encryption key not found at '{key_path}'. Cannot proceed.")
            raise
        except (ValueError, TypeError) as e:
            logger.error(f"FATAL: Key file at '{key_path}' is corrupt or not a valid Fernet key: {e}", exc_info=True)
            raise

    @staticmethod
    def encrypt_file(file_path: str, key_path: str) -> bool:
        """
        Encrypts a file in place using the provided key.
        Returns True on success, False on failure.
        """
        logger.info(f"Attempting to encrypt file: '{file_path}'")
        try:
            fernet = SecurityManager.load_key(key_path)

            with open(file_path, "rb") as file:
                file_data = file.read()

            encrypted_data = fernet.encrypt(file_data)

            # Atomic write to prevent partial file corruption
            tmp_path = Path(file_path).with_suffix(Path(file_path).suffix + '.enc_tmp')
            with open(tmp_path, "wb") as file:
                file.write(encrypted_data)
            os.replace(tmp_path, file_path)

            logger.info(f"File '{file_path}' has been successfully encrypted.")
            return True
        except Exception as e:
            logger.error(f"An unexpected error occurred during encryption of '{file_path}': {e}", exc_info=True)
            return False

    @staticmethod
    def decrypt_file_safely(file_path: str, key_path: str) -> bool:
        """
        Decrypts a file non-destructively. The original file is only replaced upon
        successful decryption. This prevents data loss on failure.

        Returns:
            True if decryption was successful, False otherwise.
        """
        logger.info(f"Attempting to safely decrypt file: '{file_path}'")
        original_file = Path(file_path)
        decrypted_temp_file = original_file.with_suffix(original_file.suffix + '.decrypted_tmp')

        try:
            fernet = SecurityManager.load_key(key_path)

            with open(original_file, "rb") as file:
                encrypted_data = file.read()

            # Specifically catch the most common crypto error
            decrypted_data = fernet.decrypt(encrypted_data)

            # Non-destructive write to a temporary file first
            with open(decrypted_temp_file, "wb") as file:
                file.write(decrypted_data)

            # Only replace the original if the entire process was successful
            os.replace(decrypted_temp_file, original_file)

            logger.info(f"File '{file_path}' has been successfully decrypted.")
            return True

        except FileNotFoundError:
            logger.error(f"Cannot decrypt: File not found at '{file_path}'.")
            return False
        except InvalidToken:
            logger.error(f"DECRYPTION FAILED for '{file_path}': The key is incorrect or the data is corrupt.")
            if decrypted_temp_file.exists():
                os.remove(decrypted_temp_file)
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during decryption of '{file_path}': {e}", exc_info=True)
            if decrypted_temp_file.exists():
                os.remove(decrypted_temp_file)
            return False
