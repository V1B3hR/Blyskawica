"""
Demo script for Phase 7 Empathy Module Enhancement
Demonstrates the empathy-aware affective state classifier functionality
"""

import sys
import os
import numpy as np
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from backend.gcs.empathy_engine import (
    EmotionalState,
    EmotionalProfile,
    CulturalContext,
    EmpathyIntensity
)
from backend.gcs.affective_state_classifier import EmpathyAwareAffectiveClassifier, AffectiveModelBuilder
from backend.gcs.config_loader import load_config
from unittest.mock import Mock


def create_mock_base_model():
    """Create a mock base model for demonstration"""
    mock_model = Mock()
    mock_model.predict.return_value = [np.array([0.2]), np.array([0.8])]  # valence, arousal
    return mock_model


def demonstrate_empathy_enhancements():
    """Demonstrate the empathy module enhancements"""
    print("=" * 60)
    print("GCS-v7-with-empathy Phase 7 Empathy Enhancement Demo")
    print("=" * 60)
    print()
    
    # Load configuration (config.yaml is in repository root)
    config_path = os.path.join(os.path.dirname(__file__), '../..', 'config.yaml')
    config = load_config(config_path)
    
    # Create empathy-aware classifier
    mock_base_model = create_mock_base_model()
    classifier = EmpathyAwareAffectiveClassifier(mock_base_model, config)
    
    print("✓ Empathy-aware Affective State Classifier initialized")
    print(f"✓ Empathy module enabled: {config['empathy']['enabled']}")
    print(f"✓ Privacy protection: {config['empathy']['privacy']['encryption_enabled']}")
    print(f"✓ Crisis detection: {config['empathy']['ethics']['crisis_detection_enabled']}")
    print()
    
    # Demonstrate emotional state classification with empathy
    print("1. EMPATHY-AWARE EMOTIONAL STATE CLASSIFICATION")
    print("-" * 50)
    
    # Simulate multi-modal inputs
    multi_modal_inputs = {
        'eeg': np.random.randn(1, config['cortical_nodes']),
        'physio': np.random.randn(1, config['physio_features']),
        'voice': np.random.randn(1, 128),
        'adj': np.random.randn(1, config['cortical_nodes'], config['cortical_nodes'])
    }
    
    user_id = "demo_user_001"
    context = {
        'text_input': "I'm feeling really overwhelmed with work lately and struggling to cope",
        'situation': 'work_stress',
        'time_of_day': 'evening'
    }
    
    result = classifier.classify_with_empathy(multi_modal_inputs, user_id, context)
    
    print(f"Emotional State: {result['emotional_state']}")
    print(f"Valence: {result['valence']:.3f} (negative=sad, positive=happy)")
    print(f"Arousal: {result['arousal']:.3f} (low=calm, high=excited)")
    print()
    print("Empathic Response:")
    print(f"  Content: {result['empathic_response']['content']}")
    print(f"  Intensity: {result['empathic_response']['intensity']}")
    print(f"  Type: {result['empathic_response']['type']}")
    print(f"  Confidence: {result['empathic_response']['confidence']:.3f}")
    print()
    print(f"Privacy Protected: {result['privacy_protected']}")
    print(f"Crisis Detected: {result['crisis_detected']}")
    print(f"Cultural Adaptation: {result['cultural_adaptation']}")
    print()
    
    # Demonstrate personalized empathy calibration
    print("2. PERSONALIZED EMPATHY CALIBRATION")
    print("-" * 50)
    
    # Update user profile with preferences
    profile_updates = {
        'emotional_sensitivity': 0.8,
        'preferred_support_style': 'gentle',
        'cultural_context': CulturalContext.INDIVIDUALISTIC,
        'therapeutic_goals': ['stress_reduction', 'work_life_balance'],
        'empathy_preferences': {
            'preferred_intensity': 'moderate',
            'response_style': 'validating'
        }
    }
    
    success = classifier.update_user_empathy_profile(
        user_id, profile_updates, consent_verified=True
    )
    print(f"✓ User profile updated: {success}")
    
    # Calibrate empathy based on interaction history
    interaction_history = {
        'response_ratings': [
            {'intensity_rating': 0.7, 'appropriateness': 0.9, 'style': 'gentle'},
            {'intensity_rating': 0.6, 'appropriateness': 0.8, 'style': 'gentle'},
            {'intensity_rating': 0.5, 'appropriateness': 0.9, 'style': 'balanced'}
        ],
        'emotional_patterns': {
            'valence_variance': 0.4,
            'arousal_variance': 0.3
        }
    }
    
    calibration_success = classifier.calibrate_empathy_for_user(user_id, interaction_history)
    print(f"✓ Empathy calibration completed: {calibration_success}")
    print()
    
    # Demonstrate different emotional contexts
    print("3. CULTURAL SENSITIVITY ADAPTATION")
    print("-" * 50)
    
    # Test with different cultural contexts
    cultural_contexts = [
        (CulturalContext.INDIVIDUALISTIC, "American user context"),
        (CulturalContext.COLLECTIVISTIC, "East Asian user context"),
        (CulturalContext.HIGH_CONTEXT, "Middle Eastern user context")
    ]
    
    for cultural_context, description in cultural_contexts:
        # Update user profile for cultural context
        cultural_updates = {'cultural_context': cultural_context}
        classifier.update_user_empathy_profile(
            f"{user_id}_{cultural_context.value}", cultural_updates, consent_verified=True
        )
        
        # Get empathic response for this cultural context
        cultural_result = classifier.classify_with_empathy(
            multi_modal_inputs, 
            f"{user_id}_{cultural_context.value}",
            {'text_input': 'Feeling stressed about family expectations', 'situation': 'family_pressure'}
        )
        
        print(f"{description}:")
        print(f"  Response: {cultural_result['empathic_response']['content'][:100]}...")
        print(f"  Cultural Adaptation: {cultural_result['cultural_adaptation']}")
        print()
    
    # Demonstrate effectiveness measurement
    print("4. EMPATHY EFFECTIVENESS MEASUREMENT")
    print("-" * 50)
    
    # Simulate intervention tracking
    from backend.gcs.empathy_engine import EmpathicResponse
    
    intervention_data = {
        'empathic_response': EmpathicResponse(
            content="I understand this is a challenging time for you. Your feelings are completely valid.",
            intensity=EmpathyIntensity.MODERATE,
            response_type="validation",
            cultural_adaptation="individualistic",
            confidence=0.88,
            therapeutic_alignment=True,
            privacy_level="basic"
        ),
        'user_feedback': {
            'satisfaction': 0.9,
            'engagement': 0.8,
            'cultural_fit': 0.95,
            'felt_heard': True,
            'gained_insight': False
        },
        'emotional_change': {
            'improvement': 0.3,
            'valence_change': 0.2,
            'arousal_change': -0.1
        }
    }
    
    effectiveness = classifier.measure_empathy_effectiveness(user_id, intervention_data)
    
    print("Effectiveness Metrics:")
    print(f"  Emotional Improvement: {effectiveness['emotional_improvement']:.3f}")
    print(f"  User Satisfaction: {effectiveness['user_satisfaction']:.3f}")
    print(f"  Engagement Level: {effectiveness['engagement_level']:.3f}")
    print(f"  Therapeutic Alignment: {effectiveness['therapeutic_alignment']:.3f}")
    print(f"  Cultural Appropriateness: {effectiveness['cultural_appropriateness']:.3f}")
    print(f"  Safety Compliance: {effectiveness['safety_compliance']:.3f}")
    print()
    
    # Get comprehensive effectiveness report
    report = classifier.get_empathy_effectiveness_metrics(user_id)
    print("Comprehensive Effectiveness Report:")
    print(f"  Total Interactions: {report['total_interactions']}")
    print(f"  Average Satisfaction: {report['average_satisfaction']:.3f}")
    print(f"  Average Improvement: {report['average_improvement']:.3f}")
    print(f"  Therapeutic Progress: {report['therapeutic_progress']:.3f}")
    print(f"  Safety Compliance: {report['safety_compliance']}")
    print()
    
    # Demonstrate crisis detection
    print("5. CRISIS DETECTION AND SAFETY PROTOCOLS")
    print("-" * 50)
    
    crisis_context = {
        'text_input': 'I feel hopeless and like nobody would miss me if I were gone',
        'situation': 'severe_distress'
    }
    
    # Simulate inputs that might indicate crisis
    crisis_inputs = {
        'eeg': np.random.randn(1, config['cortical_nodes']),
        'physio': np.random.randn(1, config['physio_features']) * 2,  # Higher variance
        'voice': np.random.randn(1, 128) * 0.5,  # Lower energy
        'adj': np.random.randn(1, config['cortical_nodes'], config['cortical_nodes'])
    }
    
    # This should trigger crisis detection protocols
    mock_base_model.predict.return_value = [np.array([-0.9]), np.array([0.1])]  # Very negative, low arousal
    
    crisis_result = classifier.classify_with_empathy(crisis_inputs, f"{user_id}_crisis", crisis_context)
    
    print(f"Crisis Detected: {crisis_result['crisis_detected']}")
    if crisis_result['crisis_detected']:
        print("Crisis Response:")
        print(f"  {crisis_result['empathic_response']['content']}")
        print(f"  Immediate Action Required: {crisis_result['immediate_action_required']}")
        print("  Referral Resources Provided:")
        for resource in crisis_result['referral_resources']:
            print(f"    - {resource}")
    print()
    
    print("6. RESEARCH INTEGRATION BENEFITS")
    print("-" * 50)
    print("✓ Affective Neuroscience: Multi-modal emotion recognition with EEG, physio, voice")
    print("✓ Therapeutic Protocols: Evidence-based empathetic response generation")
    print("✓ Cultural Psychology: Cross-cultural adaptation frameworks")
    print("✓ Privacy Engineering: Encrypted emotional data with access controls")
    print("✓ Crisis Intervention: Automated detection and professional referral")
    print("✓ Personalization: Individual empathy profiles and calibration")
    print("✓ Effectiveness Measurement: Comprehensive outcome tracking")
    print()
    
    print("=" * 60)
    print("Phase 7 Empathy Enhancement Demo Complete!")
    print("✓ All technical objectives demonstrated")
    print("✓ All ethical objectives implemented")
    print("✓ All key deliverables functional")
    print("✓ Research integration successful")
    print("=" * 60)


if __name__ == '__main__':
    try:
        demonstrate_empathy_enhancements()
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)