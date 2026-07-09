use std::time::{Instant, Duration};
use tokio::time::sleep;

pub struct TempoThrottle {
    last_request_time: Instant,
    request_count_window: usize,
    window_start: Instant,
    cortisol_multiplier: f32,
}

impl Default for TempoThrottle {
    fn default() -> Self {
        Self::new()
    }
}

impl TempoThrottle {
    pub fn new() -> Self {
        Self {
            last_request_time: Instant::now(),
            request_count_window: 0,
            window_start: Instant::now(),
            cortisol_multiplier: 1.0,
        }
    }

    /// Analizuje czas nadejścia zapytania i decyduje o nałożeniu kary opóźniającej (Jitter)
    pub async fn audit_request_speed(&mut self, current_cortisol: f32) -> f32 {
        let now = Instant::now();
        let elapsed_since_last = now.duration_since(self.last_request_time);
        self.last_request_time = now;

        // Aktualizacja okna czasowego (1 sekunda)
        if now.duration_since(self.window_start) > Duration::from_secs(1) {
            self.request_count_window = 0;
            self.window_start = now;
        }
        self.request_count_window += 1;

        // Dynamiczne wyliczenie poziomu zagrożenia na podstawie Kortyzolu
        self.cortisol_multiplier = 1.0 + (current_cortisol * 0.5);

        // Detekcja nieludzkiej prędkości (Machine-Speed Detection)
        if self.request_count_window > 8 || elapsed_since_last < Duration::from_millis(150) {
            // Obliczenie kary czasowej z dodatkiem losowego szumu (Jitter) w celu zmylenia potencjalnego agenta
            let raw_delay = 200 * self.request_count_window as u64;
            let jitter = {
                let mut rng = rand::thread_rng();
                use rand::Rng;
                rng.gen_range(0..300) * (self.cortisol_multiplier as u64)
            };
            let total_delay = Duration::from_millis(raw_delay + jitter);
            
            println!(
                "🛡️ [TEMPO THROTTLE]: Wykryto prędkość maszynową! Opóźnienie: {} ms",
                raw_delay + jitter
            );
            // Wstrzymanie pętli wykonawczej Tokio (Throttling)
            sleep(total_delay).await;

            // Zwracamy współczynnik wzrostu stresu dla neurochemii
            return 0.15 * self.request_count_window as f32;
        }

        0.0 // Brak anomalii szybkościowych
    }
}
