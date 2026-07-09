"""
test_wireless_security.py - Comprehensive security tests for wireless BCI communications

Tests the enhanced SecurityManager and WirelessIntrusionDetectionSystem for:
1. Neural/emotional data encryption and decryption
2. Wireless protocol security
3. Key management and rotation
4. Intrusion detection capabilities
5. Threat model validation
"""

import pytest
import os
import time
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the modules we're testing
from gcs.security import (
    SecurityManager, WirelessIntrusionDetectionSystem,
    DataClassification, WirelessProtocol, EncryptionMetadata
)


class TestSecurityManagerWirelessEnhancements:
    """Test enhanced SecurityManager wireless capabilities"""
    
    def setup_method(self):
        """Set up test environment"""
        self.security_manager = SecurityManager()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.master_key_path = self.temp_dir / "master.key"
        
    def teardown_method(self):
        """Clean up test environment"""
        # Clean up temporary files
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_generate_wireless_master_key(self):
        """Test wireless master key generation"""
        # Generate master key
        SecurityManager.generate_wireless_master_key(str(self.master_key_path), 32)
        
        # Verify key file exists and has correct permissions
        assert self.master_key_path.exists()
        stat = self.master_key_path.stat()
        assert oct(stat.st_mode)[-3:] == '600'  # Check permissions
        
        # Verify key size
        key_data = self.master_key_path.read_bytes()
        assert len(key_data) == 32  # 256-bit key
    
    def test_derive_protocol_key(self):
        """Test protocol-specific key derivation"""
        # Generate master key
        master_key = os.urandom(32)
        
        # Derive keys for different protocols
        wifi_key = SecurityManager.derive_protocol_key(
            master_key, WirelessProtocol.WIFI_6E, DataClassification.CRITICAL_NEURAL
        )
        ble_key = SecurityManager.derive_protocol_key(
            master_key, WirelessProtocol.BLUETOOTH_LE, DataClassification.SENSITIVE_EMOTIONAL
        )
        
        # Keys should be different
        assert wifi_key != ble_key
        assert len(wifi_key) == 32
        assert len(ble_key) == 32
        
        # Same parameters should produce same key
        wifi_key2 = SecurityManager.derive_protocol_key(
            master_key, WirelessProtocol.WIFI_6E, DataClassification.CRITICAL_NEURAL
        )
        assert wifi_key == wifi_key2
    
    def test_neural_data_encryption_decryption(self):
        """Test neural data encryption and decryption"""
        # Generate master key
        SecurityManager.generate_wireless_master_key(str(self.master_key_path))
        
        # Test data (simulated neural signal)
        neural_data = b"EEG_SIGNAL_ALPHA_WAVES_8_13_HZ" + os.urandom(1024)
        
        # Encrypt neural data
        encrypted_data, metadata = self.security_manager.encrypt_neural_data(
            neural_data,
            WirelessProtocol.WIFI_6E,
            DataClassification.CRITICAL_NEURAL,
            str(self.master_key_path)
        )
        
        # Verify encryption
        assert encrypted_data != neural_data
        assert len(encrypted_data) > len(neural_data)  # Includes nonce + auth tag
        assert isinstance(metadata, EncryptionMetadata)
        assert metadata.protocol == WirelessProtocol.WIFI_6E
        assert metadata.data_classification == DataClassification.CRITICAL_NEURAL
        
        # Decrypt neural data
        decrypted_data = self.security_manager.decrypt_neural_data(
            encrypted_data, metadata, str(self.master_key_path)
        )
        
        # Verify decryption
        assert decrypted_data == neural_data
    
    def test_different_data_classifications(self):
        """Test encryption for different data sensitivity levels"""
        SecurityManager.generate_wireless_master_key(str(self.master_key_path))
        
        test_data = b"TEST_DATA_FOR_CLASSIFICATION"
        
        # Encrypt data with different classifications
        critical_encrypted, critical_metadata = self.security_manager.encrypt_neural_data(
            test_data, WirelessProtocol.WIFI_6E, DataClassification.CRITICAL_NEURAL,
            str(self.master_key_path)
        )
        
        sensitive_encrypted, sensitive_metadata = self.security_manager.encrypt_neural_data(
            test_data, WirelessProtocol.WIFI_6E, DataClassification.SENSITIVE_EMOTIONAL,
            str(self.master_key_path)
        )
        
        # Different classifications should produce different ciphertexts
        assert critical_encrypted != sensitive_encrypted
        assert critical_metadata.data_classification != sensitive_metadata.data_classification
    
    def test_wireless_protocols_encryption(self):
        """Test encryption across different wireless protocols"""
        SecurityManager.generate_wireless_master_key(str(self.master_key_path))
        
        neural_data = b"NEURAL_PATTERN_TEST_DATA"
        
        protocols = [
            WirelessProtocol.WIFI_6E,
            WirelessProtocol.BLUETOOTH_LE,
            WirelessProtocol.CUSTOM_2_4GHZ
        ]
        
        encrypted_results = {}
        
        for protocol in protocols:
            encrypted_data, metadata = self.security_manager.encrypt_neural_data(
                neural_data, protocol, DataClassification.CRITICAL_NEURAL,
                str(self.master_key_path)
            )
            encrypted_results[protocol] = (encrypted_data, metadata)
            
            # Verify each can be decrypted correctly
            decrypted = self.security_manager.decrypt_neural_data(
                encrypted_data, metadata, str(self.master_key_path)
            )
            assert decrypted == neural_data
        
        # Verify different protocols produce different encryptions
        wifi_data = encrypted_results[WirelessProtocol.WIFI_6E][0]
        ble_data = encrypted_results[WirelessProtocol.BLUETOOTH_LE][0]
        custom_data = encrypted_results[WirelessProtocol.CUSTOM_2_4GHZ][0]
        
        assert wifi_data != ble_data != custom_data
    
    def test_sequence_number_tracking(self):
        """Test sequence number tracking for replay attack prevention"""
        SecurityManager.generate_wireless_master_key(str(self.master_key_path))
        
        neural_data = b"SEQUENCE_TEST_DATA"
        
        # Encrypt multiple messages
        results = []
        for i in range(5):
            encrypted_data, metadata = self.security_manager.encrypt_neural_data(
                neural_data, WirelessProtocol.WIFI_6E, DataClassification.CRITICAL_NEURAL,
                str(self.master_key_path)
            )
            results.append(metadata.sequence_number)
        
        # Sequence numbers should increment
        for i in range(1, len(results)):
            assert results[i] == results[i-1] + 1
    
    def test_encryption_performance(self):
        """Test encryption performance for real-time neural data"""
        SecurityManager.generate_wireless_master_key(str(self.master_key_path))
        
        # Simulate 1KB of neural data (typical EEG packet)
        neural_data = os.urandom(1024)
        
        # Measure encryption time
        start_time = time.time()
        encrypted_data, metadata = self.security_manager.encrypt_neural_data(
            neural_data, WirelessProtocol.WIFI_6E, DataClassification.CRITICAL_NEURAL,
            str(self.master_key_path)
        )
        encryption_time = time.time() - start_time
        
        # Measure decryption time
        start_time = time.time()
        decrypted_data = self.security_manager.decrypt_neural_data(
            encrypted_data, metadata, str(self.master_key_path)
        )
        decryption_time = time.time() - start_time
        
        # Assert performance requirements (should be < 1ms for real-time use)
        assert encryption_time < 0.001  # 1ms
        assert decryption_time < 0.001  # 1ms
        assert decrypted_data == neural_data


class TestWirelessIntrusionDetectionSystem:
    """Test WIDS functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.wids = WirelessIntrusionDetectionSystem()
        self.alert_received = None
        
        # Register alert callback
        def alert_callback(alert):
            self.alert_received = alert
            
        self.wids.register_alert_callback(alert_callback)
    
    def test_rf_spectrum_analysis_normal(self):
        """Test RF spectrum analysis with normal conditions"""
        spectrum_data = {
            "power_levels": [10, 12, 9, 11, 10, 8, 13],
            "noise_floor": 5,
            "interference_score": 0.3
        }
        
        result = self.wids.analyze_rf_spectrum(spectrum_data)
        
        assert "threats_detected" in result
        assert len(result["threats_detected"]) == 0  # No threats in normal conditions
        assert result["interference_level"] == "normal"
    
    def test_rf_spectrum_analysis_jamming(self):
        """Test RF spectrum analysis with jamming detection"""
        spectrum_data = {
            "power_levels": [40, 45, 42, 44, 43, 41, 46],  # High power levels
            "noise_floor": 5,
            "interference_score": 0.2,
            "affected_bands": ["2.4GHz"]
        }
        
        result = self.wids.analyze_rf_spectrum(spectrum_data)
        
        assert len(result["threats_detected"]) > 0
        assert any(threat["type"] == "rf_jamming" for threat in result["threats_detected"])
        assert "Switch to alternative frequency bands" in result["recommendations"]
        assert self.alert_received is not None  # Alert should be triggered
    
    def test_protocol_anomaly_detection(self):
        """Test protocol anomaly detection"""
        traffic_data = {
            "packet_sizes": [100, 105, 95, 102, 500],  # One anomalous size
            "timestamps": [1.0, 2.0, 3.0, 4.0, 5.0],
            "device_ids": ["device1", "device2", "unknown_device"],
            "authorized_devices": {"device1", "device2"}
        }
        
        result = self.wids.detect_protocol_anomalies(WirelessProtocol.WIFI_6E, traffic_data)
        
        assert "anomalies" in result
        assert len(result["anomalies"]) > 0
        assert any(anomaly["type"] == "unknown_device" for anomaly in result["anomalies"])
        assert result["risk_score"] > 0
    
    def test_device_behavior_monitoring(self):
        """Test device behavior monitoring"""
        device_id = "neural_sensor_001"
        
        # Establish baseline
        baseline_metrics = {
            "packet_rate": 100,
            "power_consumption": 50,
            "latency": 5
        }
        
        result1 = self.wids.monitor_device_behavior(device_id, baseline_metrics)
        assert result1["status"] == "baseline_established"
        
        # Test normal behavior
        normal_metrics = {
            "packet_rate": 105,
            "power_consumption": 52,
            "latency": 4
        }
        
        result2 = self.wids.monitor_device_behavior(device_id, normal_metrics)
        assert result2["threat_level"] in ["normal", "low"]
        
        # Test anomalous behavior
        anomalous_metrics = {
            "packet_rate": 200,  # 100% increase
            "power_consumption": 100,  # 100% increase
            "latency": 15  # 200% increase
        }
        
        result3 = self.wids.monitor_device_behavior(device_id, anomalous_metrics)
        assert result3["threat_level"] in ["medium", "high"]
        assert len(result3["deviations"]) > 0
    
    def test_threat_level_assessment(self):
        """Test threat level assessment logic"""
        # High deviation should result in high threat
        high_deviation = [{"deviation_score": 2.0}]
        threat_level = self.wids._assess_threat_level(high_deviation)
        assert threat_level == "high"
        
        # Medium deviation should result in medium threat
        medium_deviation = [{"deviation_score": 1.0}]
        threat_level = self.wids._assess_threat_level(medium_deviation)
        assert threat_level == "medium"
        
        # Low deviation should result in low threat
        low_deviation = [{"deviation_score": 0.5}]
        threat_level = self.wids._assess_threat_level(low_deviation)
        assert threat_level == "low"
    
    def test_risk_score_calculation(self):
        """Test risk score calculation"""
        # High severity anomalies
        high_risk_anomalies = [
            {"severity": "high"},
            {"severity": "critical"}
        ]
        score = self.wids._calculate_risk_score(high_risk_anomalies)
        assert score >= 0.8
        
        # Low severity anomalies
        low_risk_anomalies = [
            {"severity": "low"},
            {"severity": "medium"}
        ]
        score = self.wids._calculate_risk_score(low_risk_anomalies)
        assert score < 0.6


class TestSecurityIntegration:
    """Integration tests for security components"""
    
    def setup_method(self):
        """Set up test environment"""
        self.security_manager = SecurityManager()
        self.wids = WirelessIntrusionDetectionSystem()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.master_key_path = self.temp_dir / "master.key"
        
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_neural_data_security(self):
        """Test complete neural data security pipeline"""
        # Generate master key
        SecurityManager.generate_wireless_master_key(str(self.master_key_path))
        
        # Simulate neural data collection
        neural_data = {
            "eeg_channels": list(range(64)),
            "sample_rate": 1000,
            "data": os.urandom(2048)  # Simulated EEG data
        }
        
        data_bytes = str(neural_data).encode()
        
        # Encrypt for transmission
        encrypted_data, metadata = self.security_manager.encrypt_neural_data(
            data_bytes,
            WirelessProtocol.WIFI_6E,
            DataClassification.CRITICAL_NEURAL,
            str(self.master_key_path)
        )
        
        # Simulate wireless transmission monitoring
        traffic_data = {
            "packet_sizes": [len(encrypted_data)],
            "timestamps": [time.time()],
            "device_ids": ["neural_headset_001"],
            "authorized_devices": {"neural_headset_001"}
        }
        
        wids_result = self.wids.detect_protocol_anomalies(
            WirelessProtocol.WIFI_6E, traffic_data
        )
        
        # Should detect no anomalies for legitimate traffic
        assert wids_result["risk_score"] < 0.5
        
        # Decrypt received data
        decrypted_data = self.security_manager.decrypt_neural_data(
            encrypted_data, metadata, str(self.master_key_path)
        )
        
        # Verify data integrity
        assert decrypted_data == data_bytes
        
    def test_attack_simulation_and_detection(self):
        """Simulate various attacks and verify detection"""
        # Simulate RF jamming attack
        jamming_spectrum = {
            "power_levels": [50, 55, 52, 54, 53],  # High power
            "noise_floor": 5,
            "interference_score": 0.2
        }
        
        jamming_result = self.wids.analyze_rf_spectrum(jamming_spectrum)
        assert len(jamming_result["threats_detected"]) > 0
        
        # Simulate device spoofing attack
        spoofing_traffic = {
            "packet_sizes": [100, 105, 95],
            "timestamps": [1.0, 2.0, 3.0],
            "device_ids": ["legitimate_device", "spoofed_device"],
            "authorized_devices": {"legitimate_device"}
        }
        
        spoofing_result = self.wids.detect_protocol_anomalies(
            WirelessProtocol.BLUETOOTH_LE, spoofing_traffic
        )
        assert any(anomaly["type"] == "unknown_device" 
                  for anomaly in spoofing_result["anomalies"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])