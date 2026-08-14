//! Native, zero-dependency offline text embedding engine for Blyskawica Core.
//! Generates L2-normalized dense vector representations for offline semantic search,
//! anomaly detection, and HNSW vector indexing.

use std::hash::{Hash, Hasher};
use std::collections::hash_map::DefaultHasher;

#[derive(Debug, Clone)]
pub struct NativeEmbedder {
    dimension: usize,
}

impl NativeEmbedder {
    /// Tworzy nowy instancję embeddera o zadanej wymiarowości (domyślnie 128).
    pub fn new(dimension: usize) -> Self {
        Self { dimension }
    }

    /// Generuje gęsty, znormalizowany wektor cech semantycznych z tekstu wejściowego.
    pub fn embed(&self, text: &str) -> Vec<f32> {
        let mut vector = vec![0.0f32; self.dimension];
        let cleaned = text.to_lowercase();
        let words: Vec<&str> = cleaned.split_whitespace().collect();

        if words.is_empty() {
            // Zwróć losowy zbalansowany wektor zerowy
            return vector;
        }

        // 1. Projekcja słów z wagowaniem pozycji (Sinusoidal Positional Encoding)
        for (pos, word) in words.iter().enumerate() {
            let mut hasher = DefaultHasher::new();
            word.hash(&mut hasher);
            let word_hash = hasher.finish();

            let base_idx = (word_hash as usize) % self.dimension;
            let weight = 1.0 / (1.0 + (pos as f32) * 0.05);

            // Aktywacja sąsiadujących wymiarów
            for offset in 0..4 {
                let idx = (base_idx + offset) % self.dimension;
                let angle = (pos as f32) / (100.0f32.powf((offset as f32) / 4.0));
                let harmonic = if offset % 2 == 0 { angle.sin() } else { angle.cos() };
                vector[idx] += weight * (1.0 + 0.5 * harmonic);
            }

            // 2. Character N-Grams (subword feature projection)
            let chars: Vec<char> = word.chars().collect();
            if chars.len() >= 3 {
                for window in chars.windows(3) {
                    let gram: String = window.iter().collect();
                    let mut gram_hasher = DefaultHasher::new();
                    gram.hash(&mut gram_hasher);
                    let gram_idx = (gram_hasher.finish() as usize) % self.dimension;
                    vector[gram_idx] += 0.3 * weight;
                }
            }
        }

        // 3. Normalizacja L2 (Unit Vector) do porównań cosinusowych w HNSW
        let norm_sq: f32 = vector.iter().map(|v| v * v).sum();
        if norm_sq > 0.0 {
            let norm = norm_sq.sqrt();
            for val in vector.iter_mut() {
                *val /= norm;
            }
        }

        vector
    }

    /// Oblicza podobieństwo cosinusowe pomiędzy dwoma tekstami bezpośrednio w pamięci.
    pub fn cosine_similarity(&self, text_a: &str, text_b: &str) -> f32 {
        let vec_a = self.embed(text_a);
        let vec_b = self.embed(text_b);

        vec_a.iter().zip(vec_b.iter()).map(|(a, b)| a * b).sum()
    }
}

impl Default for NativeEmbedder {
    fn default() -> Self {
        Self::new(128)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_native_embedder_dimension_and_norm() {
        let embedder = NativeEmbedder::new(128);
        let vec = embedder.embed("Błyskawica to natywny system kognitywny offline");

        assert_eq!(vec.len(), 128);
        let norm_sq: f32 = vec.iter().map(|v| v * v).sum();
        assert!((norm_sq - 1.0).abs() < 1e-4, "Wektor musi mieć długość 1.0 (L2-norm)");
    }

    #[test]
    fn test_semantic_similarity_ranking() {
        let embedder = NativeEmbedder::new(128);
        let query = "bezpieczeństwo cybernetyczne i ochrona danych";
        let match_similar = "ochrona danych oraz systemy cybernetyczne";
        let match_dissimilar = "przepis na pyszne ciasto truskawkowe z kremem";

        let sim_similar = embedder.cosine_similarity(query, match_similar);
        let sim_dissimilar = embedder.cosine_similarity(query, match_dissimilar);

        assert!(
            sim_similar > sim_dissimilar,
            "Podobne teksty ({:.4}) muszą mieć wyższe podobieństwo niż odmienne ({:.4})",
            sim_similar,
            sim_dissimilar
        );
    }
}
