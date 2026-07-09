"""
Unified multimodal data schema for affective state classification

Provides standardized data structures and interfaces for multimodal data:
- EEG signals
- Physiological signals (HRV, GSR, etc.)
- Voice/audio features
- Text inputs
- Labels (valence, arousal, categorical emotions)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple
import numpy as np
from enum import Enum


class ModalityType(str, Enum):
    """Available modality types"""
    EEG = "eeg"
    PHYSIO = "physio"
    VOICE = "voice"
    TEXT = "text"


@dataclass
class ModalityData:
    """Container for single modality data"""
    data: np.ndarray
    available: bool = True
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.data is None:
            self.available = False
            self.confidence = 0.0


@dataclass
class MultiModalSample:
    """
    Single multimodal sample with all modalities and labels
    
    Attributes:
        eeg: EEG data, shape (channels, timesteps) or (nodes, timesteps) after source localization
        physio: Physiological features, shape (features,)
        voice: Voice/audio features, shape (features,)
        text: Text embedding, shape (features,) [optional]
        valence: Continuous valence rating in [-1, 1] or [0, 1]
        arousal: Continuous arousal rating in [0, 1]
        categorical_label: Integer class label for 28-category emotion taxonomy
        user_id: User identifier for personalization
        context: Additional contextual information
    """
    # Modality data
    eeg: Optional[ModalityData] = None
    physio: Optional[ModalityData] = None
    voice: Optional[ModalityData] = None
    text: Optional[ModalityData] = None
    
    # Labels
    valence: Optional[float] = None
    arousal: Optional[float] = None
    categorical_label: Optional[int] = None
    
    # Metadata
    user_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[float] = None
    
    def get_available_modalities(self) -> List[ModalityType]:
        """Return list of available modalities"""
        available = []
        if self.eeg and self.eeg.available:
            available.append(ModalityType.EEG)
        if self.physio and self.physio.available:
            available.append(ModalityType.PHYSIO)
        if self.voice and self.voice.available:
            available.append(ModalityType.VOICE)
        if self.text and self.text.available:
            available.append(ModalityType.TEXT)
        return available
    
    def has_labels(self) -> bool:
        """Check if sample has any labels"""
        return (self.valence is not None or 
                self.arousal is not None or 
                self.categorical_label is not None)


@dataclass
class MultiModalBatch:
    """
    Batch of multimodal samples for training/inference
    
    All arrays have batch dimension as first axis
    """
    # Modality data (None if modality not available)
    eeg: Optional[np.ndarray] = None  # (batch, channels/nodes, timesteps)
    physio: Optional[np.ndarray] = None  # (batch, features)
    voice: Optional[np.ndarray] = None  # (batch, features)
    text: Optional[np.ndarray] = None  # (batch, features)
    
    # Availability masks
    eeg_mask: Optional[np.ndarray] = None  # (batch,) boolean
    physio_mask: Optional[np.ndarray] = None
    voice_mask: Optional[np.ndarray] = None
    text_mask: Optional[np.ndarray] = None
    
    # Labels
    valence: Optional[np.ndarray] = None  # (batch,)
    arousal: Optional[np.ndarray] = None  # (batch,)
    categorical: Optional[np.ndarray] = None  # (batch,) integer labels
    
    # Metadata
    user_ids: Optional[List[str]] = None
    batch_size: int = 0
    
    @classmethod
    def from_samples(cls, samples: List[MultiModalSample], 
                    expected_shapes: Dict[str, Tuple[int, ...]]) -> 'MultiModalBatch':
        """
        Create batch from list of samples
        
        Args:
            samples: List of MultiModalSample objects
            expected_shapes: Expected shapes for each modality
                            e.g., {'eeg': (8, 1000), 'physio': (24,)}
        """
        if not samples:
            return cls(batch_size=0)
        
        batch_size = len(samples)
        batch = cls(batch_size=batch_size)
        
        # Process EEG
        if 'eeg' in expected_shapes:
            eeg_list = []
            eeg_mask_list = []
            for sample in samples:
                if sample.eeg and sample.eeg.available:
                    eeg_list.append(sample.eeg.data)
                    eeg_mask_list.append(True)
                else:
                    # Create zero-filled placeholder
                    eeg_list.append(np.zeros(expected_shapes['eeg']))
                    eeg_mask_list.append(False)
            batch.eeg = np.stack(eeg_list)
            batch.eeg_mask = np.array(eeg_mask_list)
        
        # Process physio
        if 'physio' in expected_shapes:
            physio_list = []
            physio_mask_list = []
            for sample in samples:
                if sample.physio and sample.physio.available:
                    physio_list.append(sample.physio.data)
                    physio_mask_list.append(True)
                else:
                    physio_list.append(np.zeros(expected_shapes['physio']))
                    physio_mask_list.append(False)
            batch.physio = np.stack(physio_list)
            batch.physio_mask = np.array(physio_mask_list)
        
        # Process voice
        if 'voice' in expected_shapes:
            voice_list = []
            voice_mask_list = []
            for sample in samples:
                if sample.voice and sample.voice.available:
                    voice_list.append(sample.voice.data)
                    voice_mask_list.append(True)
                else:
                    voice_list.append(np.zeros(expected_shapes['voice']))
                    voice_mask_list.append(False)
            batch.voice = np.stack(voice_list)
            batch.voice_mask = np.array(voice_mask_list)
        
        # Process text
        if 'text' in expected_shapes:
            text_list = []
            text_mask_list = []
            for sample in samples:
                if sample.text and sample.text.available:
                    text_list.append(sample.text.data)
                    text_mask_list.append(True)
                else:
                    text_list.append(np.zeros(expected_shapes['text']))
                    text_mask_list.append(False)
            batch.text = np.stack(text_list)
            batch.text_mask = np.array(text_mask_list)
        
        # Process labels
        valence_list = [s.valence for s in samples if s.valence is not None]
        if valence_list:
            batch.valence = np.array([s.valence if s.valence is not None else 0.0 
                                     for s in samples])
        
        arousal_list = [s.arousal for s in samples if s.arousal is not None]
        if arousal_list:
            batch.arousal = np.array([s.arousal if s.arousal is not None else 0.0 
                                     for s in samples])
        
        categorical_list = [s.categorical_label for s in samples 
                           if s.categorical_label is not None]
        if categorical_list:
            batch.categorical = np.array([s.categorical_label if s.categorical_label is not None else 0 
                                         for s in samples])
        
        # User IDs
        batch.user_ids = [s.user_id for s in samples]
        
        return batch


class DatasetInterface:
    """Base interface for affective datasets"""
    
    def load(self) -> List[MultiModalSample]:
        """Load and return all samples"""
        raise NotImplementedError
    
    def get_sample(self, idx: int) -> MultiModalSample:
        """Get single sample by index"""
        raise NotImplementedError
    
    def __len__(self) -> int:
        """Return number of samples"""
        raise NotImplementedError
    
    def get_statistics(self) -> Dict[str, Any]:
        """Return dataset statistics"""
        raise NotImplementedError


def create_dummy_sample(eeg_shape: Tuple[int, ...], 
                       physio_dim: int, 
                       voice_dim: int,
                       text_dim: Optional[int] = None,
                       include_all_modalities: bool = True) -> MultiModalSample:
    """
    Create a synthetic sample for testing and simulation
    
    Args:
        eeg_shape: Shape of EEG data (channels, timesteps) or (nodes, timesteps)
        physio_dim: Dimensionality of physiological features
        voice_dim: Dimensionality of voice features
        text_dim: Dimensionality of text features (optional)
        include_all_modalities: If False, randomly drop some modalities
    """
    sample = MultiModalSample()
    
    # EEG data
    if include_all_modalities or np.random.rand() > 0.2:
        sample.eeg = ModalityData(
            data=np.random.randn(*eeg_shape).astype(np.float32),
            available=True,
            confidence=np.random.uniform(0.8, 1.0)
        )
    
    # Physio data
    if include_all_modalities or np.random.rand() > 0.2:
        sample.physio = ModalityData(
            data=np.random.randn(physio_dim).astype(np.float32),
            available=True,
            confidence=np.random.uniform(0.8, 1.0)
        )
    
    # Voice data
    if include_all_modalities or np.random.rand() > 0.2:
        sample.voice = ModalityData(
            data=np.random.randn(voice_dim).astype(np.float32),
            available=True,
            confidence=np.random.uniform(0.8, 1.0)
        )
    
    # Text data (optional)
    if text_dim and (include_all_modalities or np.random.rand() > 0.5):
        sample.text = ModalityData(
            data=np.random.randn(text_dim).astype(np.float32),
            available=True,
            confidence=np.random.uniform(0.8, 1.0)
        )
    
    # Generate labels
    sample.valence = np.random.uniform(-1, 1)
    sample.arousal = np.random.uniform(0, 1)
    sample.categorical_label = np.random.randint(0, 28)
    sample.user_id = f"user_{np.random.randint(1, 100)}"
    
    return sample
