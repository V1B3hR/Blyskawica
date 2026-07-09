"""
RAVDESS Dataset Loader

RAVDESS (Ryerson Audio-Visual Database of Emotional Speech and Song)
- 24 actors (12 male, 12 female)
- 8 emotions: neutral, calm, happy, sad, angry, fearful, disgust, surprised
- Audio files with speech and song

Dataset structure expected:
  data/ravdess/ directory with actor subdirectories
  Audio files named: XX-XX-XX-XX-XX-XX-XX.wav
  Emotion codes: 01=neutral, 02=calm, 03=happy, 04=sad, 05=angry, 06=fearful, 07=disgust, 08=surprised
"""

import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from ..multimodal_schema import (
    MultiModalSample, ModalityData, DatasetInterface
)


class RAVDESSLoader(DatasetInterface):
    """
    Loader for RAVDESS dataset
    
    Loads pre-extracted voice features or generates synthetic features
    Maps emotion labels to categorical taxonomy
    """
    
    # Emotion mapping from RAVDESS to our 28-category taxonomy
    EMOTION_MAP = {
        1: 24,   # neutral -> boredom (closest match)
        2: 5,    # calm -> contentment
        3: 1,    # happy -> joy
        4: 15,   # sad -> sadness
        5: 10,   # angry -> anger
        6: 11,   # fearful -> fear
        7: 14,   # disgust -> frustration (closest match)
        8: 22,   # surprised -> surprise
    }
    
    def __init__(self, 
                 dataset_path: str,
                 feature_extractor: Optional[Any] = None,
                 feature_dim: int = 128):
        """
        Args:
            dataset_path: Path to RAVDESS directory or pre-extracted features .npz
            feature_extractor: Optional feature extraction function
            feature_dim: Dimensionality of voice features
        """
        self.dataset_path = dataset_path
        self.feature_extractor = feature_extractor
        self.feature_dim = feature_dim
        self.samples = []
        self._loaded = False
        
        logging.info(f"Initializing RAVDESS loader for {dataset_path}")
    
    def load(self) -> List[MultiModalSample]:
        """Load all samples from dataset"""
        if self._loaded:
            return self.samples
        
        # Check for pre-extracted features
        if self.dataset_path.endswith('.npz'):
            return self._load_from_npz()
        
        if not os.path.exists(self.dataset_path):
            logging.warning(f"RAVDESS dataset not found at {self.dataset_path}, using simulation")
            return self._simulate_data()
        
        # Directory-based loading would require audio processing
        # For now, use simulation
        logging.warning("Directory-based RAVDESS loading requires audio processing. Using simulation.")
        return self._simulate_data()
    
    def _load_from_npz(self) -> List[MultiModalSample]:
        """Load from pre-extracted features file"""
        try:
            data = np.load(self.dataset_path)
            logging.info(f"Loading RAVDESS features from {self.dataset_path}")
            
            voice_features = data.get('voice', data.get('features'))
            emotion_labels = data.get('emotion', data.get('labels'))
            actor_ids = data.get('actor', data.get('subject_id'))
            
            if voice_features is None:
                logging.warning("No voice features found in file")
                return self._simulate_data()
            
            n_samples = voice_features.shape[0]
            logging.info(f"Loaded {n_samples} RAVDESS samples")
            
            for i in range(n_samples):
                sample = MultiModalSample()
                
                sample.voice = ModalityData(
                    data=voice_features[i].astype(np.float32),
                    available=True
                )
                
                # Map emotion label
                if emotion_labels is not None and i < len(emotion_labels):
                    ravdess_emotion = int(emotion_labels[i])
                    sample.categorical_label = self.EMOTION_MAP.get(ravdess_emotion, 0)
                    
                    # Estimate valence/arousal from categorical
                    sample.valence, sample.arousal = self._categorical_to_va(sample.categorical_label)
                
                # Actor ID
                if actor_ids is not None and i < len(actor_ids):
                    sample.user_id = f"ravdess_actor_{int(actor_ids[i])}"
                else:
                    sample.user_id = f"ravdess_actor_{i % 24}"
                
                self.samples.append(sample)
            
            logging.info(f"Successfully loaded {len(self.samples)} RAVDESS samples")
            self._loaded = True
            return self.samples
            
        except Exception as e:
            logging.error(f"Error loading RAVDESS features: {e}", exc_info=True)
            return self._simulate_data()
    
    def _categorical_to_va(self, category: int) -> tuple:
        """Estimate valence/arousal from categorical emotion"""
        # Rough mapping based on Russell's circumplex model
        va_map = {
            0: (0.6, 0.8), 1: (0.8, 0.6), 2: (0.7, 0.7),   # excitement, joy, enthusiasm
            5: (0.6, 0.3), 6: (0.7, 0.2), 7: (0.5, 0.3),   # contentment, peacefulness, gratitude
            10: (-0.6, 0.8), 11: (-0.7, 0.8), 12: (-0.5, 0.7),  # anger, fear, anxiety
            15: (-0.6, 0.3), 16: (-0.8, 0.2), 17: (-0.7, 0.3),  # sadness, depression, loneliness
            22: (0.0, 0.7), 24: (0.0, 0.2),  # surprise, boredom
        }
        return va_map.get(category, (0.0, 0.5))
    
    def _simulate_data(self, n_samples: int = 800) -> List[MultiModalSample]:
        """Generate simulated RAVDESS-like data"""
        logging.info(f"Generating {n_samples} simulated RAVDESS samples")
        
        for i in range(n_samples):
            sample = MultiModalSample()
            
            # Simulated voice features
            sample.voice = ModalityData(
                data=np.random.randn(self.feature_dim).astype(np.float32),
                available=True
            )
            
            # Random emotion from RAVDESS set
            ravdess_emotion = np.random.choice(list(self.EMOTION_MAP.keys()))
            sample.categorical_label = self.EMOTION_MAP[ravdess_emotion]
            sample.valence, sample.arousal = self._categorical_to_va(sample.categorical_label)
            sample.user_id = f"sim_ravdess_{i % 24}"
            
            self.samples.append(sample)
        
        self._loaded = True
        return self.samples
    
    def get_sample(self, idx: int) -> MultiModalSample:
        """Get single sample by index"""
        if not self._loaded:
            self.load()
        return self.samples[idx]
    
    def __len__(self) -> int:
        """Return number of samples"""
        if not self._loaded:
            self.load()
        return len(self.samples)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Return dataset statistics"""
        if not self._loaded:
            self.load()
        
        categories = [s.categorical_label for s in self.samples if s.categorical_label is not None]
        
        return {
            'n_samples': len(self.samples),
            'n_actors': len(set(s.user_id for s in self.samples)),
            'modalities': ['voice'],
            'categorical_distribution': {
                int(k): int(v) for k, v in zip(*np.unique(categories, return_counts=True))
            } if categories else {}
        }
