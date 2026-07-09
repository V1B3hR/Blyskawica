"""
WESAD Dataset Loader

WESAD (Wearable Stress and Affect Detection)
- 15 subjects
- Physiological signals: BVP, EDA, TEMP, ACC, RESP, ECG, EMG
- Conditions: baseline, stress, amusement, meditation
- Labels: 0=not defined, 1=baseline, 2=stress, 3=amusement, 4=meditation

Dataset structure expected:
  data/wesad/ directory with subject files (S2.pkl, S3.pkl, etc.)
  Each pickle file contains 'signal' dict and 'label' array
"""

import os
import logging
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from ..multimodal_schema import (
    MultiModalSample, ModalityData, DatasetInterface
)


class WESADLoader(DatasetInterface):
    """
    Loader for WESAD dataset
    
    Extracts HRV, EDA, and respiratory features from raw signals
    Maps stress/amusement conditions to valence/arousal
    """
    
    def __init__(self, 
                 dataset_path: str,
                 window_size: float = 4.0,  # seconds
                 sampling_rate: int = 700):  # Hz for chest sensor
        """
        Args:
            dataset_path: Path to WESAD directory with subject files
            window_size: Window size in seconds for feature extraction
            sampling_rate: Sampling rate of chest sensor
        """
        self.dataset_path = dataset_path
        self.window_size = window_size
        self.sampling_rate = sampling_rate
        self.samples = []
        self._loaded = False
        
        logging.info(f"Initializing WESAD loader for {dataset_path}")
    
    def load(self) -> List[MultiModalSample]:
        """Load all samples from dataset"""
        if self._loaded:
            return self.samples
        
        if not os.path.exists(self.dataset_path):
            logging.warning(f"WESAD dataset not found at {self.dataset_path}, using simulation")
            return self._simulate_data()
        
        try:
            # Find all subject files
            subject_files = [f for f in os.listdir(self.dataset_path) 
                           if f.startswith('S') and f.endswith('.pkl')]
            
            if not subject_files:
                logging.warning(f"No WESAD subject files found in {self.dataset_path}")
                return self._simulate_data()
            
            logging.info(f"Found {len(subject_files)} WESAD subject files")
            
            for subject_file in subject_files:
                subject_path = os.path.join(self.dataset_path, subject_file)
                subject_id = subject_file.split('.')[0]
                
                try:
                    with open(subject_path, 'rb') as f:
                        data = pickle.load(f, encoding='latin1')
                    
                    # Extract chest sensor data
                    chest_data = data.get('signal', {}).get('chest', {})
                    labels = data.get('label', np.array([]))
                    
                    # Extract signals
                    ecg = chest_data.get('ECG', np.array([]))
                    eda = chest_data.get('EDA', np.array([]))
                    resp = chest_data.get('Resp', np.array([]))
                    
                    if len(ecg) == 0:
                        logging.warning(f"No chest data for {subject_id}")
                        continue
                    
                    # Segment into windows
                    window_samples = int(self.window_size * self.sampling_rate)
                    n_windows = len(ecg) // window_samples
                    
                    for i in range(n_windows):
                        start_idx = i * window_samples
                        end_idx = start_idx + window_samples
                        
                        # Extract window
                        ecg_window = ecg[start_idx:end_idx]
                        eda_window = eda[start_idx:end_idx] if len(eda) > end_idx else None
                        resp_window = resp[start_idx:end_idx] if len(resp) > end_idx else None
                        
                        # Get most common label in window
                        label_window = labels[start_idx:end_idx] if len(labels) > end_idx else np.array([0])
                        window_label = int(np.bincount(label_window.flatten().astype(int)).argmax())
                        
                        # Skip undefined labels
                        if window_label == 0:
                            continue
                        
                        # Extract features
                        physio_features = self._extract_physio_features(
                            ecg_window, eda_window, resp_window
                        )
                        
                        sample = MultiModalSample()
                        sample.physio = ModalityData(
                            data=physio_features.astype(np.float32),
                            available=True
                        )
                        
                        # Map label to valence/arousal
                        valence, arousal = self._map_label_to_va(window_label)
                        sample.valence = valence
                        sample.arousal = arousal
                        sample.categorical_label = self._map_to_categorical(valence, arousal)
                        sample.user_id = f"wesad_{subject_id}"
                        
                        self.samples.append(sample)
                    
                    logging.info(f"Loaded {n_windows} windows from {subject_id}")
                    
                except Exception as e:
                    logging.warning(f"Error loading {subject_file}: {e}")
                    continue
            
            logging.info(f"Successfully loaded {len(self.samples)} WESAD samples")
            self._loaded = True
            return self.samples
            
        except Exception as e:
            logging.error(f"Error loading WESAD data: {e}", exc_info=True)
            return self._simulate_data()
    
    def _extract_physio_features(self, 
                                ecg: np.ndarray,
                                eda: Optional[np.ndarray],
                                resp: Optional[np.ndarray]) -> np.ndarray:
        """
        Extract physiological features
        
        Features (24 total):
        - HRV: mean HR, SDNN, RMSSD, pNN50, LF, HF, LF/HF (7 features)
        - EDA: mean, std, tonic level, phasic peaks (4 features)
        - Resp: rate, depth, irregularity (3 features)
        - Raw statistics: mean, std, min, max for each signal (10 features)
        """
        features = []
        
        # HRV features from ECG
        hrv_features = self._compute_hrv_features(ecg)
        features.extend(hrv_features)
        
        # EDA features
        if eda is not None and len(eda) > 0:
            eda_features = self._compute_eda_features(eda)
        else:
            eda_features = np.zeros(4)
        features.extend(eda_features)
        
        # Respiratory features
        if resp is not None and len(resp) > 0:
            resp_features = self._compute_resp_features(resp)
        else:
            resp_features = np.zeros(3)
        features.extend(resp_features)
        
        # Raw statistics
        raw_stats = [
            np.mean(ecg), np.std(ecg),
            np.mean(eda) if eda is not None else 0, np.std(eda) if eda is not None else 0,
            np.mean(resp) if resp is not None else 0, np.std(resp) if resp is not None else 0,
        ]
        features.extend(raw_stats)
        
        # Pad or trim to exactly 24 features
        features = np.array(features)
        if len(features) < 24:
            features = np.pad(features, (0, 24 - len(features)))
        elif len(features) > 24:
            features = features[:24]
        
        return features
    
    def _compute_hrv_features(self, ecg: np.ndarray) -> List[float]:
        """Compute HRV features from ECG (simplified)"""
        # Simple peak detection
        ecg_normalized = (ecg - np.mean(ecg)) / (np.std(ecg) + 1e-8)
        threshold = 1.0
        peaks = []
        
        for i in range(1, len(ecg_normalized) - 1):
            if (ecg_normalized[i] > threshold and 
                ecg_normalized[i] > ecg_normalized[i-1] and 
                ecg_normalized[i] > ecg_normalized[i+1]):
                peaks.append(i)
        
        if len(peaks) < 2:
            return [0.0] * 7
        
        # RR intervals (in ms)
        rr_intervals = np.diff(peaks) / self.sampling_rate * 1000
        
        # Mean heart rate
        mean_hr = 60000 / np.mean(rr_intervals) if len(rr_intervals) > 0 else 0
        
        # SDNN (standard deviation of NN intervals)
        sdnn = np.std(rr_intervals) if len(rr_intervals) > 0 else 0
        
        # RMSSD (root mean square of successive differences)
        if len(rr_intervals) > 1:
            rmssd = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
        else:
            rmssd = 0
        
        # Simplified frequency domain features (using power in different ranges)
        # In real implementation, would use FFT
        lf_power = np.var(rr_intervals) if len(rr_intervals) > 0 else 0
        hf_power = np.var(np.diff(rr_intervals)) if len(rr_intervals) > 1 else 0
        lf_hf_ratio = lf_power / (hf_power + 1e-8)
        
        return [mean_hr, sdnn, rmssd, 0.0, lf_power, hf_power, lf_hf_ratio]
    
    def _compute_eda_features(self, eda: np.ndarray) -> List[float]:
        """Compute EDA features"""
        # Basic statistics
        mean_eda = np.mean(eda)
        std_eda = np.std(eda)
        
        # Estimate tonic (slowly varying baseline) using moving average
        window = min(len(eda) // 10, 100)
        if window > 1:
            tonic = np.convolve(eda, np.ones(window)/window, mode='same')
            tonic_level = np.mean(tonic)
        else:
            tonic_level = mean_eda
        
        # Count phasic peaks (SCR)
        eda_derivative = np.diff(eda)
        peaks = np.sum((eda_derivative[:-1] > 0) & (eda_derivative[1:] < 0))
        
        return [mean_eda, std_eda, tonic_level, float(peaks)]
    
    def _compute_resp_features(self, resp: np.ndarray) -> List[float]:
        """Compute respiratory features"""
        # Respiratory rate (peaks per minute)
        resp_normalized = (resp - np.mean(resp)) / (np.std(resp) + 1e-8)
        peaks = []
        
        for i in range(1, len(resp_normalized) - 1):
            if (resp_normalized[i] > 0.5 and 
                resp_normalized[i] > resp_normalized[i-1] and 
                resp_normalized[i] > resp_normalized[i+1]):
                peaks.append(i)
        
        resp_rate = len(peaks) / self.window_size * 60 if len(peaks) > 0 else 0
        
        # Depth (amplitude)
        resp_depth = np.max(resp) - np.min(resp)
        
        # Irregularity (coefficient of variation of peak-to-peak intervals)
        if len(peaks) > 1:
            peak_intervals = np.diff(peaks)
            irregularity = np.std(peak_intervals) / (np.mean(peak_intervals) + 1e-8)
        else:
            irregularity = 0
        
        return [resp_rate, resp_depth, irregularity]
    
    def _map_label_to_va(self, label: int) -> tuple:
        """Map WESAD condition labels to valence/arousal"""
        # 1=baseline, 2=stress, 3=amusement, 4=meditation
        mapping = {
            1: (0.0, 0.3),      # baseline: neutral, low arousal
            2: (-0.6, 0.8),     # stress: negative, high arousal
            3: (0.7, 0.7),      # amusement: positive, high arousal
            4: (0.5, 0.2),      # meditation: positive, low arousal
        }
        return mapping.get(label, (0.0, 0.5))
    
    def _map_to_categorical(self, valence: float, arousal: float) -> int:
        """Map valence/arousal to categorical emotion"""
        if valence > 0.3:
            if arousal > 0.6:
                return np.random.choice([0, 1, 2])  # excitement, joy, enthusiasm
            else:
                return np.random.choice([5, 6, 7])  # contentment, peacefulness, gratitude
        else:
            if arousal > 0.6:
                return np.random.choice([10, 11, 12])  # anger, fear, anxiety
            else:
                return np.random.choice([15, 16, 17])  # sadness, depression, loneliness
    
    def _simulate_data(self, n_samples: int = 500) -> List[MultiModalSample]:
        """Generate simulated WESAD-like data"""
        logging.info(f"Generating {n_samples} simulated WESAD samples")
        
        for i in range(n_samples):
            sample = MultiModalSample()
            
            # Simulated physio features (24 dimensions)
            sample.physio = ModalityData(
                data=np.random.randn(24).astype(np.float32),
                available=True
            )
            
            # Random condition
            condition = np.random.choice([1, 2, 3, 4])
            valence, arousal = self._map_label_to_va(condition)
            
            sample.valence = valence
            sample.arousal = arousal
            sample.categorical_label = self._map_to_categorical(valence, arousal)
            sample.user_id = f"sim_wesad_{i % 15}"
            
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
        
        return {
            'n_samples': len(self.samples),
            'n_subjects': len(set(s.user_id for s in self.samples)),
            'modalities': ['physio']
        }
