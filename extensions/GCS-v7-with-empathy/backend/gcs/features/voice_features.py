"""
Voice/Audio Feature Extraction — improved

This module extracts robust, emotion-relevant features from audio:
- MFCC (with librosa when available, robust scipy fallback otherwise)
- Prosodic features (pitch via autocorrelation, RMS energy, zero-crossing)
- Spectral features (centroid, rolloff, contrast; robust fallback)
- Optional: pre-trained embeddings (wav2vec2 / torchaudio) if available
- Optional: simple VAD trimming (webrtcvad) if available
- Improved mel filterbank (triangular filters with mel scale)
- Normalization, configurable output dimension, better handling of short audio

Design goals:
- Best-effort use of high-quality libraries when present, safe fallbacks otherwise
- Deterministic output dimension (configurable, default 128)
- Clear logging and graceful degradation if optional deps missing
- Robust handling of very short audio and multichannel audio

Notes:
- This file is self-contained. Optional dependencies: librosa, torch, torchaudio,
  transformers, webrtcvad. All are used only when available.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy import signal as sp_signal
from scipy.fftpack import dct
import logging

# Configure logger for module consumers
logger = logging.getLogger(__name__)

# Constants
EPS = 1e-8


def _safe_import_librosa():
    try:
        import librosa
        return librosa
    except Exception:
        logger.debug("librosa not available.")
        return None


def _safe_import_torch_audio_embedding_tools():
    """
    Try to import torch/torchaudio or transformers for wav2vec2 embeddings.
    Return a small helper dict with the available backend ('torchaudio' or 'transformers') and module references.
    """
    backend = {}
    try:
        import torch
        import torchaudio
        backend["name"] = "torchaudio"
        backend["torch"] = torch
        backend["torchaudio"] = torchaudio
        return backend
    except Exception:
        logger.debug("torchaudio not available, trying transformers.")
    try:
        from transformers import Wav2Vec2Processor, Wav2Vec2Model
        import torch
        backend["name"] = "transformers"
        backend["torch"] = torch
        backend["processor"] = Wav2Vec2Processor
        backend["model_class"] = Wav2Vec2Model
        return backend
    except Exception:
        logger.debug("transformers wav2vec2 not available.")
        return None


def _hz_to_mel(freq_hz: float) -> float:
    """Convert Hz to mel (HTK formula)."""
    return 2595.0 * np.log10(1.0 + freq_hz / 700.0)


def _mel_to_hz(mel: float) -> float:
    """Convert mel to Hz (HTK formula)."""
    return 700.0 * (10 ** (mel / 2595.0) - 1.0)


def _triangular_filterbank(n_fft_bins: int, sr: int, n_mels: int, fmin: float = 0.0, fmax: Optional[float] = None) -> np.ndarray:
    """
    Create a mel filterbank with triangular filters (better than naive rectangular).
    Returns filterbank matrix of shape (n_mels, n_fft_bins)
    """
    if fmax is None:
        fmax = float(sr) / 2.0

    # center frequencies in mel scale
    mel_min = _hz_to_mel(fmin)
    mel_max = _hz_to_mel(fmax)
    mel_points = np.linspace(mel_min, mel_max, n_mels + 2)
    hz_points = _mel_to_hz(mel_points)

    # map hz to fft bin numbers
    fft_bins = np.floor((n_fft_bins - 1) * hz_points / (sr / 2.0)).astype(int)
    filterbank = np.zeros((n_mels, n_fft_bins))

    for i in range(n_mels):
        start, center, end = fft_bins[i], fft_bins[i + 1], fft_bins[i + 2]
        if center - start > 0:
            up = (np.arange(start, center) - start) / max(1, (center - start))
            filterbank[i, start:center] = up
        if end - center > 0:
            down = (end - np.arange(center, end)) / max(1, (end - center))
            filterbank[i, center:end] = down

    # avoid divide by zero, normalize energy per filter
    enorm = 2.0 / (hz_points[2:n_mels + 2] - hz_points[:n_mels])
    filterbank *= enorm[:, np.newaxis]
    # Clip any NaNs
    filterbank = np.nan_to_num(filterbank)
    return filterbank


class VoiceFeatureExtractor:
    """
    High-quality voice feature extractor with optional advanced backends.

    Main method: extract_features(audio_signal) -> 1D np.ndarray of length output_dim.

    Parameters:
    - sampling_rate: sample rate in Hz
    - n_mfcc: number of MFCC coefficients to compute (will produce mean+std => 2*n_mfcc dims)
    - n_fft: FFT window size (samples)
    - hop_length: hop length for STFT
    - extract_prosody: whether to include prosodic features
    - extract_spectral: whether to include spectral features
    - use_librosa: try to use librosa for higher-quality features
    - use_vad: if True, attempt to trim leading/trailing silence with webrtcvad (if available)
    - embeddings_backend: 'auto' to attempt wav2vec2 embeddings, None to disable embeddings
    - output_dim: final feature vector length (will pad/trim)
    """

    def __init__(self,
                 sampling_rate: int = 16000,
                 n_mfcc: int = 13,
                 n_fft: int = 512,
                 hop_length: int = 160,
                 extract_prosody: bool = True,
                 extract_spectral: bool = True,
                 use_librosa: bool = True,
                 use_vad: bool = False,
                 embeddings_backend: Optional[str] = "auto",
                 output_dim: int = 128):
        self.sr = int(sampling_rate)
        self.n_mfcc = int(n_mfcc)
        self.n_fft = int(n_fft)
        self.hop_length = int(hop_length)
        self.extract_prosody = bool(extract_prosody)
        self.extract_spectral = bool(extract_spectral)
        self.use_vad = bool(use_vad)
        self.output_dim = int(output_dim)

        self.librosa = _safe_import_librosa() if use_librosa else None
        if self.librosa is not None:
            logger.debug("librosa available and will be used where appropriate.")
        self.embedding_tools = None
        if embeddings_backend is not None:
            self.embedding_tools = _safe_import_torch_audio_embedding_tools()
            if self.embedding_tools:
                logger.debug(f"Embedding backend available: {self.embedding_tools.get('name')}")

        # optional webrtcvad for quick VAD trimming
        self.webrtcvad = None
        if use_vad:
            try:
                import webrtcvad
                self.webrtcvad = webrtcvad
                logger.debug("webrtcvad available for simple VAD trimming.")
            except Exception:
                logger.debug("webrtcvad not available; skipping VAD trimming.")

    def _ensure_mono_and_float(self, audio: np.ndarray) -> np.ndarray:
        """
        Convert multichannel to mono and ensure float32 in [-1, 1].
        """
        if audio is None:
            return np.zeros(1, dtype=np.float32)
        audio = np.asarray(audio)
        if audio.ndim > 1:
            # average channels
            audio = np.mean(audio, axis=1)
        # normalize integers to float
        if np.issubdtype(audio.dtype, np.integer):
            max_abs = np.iinfo(audio.dtype).max
            audio = audio.astype(np.float32) / max_abs
        else:
            audio = audio.astype(np.float32)
            # clip to [-1, 1] if likely out of bounds
            audio = np.clip(audio, -1.0, 1.0)
        return audio

    def _vad_trim(self, audio: np.ndarray) -> np.ndarray:
        """
        Very small wrapper for trimming silent edges using webrtcvad if available.
        If not available, returns the original audio.
        This is intentionally simple and conservative.
        """
        if self.webrtcvad is None:
            return audio
        try:
            # webrtcvad requires 16-bit mono PCM and frame sizes 10/20/30 ms
            vad = self.webrtcvad.Vad(2)  # aggressive mode
            frame_ms = 30
            frame_len = int(self.sr * frame_ms / 1000)
            if frame_len % 2 != 0:
                frame_len += 1
            # convert to 16-bit PCM
            pcm = (audio * 32767.0).astype(np.int16).tobytes()
            # naive chunking
            voiced = bytearray()
            for i in range(0, len(pcm), frame_len * 2):  # 2 bytes per sample
                chunk = pcm[i:i + frame_len * 2]
                if len(chunk) < frame_len * 2:
                    break
                is_voiced = vad.is_speech(chunk, sample_rate=self.sr)
                if is_voiced:
                    voiced.extend(chunk)
            if len(voiced) == 0:
                return audio
            arr = np.frombuffer(bytes(voiced), dtype=np.int16).astype(np.float32) / 32767.0
            return arr
        except Exception as e:
            logger.debug(f"VAD trimming failed: {e}")
            return audio

    def extract_features(self, audio_signal: np.ndarray) -> np.ndarray:
        """
        Main entry: return a fixed-length feature vector (self.output_dim).
        """
        audio = self._ensure_mono_and_float(audio_signal)
        if audio.size == 0:
            logger.debug("Empty audio_signal provided; returning zeros.")
            return np.zeros(self.output_dim, dtype=np.float32)

        if self.use_vad and self.webrtcvad is not None:
            try:
                audio = self._vad_trim(audio)
            except Exception as e:
                logger.debug(f"VAD trimming raised: {e}")

        # If already precomputed features with desired dim, return as-is
        if audio.ndim == 1 and audio.shape[0] == self.output_dim and not np.any(np.isnan(audio)):
            return audio.astype(np.float32)

        features = []

        # MFCCs (mean and std)
        mfcc = self.extract_mfcc(audio)
        features.append(mfcc)

        # Prosodic
        if self.extract_prosody:
            pros = self.extract_prosody_features(audio)
            features.append(pros)

        # Spectral
        if self.extract_spectral:
            spec = self.extract_spectral_features(audio)
            features.append(spec)

        # Optional embeddings (low-dimensional summary)
        emb = self.extract_embeddings(audio)
        if emb is not None:
            features.append(emb)

        all_features = np.concatenate([f for f in features if f is not None])

        # Final normalization: z-score if possible, else scale to [-1, 1]
        if np.any(np.isnan(all_features)) or np.all(all_features == 0):
            all_features = np.nan_to_num(all_features)
        else:
            # robust scaling
            mean = np.mean(all_features)
            std = np.std(all_features)
            if std > EPS:
                all_features = (all_features - mean) / std
            else:
                all_features = all_features - mean

        # Pad/trim to output_dim
        if all_features.size < self.output_dim:
            pad_width = self.output_dim - all_features.size
            all_features = np.pad(all_features, (0, pad_width), mode='constant')
        elif all_features.size > self.output_dim:
            all_features = all_features[:self.output_dim]

        return all_features.astype(np.float32)

    def extract_mfcc(self, audio_signal: np.ndarray) -> np.ndarray:
        """
        Extract MFCC features: returns concatenated mean and std of n_mfcc coefficients.
        Uses librosa if available (more robust), falls back to scipy-based pipeline.
        """
        audio = self._ensure_mono_and_float(audio_signal)

        # Attempt librosa
        if self.librosa is not None:
            try:
                # librosa's mfcc expects floating audio in [-1, 1]
                mfccs = self.librosa.feature.mfcc(
                    y=audio,
                    sr=self.sr,
                    n_mfcc=self.n_mfcc,
                    n_fft=self.n_fft,
                    hop_length=self.hop_length,
                    htk=True
                )
                # If very short audio, librosa may return smaller frames; handle gracefully
                if mfccs.size == 0:
                    raise RuntimeError("librosa returned empty MFCCs")
                mean = np.mean(mfccs, axis=1)
                std = np.std(mfccs, axis=1)
                return np.concatenate([mean, std])
            except Exception as e:
                logger.debug(f"librosa MFCC failed: {e}; falling back to scipy MFCC.")

        # Fallback: robust scipy-based MFCC
        return self._extract_mfcc_scipy(audio)

    def _extract_mfcc_scipy(self, audio_signal: np.ndarray) -> np.ndarray:
        """
        Simplified MFCC via STFT -> mel filterbank -> log -> DCT.
        More robust handling of short audio and numerical stability.
        """
        audio = self._ensure_mono_and_float(audio_signal)

        # Ensure at least one full frame
        if len(audio) < self.n_fft:
            pad = self.n_fft - len(audio)
            audio = np.pad(audio, (0, pad), mode='reflect')

        try:
            # STFT (magnitude)
            freqs, times, stft = sp_signal.stft(
                audio,
                fs=self.sr,
                nperseg=self.n_fft,
                noverlap=self.n_fft - self.hop_length,
                padded=True,
                boundary='reflect'
            )
            power_spec = np.abs(stft) ** 2  # shape (freq_bins, time_frames)
            n_freqs = power_spec.shape[0]

            # mel filterbank
            n_mels = max(20, min(128, 40))
            mel_fb = _triangular_filterbank(n_freqs, self.sr, n_mels, fmin=0.0, fmax=self.sr / 2.0)
            # mel spectrogram (n_mels, time_frames)
            mel_spec = mel_fb @ power_spec
            mel_spec = np.maximum(mel_spec, EPS)

            log_mel = np.log(mel_spec)

            # DCT to get MFCCs
            mfccs = dct(log_mel, axis=0, norm='ortho')[:self.n_mfcc, :]

            mean = np.mean(mfccs, axis=1)
            std = np.std(mfccs, axis=1)
            return np.concatenate([mean, std])
        except Exception as e:
            logger.warning(f"Scipy-based MFCC extraction failed: {e}")
            return np.zeros(self.n_mfcc * 2, dtype=np.float32)

    def extract_prosody_features(self, audio_signal: np.ndarray) -> np.ndarray:
        """
        Prosody: [pitch_mean, pitch_std, pitch_range, energy_mean, energy_std, zcr_mean]
        Uses librosa when available for better pitch or fallback to autocorrelation per frame.
        """
        audio = self._ensure_mono_and_float(audio_signal)
        # short-circuit
        if audio.size < 2:
            return np.zeros(6, dtype=np.float32)

        # Energy (frame-wise RMS)
        frame_len = self.n_fft
        hop = self.hop_length
        if len(audio) < frame_len:
            pad = frame_len - len(audio)
            audio_padded = np.pad(audio, (0, pad), mode='reflect')
        else:
            audio_padded = audio

        # energy frames
        frames = []
        for start in range(0, len(audio_padded) - frame_len + 1, hop):
            frame = audio_padded[start:start + frame_len]
            frames.append(np.sqrt(np.mean(frame ** 2)))
        if len(frames) == 0:
            energy_mean = energy_std = 0.0
        else:
            frames = np.array(frames)
            energy_mean = float(np.mean(frames))
            energy_std = float(np.std(frames))

        # zero crossing rate (global)
        zcr = float(np.mean(np.abs(np.diff(np.sign(audio))))) / 2.0  # normalized approx

        # Pitch estimation
        pitches = []
        # Try librosa piptrack if available
        if self.librosa is not None:
            try:
                pitches_lib, mags = self.librosa.piptrack(y=audio, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length)
                for t in range(pitches_lib.shape[1]):
                    col = pitches_lib[:, t]
                    magcol = mags[:, t]
                    if magcol.size == 0:
                        continue
                    idx = magcol.argmax()
                    p = col[idx]
                    if p > 0:
                        pitches.append(p)
            except Exception as e:
                logger.debug(f"librosa piptrack failed for prosody: {e}")

        # fallback: autocorrelation per frame
        if len(pitches) == 0:
            min_f0 = 50.0
            max_f0 = 500.0
            min_lag = int(self.sr / max_f0)
            max_lag = int(self.sr / min_f0)
            for start in range(0, len(audio_padded) - frame_len + 1, hop):
                frame = audio_padded[start:start + frame_len]
                frame = frame - np.mean(frame)
                if np.all(np.abs(frame) < 1e-7):
                    continue
                autocorr = np.correlate(frame, frame, mode='full')
                autocorr = autocorr[autocorr.size // 2:]
                # limit lags
                if max_lag >= len(autocorr):
                    max_lag = len(autocorr) - 1
                if min_lag >= max_lag:
                    continue
                lag = np.argmax(autocorr[min_lag:max_lag]) + min_lag
                if autocorr[lag] > 0:
                    pitch = float(self.sr / lag)
                    if min_f0 <= pitch <= max_f0:
                        pitches.append(pitch)
        pitches = np.array(pitches) if len(pitches) > 0 else np.array([])

        if pitches.size > 0:
            pitch_mean = float(np.mean(pitches))
            pitch_std = float(np.std(pitches))
            pitch_range = float(np.max(pitches) - np.min(pitches))
        else:
            pitch_mean = pitch_std = pitch_range = 0.0

        return np.array([pitch_mean, pitch_std, pitch_range, energy_mean, energy_std, zcr], dtype=np.float32)

    def extract_spectral_features(self, audio_signal: np.ndarray) -> np.ndarray:
        """
        Spectral signature including centroid_mean, centroid_std, rolloff_mean, rolloff_std,
        and spectral contrast band means (7 bands -> total dims 4 + 7 = 11).
        Uses librosa if available, otherwise computes robust approximations.
        """
        audio = self._ensure_mono_and_float(audio_signal)

        if self.librosa is not None:
            try:
                cent = self.librosa.feature.spectral_centroid(y=audio, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length)[0]
                roll = self.librosa.feature.spectral_rolloff(y=audio, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length, roll_percent=0.85)[0]
                contrast = self.librosa.feature.spectral_contrast(y=audio, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length)
                features = [
                    float(np.mean(cent)), float(np.std(cent)),
                    float(np.mean(roll)), float(np.std(roll))
                ]
                # contrast has shape (n_bands + 1, frames). We will return the mean across time for each band.
                contrast_mean = np.mean(contrast, axis=1)
                features.extend([float(v) for v in contrast_mean])
                # Ensure length 11 (librosa default contrast yields 7 bands)
                return np.array(features[:11], dtype=np.float32)
            except Exception as e:
                logger.debug(f"librosa spectral features failed: {e}")

        # Fallback: compute centroid and rolloff from STFT
        try:
            freqs, times, stft = sp_signal.stft(audio, fs=self.sr, nperseg=self.n_fft, noverlap=self.n_fft - self.hop_length, padded=True, boundary='reflect')
            mag = np.abs(stft)
            eps = EPS
            # centroid
            magsum = np.sum(mag + eps, axis=0)
            centroid = np.sum(freqs[:, None] * mag, axis=0) / magsum
            # rolloff (85% energy)
            cum = np.cumsum(mag, axis=0)
            total = cum[-1, :]
            rolloff_bins = np.argmax(cum >= 0.85 * total, axis=0)
            rolloff = freqs[rolloff_bins]
            # spectral contrast: simple band-wise log ratio between peaks and valleys
            n_bands = 7
            band_edges = np.linspace(0, len(freqs) - 1, n_bands + 2).astype(int)
            contrast = []
            for b in range(n_bands):
                start, end = band_edges[b], band_edges[b + 2]
                band = mag[start:end + 1, :]
                if band.size == 0:
                    contrast.append(0.0)
                    continue
                # peak minus trough in log-space per frame, then mean across time
                band_max = np.max(band, axis=0) + eps
                band_min = np.min(band, axis=0) + eps
                contrast_val = np.mean(np.log(band_max) - np.log(band_min))
                contrast.append(float(contrast_val))
            features = [
                float(np.mean(centroid)), float(np.std(centroid)),
                float(np.mean(rolloff)), float(np.std(rolloff)),
            ]
            features.extend(contrast)
            # Ensure length 11
            out = np.array(features[:11], dtype=np.float32)
            return out
        except Exception as e:
            logger.warning(f"Spectral fallback failed: {e}")
            return np.zeros(11, dtype=np.float32)

    def extract_embeddings(self, audio_signal: np.ndarray) -> Optional[np.ndarray]:
        """
        Attempt to compute a compact embedding using wav2vec2 if available.
        Returns a low-dimensional vector (e.g., 16 dims) or None if embeddings are not available.
        This function will not raise if backends are missing.
        """
        if self.embedding_tools is None:
            return None
        try:
            backend_name = self.embedding_tools.get("name")
            if backend_name == "torchaudio":
                torch = self.embedding_tools["torch"]
                torchaudio = self.embedding_tools["torchaudio"]
                model = None
                # Try to load a widely available wav2vec2 model from torchaudio.pipelines (if present)
                try:
                    # This is best-effort; if unavailable it will raise
                    bundle = torchaudio.pipelines.WAV2VEC2_BASE
                    model = bundle.get_model().to('cpu')
                    resampler = torchaudio.transforms.Resample(orig_freq=self.sr, new_freq=bundle.sample_rate)
                    # prepare tensor
                    wav = torch.from_numpy(audio_signal).float().unsqueeze(0)
                    if self.sr != bundle.sample_rate:
                        wav = resampler(wav)
                    with torch.inference_mode():
                        embs, _ = model.extract_features(wav)
                    # embs is a list; take last layer mean
                    if isinstance(embs, (list, tuple)):
                        emb = torch.mean(embs[-1], dim=1).squeeze(0).cpu().numpy()
                    else:
                        emb = np.mean(embs.squeeze(0).cpu().numpy(), axis=0)
                    # reduce to small summary (take first/last/mean)
                    summary = np.concatenate([emb[:8], emb[-8:]]) if emb.size >= 16 else np.pad(emb, (0, max(0, 16 - emb.size)))
                    # reduce dimension to 16 exactly
                    return np.asarray(summary[:16], dtype=np.float32)
                except Exception as e:
                    logger.debug(f"torchaudio wav2vec2 fetch failed: {e}")
                    return None
            elif backend_name == "transformers":
                torch = self.embedding_tools["torch"]
                Processor = self.embedding_tools["processor"]
                ModelClass = self.embedding_tools["model_class"]
                try:
                    processor = Processor.from_pretrained("facebook/wav2vec2-base-960h")
                    model = ModelClass.from_pretrained("facebook/wav2vec2-base-960h")
                    inputs = processor(audio_signal, sampling_rate=self.sr, return_tensors="pt", padding=True)
                    with torch.inference_mode():
                        outputs = model(**inputs)
                        last_hidden = outputs.last_hidden_state  # (batch, seq, hidden)
                        emb = torch.mean(last_hidden, dim=1).squeeze(0).cpu().numpy()
                    summary = np.concatenate([emb[:8], emb[-8:]]) if emb.size >= 16 else np.pad(emb, (0, max(0, 16 - emb.size)))
                    return np.asarray(summary[:16], dtype=np.float32)
                except Exception as e:
                    logger.debug(f"transformers wav2vec2 fetch failed: {e}")
                    return None
            else:
                return None
        except Exception as e:
            logger.debug(f"Embeddings extraction error: {e}")
            return None


def extract_voice_features_batch(audio_batch: np.ndarray,
                                 sampling_rate: int = 16000,
                                 **kwargs) -> np.ndarray:
    """
    Convenience batch extractor. Accepts:
      - audio_batch: np.ndarray of shape (batch, samples) OR (batch, 128) (already features)
    Returns:
      - np.ndarray shape (batch, output_dim)
    """
    if not isinstance(audio_batch, np.ndarray):
        audio_batch = np.asarray(audio_batch)

    # Already features?
    if audio_batch.ndim == 2 and audio_batch.shape[1] == kwargs.get("output_dim", 128):
        return audio_batch.astype(np.float32)

    if audio_batch.ndim != 2:
        raise ValueError("audio_batch must be a 2D array (batch, samples) or (batch, feature_dim)")

    extractor = VoiceFeatureExtractor(sampling_rate=sampling_rate, **kwargs)
    batch_size = audio_batch.shape[0]
    features_list = []
    for i in range(batch_size):
        try:
            feats = extractor.extract_features(audio_batch[i])
            features_list.append(feats)
        except Exception as e:
            logger.warning(f"Feature extraction failed for index {i}: {e}")
            features_list.append(np.zeros(extractor.output_dim, dtype=np.float32))
    return np.stack(features_list, axis=0)
