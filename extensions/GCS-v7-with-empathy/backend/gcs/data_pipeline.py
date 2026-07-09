import numpy as np
import logging
import pickle
import os
from typing import List, Dict, Any, Tuple

class DataPipeline:
    """Handles all data loading and preprocessing for both foundational and affective models."""
    def __init__(self, config):
        self.config = config
        logging.info("Data Pipeline Initialized.")

    def _simulate_source_localization(self, raw_eeg_data):
        """CONCEPTUAL: Simulates eLORETA source localization."""
        logging.info(f"Applying source localization to data of shape {raw_eeg_data.shape}...")
        projection_matrix = np.random.randn(self.config["eeg_channels"], self.config["cortical_nodes"])
        # Transform from (samples, timesteps, channels) to (samples, nodes, timesteps)
        result = np.einsum('...tc,...cn->...nt', raw_eeg_data, projection_matrix)
        return result

    def load_real_data_for_loso(self):
        """Loads and preprocesses real multi-subject EEG for foundational training."""
        logging.info("Loading and preprocessing real multi-subject EEG data for LOSO...")
        
        # Check if we have real data paths configured
        real_data_paths = self.config.get("real_data_paths", {})
        eeg_data_dir = real_data_paths.get("eeg_data_dir")
        
        all_subjects_data = []
        
        if eeg_data_dir and os.path.exists(eeg_data_dir):
            # Load real EEG data from directory
            logging.info(f"Loading real EEG data from {eeg_data_dir}")
            eeg_files = [f for f in os.listdir(eeg_data_dir) if f.endswith(('.npz', '.npy'))]
            
            for i, eeg_file in enumerate(eeg_files[:self.config["train_subjects"]]):
                file_path = os.path.join(eeg_data_dir, eeg_file)
                try:
                    if eeg_file.endswith('.npz'):
                        data = np.load(file_path)
                        # Try to find EEG data in the file
                        eeg_key = None
                        for key in ['eeg', 'data', 'signals']:
                            if key in data.files:
                                eeg_key = key
                                break
                        
                        if eeg_key is None:
                            logging.warning(f"No EEG data found in {eeg_file}, using first array")
                            eeg_key = data.files[0]
                        
                        raw_eeg = data[eeg_key]
                        
                        # Try to find labels
                        labels_key = None
                        for key in ['labels', 'targets', 'y']:
                            if key in data.files:
                                labels_key = key
                                break
                        
                        if labels_key is not None:
                            labels = data[labels_key]
                        else:
                            # Generate simple labels based on task assumption (motor imagery)
                            labels = np.random.randint(0, 2, raw_eeg.shape[0])
                            logging.warning(f"No labels found in {eeg_file}, generating random labels")
                    
                    else:  # .npy file
                        raw_eeg = np.load(file_path)
                        # Generate labels for .npy files
                        labels = np.random.randint(0, 2, raw_eeg.shape[0])
                        logging.warning(f"No labels available for .npy file {eeg_file}, generating random labels")
                    
                    # Ensure proper shape: (samples, timesteps, channels)
                    if raw_eeg.ndim == 2:
                        # Assume (channels, timesteps) -> reshape to (1, timesteps, channels)
                        raw_eeg = raw_eeg.T.reshape(1, raw_eeg.shape[1], raw_eeg.shape[0])
                    elif raw_eeg.ndim == 3 and raw_eeg.shape[2] != self.config["eeg_channels"]:
                        # If last dimension matches expected channels, assume (samples, timesteps, channels)
                        if raw_eeg.shape[1] == self.config["eeg_channels"]:
                            # Assume (samples, channels, timesteps) -> transpose to (samples, timesteps, channels)
                            raw_eeg = raw_eeg.transpose(0, 2, 1)
                    
                    # Apply source localization
                    source_activity = self._simulate_source_localization(raw_eeg)
                    
                    all_subjects_data.append({
                        'data': source_activity, 
                        'labels': labels, 
                        'subject_id': i + 1,
                        'source_file': eeg_file
                    })
                    
                    logging.info(f"Loaded subject {i+1} data from {eeg_file}: shape {source_activity.shape}")
                
                except Exception as e:
                    logging.error(f"Failed to load {eeg_file}: {e}")
                    continue
        
        # If no real data found or insufficient subjects, supplement with simulated data
        num_loaded = len(all_subjects_data)
        if num_loaded < self.config["train_subjects"]:
            logging.warning(f"Only loaded {num_loaded} real subjects, supplementing with {self.config['train_subjects'] - num_loaded} simulated subjects")
            
            for i in range(num_loaded, self.config["train_subjects"]):
                raw_eeg = np.random.randn(40, self.config["timesteps"], self.config["eeg_channels"])
                source_activity = self._simulate_source_localization(raw_eeg)
                labels = np.random.randint(0, 2, 40)
                all_subjects_data.append({
                    'data': source_activity, 
                    'labels': labels, 
                    'subject_id': i + 1,
                    'source_file': 'simulated'
                })
        
        logging.info(f"LOSO dataset ready: {len(all_subjects_data)} subjects")
        return all_subjects_data

    def load_affective_data(self, dataset_paths: list):
        """Loads and combines multi-modal affective datasets."""
        logging.info(f"Loading affective data from: {dataset_paths}")
        
        # Initialize data containers
        X_eeg_list = []
        X_physio_list = []
        X_voice_list = []
        y_valence_list = []
        y_arousal_list = []
        
        num_real_samples = 0
        
        # Try to load real data from specified paths
        for dataset_path in dataset_paths:
            if os.path.exists(dataset_path):
                try:
                    logging.info(f"Loading real affective data from {dataset_path}")
                    
                    if dataset_path.endswith('.npz'):
                        data = np.load(dataset_path)
                        
                        # Load EEG data
                        eeg_data = None
                        for key in ['eeg', 'signals', 'data']:
                            if key in data.files:
                                eeg_data = data[key]
                                break
                        
                        if eeg_data is not None:
                            # Apply source localization to EEG
                            X_source = self._simulate_source_localization(eeg_data)
                            X_eeg_list.append(X_source)
                        
                        # Load physiological data
                        physio_data = None
                        for key in ['physio', 'physiological', 'bio']:
                            if key in data.files:
                                physio_data = data[key]
                                break
                        
                        if physio_data is not None:
                            X_physio_list.append(physio_data)
                        
                        # Load voice data
                        voice_data = None
                        for key in ['voice', 'audio', 'speech']:
                            if key in data.files:
                                voice_data = data[key]
                                break
                        
                        if voice_data is not None:
                            X_voice_list.append(voice_data)
                        
                        # Load labels
                        valence_data = None
                        arousal_data = None
                        for key in ['valence', 'val']:
                            if key in data.files:
                                valence_data = data[key]
                                break
                        
                        for key in ['arousal', 'aro']:
                            if key in data.files:
                                arousal_data = data[key]
                                break
                        
                        if valence_data is not None:
                            y_valence_list.append(valence_data)
                        if arousal_data is not None:
                            y_arousal_list.append(arousal_data)
                        
                        if eeg_data is not None:
                            num_real_samples += eeg_data.shape[0]
                            logging.info(f"Loaded {eeg_data.shape[0]} samples from {dataset_path}")
                    
                    elif dataset_path.endswith('.pkl'):
                        with open(dataset_path, 'rb') as f:
                            data = pickle.load(f)
                        
                        # Handle different pickle formats
                        if isinstance(data, dict):
                            for key in ['eeg', 'signals', 'data']:
                                if key in data and data[key] is not None:
                                    eeg_data = data[key]
                                    X_source = self._simulate_source_localization(eeg_data)
                                    X_eeg_list.append(X_source)
                                    break
                            
                            for key in ['physio', 'physiological']:
                                if key in data and data[key] is not None:
                                    X_physio_list.append(data[key])
                                    break
                            
                            for key in ['voice', 'audio']:
                                if key in data and data[key] is not None:
                                    X_voice_list.append(data[key])
                                    break
                            
                            for key in ['valence', 'val']:
                                if key in data and data[key] is not None:
                                    y_valence_list.append(data[key])
                                    break
                            
                            for key in ['arousal', 'aro']:
                                if key in data and data[key] is not None:
                                    y_arousal_list.append(data[key])
                                    break
                        
                        if eeg_data is not None:
                            num_real_samples += eeg_data.shape[0]
                            logging.info(f"Loaded {eeg_data.shape[0]} samples from {dataset_path}")
                
                except Exception as e:
                    logging.error(f"Failed to load {dataset_path}: {e}")
                    continue
            else:
                logging.warning(f"Dataset path does not exist: {dataset_path}")
        
        # If we have real data, concatenate it
        if X_eeg_list:
            X_source = np.concatenate(X_eeg_list, axis=0)
        else:
            X_source = None
        
        if X_physio_list:
            X_physio = np.concatenate(X_physio_list, axis=0)
        else:
            X_physio = None
        
        if X_voice_list:
            X_voice = np.concatenate(X_voice_list, axis=0)
        else:
            X_voice = None
        
        if y_valence_list:
            y_valence = np.concatenate(y_valence_list, axis=0)
        else:
            y_valence = None
        
        if y_arousal_list:
            y_arousal = np.concatenate(y_arousal_list, axis=0)
        else:
            y_arousal = None
        
        # If no real data or insufficient data, supplement with simulated data
        target_samples = 1000  # Default number of samples
        
        if num_real_samples < target_samples:
            logging.warning(f"Only {num_real_samples} real samples found, generating {target_samples - num_real_samples} simulated samples")
            
            sim_samples = target_samples - num_real_samples
            X_eeg_sim = np.random.randn(sim_samples, self.config["timesteps"], self.config["eeg_channels"])
            X_source_sim = self._simulate_source_localization(X_eeg_sim)
            X_physio_sim = np.random.randn(sim_samples, 2)  # HRV, GSR
            X_voice_sim = np.random.randn(sim_samples, 128)  # Prosody features
            y_valence_sim = np.random.uniform(1, 9, sim_samples)
            y_arousal_sim = np.random.uniform(1, 9, sim_samples)
            
            # Combine real and simulated data
            X_source = np.concatenate([X_source, X_source_sim], axis=0) if X_source is not None else X_source_sim
            X_physio = np.concatenate([X_physio, X_physio_sim], axis=0) if X_physio is not None else X_physio_sim
            X_voice = np.concatenate([X_voice, X_voice_sim], axis=0) if X_voice is not None else X_voice_sim
            y_valence = np.concatenate([y_valence, y_valence_sim], axis=0) if y_valence is not None else y_valence_sim
            y_arousal = np.concatenate([y_arousal, y_arousal_sim], axis=0) if y_arousal is not None else y_arousal_sim
        
        else:
            # Use only real data if we have enough
            X_source = X_source[:target_samples] if X_source is not None else np.random.randn(target_samples, self.config["cortical_nodes"], self.config["timesteps"])
            X_physio = X_physio[:target_samples] if X_physio is not None else np.random.randn(target_samples, 2)
            X_voice = X_voice[:target_samples] if X_voice is not None else np.random.randn(target_samples, 128)
            y_valence = y_valence[:target_samples] if y_valence is not None else np.random.uniform(1, 9, target_samples)
            y_arousal = y_arousal[:target_samples] if y_arousal is not None else np.random.uniform(1, 9, target_samples)
        
        logging.info(f"Affective data loaded and combined successfully. Final shapes: EEG {X_source.shape}, Physio {X_physio.shape}, Voice {X_voice.shape}")
        return {'eeg': X_source, 'physio': X_physio, 'voice': X_voice}, {'valence': y_valence, 'arousal': y_arousal}
