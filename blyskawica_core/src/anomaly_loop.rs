
pub struct VirtualGround {
    pub ground_potential: f32,
}

impl VirtualGround {
    pub fn new() -> Self {
        Self { ground_potential: 0.0 }
    }

    /// Odprowadza szum poznawczy do wirtualnej ziemi.
    pub fn shunt(&mut self, noise: &[f32]) -> f32 {
        if noise.is_empty() {
            return self.ground_potential;
        }
        // Obliczamy energię (średnią kwadratową szumu)
        let sum_sq: f32 = noise.iter().map(|&x| x * x).sum();
        let energy = sum_sq / (noise.len() as f32);
        
        // Zmniejszamy potencjał asynchronicznie, rozpraszając energię do zera
        self.ground_potential = 0.99 * self.ground_potential + 0.01 * energy;
        self.ground_potential
    }
}

pub struct GroundLoopIsolator {
    pub isolation_ratio: f32,
    pub ground: VirtualGround,
}

impl GroundLoopIsolator {
    pub fn new(isolation_ratio: f32) -> Self {
        Self {
            isolation_ratio,
            ground: VirtualGround::new(),
        }
    }

    /// Przetwarza wektor wejściowy, filtruje składowe szumu (buczenie) i izoluje je galwanicznie.
    pub fn forward(&mut self, input_signal: &[f32]) -> Vec<f32> {
        if input_signal.is_empty() {
            return Vec::new();
        }

        // KROK 1: Identyfikacja "buczenia" (Hum / DC offset jako wartość średnia)
        let sum: f32 = input_signal.iter().sum();
        let hum = sum / (input_signal.len() as f32);

        // Adaptacyjny współczynnik izolacji na podstawie aktualnego potencjału ziemi
        let current_cutoff = self.isolation_ratio * (1.0 + self.ground.ground_potential * 0.2);

        // KROK 2: Oddzielenie szumu błądzącego
        let mut noise = Vec::with_capacity(input_signal.len());
        for &val in input_signal {
            let diff = (val - hum).abs();
            if diff < current_cutoff {
                // Prąd błądzący: szum statyczny blisko wartości średniej
                noise.push(val + hum * 0.1);
            } else {
                noise.push(0.0);
            }
        }

        // KROK 3: Uziemienie (rozproszenie w VirtualGround)
        let ground_energy = self.ground.shunt(&noise);

        // KROK 4: Indukcja matematyczna (Galvanic Isolation)
        let mut clean_signal = Vec::with_capacity(input_signal.len());
        for (i, &val) in input_signal.iter().enumerate() {
            let clean = val - noise[i];
            // Przywrócenie dynamiki za pomocą zgromadzonej energii uziemienia
            let restored = clean * (1.0 + ground_energy * 0.005);
            clean_signal.push(restored);
        }

        clean_signal
    }
}

#[derive(Debug, Clone)]
pub struct AnomalyQueueItem {
    pub id: usize,
    pub vector: Vec<f32>,
    pub metadata: String,
}

pub struct AnomalyDetector {
    pub surprise_threshold: f32,
    pub queue: Vec<AnomalyQueueItem>,
    pub ground_isolator: GroundLoopIsolator,
}

impl AnomalyDetector {
    pub fn new(surprise_threshold: f32, isolation_ratio: f32) -> Self {
        Self {
            surprise_threshold,
            queue: Vec::new(),
            ground_isolator: GroundLoopIsolator::new(isolation_ratio),
        }
    }

    /// Analizuje surowy wektor wejściowy, oczyszcza go izolatorem pętli masy,
    /// sprawdza poziom zaskoczenia na podstawie odległości cosinusowej i ewentualnie kolejkuje jako anomalię.
    pub fn inspect_and_queue(
        &mut self,
        vector_id: usize,
        raw_vector: &[f32],
        best_distance: f32,
        metadata: String,
    ) -> (Vec<f32>, bool) {
        // Izolacja szumu
        let clean_vector = self.ground_isolator.forward(raw_vector);

        // Wyznaczenie anomalii (dystans cosinusowy powyżej progu zaskoczenia)
        let is_anomaly = best_distance > self.surprise_threshold;

        if is_anomaly {
            self.queue.push(AnomalyQueueItem {
                id: vector_id,
                vector: clean_vector.clone(),
                metadata,
            });
        }

        (clean_vector, is_anomaly)
    }

    pub fn get_queue_len(&self) -> usize {
        self.queue.len()
    }

    pub fn drain_queue(&mut self) -> Vec<AnomalyQueueItem> {
        std::mem::take(&mut self.queue)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_virtual_ground_shunting() {
        let mut ground = VirtualGround::new();
        let noise = vec![0.5, -0.5, 0.2];
        let potential_before = ground.ground_potential;
        ground.shunt(&noise);
        assert!(ground.ground_potential > potential_before);
    }

    #[test]
    fn test_ground_loop_isolator() {
        let mut isolator = GroundLoopIsolator::new(0.1);
        let signal = vec![0.5, 0.52, 0.9, 0.1];
        let clean = isolator.forward(&signal);
        assert_eq!(clean.len(), signal.len());
        // Wartości bliskie średniej powinny zostać częściowo wygładzone (odjęte)
        assert!(isolator.ground.ground_potential > 0.0);
    }
}
