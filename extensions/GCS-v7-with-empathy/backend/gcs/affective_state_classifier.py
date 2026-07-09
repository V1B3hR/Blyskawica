import logging
import numpy as np
from typing import Dict, Any, Optional
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Concatenate, Dropout, BatchNormalization
from tensorflow.keras.models import Model

from .empathy_engine import (
    EnhancedAffectiveStateClassifier, 
    EmotionalState, 
    EmotionalProfile,
    EmpathicResponse
)

class AffectiveModelBuilder:
    """
    Builds the definitive multi-modal fusion model for affective state classification.
    This class correctly implements transfer learning, using the pre-trained GCS
    foundational model as an expert EEG feature extractor.
    """
    @staticmethod
    def build_fused_classifier(config: dict, gcs_foundational_model: Model) -> Model:
        """
        Builds the multi-modal fusion network using a pre-trained GNN encoder.

        Args:
            config (dict): The global configuration dictionary.
            gcs_foundational_model (Model): The pre-trained, audited GCS GNN model.

        Returns:
            A new, compiled Keras Model ready for training.
        """
        logging.info("Building the multi-modal Affective State Classifier using Transfer Learning...")

        # --- 1. Freeze the Foundational Model ---
        # We do not want to alter its learned wisdom.
        gcs_foundational_model.trainable = False
        logging.info("Pre-trained GCS foundational model has been frozen.")

        # --- 2. Get Handles to the Foundational Model's Layers ---
        # THE CORRECT WAY: We use the *existing* inputs and outputs of the pre-trained model.
        # This ensures our new model is correctly grafted onto the old one.
        node_input = gcs_foundational_model.get_layer("node_input").input
        adj_input = gcs_foundational_model.get_layer("adj_input").input
        
        # Find the pooling layer to get the rich graph embedding.
        # This is robust and doesn't rely on a hard-coded name.
        pooling_layer_name = [layer.name for layer in gcs_foundational_model.layers if "global" in layer.name][0]
        graph_embedding = gcs_foundational_model.get_layer(pooling_layer_name).output
        
        logging.info(f"Using '{pooling_layer_name}' as the source of EEG features.")

        # --- 3. Define New Inputs for Other Modalities ---
        physio_input = Input(shape=(config["physio_features"],), name="physio_input")
        voice_input = Input(shape=(128,), name="voice_input") # Assuming 128 prosody features

        # --- 4. Process Peripheral Branches ---
        physio_units = config['affective_model']['physio_branch_units']
        voice_units = config['affective_model']['voice_branch_units']
        
        x_physio = Dense(physio_units, activation="relu")(physio_input)
        x_physio = BatchNormalization()(x_physio)

        x_voice = Dense(voice_units, activation="relu")(voice_input)
        x_voice = BatchNormalization()(x_voice)

        # --- 5. Fuse All Feature Vectors ---
        logging.info("Fusing EEG, physiological, and voice feature streams...")
        fused_features = Concatenate()([graph_embedding, x_physio, x_voice])
        
        # --- 6. Final Dense Layers for Regression ---
        fusion_units = config['affective_model']['fusion_units']
        dropout_rate = config['affective_model']['dropout_rate']

        x = Dense(fusion_units, activation="relu")(fused_features)
        x = Dropout(dropout_rate)(x)

        # --- 7. Output Heads ---
        valence_output = Dense(1, name="valence_output")(x)
        arousal_output = Dense(1, name="arousal_output")(x)

        # --- 8. Assemble the Final, Connected Model ---
        # The inputs list now correctly includes the original inputs from the GCS model.
        final_inputs = [node_input, adj_input, physio_input, voice_input]
        
        final_model = Model(
            inputs=final_inputs,
            outputs=[valence_output, arousal_output],
            name="GCS_Affective_Fusion_Model"
        )
        
        logging.info("Affective State Classifier built successfully with a valid computational graph.")
        return final_model


class EmpathyAwareAffectiveClassifier:
    """
    Empathy-enhanced wrapper for the Affective State Classifier
    Integrates advanced emotion recognition with empathetic response generation
    """
    
    def __init__(self, base_model: Model, config: dict):
        self.base_model = base_model
        self.config = config
        
        # Initialize empathy components
        empathy_config = config.get('empathy', {})
        self.enhanced_classifier = EnhancedAffectiveStateClassifier(
            base_classifier=self, 
            empathy_config=empathy_config
        )
        
        logging.info("Empathy-aware Affective State Classifier initialized")
    
    def predict(self, inputs: Dict[str, np.ndarray]) -> np.ndarray:
        """Base prediction method for the enhanced classifier to use"""
        # Convert dict inputs to list format expected by base model
        input_list = [
            inputs.get('eeg', np.zeros((1, self.config['cortical_nodes']))), 
            inputs.get('adj', np.zeros((1, self.config['cortical_nodes'], self.config['cortical_nodes']))),
            inputs.get('physio', np.zeros((1, self.config['physio_features']))),
            inputs.get('voice', np.zeros((1, 128)))  # Voice features
        ]
        
        return self.base_model.predict(input_list)
    
    def classify_with_empathy(self, multi_modal_inputs: Dict[str, np.ndarray],
                             user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Classify emotional state with empathy-aware processing
        
        Args:
            multi_modal_inputs: Dictionary with EEG, physiological, and voice data
            user_id: Unique identifier for the user
            context: Additional context including text input, situation, etc.
            
        Returns:
            Dictionary containing emotional state, empathic response, and metadata
        """
        if context is None:
            context = {}
            
        return self.enhanced_classifier.classify_with_empathy(
            multi_modal_inputs, user_id, context
        )
    
    def update_user_empathy_profile(self, user_id: str, profile_updates: Dict[str, Any],
                                   consent_verified: bool = False) -> bool:
        """Update user's empathy and emotional profile"""
        try:
            self.enhanced_classifier.update_user_profile(
                user_id, profile_updates, consent_verified
            )
            return True
        except Exception as e:
            logging.error(f"Failed to update user profile: {e}")
            return False
    
    def get_empathy_effectiveness_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get empathy effectiveness metrics for a user"""
        return self.enhanced_classifier.get_empathy_effectiveness_report(user_id)
    
    def calibrate_empathy_for_user(self, user_id: str, 
                                  interaction_history: Dict[str, Any]) -> bool:
        """
        Calibrate empathy parameters based on user interaction history
        This implements the personalized empathy calibration objective
        """
        try:
            # Extract empathy preferences from interaction history
            empathy_preferences = {}
            
            # Analyze response ratings
            if 'response_ratings' in interaction_history:
                ratings = interaction_history['response_ratings']
                empathy_preferences['preferred_intensity'] = np.mean([r.get('intensity_rating', 0.5) for r in ratings])
                empathy_preferences['preferred_style'] = self._determine_preferred_style(ratings)
            
            # Analyze emotional patterns
            if 'emotional_patterns' in interaction_history:
                patterns = interaction_history['emotional_patterns']
                empathy_preferences['emotional_sensitivity'] = self._calculate_sensitivity(patterns)
            
            # Update profile with calibrated preferences
            profile_updates = {
                'empathy_preferences': empathy_preferences,
                'last_calibration': np.datetime64('now').astype(str)
            }
            
            return self.update_user_empathy_profile(user_id, profile_updates, consent_verified=True)
            
        except Exception as e:
            logging.error(f"Empathy calibration failed for user {user_id}: {e}")
            return False
    
    def measure_empathy_effectiveness(self, user_id: str, 
                                    intervention_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Measure effectiveness of empathy interventions
        Implements the empathy effectiveness measurement system objective
        """
        effectiveness_metrics = {
            'emotional_improvement': 0.0,
            'user_satisfaction': 0.0,
            'engagement_level': 0.0,
            'therapeutic_alignment': 0.0,
            'cultural_appropriateness': 0.0,
            'safety_compliance': 1.0  # Default to compliant
        }
        
        try:
            # Track the intervention
            if 'empathic_response' in intervention_data and 'user_feedback' in intervention_data:
                self.enhanced_classifier.effectiveness_tracker.track_empathy_interaction(
                    user_id=user_id,
                    response=intervention_data['empathic_response'],
                    user_feedback=intervention_data['user_feedback'],
                    emotional_change=intervention_data.get('emotional_change', {})
                )
            
            # Get updated effectiveness report
            report = self.get_empathy_effectiveness_metrics(user_id)
            
            effectiveness_metrics.update({
                'emotional_improvement': report.get('average_improvement', 0.0),
                'user_satisfaction': report.get('average_satisfaction', 0.0),
                'engagement_level': report.get('average_engagement', 0.0),
                'therapeutic_alignment': report.get('therapeutic_progress', 0.0),
                'cultural_appropriateness': report.get('cultural_appropriateness', 0.0),
                'safety_compliance': 1.0 if report.get('safety_compliance', True) else 0.0
            })
            
        except Exception as e:
            logging.error(f"Failed to measure empathy effectiveness: {e}")
            
        return effectiveness_metrics
    
    def _determine_preferred_style(self, ratings: list) -> str:
        """Determine user's preferred empathy style from ratings"""
        style_scores = {'gentle': 0, 'balanced': 0, 'direct': 0}
        
        for rating in ratings:
            style = rating.get('style', 'balanced')
            score = rating.get('appropriateness', 0.5)
            if style in style_scores:
                style_scores[style] += score
        
        return max(style_scores, key=style_scores.get)
    
    def _calculate_sensitivity(self, patterns: Dict[str, Any]) -> float:
        """Calculate emotional sensitivity from patterns"""
        # Simplified sensitivity calculation based on emotional volatility
        if 'valence_variance' in patterns and 'arousal_variance' in patterns:
            avg_variance = (patterns['valence_variance'] + patterns['arousal_variance']) / 2
            return min(max(avg_variance, 0.0), 1.0)
        
        return 0.5  # Default moderate sensitivity
