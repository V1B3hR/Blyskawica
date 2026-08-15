use candle_core::{Device, Tensor, Result as CandleResult};

#[derive(Debug)]
pub struct LocalInferenceEngine {
    device: Device,
    w1: Tensor,
    b1: Tensor,
    w2: Tensor,
    b2: Tensor,
}

impl LocalInferenceEngine {
    pub fn load_cpu(data: &[u8]) -> Result<Self, String> {
        Self::load_from_slice(data, &Device::Cpu)
    }

    /// Tworzy silnik wnioskowania na podstawie surowego bufora bajtów (np. z mock_weights.bin).
    pub fn load_from_slice(data: &[u8], device: &Device) -> Result<Self, String> {
        let input_dim = 128;
        let hidden_dim = 64;
        
        let required_bytes = (input_dim * hidden_dim + hidden_dim + hidden_dim * input_dim + input_dim) * 4;
        if data.len() < required_bytes {
            return Err(format!(
                "Brak wystarczającej ilości danych w pliku wag. Otrzymano {} bajtów, wymagane co najmniej {} bajtów.",
                data.len(),
                required_bytes
            ));
        }

        // Odczyt f32 z Little Endian
        let mut floats = vec![0.0f32; required_bytes / 4];
        for (i, float_val) in floats.iter_mut().enumerate() {
            let start = i * 4;
            let bytes = [data[start], data[start + 1], data[start + 2], data[start + 3]];
            *float_val = f32::from_le_bytes(bytes);
        }

        let mut offset = 0;
        
        // Layer 1 weights: [64, 128]
        let w1_len = hidden_dim * input_dim;
        let w1_data = floats[offset..offset + w1_len].to_vec();
        offset += w1_len;
        
        // Layer 1 biases: [64]
        let b1_len = hidden_dim;
        let b1_data = floats[offset..offset + b1_len].to_vec();
        offset += b1_len;
        
        // Layer 2 weights: [128, 64]
        let w2_len = input_dim * hidden_dim;
        let w2_data = floats[offset..offset + w2_len].to_vec();
        offset += w2_len;
        
        // Layer 2 biases: [128]
        let b2_len = input_dim;
        let b2_data = floats[offset..offset + b2_len].to_vec();

        // Konwersja do tensorów Candle
        let w1 = Tensor::from_slice(&w1_data, &[hidden_dim, input_dim], device)
            .map_err(|e| format!("Błąd ładowania w1: {}", e))?;
        let b1 = Tensor::from_slice(&b1_data, &[hidden_dim], device)
            .map_err(|e| format!("Błąd ładowania b1: {}", e))?;
        let w2 = Tensor::from_slice(&w2_data, &[input_dim, hidden_dim], device)
            .map_err(|e| format!("Błąd ładowania w2: {}", e))?;
        let b2 = Tensor::from_slice(&b2_data, &[input_dim], device)
            .map_err(|e| format!("Błąd ładowania b2: {}", e))?;

        Ok(Self {
            device: device.clone(),
            w1,
            b1,
            w2,
            b2,
        })
    }

    /// Przeprowadza projekcję wektora o wymiarowości 128 przez sieć MLP.
    pub fn project(&self, input: &[f32]) -> Result<Vec<f32>, String> {
        if input.len() != 128 {
            return Err(format!("Nieprawidłowy wymiar wektora wejściowego: {}, oczekiwano 128.", input.len()));
        }

        let run = || -> CandleResult<Vec<f32>> {
            let x = Tensor::from_slice(input, &[1, 128], &self.device)?;
            
            // Warstwa 1: matmul z transponowaną wagą [128, 64] + bias [64] -> ReLU
            let x = x.matmul(&self.w1.t()?)?;
            let x = x.broadcast_add(&self.b1)?;
            let x = x.relu()?;
            
            // Warstwa 2: matmul z transponowaną wagą [64, 128] + bias [128]
            let x = x.matmul(&self.w2.t()?)?;
            let x = x.broadcast_add(&self.b2)?;
            
            // Normalizacja L2 wyjściowego wektora
            let sq_sum = x.sqr()?.sum_all()?;
            let norm_val = sq_sum.to_scalar::<f32>()?.sqrt();
            let x = if norm_val > 1e-6 {
                let norm_tensor = Tensor::new(norm_val, &self.device)?;
                x.broadcast_div(&norm_tensor)?
            } else {
                x
            };
            
            let output = x.to_vec2::<f32>()?;
            Ok(output[0].clone())
        };

        run().map_err(|e| format!("Błąd obliczeń tensorowych w Candle: {}", e))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_local_inference_engine() {
        let device = Device::Cpu;
        let mut weights = vec![0.0f32; 16576];
        
        // Inicjalizacja Layer 1 (128 * 64) jako diagonalne przekładnie
        for h in 0..64 {
            weights[h * 128 + h * 2] = 0.5f32;
        }
        // Biases Layer 1 (64)
        for h in 0..64 {
            weights[128 * 64 + h] = 0.01f32;
        }
        // Inicjalizacja Layer 2 (64 * 128) jako diagonalne przekładnie wsteczne
        let l2_offset = 128 * 64 + 64;
        for o in 0..128 {
            let h = (o / 2).min(63);
            weights[l2_offset + o * 64 + h] = 0.5f32;
        }
        // Biases Layer 2 (128)
        let l2_bias_offset = l2_offset + 64 * 128;
        for o in 0..128 {
            weights[l2_bias_offset + o] = 0.005f32;
        }

        let mut byte_data = Vec::new();
        for &w in &weights {
            byte_data.extend_from_slice(&w.to_le_bytes());
        }

        let engine = LocalInferenceEngine::load_from_slice(&byte_data, &device);
        assert!(engine.is_ok(), "Błąd wczytywania silnika Candle: {:?}", engine.err());
        
        let engine = engine.unwrap();
        let mut input = vec![0.0f32; 128];
        input[0] = 1.0;
        
        let output = engine.project(&input);
        assert!(output.is_ok(), "Błąd projekcji wektora: {:?}", output.err());
        
        let output_vec = output.unwrap();
        assert_eq!(output_vec.len(), 128);
        
        // Normalizacja L2 gwarantuje, że długość wektora wynosi w przybliżeniu 1.0
        let sum_sq: f32 = output_vec.iter().map(|&x| x * x).sum();
        assert!((sum_sq - 1.0).abs() < 1e-4, "Długość wektora po normalizacji L2 powinna być bliska 1.0, a wynosi {}", sum_sq);
    }
}
