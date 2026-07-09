"""
DEAP Dataset Loader

DEAP (Database for Emotion Analysis using Physiological Signals)
- 32 participants
- 40 music video trials per participant  
- EEG (32 channels), physiological (8 channels)
- Self-reported valence, arousal, dominance, liking (1-9 scale)

Dataset structure expected:
  data/deap_dataset.npz with keys:
    - 'eeg': (samples, channels, timesteps)
    - 'physio': (samples, physio_features)  
    - 'valence': (samples,) ratings 1-9
    - 'arousal': (samples,) ratings 1-9
    - Optional: 'dominance', 'subject_id'
"""

import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from ..multimodal_schema import (
    MultiModalSample, ModalityData, DatasetInterface
)


class DEAPLoader(DatasetInterface):
    """
    Loader for DEAP dataset
    
    Normalizes ratings to standard ranges:
    - Valence: [1-9] -> [-1, 1]
    - Arousal: [1-9] -> [0, 1]
    """
    
    def __init__(self, 
                 dataset_path: str,
                 normalize_eeg: bool = True,
                 source_localization: Optional[Any] = None,
                 include_physio: bool = True):
        """
        Args:
            dataset_path: Path to DEAP .npz file
            normalize_eeg: Whether to z-score normalize EEG
            source_localization: Optional projection matrix or function for EEG source localization
            include_physio: Whether to include physiological signals
        """
        self.dataset_path = dataset_path
        self.normalize_eeg = normalize_eeg
        self.source_localization = source_localization
        self.include_physio = include_physio
        self.samples = []
        self._loaded = False
        
        logging.info(f"Initializing DEAP loader for {dataset_path}")
    
    def load(self) -> List[MultiModalSample]:
        """Load all samples from dataset"""
        if self._loaded:
            return self.samples
        
        if not os.path.exists(self.dataset_path):
            logging.warning(f"DEAP dataset not found at {self.dataset_path}, using simulation")
            return self._simulate_data()
        
        try:
            data = np.load(self.dataset_path)
            logging.info(f"Loading DEAP data from {self.dataset_path}")
            logging.info(f"Available keys: {data.files}")
            
            # Extract data arrays
            eeg_data = self._get_array(data, ['eeg', 'signals', 'data'])
            physio_data = self._get_array(data, ['physio', 'physiological', 'bio']) if self.include_physio else None
            valence = self._get_array(data, ['valence', 'val'])
            arousal = self._get_array(data, ['arousal', 'aro'])
            subject_ids = self._get_array(data, ['subject_id', 'subject', 'participant'])
            
            if eeg_data is None:
                logging.warning("No EEG data found in DEAP file")
                return self._simulate_data()
            
            n_samples = eeg_data.shape[0]
            logging.info(f"Loaded {n_samples} samples from DEAP")
            logging.info(f"EEG shape: {eeg_data.shape}")
            
            # Process each sample
            for i in range(n_samples):
                sample = MultiModalSample()
                
                # Process EEG
                eeg_sample = eeg_data[i]
                
                # Apply source localization if provided
                if self.source_localization is not None:
                    if callable(self.source_localization):
                        eeg_sample = self.source_localization(eeg_sample)
                    elif isinstance(self.source_localization, np.ndarray):
                        # Projection matrix: (channels, nodes)
                        # Input: (channels, timesteps) -> Output: (nodes, timesteps)
                        eeg_sample = self.source_localization.T @ eeg_sample
                
                # Normalize EEG
                if self.normalize_eeg:
                    eeg_sample = (eeg_sample - eeg_sample.mean()) / (eeg_sample.std() + 1e-8)
                
                sample.eeg = ModalityData(
                    data=eeg_sample.astype(np.float32),
                    available=True,
                    metadata={'original_shape': eeg_data[i].shape}
                )
                
                # Process physiological data
                if physio_data is not None and i < len(physio_data):
                    sample.physio = ModalityData(
                        data=physio_data[i].astype(np.float32),
                        available=True
                    )
                
                # Process labels - normalize from [1-9] scale
                if valence is not None and i < len(valence):
                    # Normalize to [-1, 1]
                    sample.valence = float((valence[i] - 5.0) / 4.0)
                
                if arousal is not None and i < len(arousal):
                    # Normalize to [0, 1]
                    sample.arousal = float((arousal[i] - 1.0) / 8.0)
                
                # Map to categorical emotion (simplified heuristic)
                if sample.valence is not None and sample.arousal is not None:
                    sample.categorical_label = self._map_to_categorical(
                        sample.valence, sample.arousal
                    )
                
                # User ID
                if subject_ids is not None and i < len(subject_ids):
                    sample.user_id = f"deap_subject_{int(subject_ids[i])}"
                else:
                    sample.user_id = f"deap_subject_{i % 32}"
                
                self.samples.append(sample)
            
            logging.info(f"Successfully loaded {len(self.samples)} DEAP samples")
            self._loaded = True
            return self.samples
            
        except Exception as e:
            logging.error(f"Error loading DEAP data: {e}", exc_info=True)
            return self._simulate_data()
    
    def _get_array(self, data_dict, possible_keys: List[str]) -> Optional[np.ndarray]:
        """Try to get array using multiple possible key names"""
        for key in possible_keys:
            if key in data_dict.files:
                return data_dict[key]
        return None
    
    def _map_to_categorical(self, valence: float, arousal: float) -> int:
        """
        Map valence/arousal to 28-category emotion taxonomy
        
        Uses Russell's circumplex model mapping:
        - High arousal positive -> excitement, joy, enthusiasm
        - Low arousal positive -> contentment, peacefulness, gratitude
        - High arousal negative -> anger, fear, anxiety
        - Low arousal negative -> sadness, depression, loneliness
        """
        # Simple quadrant-based mapping
        if valence > 0.3:
            if arousal > 0.6:
                # High arousal positive
                return np.random.choice([0, 1, 2, 3, 4])  # excitement, joy, enthusiasm, euphoria, amusement
            else:
                # Low arousal positive
                return np.random.choice([5, 6, 7, 8, 9])  # contentment, peacefulness, gratitude, serenity, satisfaction
        else:
            if arousal > 0.6:
                # High arousal negative
                return np.random.choice([10, 11, 12, 13, 14])  # anger, fear, anxiety, panic, frustration
            else:
                # Low arousal negative
                return np.random.choice([15, 16, 17, 18, 19])  # sadness, depression, loneliness, melancholy, hopelessness
    
    def _simulate_data(self, n_samples: int = 1000) -> List[MultiModalSample]:
        """Generate simulated DEAP-like data"""
        logging.info(f"Generating {n_samples} simulated DEAP samples")
        
        for i in range(n_samples):
            sample = MultiModalSample()
            
            # Simulated EEG (32 channels, 128 Hz, 3 seconds = 384 samples)
            eeg_shape = (32, 384)
            if self.source_localization is not None:
                if isinstance(self.source_localization, np.ndarray):
                    eeg_shape = (self.source_localization.shape[1], 384)  # (nodes, timesteps)
                else:
                    eeg_shape = (68, 384)  # Assume source localization to 68 nodes
            
            sample.eeg = ModalityData(
                data=np.random.randn(*eeg_shape).astype(np.float32),
                available=True
            )
            
            # Simulated physio (8 features: GSR, heart rate, etc.)
            if self.include_physio:
                sample.physio = ModalityData(
                    data=np.random.randn(8).astype(np.float32),
                    available=True
                )
            
            # Random valence/arousal
            sample.valence = np.random.uniform(-1, 1)
            sample.arousal = np.random.uniform(0, 1)
            sample.categorical_label = self._map_to_categorical(sample.valence, sample.arousal)
            sample.user_id = f"sim_subject_{i % 32}"
            
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
        
        stats = {
            'n_samples': len(self.samples),
            'n_subjects': len(set(s.user_id for s in self.samples)),
        }
        
        # Compute valence/arousal distributions
        valences = [s.valence for s in self.samples if s.valence is not None]
        arousals = [s.arousal for s in self.samples if s.arousal is not None]
        
        if valences:
            stats['valence'] = {
                'mean': np.mean(valences),
                'std': np.std(valences),
                'min': np.min(valences),
                'max': np.max(valences)
            }
        
        if arousals:
            stats['arousal'] = {
                'mean': np.mean(arousals),
                'std': np.std(arousals),
                'min': np.min(arousals),
                'max': np.max(arousals)
            }
        
        # Categorical distribution
        categories = [s.categorical_label for s in self.samples if s.categorical_label is not None]
        if categories:
            stats['categorical_distribution'] = {
                int(k): int(v) for k, v in zip(*np.unique(categories, return_counts=True))
            }
        
        return stats
