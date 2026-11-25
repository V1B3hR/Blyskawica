//! V11.3: Asynchroniczny Sen Kognitywny i Regularyzacja EWC (Elastic Weight Consolidation).
//!
//! Natywny port Rust mechanizmu konsolidacji wektorów zaskoczenia (Surprise Vectors)
//! z zachowaniem ciągłości matematycznej względem referencji Python
//! (`adaptiveneuralnetwork/central_nervous_system/intelligence/consolidation.py`)
//! oraz zgodności binarnej z układem wag `LocalInferenceEngine` (128 → 64 → 128 MLP).
//!
//! Gwarancje bezpieczeństwa (fail-closed):
//! - Wszystkie wektory wejściowe i wagi przechodzą walidację IEEE 754 (`is_finite()`).
//! - Kolejka anomalii ma sztywny limit pojemności (`MAX_SURPRISE_QUEUE`) chroniący przed OOM/DoS.
//! - Aktualizacja gradientowa stosuje przycinanie normy L2 (`MAX_GRAD_NORM`) oraz atomowy rollback
//!   w przypadku wykrycia wartości niefinitywnych.
//! - Krystalizacja wag na dysku jest atomowa (plik tymczasowy + `sync_all` + `rename`)
//!   i zabezpieczona pieczęcią SHA-256 + HMAC-SHA256 (weryfikowaną w czasie stałym).

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::fs::{self, File};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use crate::neurochemistry::NeurochemicalState;

pub const INPUT_DIM: usize = 128;
pub const HIDDEN_DIM: usize = 64;
pub const W1_LEN: usize = HIDDEN_DIM * INPUT_DIM; // 8_192
pub const B1_LEN: usize = HIDDEN_DIM; // 64
pub const W2_LEN: usize = INPUT_DIM * HIDDEN_DIM; // 8_192
pub const B2_LEN: usize = INPUT_DIM; // 128
pub const TOTAL_PARAMS: usize = W1_LEN + B1_LEN + W2_LEN + B2_LEN; // 16_576
pub const REQUIRED_WEIGHT_BYTES: usize = TOTAL_PARAMS * 4; // 66_304

pub const MAX_SURPRISE_QUEUE: usize = 256;
pub const MAX_METADATA_CHARS: usize = 256;
pub const MAX_GRAD_NORM: f32 = 1.0;
pub const MAX_ADAPT_STRENGTH: f32 = 0.05;
pub const DEFAULT_EWC_LAMBDA: f32 = 10.0;
pub const SEAL_FORMAT_VERSION: u32 = 1;

/// Neurochemiczny profil snu mapujący stan neuroprzekaźników na parametry plastyczności.
/// Zachowuje pełną zgodność formuł z `SleepProfile` w Pythonie.
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq)]
pub struct SleepProfile {
    pub melatonin: f32,
    pub gaba: f32,
    pub serotonin: f32,
    pub adenosine_cleared: f32,
}

impl Default for SleepProfile {
    fn default() -> Self {
        Self {
            melatonin: 0.7,
            gaba: 0.6,
            serotonin: 0.75,
            adenosine_cleared: 0.8,
        }
    }
}

impl SleepProfile {
    pub fn from_neurochemistry(ns: &NeurochemicalState) -> Self {
        let sanitize = |val: f32, default: f32| -> f32 {
            if val.is_finite() {
                val.clamp(0.0, 1.0)
            } else {
                default
            }
        };
        let serotonin = sanitize(ns.serotonin, 0.75);
        let adenosine = sanitize(ns.adenosine, 0.4);
        let gaba = sanitize(ns.gaba, 0.6);

        let melatonin = (1.0 - adenosine / 1.5).clamp(0.1, 1.0);
        let adenosine_cleared = (1.0 - adenosine).clamp(0.0, 1.0);

        Self {
            melatonin,
            gaba,
            serotonin,
            adenosine_cleared,
        }
    }

    /// Głębokość konsolidacji: melatonina × wypoczynek.
    pub fn consolidation_depth(&self) -> f32 {
        (self.melatonin * self.adenosine_cleared).clamp(0.0, 1.0)
    }

    /// Próg poniżej którego niekrytyczne wagi ulegają wygaszeniu (0.05..0.20).
    pub fn pruning_threshold(&self) -> f32 {
        0.05 + self.gaba.clamp(0.0, 1.0) * 0.15
    }

    /// Bramka plastyczności modulowana serotoniną (0.5..1.0).
    pub fn plasticity_gate(&self) -> f32 {
        1.0 - self.serotonin.clamp(0.0, 1.0) * 0.5
    }
}

/// Zarejestrowany wektor zaskoczenia (anomalia dzienna do asymilacji podczas snu).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SurpriseRecord {
    pub id: usize,
    pub surprise: f32,
    pub metadata: String,
    pub vector: Vec<f32>,
    pub timestamp_unix: u64,
}

/// Układ wag MLP 128 → 64 (ReLU) → 128 kompatybilny binarnie z `LocalInferenceEngine`.
#[derive(Debug, Clone)]
pub struct MlpWeights {
    pub params: Vec<f32>,
}

impl MlpWeights {
    /// Tworzy deterministyczny zestaw bazowych wag (zgodny z inicjalizacją w `sparkle_app`).
    pub fn deterministic_baseline() -> Self {
        let mut params = vec![0.0f32; TOTAL_PARAMS];
        for h in 0..HIDDEN_DIM {
            params[h * INPUT_DIM + h * 2] = 0.5f32;
        }
        for h in 0..HIDDEN_DIM {
            params[W1_LEN + h] = 0.01f32;
        }
        let l2_offset = W1_LEN + B1_LEN;
        for o in 0..INPUT_DIM {
            let h = (o / 2).min(HIDDEN_DIM - 1);
            params[l2_offset + o * HIDDEN_DIM + h] = 0.5f32;
        }
        let l2_bias_offset = l2_offset + W2_LEN;
        for o in 0..INPUT_DIM {
            params[l2_bias_offset + o] = 0.005f32;
        }
        Self { params }
    }

    /// Odczytuje wagi z surowego bufora Little Endian (`mock_weights.bin`).
    pub fn from_bytes(data: &[u8]) -> Result<Self, String> {
        if data.len() < REQUIRED_WEIGHT_BYTES {
            return Err(format!(
                "Za mało bajtów w pliku wag EWC: otrzymano {}, wymagane co najmniej {}.",
                data.len(),
                REQUIRED_WEIGHT_BYTES
            ));
        }
        let mut params = Vec::with_capacity(TOTAL_PARAMS);
        for i in 0..TOTAL_PARAMS {
            let start = i * 4;
            let val = f32::from_le_bytes([
                data[start],
                data[start + 1],
                data[start + 2],
                data[start + 3],
            ]);
            if !val.is_finite() {
                return Err(format!(
                    "Wykryto niefinitywną wartość wagi (NaN/Inf) pod indeksem {}.",
                    i
                ));
            }
            params.push(val);
        }
        Ok(Self { params })
    }

    /// Serializuje wagi do formatu Little Endian z opcjonalnym dopełnieniem rozmiaru pliku.
    pub fn to_bytes(&self, min_file_size: usize) -> Vec<u8> {
        let target_len = REQUIRED_WEIGHT_BYTES.max(min_file_size);
        let mut out = Vec::with_capacity(target_len);
        for &w in &self.params {
            out.extend_from_slice(&w.to_le_bytes());
        }
        if out.len() < target_len {
            out.resize(target_len, 0u8);
        }
        out
    }

    /// Zwraca skrót SHA-256 aktualnego wektora wag w formacie szesnastkowym.
    pub fn sha256_hex(&self) -> String {
        let raw = self.to_bytes(REQUIRED_WEIGHT_BYTES);
        sha256_hex_bytes(&raw)
    }

    /// Przebieg w przód (bez normalizacji L2 — surowa rekonstrukcja autoenkodera MLP).
    pub fn forward_raw(&self, input: &[f32]) -> Result<(Vec<f32>, Vec<f32>), String> {
        if input.len() != INPUT_DIM {
            return Err(format!(
                "Nieprawidłowy wymiar wektora: {}, oczekiwano {}.",
                input.len(),
                INPUT_DIM
            ));
        }

        let w1 = &self.params[0..W1_LEN];
        let b1 = &self.params[W1_LEN..W1_LEN + B1_LEN];
        let w2_start = W1_LEN + B1_LEN;
        let w2 = &self.params[w2_start..w2_start + W2_LEN];
        let b2 = &self.params[w2_start + W2_LEN..TOTAL_PARAMS];

        let mut hidden = vec![0.0f32; HIDDEN_DIM];
        for h in 0..HIDDEN_DIM {
            let row_offset = h * INPUT_DIM;
            let mut acc = b1[h];
            for i in 0..INPUT_DIM {
                acc += w1[row_offset + i] * input[i];
            }
            hidden[h] = if acc > 0.0 { acc } else { 0.0 };
        }

        let mut output = vec![0.0f32; INPUT_DIM];
        for o in 0..INPUT_DIM {
            let row_offset = o * HIDDEN_DIM;
            let mut acc = b2[o];
            for h in 0..HIDDEN_DIM {
                acc += w2[row_offset + h] * hidden[h];
            }
            output[o] = acc;
        }

        Ok((hidden, output))
    }

    /// Oblicza stratę rekonstrukcji MSE `1/D * ||y - target||^2` oraz dokładny gradient analityczny.
    pub fn mse_loss_and_grad(
        &self,
        input: &[f32],
        target: &[f32],
    ) -> Result<(f32, Vec<f32>), String> {
        if input.len() != INPUT_DIM || target.len() != INPUT_DIM {
            return Err(format!(
                "Nieprawidłowy wymiar wejścia/celu ({}/{}) — oczekiwano {}.",
                input.len(),
                target.len(),
                INPUT_DIM
            ));
        }

        let (hidden, output) = self.forward_raw(input)?;
        let mut grad = vec![0.0f32; TOTAL_PARAMS];

        let w2_start = W1_LEN + B1_LEN;
        let b2_start = w2_start + W2_LEN;
        let w2 = &self.params[w2_start..b2_start];

        let scale = 2.0f32 / (INPUT_DIM as f32);
        let mut d_out = [0.0f32; INPUT_DIM];
        let mut loss_sum = 0.0f32;

        for o in 0..INPUT_DIM {
            let diff = output[o] - target[o];
            loss_sum += diff * diff;
            d_out[o] = diff * scale;
            grad[b2_start + o] = d_out[o];
        }
        let loss = loss_sum / (INPUT_DIM as f32);

        // Gradient dla W2 oraz propagacja wsteczna do warstwy ukrytej
        let mut d_hidden = [0.0f32; HIDDEN_DIM];
        for o in 0..INPUT_DIM {
            let do_val = d_out[o];
            let row_offset = o * HIDDEN_DIM;
            for h in 0..HIDDEN_DIM {
                grad[w2_start + row_offset + h] = do_val * hidden[h];
                d_hidden[h] += do_val * w2[row_offset + h];
            }
        }

        // Przejście przez pochodną ReLU oraz gradient dla W1 i b1
        for h in 0..HIDDEN_DIM {
            if hidden[h] <= 0.0 {
                continue;
            }
            let dh = d_hidden[h];
            grad[W1_LEN + h] = dh;
            let row_offset = h * INPUT_DIM;
            for i in 0..INPUT_DIM {
                grad[row_offset + i] = dh * input[i];
            }
        }

        Ok((loss, grad))
    }
}

/// Pieczęć kryptograficzna zapisanych wag skonsolidowanych podczas snu.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct WeightIntegritySeal {
    pub version: u32,
    pub cycle: u64,
    pub timestamp_unix: u64,
    pub weights_sha256: String,
    pub hmac_seal_hex: String,
    pub ewc_saturation: f32,
    pub assimilated_count: usize,
}

/// Strukturalny raport z ukończonego cyklu asynchronicznego snu EWC.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EwcSleepReport {
    pub cycle: u64,
    pub assimilated_count: usize,
    pub remaining_queue: usize,
    pub mean_loss_before: f32,
    pub mean_loss_after: f32,
    pub ewc_penalty: f32,
    pub max_protected_weight_drift: f32,
    pub pruned_weights: usize,
    pub ewc_saturation: f32,
    pub weights_sha256: String,
    pub seal_verified: bool,
    pub profile: SleepProfile,
}

/// Główny koordynator asynchronicznego snu i regularyzacji EWC (V11.3).
#[derive(Debug, Clone)]
pub struct EwcSleepConsolidator {
    anchor_weights: Vec<f32>,
    fisher_diag: Vec<f32>,
    pub ewc_lambda: f32,
    surprise_queue: Vec<SurpriseRecord>,
    pub completed_cycles: u64,
    pub total_assimilated: u64,
    pub last_report: Option<EwcSleepReport>,
}

impl Default for EwcSleepConsolidator {
    fn default() -> Self {
        Self::new(DEFAULT_EWC_LAMBDA)
    }
}

impl EwcSleepConsolidator {
    pub fn new(ewc_lambda: f32) -> Self {
        let safe_lambda = if ewc_lambda.is_finite() && ewc_lambda >= 0.0 {
            ewc_lambda
        } else {
            DEFAULT_EWC_LAMBDA
        };
        let baseline = MlpWeights::deterministic_baseline();
        Self {
            anchor_weights: baseline.params,
            fisher_diag: vec![0.0f32; TOTAL_PARAMS],
            ewc_lambda: safe_lambda,
            surprise_queue: Vec::new(),
            completed_cycles: 0,
            total_assimilated: 0,
            last_report: None,
        }
    }

    pub fn queue_len(&self) -> usize {
        self.surprise_queue.len()
    }

    pub fn fisher_diagonal(&self) -> &[f32] {
        &self.fisher_diag
    }

    pub fn anchor_weights(&self) -> &[f32] {
        &self.anchor_weights
    }

    /// Rejestruje wektor zaskoczenia do konsolidacji podczas fazy `DEEP_SLEEP`.
    /// Odrzuca niefinitywne wartości (NaN/Inf) i wymusza limit kolejki `MAX_SURPRISE_QUEUE`.
    pub fn record_surprise(
        &mut self,
        id: usize,
        surprise: f32,
        metadata: impl Into<String>,
        raw_vector: &[f32],
    ) -> Result<bool, String> {
        if !surprise.is_finite() || surprise < 0.0 {
            return Err("Nieprawidłowa wartość zaskoczenia (wymagana skończona >= 0.0).".into());
        }
        if raw_vector.is_empty() {
            return Err("Wektor zaskoczenia nie może być pusty.".into());
        }
        if raw_vector.iter().any(|v| !v.is_finite()) {
            return Err("Wektor zaskoczenia zawiera wartości niefinitywne (NaN/Inf).".into());
        }

        let vector = normalize_vector_128(raw_vector);
        let mut meta = metadata.into();
        if meta.chars().count() > MAX_METADATA_CHARS {
            meta = meta.chars().take(MAX_METADATA_CHARS).collect();
        }

        let record = SurpriseRecord {
            id,
            surprise: surprise.min(10.0),
            metadata: meta,
            vector,
            timestamp_unix: unix_timestamp_secs(),
        };

        if self.surprise_queue.len() >= MAX_SURPRISE_QUEUE {
            // Ochrona przed OOM/DoS: zastąp pozycję o najmniejszym zaskoczeniu, jeśli nowa jest ważniejsza
            if let Some((min_idx, min_item)) = self
                .surprise_queue
                .iter()
                .enumerate()
                .min_by(|(_, a), (_, b)| a.surprise.total_cmp(&b.surprise))
            {
                if record.surprise > min_item.surprise {
                    self.surprise_queue[min_idx] = record;
                    return Ok(true);
                }
            }
            return Ok(false);
        }

        self.surprise_queue.push(record);
        Ok(true)
    }

    /// Estymuje diagonalną macierz informacyjną Fishera na próbkach bazowych i kotwiczy wagi `theta*`.
    pub fn estimate_fisher(
        &mut self,
        weights: &MlpWeights,
        baseline_samples: &[Vec<f32>],
    ) -> Result<f32, String> {
        if baseline_samples.is_empty() {
            return Err("Brak próbek bazowych do estymacji macierzy Fishera.".into());
        }

        let mut accum = vec![0.0f32; TOTAL_PARAMS];
        let mut valid_count = 0usize;

        for sample in baseline_samples {
            if sample.is_empty() || sample.iter().any(|v| !v.is_finite()) {
                return Err("Próbka bazowa Fishera zawiera niefinitywne lub puste dane.".into());
            }
            let x = normalize_vector_128(sample);
            let (_, grad) = weights.mse_loss_and_grad(&x, &x)?;
            for (acc, g) in accum.iter_mut().zip(grad.iter()) {
                *acc += g * g;
            }
            valid_count += 1;
        }

        let inv_n = 1.0f32 / (valid_count as f32);
        let mut total_fisher = 0.0f32;
        for (f_slot, sq_sum) in self.fisher_diag.iter_mut().zip(accum.iter()) {
            let estimated = (*sq_sum * inv_n).clamp(0.0, 1e4);
            // Akumulacja ciągła (online EWC): zachowujemy ochronę wcześniejszych zadań
            *f_slot = (*f_slot * 0.85 + estimated).clamp(0.0, 1e4);
            total_fisher += *f_slot;
        }
        self.anchor_weights = weights.params.clone();

        Ok(total_fisher)
    }

    /// Ustawia jawnie diagonalę Fishera oraz wagi kotwiczące (przydatne w testach ciągłości i przywracaniu stanu).
    pub fn set_anchor_and_fisher(
        &mut self,
        anchor_weights: Vec<f32>,
        fisher_diag: Vec<f32>,
    ) -> Result<(), String> {
        if anchor_weights.len() != TOTAL_PARAMS || fisher_diag.len() != TOTAL_PARAMS {
            return Err(format!(
                "Nieprawidłowy rozmiar wektorów kotwicy/Fishera: oczekiwano {}.",
                TOTAL_PARAMS
            ));
        }
        if anchor_weights.iter().any(|v| !v.is_finite())
            || fisher_diag.iter().any(|v| !v.is_finite() || *v < 0.0)
        {
            return Err("Kotwica lub diagonala Fishera zawiera nieprawidłowe wartości.".into());
        }
        self.anchor_weights = anchor_weights;
        self.fisher_diag = fisher_diag;
        Ok(())
    }

    /// Oblicza bieżącą karę EWC: `0.5 * lambda * sum(F_i * (theta_i - theta*_i)^2)`.
    pub fn compute_ewc_penalty(&self, weights: &MlpWeights) -> f32 {
        let mut sum = 0.0f64;
        for ((&w, &anchor), &fisher) in weights
            .params
            .iter()
            .zip(self.anchor_weights.iter())
            .zip(self.fisher_diag.iter())
        {
            let diff = (w - anchor) as f64;
            sum += (fisher as f64) * diff * diff;
        }
        (0.5 * (self.ewc_lambda as f64) * sum) as f32
    }

    /// Oblicza aktualny poziom saturacji EWC w przedziale `[0.0, 1.0]`.
    pub fn compute_ewc_saturation(&self) -> f32 {
        let mean_fisher: f64 =
            self.fisher_diag.iter().map(|&f| f as f64).sum::<f64>() / (TOTAL_PARAMS as f64);
        // Płynna saturacja asymptotyczna `1 - exp(-k * mean_fisher)`
        let sat = 1.0 - (-mean_fisher * 500.0).exp();
        (sat as f32).clamp(0.0, 1.0)
    }

    /// Wykonuje pojedynczy cykl konsolidacji EWC na wagach MLP, opróżniając zakolejkowane anomalie.
    /// W przypadku jakiegokolwiek błędu numerycznego (NaN/Inf) wykonuje atomowy rollback wag.
    pub fn consolidate_weights(
        &mut self,
        weights: &mut MlpWeights,
        profile: &SleepProfile,
    ) -> Result<EwcSleepReport, String> {
        if weights.params.len() != TOTAL_PARAMS {
            return Err("Nieprawidłowa liczba parametrów MLP.".into());
        }

        if self.surprise_queue.is_empty() {
            let report = EwcSleepReport {
                cycle: self.completed_cycles,
                assimilated_count: 0,
                remaining_queue: 0,
                mean_loss_before: 0.0,
                mean_loss_after: 0.0,
                ewc_penalty: self.compute_ewc_penalty(weights),
                max_protected_weight_drift: 0.0,
                pruned_weights: 0,
                ewc_saturation: self.compute_ewc_saturation(),
                weights_sha256: weights.sha256_hex(),
                seal_verified: true,
                profile: *profile,
            };
            self.last_report = Some(report.clone());
            return Ok(report);
        }

        // Snapshot wag przed konsolidacją (atomowy rollback w razie anomalii numerycznej)
        let rollback_snapshot = weights.params.clone();

        // Priorytetyzacja anomalii od największego zaskoczenia (zgodnie z Python ConsolidationEngine)
        let mut batch = std::mem::take(&mut self.surprise_queue);
        batch.sort_by(|a, b| b.surprise.total_cmp(&a.surprise));

        // Średnia strata rekonstrukcji przed konsolidacją
        let mut loss_before_sum = 0.0f32;
        for item in &batch {
            let (loss, _) = weights.mse_loss_and_grad(&item.vector, &item.vector)?;
            loss_before_sum += loss;
        }
        let mean_loss_before = loss_before_sum / (batch.len() as f32);

        // Kroki gradientowe EWC (3 epoki mikro-konsolidacji na paczce)
        let depth = profile.consolidation_depth().max(0.1);
        let gate = profile.plasticity_gate().max(0.25);

        for _epoch in 0..3 {
            for item in &batch {
                let adapt_strength =
                    (item.surprise * depth * gate * 0.05).clamp(1e-4, MAX_ADAPT_STRENGTH);
                let (_, mut grad) = weights.mse_loss_and_grad(&item.vector, &item.vector)?;

                // Dodanie pochodnej kary EWC: lambda * F_i * (theta_i - theta*_i)
                let mut sq_norm = 0.0f64;
                for i in 0..TOTAL_PARAMS {
                    let ewc_grad = self.ewc_lambda
                        * self.fisher_diag[i]
                        * (weights.params[i] - self.anchor_weights[i]);
                    grad[i] += ewc_grad;
                    sq_norm += (grad[i] as f64) * (grad[i] as f64);
                }

                // Przycinanie normy L2 gradientu (ochrona przed wybuchem gradientów)
                let norm = sq_norm.sqrt() as f32;
                let clip_scale = if norm > MAX_GRAD_NORM && norm.is_finite() {
                    MAX_GRAD_NORM / norm
                } else {
                    1.0
                };

                for i in 0..TOTAL_PARAMS {
                    let updated = weights.params[i] - adapt_strength * grad[i] * clip_scale;
                    if !updated.is_finite() {
                        weights.params = rollback_snapshot;
                        self.surprise_queue = batch;
                        return Err(
                            "Przerwano konsolidację EWC: wykryto niefinitywną wagę (wykonano rollback)."
                                .into(),
                        );
                    }
                    weights.params[i] = updated;
                }
            }
        }

        // Delikatny GABA-modulowany pruning wyłącznie na niechronionych wagach (niskie F_i)
        let fisher_max = self.fisher_diag.iter().copied().fold(0.0f32, f32::max);
        let protected_cutoff = (fisher_max * 0.1).max(1e-6);
        let prune_amp = profile.pruning_threshold() * 0.05; // konserwatywny próg wygaszania małych wag
        let mut pruned_weights = 0usize;

        for i in 0..TOTAL_PARAMS {
            if self.fisher_diag[i] < protected_cutoff
                && weights.params[i].abs() > 0.0
                && weights.params[i].abs() < prune_amp
            {
                weights.params[i] *= 0.9;
                pruned_weights += 1;
            }
        }

        // Pomiar maksymalnego dryfu na chronionych wagach o wysokim Fisherze
        let mut max_protected_weight_drift = 0.0f32;
        if fisher_max > 0.0 {
            for i in 0..TOTAL_PARAMS {
                if self.fisher_diag[i] >= protected_cutoff {
                    let drift = (weights.params[i] - self.anchor_weights[i]).abs();
                    if drift > max_protected_weight_drift {
                        max_protected_weight_drift = drift;
                    }
                }
            }
        }

        // Średnia strata po konsolidacji
        let mut loss_after_sum = 0.0f32;
        for item in &batch {
            let (loss, _) = weights.mse_loss_and_grad(&item.vector, &item.vector)?;
            loss_after_sum += loss;
        }
        let mean_loss_after = loss_after_sum / (batch.len() as f32);
        let ewc_penalty = self.compute_ewc_penalty(weights);

        // Aktualizacja macierzy Fishera i kotwicy nowo przyswojonymi pojęciami
        let assimilated_vectors: Vec<Vec<f32>> = batch.iter().map(|b| b.vector.clone()).collect();
        let _ = self.estimate_fisher(weights, &assimilated_vectors);

        self.completed_cycles += 1;
        self.total_assimilated += batch.len() as u64;
        let ewc_saturation = self.compute_ewc_saturation();

        let report = EwcSleepReport {
            cycle: self.completed_cycles,
            assimilated_count: batch.len(),
            remaining_queue: self.surprise_queue.len(),
            mean_loss_before,
            mean_loss_after,
            ewc_penalty,
            max_protected_weight_drift,
            pruned_weights,
            ewc_saturation,
            weights_sha256: weights.sha256_hex(),
            seal_verified: true,
            profile: *profile,
        };
        self.last_report = Some(report.clone());
        Ok(report)
    }

    /// Asynchroniczna konsolidacja EWC uruchamiana w puli wątków blokujących Tokio (`spawn_blocking`),
    /// dzięki czemu pętla czatu i zdarzeń pozostaje w pełni responsywna.
    pub async fn consolidate_file_async(
        consolidator: std::sync::Arc<tokio::sync::Mutex<Self>>,
        weights_path: PathBuf,
        profile: SleepProfile,
        seal_key: [u8; 32],
    ) -> Result<EwcSleepReport, String> {
        let mut guard = consolidator.lock().await;
        if guard.surprise_queue.is_empty() {
            let dummy = if weights_path.is_file() {
                fs::read(&weights_path)
                    .ok()
                    .and_then(|b| MlpWeights::from_bytes(&b).ok())
                    .unwrap_or_else(MlpWeights::deterministic_baseline)
            } else {
                MlpWeights::deterministic_baseline()
            };
            let mut w = dummy;
            return guard.consolidate_weights(&mut w, &profile);
        }

        // Wyjmujemy stan roboczy pod krótką blokadą i liczymy poza wątkami async Tokio
        let mut working = guard.clone();
        drop(guard);

        let path_clone = weights_path.clone();
        let (updated_consolidator, report) = tokio::task::spawn_blocking(move || {
            let (mut weights, original_size) = if path_clone.is_file() {
                let raw = fs::read(&path_clone)
                    .map_err(|e| format!("Błąd odczytu pliku wag przed snem EWC: {}", e))?;
                let len = raw.len();
                let w = MlpWeights::from_bytes(&raw)?;
                (w, len)
            } else {
                (MlpWeights::deterministic_baseline(), 1_024_000)
            };

            let mut report = working.consolidate_weights(&mut weights, &profile)?;
            if let Some(parent) = path_clone.parent()
                && !parent.as_os_str().is_empty()
            {
                let _ = fs::create_dir_all(parent);
            }
            let seal =
                save_sealed_weights(&path_clone, &weights, original_size, &report, &seal_key)?;
            report.seal_verified = verify_sealed_weights(&path_clone, &seal, &seal_key).is_ok();
            Ok::<(EwcSleepConsolidator, EwcSleepReport), String>((working, report))
        })
        .await
        .map_err(|e| format!("Błąd wątku roboczego snu EWC: {}", e))??;

        // Scalenie zaktualizowanego stanu Fishera, liczników i ewentualnych nowych anomalii z fazy czuwania
        let mut guard = consolidator.lock().await;
        let newly_arrived = std::mem::take(&mut guard.surprise_queue);
        *guard = updated_consolidator;
        for rec in newly_arrived {
            let _ = guard.record_surprise(rec.id, rec.surprise, rec.metadata, &rec.vector);
        }
        Ok(report)
    }
}

/// Zapisuje skonsolidowane wagi atomowo na dysku i generuje pieczęć HMAC-SHA256 w pliku `.ewc.seal.json`.
pub fn save_sealed_weights(
    weights_path: &Path,
    weights: &MlpWeights,
    min_file_size: usize,
    report: &EwcSleepReport,
    seal_key: &[u8; 32],
) -> Result<WeightIntegritySeal, String> {
    let bytes = weights.to_bytes(min_file_size);
    let weights_sha256 = sha256_hex_bytes(&bytes[..REQUIRED_WEIGHT_BYTES]);
    let timestamp_unix = unix_timestamp_secs();

    let seal_payload = format!(
        "v{}|c{}|t{}|{}|{:.6}|{}",
        SEAL_FORMAT_VERSION,
        report.cycle,
        timestamp_unix,
        weights_sha256,
        report.ewc_saturation,
        report.assimilated_count
    );
    let hmac_seal_hex = hex_encode(&hmac_sha256(seal_key, seal_payload.as_bytes()));

    let seal = WeightIntegritySeal {
        version: SEAL_FORMAT_VERSION,
        cycle: report.cycle,
        timestamp_unix,
        weights_sha256,
        hmac_seal_hex,
        ewc_saturation: report.ewc_saturation,
        assimilated_count: report.assimilated_count,
    };

    atomic_write_file(weights_path, &bytes)?;

    let seal_path = seal_manifest_path(weights_path);
    let manifest_bytes = serde_json::to_vec_pretty(&seal)
        .map_err(|e| format!("Błąd serializacji pieczęci EWC: {}", e))?;
    atomic_write_file(&seal_path, &manifest_bytes)?;

    Ok(seal)
}

/// Weryfikuje integralność pliku wag względem pieczęci kryptograficznej (fail-closed).
pub fn verify_sealed_weights(
    weights_path: &Path,
    seal: &WeightIntegritySeal,
    seal_key: &[u8; 32],
) -> Result<MlpWeights, String> {
    if seal.version != SEAL_FORMAT_VERSION {
        return Err(format!(
            "Nieobsługiwana wersja pieczęci EWC: {}",
            seal.version
        ));
    }

    let raw =
        fs::read(weights_path).map_err(|e| format!("Błąd odczytu zapieczętowanych wag: {}", e))?;
    let weights = MlpWeights::from_bytes(&raw)?;
    let actual_sha = sha256_hex_bytes(&raw[..REQUIRED_WEIGHT_BYTES]);

    if !constant_time_eq(actual_sha.as_bytes(), seal.weights_sha256.as_bytes()) {
        return Err(
            "Naruszenie integralności wag EWC: niezgodny skrót SHA-256 względem pieczęci.".into(),
        );
    }

    let seal_payload = format!(
        "v{}|c{}|t{}|{}|{:.6}|{}",
        seal.version,
        seal.cycle,
        seal.timestamp_unix,
        seal.weights_sha256,
        seal.ewc_saturation,
        seal.assimilated_count
    );
    let expected_hmac = hex_encode(&hmac_sha256(seal_key, seal_payload.as_bytes()));

    if !constant_time_eq(expected_hmac.as_bytes(), seal.hmac_seal_hex.as_bytes()) {
        return Err(
            "Naruszenie integralności pieczęci EWC: nieprawidłowy podpis HMAC-SHA256.".into(),
        );
    }

    Ok(weights)
}

/// Wyznacza ścieżkę pliku manifestu pieczęci dla danego pliku wag.
pub fn seal_manifest_path(weights_path: &Path) -> PathBuf {
    let mut os = weights_path.as_os_str().to_os_string();
    os.push(".ewc.seal.json");
    PathBuf::from(os)
}

/// Wyprowadza deterministyczny klucz pieczęci dla sesji z użyciem natywnego sejfu lub kontekstu maszyny.
pub fn derive_session_seal_key(context: &str) -> [u8; 32] {
    let mut hasher = Sha256::new();
    hasher.update(b"BLYSKAWICA_V11_EWC_SEAL_KEY_V1:");
    hasher.update(context.as_bytes());
    if let Ok(user) = std::env::var("USERNAME").or_else(|_| std::env::var("USER")) {
        hasher.update(b":");
        hasher.update(user.as_bytes());
    }
    hasher.finalize().into()
}

fn normalize_vector_128(raw: &[f32]) -> Vec<f32> {
    let mut out = vec![0.0f32; INPUT_DIM];
    let copy_len = raw.len().min(INPUT_DIM);
    out[..copy_len].copy_from_slice(&raw[..copy_len]);
    let norm = out.iter().map(|v| v * v).sum::<f32>().sqrt();
    if norm > 1e-6 && norm.is_finite() {
        for v in &mut out {
            *v /= norm;
        }
    }
    out
}

fn atomic_write_file(path: &Path, data: &[u8]) -> Result<(), String> {
    let pid = std::process::id();
    let nonce: u64 = rand::random();
    let tmp_name = format!(
        "{}.tmp.{}.{:016x}",
        path.file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("ewc_weights"),
        pid,
        nonce
    );
    let tmp_path = path.with_file_name(tmp_name);

    let mut file = File::create(&tmp_path)
        .map_err(|e| format!("Błąd tworzenia pliku tymczasowego {:?}: {}", tmp_path, e))?;
    file.write_all(data)
        .map_err(|e| format!("Błąd zapisu pliku tymczasowego {:?}: {}", tmp_path, e))?;
    file.sync_all()
        .map_err(|e| format!("Błąd synchronizacji dyskowej {:?}: {}", tmp_path, e))?;
    drop(file);

    if let Err(err) = fs::rename(&tmp_path, path) {
        let _ = fs::remove_file(&tmp_path);
        return Err(format!(
            "Błąd atomowej publikacji pliku {:?}: {}",
            path, err
        ));
    }
    Ok(())
}

fn unix_timestamp_secs() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}

fn sha256_hex_bytes(data: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    hex_encode(&hasher.finalize())
}

fn hmac_sha256(key: &[u8], data: &[u8]) -> [u8; 32] {
    let mut k_pad = [0u8; 64];
    if key.len() > 64 {
        let mut hasher = Sha256::new();
        hasher.update(key);
        let h = hasher.finalize();
        k_pad[..32].copy_from_slice(&h);
    } else {
        k_pad[..key.len()].copy_from_slice(key);
    }
    let mut ipad = [0x36u8; 64];
    let mut opad = [0x5cu8; 64];
    for i in 0..64 {
        ipad[i] ^= k_pad[i];
        opad[i] ^= k_pad[i];
    }
    let mut inner = Sha256::new();
    inner.update(ipad);
    inner.update(data);
    let inner_hash = inner.finalize();

    let mut outer = Sha256::new();
    outer.update(opad);
    outer.update(inner_hash);
    outer.finalize().into()
}

fn hex_encode(bytes: &[u8]) -> String {
    let mut s = String::with_capacity(bytes.len() * 2);
    for &b in bytes {
        use std::fmt::Write;
        let _ = write!(&mut s, "{:02x}", b);
    }
    s
}

fn constant_time_eq(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    let mut diff = 0u8;
    for (&x, &y) in a.iter().zip(b.iter()) {
        diff |= x ^ y;
    }
    diff == 0
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::local_inference::LocalInferenceEngine;

    #[test]
    fn sleep_profile_matches_python_neurochemistry_contract() {
        let mut ns = NeurochemicalState::default();
        ns.serotonin = 0.8;
        ns.gaba = 0.7;
        ns.adenosine = 0.3;

        let profile = SleepProfile::from_neurochemistry(&ns);
        // Python: melatonin = max(0.1, 1.0 - 0.3 / 1.5) = 0.8
        assert!((profile.melatonin - 0.8).abs() < 1e-5);
        assert!((profile.gaba - 0.7).abs() < 1e-5);
        assert!((profile.serotonin - 0.8).abs() < 1e-5);
        assert!((profile.adenosine_cleared - 0.7).abs() < 1e-5);
        assert!((profile.consolidation_depth() - 0.56).abs() < 1e-5);
        assert!((profile.pruning_threshold() - 0.155).abs() < 1e-5);
        assert!((profile.plasticity_gate() - 0.6).abs() < 1e-5);
    }

    #[test]
    fn mlp_weights_binary_roundtrip_matches_local_inference_engine() {
        let weights = MlpWeights::deterministic_baseline();
        let bytes = weights.to_bytes(1_024_000);
        assert_eq!(bytes.len(), 1_024_000);

        let reloaded = MlpWeights::from_bytes(&bytes).expect("roundtrip bytes should parse");
        assert_eq!(reloaded.params, weights.params);

        let engine = LocalInferenceEngine::load_cpu(&bytes)
            .expect("LocalInferenceEngine must load EWC weights");
        let mut input = vec![0.0f32; INPUT_DIM];
        input[0] = 1.0;
        input[2] = 0.5;
        let candle_out = engine.project(&input).expect("Candle projection must work");
        let (_, raw_out) = reloaded.forward_raw(&input).expect("raw forward must work");
        let norm = raw_out.iter().map(|v| v * v).sum::<f32>().sqrt();
        for (a, b) in candle_out.iter().zip(raw_out.iter()) {
            assert!((a - b / norm).abs() < 1e-4);
        }
    }

    #[test]
    fn surprise_registry_rejects_non_finite_and_enforces_dos_cap() {
        let mut consolidator = EwcSleepConsolidator::default();
        assert!(
            consolidator
                .record_surprise(1, f32::NAN, "bad", &[0.5; 4])
                .is_err()
        );
        assert!(
            consolidator
                .record_surprise(2, -0.1, "bad", &[0.5; 4])
                .is_err()
        );
        assert!(
            consolidator
                .record_surprise(3, 0.8, "bad", &[1.0, f32::INFINITY])
                .is_err()
        );
        assert!(consolidator.record_surprise(4, 0.8, "empty", &[]).is_err());

        for i in 0..(MAX_SURPRISE_QUEUE + 32) {
            let score = 0.1 + (i as f32) * 0.01;
            let _ = consolidator.record_surprise(i, score, format!("item-{i}"), &[0.5; 128]);
        }
        assert_eq!(consolidator.queue_len(), MAX_SURPRISE_QUEUE);
        // Najwyższy wynik zaskoczenia musi pozostać w kolejce
        let max_surprise = consolidator
            .surprise_queue
            .iter()
            .map(|r| r.surprise)
            .fold(0.0f32, f32::max);
        assert!(max_surprise > 2.5);
    }

    #[test]
    fn ewc_assimilates_surprise_vectors_and_reduces_loss() {
        let mut weights = MlpWeights::deterministic_baseline();
        let mut consolidator = EwcSleepConsolidator::new(5.0);

        let mut surprise_vec = vec![0.0f32; INPUT_DIM];
        for i in 0..16 {
            surprise_vec[i] = 1.0;
        }
        consolidator
            .record_surprise(101, 0.92, "nowy wzorzec fizyki kwantowej", &surprise_vec)
            .expect("valid surprise must enqueue");

        let profile = SleepProfile {
            melatonin: 0.9,
            gaba: 0.6,
            serotonin: 0.7,
            adenosine_cleared: 0.9,
        };
        let report = consolidator
            .consolidate_weights(&mut weights, &profile)
            .expect("consolidation must succeed");

        assert_eq!(report.cycle, 1);
        assert_eq!(report.assimilated_count, 1);
        assert_eq!(report.remaining_queue, 0);
        assert!(
            report.mean_loss_after < report.mean_loss_before,
            "Strata rekonstrukcji powinna spaść: przed={}, po={}",
            report.mean_loss_before,
            report.mean_loss_after
        );
        assert!(report.ewc_saturation > 0.0);
        assert_eq!(report.weights_sha256.len(), 64);
    }

    #[test]
    fn ewc_protects_high_fisher_weights_against_catastrophic_forgetting() {
        // Porównanie: silna regularyzacja EWC (lambda=200) vs brak ochrony (lambda=0)
        let mut w_protected = MlpWeights::deterministic_baseline();
        let mut w_unconstrained = MlpWeights::deterministic_baseline();

        // Zakotwiczenie z wysoką informacją Fishera dla pierwszych 1024 wag warstwy 1
        let mut fisher = vec![0.0f32; TOTAL_PARAMS];
        for f in fisher.iter_mut().take(1024) {
            *f = 10.0;
        }

        let mut ewc_protected = EwcSleepConsolidator::new(200.0);
        ewc_protected
            .set_anchor_and_fisher(w_protected.params.clone(), fisher.clone())
            .expect("anchor setup must succeed");

        let mut ewc_free = EwcSleepConsolidator::new(0.0);
        ewc_free
            .set_anchor_and_fisher(w_unconstrained.params.clone(), fisher)
            .expect("anchor setup must succeed");

        let mut anomaly = vec![0.0f32; INPUT_DIM];
        for i in 0..INPUT_DIM {
            anomaly[i] = if i % 2 == 0 { 1.0 } else { -0.5 };
        }
        ewc_protected
            .record_surprise(1, 0.95, "zadanie B", &anomaly)
            .unwrap();
        ewc_free
            .record_surprise(1, 0.95, "zadanie B", &anomaly)
            .unwrap();

        let profile = SleepProfile {
            melatonin: 0.95,
            gaba: 0.5,
            serotonin: 0.5,
            adenosine_cleared: 0.95,
        };
        let r_prot = ewc_protected
            .consolidate_weights(&mut w_protected, &profile)
            .unwrap();
        let r_free = ewc_free
            .consolidate_weights(&mut w_unconstrained, &profile)
            .unwrap();

        assert!(
            r_prot.max_protected_weight_drift < r_free.max_protected_weight_drift,
            "EWC musi ograniczać dryf chronionych wag (EWC={} vs bez EWC={})",
            r_prot.max_protected_weight_drift,
            r_free.max_protected_weight_drift
        );
    }

    #[test]
    fn sealed_weights_atomic_save_verify_and_tamper_rejection() {
        let unique: u64 = rand::random();
        let temp_dir = std::env::temp_dir().join(format!("blysk_ewc_seal_test_{unique:016x}"));
        fs::create_dir_all(&temp_dir).unwrap();
        let weights_path = temp_dir.join("ewc_weights.bin");

        let mut weights = MlpWeights::deterministic_baseline();
        let mut consolidator = EwcSleepConsolidator::default();
        consolidator
            .record_surprise(7, 0.85, "krystalizacja", &[0.25; INPUT_DIM])
            .unwrap();
        let report = consolidator
            .consolidate_weights(&mut weights, &SleepProfile::default())
            .unwrap();

        let key = derive_session_seal_key("test_context");
        let seal = save_sealed_weights(&weights_path, &weights, 1_024_000, &report, &key)
            .expect("atomic save and seal should succeed");
        assert!(seal_manifest_path(&weights_path).is_file());

        let verified = verify_sealed_weights(&weights_path, &seal, &key)
            .expect("untampered sealed weights must verify");
        assert_eq!(verified.params, weights.params);

        // 1-bitowa manipulacja w pliku wag musi zostać odrzucona (fail-closed)
        let mut tampered = fs::read(&weights_path).unwrap();
        tampered[16] ^= 0x01;
        fs::write(&weights_path, &tampered).unwrap();
        assert!(
            verify_sealed_weights(&weights_path, &seal, &key).is_err(),
            "Zmodyfikowany plik wag musi nie przejść weryfikacji SHA-256"
        );

        let _ = fs::remove_dir_all(&temp_dir);
    }

    #[tokio::test]
    async fn async_sleep_consolidation_runs_non_blocking_on_tokio() {
        let unique: u64 = rand::random();
        let temp_dir = std::env::temp_dir().join(format!("blysk_ewc_async_test_{unique:016x}"));
        fs::create_dir_all(&temp_dir).unwrap();
        let weights_path = temp_dir.join("async_weights.bin");

        let baseline = MlpWeights::deterministic_baseline();
        fs::write(&weights_path, baseline.to_bytes(1_024_000)).unwrap();

        let consolidator =
            std::sync::Arc::new(tokio::sync::Mutex::new(EwcSleepConsolidator::new(10.0)));
        {
            let mut guard = consolidator.lock().await;
            guard
                .record_surprise(42, 0.9, "asynchroniczna anomalia", &[0.4; INPUT_DIM])
                .unwrap();
        }

        let key = derive_session_seal_key("async_test");
        let report = EwcSleepConsolidator::consolidate_file_async(
            consolidator.clone(),
            weights_path.clone(),
            SleepProfile::default(),
            key,
        )
        .await
        .expect("async EWC consolidation should succeed");

        assert_eq!(report.cycle, 1);
        assert_eq!(report.assimilated_count, 1);
        assert!(report.seal_verified);
        assert!(seal_manifest_path(&weights_path).is_file());

        let _ = fs::remove_dir_all(&temp_dir);
    }
}
