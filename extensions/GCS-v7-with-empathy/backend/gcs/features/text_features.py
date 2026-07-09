"""
Text Feature Extraction (enhanced)

Improvements over original:
- Robust optional dependencies: sentence-transformers, transformers, scikit-learn.
- Automatic detection of encoder embedding dimension and dynamic final feature dimension.
- Efficient batch extraction paths (bulk encoding + bulk sentiment).
- Configurable device selection (auto detects GPU).
- Better fallback strategy:
    1) SentenceTransformer if available
    2) TF-IDF vectorizer with fixed vocabulary (scikit-learn) if available
    3) Deterministic bag-of-words / handcrafted linguistic features
- Extra linguistic features (punctuation, uppercase, exclamation/question counts).
- L2-normalization of embeddings (configurable).
- Caching for repeated texts (LRU cache).
- Stronger type hints, more defensive programming and logging.
- Clearer API: extract_features (single) and extract_features_batch (batch).
"""

from __future__ import annotations

import logging
import math
import re
from functools import lru_cache
from typing import List, Optional, Sequence

import numpy as np

# Constants
DEFAULT_EMBEDDING_DIM = 384  # safe default (e.g. all-MiniLM-L6-v2)
SENTIMENT_DIM = 3  # positive, negative, neutral
LINGUISTIC_DIM = 8  # number of handcrafted linguistic features returned

logger = logging.getLogger(__name__)


class TextFeatureExtractor:
    """
    Extract emotion-relevant features from text.

    Features returned (concatenated):
      [embedding (embedding_dim),
       sentiment (3 dims: pos, neg, neutral) if enabled,
       linguistic (LINGUISTIC_DIM dims)]

    The class will attempt to load optional dependencies when helpful:
      - sentence-transformers for high-quality embeddings
      - transformers pipeline for sentiment
      - scikit-learn (TfidfVectorizer) as an intermediate fallback

    Usage:
        extractor = TextFeatureExtractor(model_name="all-MiniLM-L6-v2", device="auto")
        x = extractor.extract_features("some text")
        X = extractor.extract_features_batch(["one", "two"])
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        use_sentiment: bool = True,
        embedding_dim: Optional[int] = None,
        device: str = "auto",
        normalize_embeddings: bool = True,
        tfidf_vocab_size: int = 384,
        cache_size: int = 4096,
    ):
        """
        Args:
            model_name: preferred SentenceTransformer model (or huggingface model id for some flows)
            use_sentiment: whether to include sentiment features
            embedding_dim: expected embedding dimension; if None, derived from encoder when possible,
                           otherwise uses DEFAULT_EMBEDDING_DIM.
            device: "cpu", "cuda", or "auto" (auto picks cuda if available)
            normalize_embeddings: L2-normalize embeddings (recommended)
            tfidf_vocab_size: vocabulary size for TF-IDF fallback (fixed-length vector)
            cache_size: LRU cache size for repeated text encodings
        """
        self.model_name = model_name
        self.use_sentiment = use_sentiment
        self._requested_embedding_dim = embedding_dim
        self._tfidf_vocab_size = int(tfidf_vocab_size)
        self._normalize = bool(normalize_embeddings)
        self._cache_size = int(cache_size)

        # Device selection
        if device not in ("cpu", "cuda", "auto"):
            logger.warning("Unknown device '%s', falling back to 'auto'", device)
            device = "auto"
        self.device = device

        # Backing components (lazy-init)
        self._sentence_encoder = None
        self._sentiment_pipeline = None
        self._tfidf_vectorizer = None

        # Determine effective device string for libraries
        self._device_str = self._choose_device()

        # Try lazy import to probe available libs
        self._probe_backends()

        # Determine final embedding dim
        self.embedding_dim = self._determine_embedding_dim()

        # Final total dimension (embedding + sentiment if enabled + linguistic)
        self.total_dim = self.embedding_dim + (SENTIMENT_DIM if self.use_sentiment else 0) + LINGUISTIC_DIM

        # Wrap encode in an LRU cache for repeated single texts
        self._encode_cached = lru_cache(maxsize=self._cache_size)(self._encode_uncached)

    def _choose_device(self) -> str:
        if self.device == "cpu":
            return "cpu"
        if self.device == "cuda":
            return "cuda"
        # auto
        try:
            import torch

            return "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            return "cpu"

    def _probe_backends(self) -> None:
        """Probe availability of optional backends and initialize what's cheap to initialize."""
        # SentenceTransformer (lazy)
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            # do not instantiate here (can be heavy), but note availability
            self._have_sentence_transformers = True
            logger.debug("sentence-transformers available")
        except Exception:
            self._have_sentence_transformers = False
            logger.debug("sentence-transformers not available")

        # transformers for sentiment
        if self.use_sentiment:
            try:
                import transformers  # type: ignore

                self._have_transformers = True
                logger.debug("transformers available for sentiment")
            except Exception:
                self._have_transformers = False
                logger.debug("transformers not available")

        # scikit-learn TF-IDF fallback
        try:
            import sklearn  # type: ignore

            from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore

            self._have_sklearn = True
            logger.debug("sklearn available for TF-IDF fallback")
        except Exception:
            self._have_sklearn = False
            logger.debug("sklearn not available")

    def _determine_embedding_dim(self) -> int:
        """Determine or infer embedding dimension."""
        # If user provided explicit embedding_dim, respect it
        if self._requested_embedding_dim is not None:
            return int(self._requested_embedding_dim)

        # Try to infer from sentence-transformer model metadata
        if self._have_sentence_transformers:
            try:
                enc = self._init_sentence_transformer()
                # Some encoders expose get_sentence_embedding_dimension
                dim = getattr(enc, "get_sentence_embedding_dimension", None)
                if callable(dim):
                    inferred = int(dim())
                    logger.info("Inferred embedding dim from SentenceTransformer: %d", inferred)
                    return inferred
                # fallback: run a quick encode
                sample = enc.encode("test", convert_to_numpy=True)
                logger.info("Inferred embedding dim by running encode: %d", sample.shape[-1])
                return int(sample.shape[-1])
            except Exception as e:
                logger.warning("Could not infer embedding dimension from SentenceTransformer: %s", e)

        # If TF-IDF available, use that vocab size
        if self._have_sklearn:
            return self._tfidf_vocab_size

        # Last resort
        return DEFAULT_EMBEDDING_DIM

    def _init_sentence_transformer(self):
        """Instantiate SentenceTransformer lazily and cache it."""
        if self._sentence_encoder is not None:
            return self._sentence_encoder
        if not self._have_sentence_transformers:
            raise RuntimeError("sentence-transformers not available")
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            # prefer small models when default provided; users can override model_name argument
            logger.info("Loading SentenceTransformer model '%s' on device '%s'", self.model_name, self._device_str)
            encoder = SentenceTransformer(self.model_name, device=self._device_str)
            self._sentence_encoder = encoder
            return encoder
        except Exception as e:
            logger.warning("Failed to load SentenceTransformer('%s'): %s", self.model_name, e)
            self._have_sentence_transformers = False
            raise

    def _init_sentiment_pipeline(self):
        """Instantiate transformers sentiment pipeline lazily."""
        if self._sentiment_pipeline is not None:
            return self._sentiment_pipeline
        if not getattr(self, "_have_transformers", False):
            raise RuntimeError("transformers not available for sentiment")
        try:
            from transformers import pipeline  # type: ignore

            logger.info("Loading transformers sentiment pipeline on device '%s'", self._device_str)
            # If device is CUDA, pass device index 0 else -1 for CPU
            device_idx = 0 if self._device_str == "cuda" else -1
            pipe = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", device=device_idx)
            self._sentiment_pipeline = pipe
            return pipe
        except Exception as e:
            logger.warning("Failed to init sentiment pipeline: %s", e)
            self._have_transformers = False
            raise

    def _init_tfidf(self):
        """Instantiate TF-IDF vectorizer as fallback (creates fixed-size vocabulary)."""
        if self._tfidf_vectorizer is not None:
            return self._tfidf_vectorizer
        if not getattr(self, "_have_sklearn", False):
            raise RuntimeError("scikit-learn not available for TF-IDF fallback")
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
            # Use simple token pattern; limit max_features to tfidf_vocab_size for fixed-length vector
            vec = TfidfVectorizer(max_features=self._tfidf_vocab_size, token_pattern=r"(?u)\b\w+\b", ngram_range=(1, 2))
            self._tfidf_vectorizer = vec
            # Note: caller must fit the vectorizer on data (we provide a minimal fit strategy below)
            return vec
        except Exception as e:
            logger.warning("Failed to init TfidfVectorizer: %s", e)
            self._have_sklearn = False
            raise

    # ---------------------
    # Encoding / Embedding
    # ---------------------
    def _encode_uncached(self, text: str) -> np.ndarray:
        """
        Actual (uncached) encoding work. This function is wrapped by LRU cache.
        """
        # Prefer high-quality sentence-transformer if available
        if self._have_sentence_transformers:
            try:
                enc = self._init_sentence_transformer()
                emb = enc.encode(text, convert_to_numpy=True)
                emb = np.asarray(emb, dtype=np.float32)
                if self._normalize and emb.sum() != 0:
                    norm = np.linalg.norm(emb)
                    if norm > 0:
                        emb = emb / norm
                # If requested embedding_dim differs, pad/trim deterministically
                emb = self._pad_or_trim(emb, self.embedding_dim)
                return emb
            except Exception as e:
                logger.warning("SentenceTransformer encode failed, falling back: %s", e)
                # fall through to fallback methods

        # Next fallback: TF-IDF (fit using the single text is not ideal, so we synthesize a minimal corpus)
        if self._have_sklearn:
            try:
                vec = self._init_tfidf()
                # Fit on the single text plus some safe tokens to make vectorizer stable
                synthetic = [text, "the a and is to of in"]  # ensure some tokens exist for fitting
                vec.fit(synthetic)
                v = vec.transform([text]).toarray().astype(np.float32)[0]
                v = self._pad_or_trim(v, self.embedding_dim)
                if self._normalize:
                    nrm = np.linalg.norm(v)
                    if nrm > 0:
                        v = v / nrm
                return v
            except Exception as e:
                logger.warning("TF-IDF fallback failed: %s", e)

        # Last resort: deterministic BOW features + engineered stats
        bow = self._bow_features_vector(text, self.embedding_dim)
        if self._normalize:
            nrm = np.linalg.norm(bow)
            if nrm > 0:
                bow = bow / nrm
        return bow

    def _pad_or_trim(self, arr: np.ndarray, dim: int) -> np.ndarray:
        """Pad with zeros or trim to ensure fixed dimensionality."""
        arr = np.asarray(arr, dtype=np.float32).ravel()
        if arr.size == dim:
            return arr
        if arr.size > dim:
            return arr[:dim].copy()
        pad_width = dim - arr.size
        return np.pad(arr, (0, pad_width), mode="constant").astype(np.float32)

    def _bow_features_vector(self, text: str, dim: int) -> np.ndarray:
        """
        Deterministic fallback representation. Fills a vector of length `dim`
        with repeated linguistic features and hashed token buckets so output is stable.
        """
        # Base engineered features
        ling = self._linguistic_features(text)  # length LINGUISTIC_DIM
        # Simple hashed bag into remainder of vector
        tokens = re.findall(r"\b\w+\b", text.lower())
        buckets = np.zeros(max(0, dim - ling.size), dtype=np.float32)
        for t in tokens:
            h = abs(hash(t)) % buckets.size if buckets.size > 0 else 0
            if buckets.size > 0:
                buckets[h] += 1.0
        if buckets.size > 0:
            # normalize counts
            s = buckets.sum()
            if s > 0:
                buckets = buckets / s
        vec = np.concatenate([ling.astype(np.float32), buckets])
        return self._pad_or_trim(vec, dim)

    def _linguistic_features(self, text: str) -> np.ndarray:
        """
        Handcrafted linguistic features (fixed length: LINGUISTIC_DIM):
          0: word count (log scaled)
          1: character count (log scaled)
          2: unique word ratio
          3: average word length
          4: punctuation ratio (punctuation chars / chars)
          5: uppercase ratio (uppercase letters / letters)
          6: exclamation count (normalized)
          7: question mark count (normalized)
        """
        if not isinstance(text, str):
            text = str(text or "")
        words = re.findall(r"\b\w+\b", text)
        chars = list(text)
        word_count = len(words)
        char_count = len(chars)
        unique_ratio = len(set(words)) / (word_count + 1)
        avg_word_len = float(np.mean([len(w) for w in words])) if words else 0.0
        punct_count = len([c for c in chars if re.match(r"[^\w\s]", c)])
        punct_ratio = punct_count / (char_count + 1)
        uppercase_letters = len([c for c in chars if c.isalpha() and c.isupper()])
        letter_count = len([c for c in chars if c.isalpha()])
        uppercase_ratio = uppercase_letters / (letter_count + 1)
        exclaim = text.count("!")
        question = text.count("?")
        # Log scale word and char counts to reduce dynamic range
        def log1p_norm(x: int) -> float:
            return math.log1p(x + 1)

        features = np.array(
            [
                log1p_norm(word_count),
                log1p_norm(char_count),
                unique_ratio,
                avg_word_len,
                punct_ratio,
                uppercase_ratio,
                math.log1p(exclaim),
                math.log1p(question),
            ],
            dtype=np.float32,
        )
        return features

    # ---------------------
    # Public API
    # ---------------------
    def extract_embedding(self, text: str) -> np.ndarray:
        """
        Get the raw embedding for a single text (shape: (embedding_dim,)).
        Uses an LRU cache for repeated inputs.
        """
        return self._encode_cached(text)

    def extract_sentiment(self, text: str) -> np.ndarray:
        """
        Extract sentiment features as a 3-d vector [pos, neg, neutral].
        Fall back to neutral when sentiment pipeline unavailable or on errors.
        """
        if not self.use_sentiment:
            return np.zeros(SENTIMENT_DIM, dtype=np.float32)

        if getattr(self, "_have_transformers", False):
            try:
                pipe = self._init_sentiment_pipeline()
                # pipeline returns a list; limit text length for performance
                out = pipe(text[:1024])
                if isinstance(out, (list, tuple)) and len(out) > 0:
                    res = out[0]
                    label = str(res.get("label", "")).lower()
                    score = float(res.get("score", 0.0))
                    # SST-2 based: POSITIVE/NEGATIVE
                    if "positive" in label:
                        vec = np.array([score, 1.0 - score, 0.0], dtype=np.float32)
                    elif "negative" in label:
                        vec = np.array([1.0 - score, score, 0.0], dtype=np.float32)
                    else:
                        # For other labels, treat as neutral
                        vec = np.array([0.0, 0.0, 1.0], dtype=np.float32)
                    return vec
            except Exception as e:
                logger.warning("Sentiment extraction failed: %s", e)

        # Default neutral fallback
        return np.array([0.0, 0.0, 1.0], dtype=np.float32)

    def extract_features(self, text: str) -> np.ndarray:
        """
        Extract the full feature vector for a single text.
        Returns an array of shape (total_dim,) dtype float32.
        """
        emb = self.extract_embedding(text)  # embedding_dim
        sent = self.extract_sentiment(text) if self.use_sentiment else np.zeros(0, dtype=np.float32)
        ling = self._linguistic_features(text)
        features = np.concatenate([emb, sent, ling]).astype(np.float32)
        # safety pad/trim
        features = self._pad_or_trim(features, self.total_dim)
        return features

    def extract_features_batch(self, texts: Sequence[str], batch_size: int = 32) -> np.ndarray:
        """
        Efficient batch extraction. Tries to use bulk encoder if possible.

        Args:
            texts: sequence of strings
            batch_size: batch size for encoding when using SentenceTransformer

        Returns:
            ndarray of shape (len(texts), total_dim)
        """
        texts = list(map(lambda x: x if isinstance(x, str) else str(x), texts))
        n = len(texts)
        if n == 0:
            return np.zeros((0, self.total_dim), dtype=np.float32)

        # 1) Bulk encode embeddings if sentence-transformers available
        embeddings = []
        if self._have_sentence_transformers:
            try:
                enc = self._init_sentence_transformer()
                # Use sentence-transformers encode in batches for speed
                arr = enc.encode(texts, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=False)
                arr = np.asarray(arr, dtype=np.float32)
                # Normalize if requested
                if self._normalize:
                    norms = np.linalg.norm(arr, axis=1, keepdims=True)
                    norms[norms == 0] = 1.0
                    arr = arr / norms
                # ensure correct dims
                arr = np.stack([self._pad_or_trim(v, self.embedding_dim) for v in arr], axis=0)
                embeddings = arr
            except Exception as e:
                logger.warning("Bulk sentence-transformer encoding failed: %s", e)
                embeddings = None

        # 2) TF-IDF fallback (vectorizer requires fit; fit on corpus if available)
        if embeddings is None and self._have_sklearn:
            try:
                vec = self._init_tfidf()
                vec.fit(texts)  # fit on the batch to create vocab
                mat = vec.transform(texts).astype(np.float32)
                arr = np.asarray(mat.todense())
                if self._normalize:
                    norms = np.linalg.norm(arr, axis=1, keepdims=True)
                    norms[norms == 0] = 1.0
                    arr = arr / norms
                arr = np.stack([self._pad_or_trim(v, self.embedding_dim) for v in arr], axis=0)
                embeddings = arr
            except Exception as e:
                logger.warning("Batch TF-IDF failed: %s", e)
                embeddings = None

        # 3) Per-sample fallback to cached single-encode
        if embeddings is None:
            embeddings = np.stack([self.extract_embedding(t) for t in texts], axis=0)

        # Sentiment batch (attempt to run pipeline in a single call if supported)
        if self.use_sentiment and getattr(self, "_have_transformers", False):
            try:
                pipe = self._init_sentiment_pipeline()
                sent_out = pipe(texts)  # most pipelines accept a list
                sent_arr = []
                for res in sent_out:
                    label = str(res.get("label", "")).lower()
                    score = float(res.get("score", 0.0))
                    if "positive" in label:
                        sent_arr.append([score, 1.0 - score, 0.0])
                    elif "negative" in label:
                        sent_arr.append([1.0 - score, score, 0.0])
                    else:
                        sent_arr.append([0.0, 0.0, 1.0])
                sentiment = np.asarray(sent_arr, dtype=np.float32)
            except Exception as e:
                logger.warning("Bulk sentiment pipeline failed: %s", e)
                sentiment = np.stack([self.extract_sentiment(t) for t in texts], axis=0)
        elif self.use_sentiment:
            sentiment = np.stack([self.extract_sentiment(t) for t in texts], axis=0)
        else:
            sentiment = np.zeros((n, 0), dtype=np.float32)

        # Linguistic features for all texts
        ling = np.stack([self._linguistic_features(t) for t in texts], axis=0).astype(np.float32)

        # Concatenate final features
        features = np.concatenate([embeddings, sentiment, ling], axis=1)
        # Safety pad/trim to total_dim
        if features.shape[1] != self.total_dim:
            features = np.asarray([self._pad_or_trim(row, self.total_dim) for row in features], dtype=np.float32)
        return features

    # Convenience top-level function equivalent
    @staticmethod
    def extract_text_features_batch(text_batch: Sequence[str], **kwargs) -> np.ndarray:
        """
        Backwards-compatible convenience function for batch extraction.
        Example: TextFeatureExtractor.extract_text_features_batch(["one", "two"], model_name="all-MiniLM-L6-v2")
        """
        extractor = TextFeatureExtractor(**kwargs)
        return extractor.extract_features_batch(text_batch)
