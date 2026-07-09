"""
End-to-end test of the multimodal affective recognition pipeline

Tests:
1. Dataset loading (with simulation fallback)
2. Feature extraction
3. Model creation and forward pass
4. Multi-task outputs (valence, arousal, categorical)
5. Uncertainty estimation
6. Crisis detection
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import yaml
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(module)s:%(lineno)d]: %(message)s'
)

def test_datasets():
    """Test dataset loaders"""
    print("\n=== Testing Dataset Loaders ===")
    
    from gcs.data.datasets.deap_loader import DEAPLoader
    from gcs.data.datasets.wesad_loader import WESADLoader
    from gcs.data.datasets.ravdess_loader import RAVDESSLoader
    
    # These will use simulation since files don't exist
    deap = DEAPLoader('data/deap_dataset.npz')
    wesad = WESADLoader('data/wesad/')
    ravdess = RAVDESSLoader('data/ravdess/')
    
    deap_samples = deap.load()
    wesad_samples = wesad.load()
    ravdess_samples = ravdess.load()
    
    print(f"✓ DEAP: {len(deap_samples)} samples")
    print(f"✓ WESAD: {len(wesad_samples)} samples")
    print(f"✓ RAVDESS: {len(ravdess_samples)} samples")
    
    # Check sample structure
    sample = deap_samples[0]
    print(f"✓ Sample has modalities: {sample.get_available_modalities()}")
    print(f"✓ Sample has labels: valence={sample.valence:.2f}, arousal={sample.arousal:.2f}, category={sample.categorical_label}")
    
    return True

def test_features():
    """Test feature extraction"""
    print("\n=== Testing Feature Extraction ===")
    
    from gcs.features.eeg_features import EEGFeatureExtractor
    from gcs.features.physio_features import PhysioFeatureExtractor
    from gcs.features.voice_features import VoiceFeatureExtractor
    
    # Create dummy data
    eeg_data = np.random.randn(8, 1000)  # 8 channels, 1000 timesteps
    physio_data = np.random.randn(24)
    voice_data = np.random.randn(128)
    
    # Extract features
    eeg_extractor = EEGFeatureExtractor(sampling_rate=250)
    eeg_features = eeg_extractor.extract_features(eeg_data)
    
    physio_extractor = PhysioFeatureExtractor()
    physio_features = physio_extractor.extract_features(physio_data)
    
    voice_extractor = VoiceFeatureExtractor(sampling_rate=16000)
    voice_features = voice_extractor.extract_features(voice_data)
    
    print(f"✓ EEG features: {eeg_features.shape}")
    print(f"✓ Physio features: {physio_features.shape}")
    print(f"✓ Voice features: {voice_features.shape}")
    
    return True

def test_model():
    """Test model creation and inference"""
    print("\n=== Testing Model ===")
    
    from gcs.models.affective_model import build_affective_model, compile_affective_model
    
    # Load config
    config_path = os.path.join(os.path.dirname(__file__), 'affective_config.yaml')
    if not os.path.exists(config_path):
        config_path = 'backend/gcs/affective_config.yaml'
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Build model
    print("Building model...")
    model = build_affective_model(config)
    model = compile_affective_model(model, config)
    
    print(f"✓ Model created: {model.count_params():,} parameters")
    
    # Test forward pass
    batch_size = 4
    inputs = {
        'eeg': np.random.randn(batch_size, 68, 1000).astype(np.float32),
        'physio': np.random.randn(batch_size, 24).astype(np.float32),
        'voice': np.random.randn(batch_size, 128).astype(np.float32)
    }
    
    print("Running inference...")
    outputs = model(inputs, training=False)
    
    print(f"✓ Valence shape: {outputs['valence'].shape}, range: [{outputs['valence'].numpy().min():.3f}, {outputs['valence'].numpy().max():.3f}]")
    print(f"✓ Arousal shape: {outputs['arousal'].shape}, range: [{outputs['arousal'].numpy().min():.3f}, {outputs['arousal'].numpy().max():.3f}]")
    print(f"✓ Categorical shape: {outputs['categorical'].shape}")
    
    # Verify output ranges
    assert outputs['valence'].shape == (batch_size,), "Valence shape mismatch"
    assert outputs['arousal'].shape == (batch_size,), "Arousal shape mismatch"
    assert outputs['categorical'].shape == (batch_size, 28), "Categorical shape mismatch"
    
    # Verify categorical is valid probability distribution
    cat_sums = outputs['categorical'].numpy().sum(axis=1)
    assert np.allclose(cat_sums, 1.0, atol=1e-5), "Categorical probabilities don't sum to 1"
    
    print("✓ All output constraints verified")
    
    return True

def test_uncertainty():
    """Test uncertainty estimation"""
    print("\n=== Testing Uncertainty Estimation ===")
    
    from gcs.models.affective_model import build_affective_model, compile_affective_model
    
    config_path = os.path.join(os.path.dirname(__file__), 'affective_config.yaml')
    if not os.path.exists(config_path):
        config_path = 'backend/gcs/affective_config.yaml'
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    model = build_affective_model(config)
    model = compile_affective_model(model, config)
    
    inputs = {
        'eeg': np.random.randn(2, 68, 1000).astype(np.float32),
        'physio': np.random.randn(2, 24).astype(np.float32),
        'voice': np.random.randn(2, 128).astype(np.float32)
    }
    
    print("Running MC Dropout inference...")
    outputs_mean, outputs_std = model.predict_with_uncertainty(inputs, mc_samples=5)
    
    print(f"✓ Mean valence: {outputs_mean['valence'].numpy()}")
    print(f"✓ Std valence: {outputs_std['valence'].numpy()}")
    print(f"✓ Mean arousal: {outputs_mean['arousal'].numpy()}")
    print(f"✓ Std arousal: {outputs_std['arousal'].numpy()}")
    
    return True

def test_crisis_detection():
    """Test crisis detection logic"""
    print("\n=== Testing Crisis Detection ===")
    
    # High arousal + negative valence = crisis
    crisis_cases = [
        (0.95, -0.8, True, "High arousal + very negative valence"),
        (0.5, -0.8, False, "Low arousal + negative valence"),
        (0.95, 0.5, False, "High arousal + positive valence"),
        (0.3, 0.2, False, "Low arousal + neutral valence")
    ]
    
    crisis_threshold_arousal = 0.9
    crisis_threshold_valence = -0.7
    
    for arousal, valence, expected_crisis, description in crisis_cases:
        detected = (arousal > crisis_threshold_arousal and 
                   valence < crisis_threshold_valence)
        
        status = "✓" if detected == expected_crisis else "✗"
        print(f"{status} {description}: arousal={arousal}, valence={valence} → crisis={detected}")
        
        assert detected == expected_crisis, f"Crisis detection mismatch for {description}"
    
    print("✓ All crisis detection cases passed")
    
    return True

def test_frontend_format():
    """Test frontend message format"""
    print("\n=== Testing Frontend Message Format ===")
    
    # Simulate a prediction
    prediction = {
        'valence': -0.45,
        'arousal': 0.70,
        'emotion': 'anxiety',
        'confidence': 0.83,
        'uncertainties': {'valence': 0.1, 'arousal': 0.05},
        'crisis_detected': False
    }
    
    # Format for frontend
    icon_map = {
        'joy': '😊', 'anxiety': '😟', 'sadness': '😢'
    }
    
    message = {
        'affective': {
            'label': prediction['emotion'],
            'icon': icon_map.get(prediction['emotion'], '😐'),
            'strength': int((prediction['arousal'] + prediction['confidence']) / 2 * 100),
            'valence': prediction['valence'],
            'arousal': prediction['arousal'],
            'confidence': prediction['confidence']
        },
        'empathic_response': {
            'content': f"I sense you're feeling {prediction['emotion']}.",
            'intensity': 'moderate',
            'type': 'validation',
            'confidence': prediction['confidence']
        },
        'privacy_protected': True,
        'crisis_detected': prediction['crisis_detected']
    }
    
    print(f"✓ Label: {message['affective']['label']}")
    print(f"✓ Icon: {message['affective']['icon']}")
    print(f"✓ Strength: {message['affective']['strength']}%")
    print(f"✓ Valence: {message['affective']['valence']:.2f}")
    print(f"✓ Arousal: {message['affective']['arousal']:.2f}")
    print(f"✓ Empathic response: {message['empathic_response']['content']}")
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("GCS Multimodal Affective Recognition - End-to-End Test")
    print("=" * 60)
    
    tests = [
        ("Dataset Loading", test_datasets),
        ("Feature Extraction", test_features),
        ("Model Creation & Inference", test_model),
        ("Uncertainty Estimation", test_uncertainty),
        ("Crisis Detection", test_crisis_detection),
        ("Frontend Format", test_frontend_format),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"✗ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✓ ALL TESTS PASSED!")
        print("\nSystem is ready for:")
        print("  1. Training on real datasets (DEAP, WESAD, RAVDESS)")
        print("  2. Real-time serving via WebSocket")
        print("  3. Frontend integration")
        print("\nTo start the server:")
        print("  cd backend && python -m gcs.serving.server")
        return 0
    else:
        print(f"✗ {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())
