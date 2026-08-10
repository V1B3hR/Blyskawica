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
from enum import Enum
from typing import Any

import numpy as np


class ModalityType(str, Enum):  # noqa: UP042
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
    metadata: dict[str, Any] = field(default_factory=dict)

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
    """  # noqa: W293
    # Modality data
    eeg: ModalityData | None = None
    physio: ModalityData | None = None
    voice: ModalityData | None = None
    text: ModalityData | None = None

    # Labels
    valence: float | None = None
    arousal: float | None = None
    categorical_label: int | None = None

    # Metadata
    user_id: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: float | None = None

    def get_available_modalities(self) -> list[ModalityType]:
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
    """  # noqa: W293
    # Modality data (None if modality not available)
    eeg: np.ndarray | None = None  # (batch, channels/nodes, timesteps)
    physio: np.ndarray | None = None  # (batch, features)
    voice: np.ndarray | None = None  # (batch, features)
    text: np.ndarray | None = None  # (batch, features)

    # Availability masks
    eeg_mask: np.ndarray | None = None  # (batch,) boolean
    physio_mask: np.ndarray | None = None
    voice_mask: np.ndarray | None = None
    text_mask: np.ndarray | None = None

    # Labels
    valence: np.ndarray | None = None  # (batch,)
    arousal: np.ndarray | None = None  # (batch,)
    categorical: np.ndarray | None = None  # (batch,) integer labels

    # Metadata
    user_ids: list[str] | None = None
    batch_size: int = 0

    @classmethod
    def from_samples(cls, samples: list[MultiModalSample],
                    expected_shapes: dict[str, tuple[int, ...]]) -> 'MultiModalBatch':
        """
        Create batch from list of samples
        
        Args:
            samples: List of MultiModalSample objects
            expected_shapes: Expected shapes for each modality
                            e.g., {'eeg': (8, 1000), 'physio': (24,)}
        """  # noqa: W293
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

    def load(self) -> list[MultiModalSample]:
        """Load and return all samples"""
        raise NotImplementedError

    def get_sample(self, idx: int) -> MultiModalSample:
        """Get single sample by index"""
        raise NotImplementedError

    def __len__(self) -> int:
        """Return number of samples"""
        raise NotImplementedError

    def get_statistics(self) -> dict[str, Any]:
        """Return dataset statistics"""
        raise NotImplementedError


def create_dummy_sample(eeg_shape: tuple[int, ...],
                       physio_dim: int,
                       voice_dim: int,
                       text_dim: int | None = None,
                       include_all_modalities: bool = True) -> MultiModalSample:
    """
    Create a synthetic sample for testing and simulation
    
    Args:
        eeg_shape: Shape of EEG data (channels, timesteps) or (nodes, timesteps)
        physio_dim: Dimensionality of physiological features
        voice_dim: Dimensionality of voice features
        text_dim: Dimensionality of text features (optional)
        include_all_modalities: If False, randomly drop some modalities
    """  # noqa: W293
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
