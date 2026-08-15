use hnsw_rs::prelude::*;
use hnsw_rs::hnswio::HnswIo;
use std::path::Path;
use std::sync::atomic::{AtomicUsize, Ordering};

pub struct SparkleVectorIndex {
    hnsw: Hnsw<'static, f32, DistCosine>,
    dimension: usize,
    max_elements: usize,
    current_count: AtomicUsize,
    _reloader: Option<Box<HnswIo>>,
}

fn compute_file_checksum(file_path: &Path) -> Result<String, String> {
    use std::fs::File;
    use std::io::Read;
    use sha2::{Sha256, Digest};

    let mut file = File::open(file_path).map_err(|e| e.to_string())?;
    let mut hasher = Sha256::new();
    let mut buffer = [0u8; 65536];
    loop {
        let bytes_read = file.read(&mut buffer).map_err(|e| e.to_string())?;
        if bytes_read == 0 {
            break;
        }
        hasher.update(&buffer[..bytes_read]);
    }
    Ok(format!("{:x}", hasher.finalize()))
}

impl SparkleVectorIndex {
    pub fn new(dimension: usize, max_elements: usize) -> Self {
        let max_nb_connection = 16;
        let nb_layer = 16;
        let ef_c = 200;

        let hnsw = Hnsw::new(
            max_nb_connection,
            max_elements,
            nb_layer,
            ef_c,
            DistCosine {},
        );

        Self {
            hnsw,
            dimension,
            max_elements,
            current_count: AtomicUsize::new(0),
            _reloader: None,
        }
    }

    pub fn default_128d() -> Self {
        Self::new(128, 100_000)
    }

    pub fn default_256d() -> Self {
        let max_nb_connection = 16;
        let nb_layer = 16;
        let ef_c = 200;

        let hnsw = Hnsw::new(
            max_nb_connection,
            100_000,
            nb_layer,
            ef_c,
            DistCosine {},
        );

        Self {
            hnsw,
            dimension: 256,
            max_elements: 100_000,
            current_count: AtomicUsize::new(0),
            _reloader: None,
        }
    }

    /// Bezpieczne dodawanie wektora z weryfikacją wymiarowości oraz limitu max_elements.
    pub fn insert(&self, id: usize, vector: &[f32]) -> Result<(), String> {
        if vector.len() != self.dimension {
            return Err(format!(
                "Wektor musi mieć wymiar równy wymiarowi indeksu (oczekiwano {}, otrzymano {}).",
                self.dimension,
                vector.len()
            ));
        }

        let current = self.current_count.load(Ordering::Relaxed);
        if current >= self.max_elements {
            return Err(format!(
                "Przekroczono maksymalną pojemność indeksu wektorowego ({}/{}).",
                current, self.max_elements
            ));
        }

        let v = vector.to_vec();
        self.hnsw.parallel_insert(&[(&v, id)]);
        self.current_count.fetch_add(1, Ordering::Relaxed);
        Ok(())
    }

    pub fn search(&self, query: &[f32], k: usize) -> Vec<Neighbour> {
        assert_eq!(query.len(), self.dimension, "Wektor zapytania musi mieć wymiar równy wymiarowi indeksu.");
        let ef_search = 50;
        self.hnsw.search(query, k, ef_search)
    }

    pub fn get_dimension(&self) -> usize {
        self.dimension
    }

    pub fn len(&self) -> usize {
        self.current_count.load(Ordering::Relaxed)
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    /// Zapisuje wektor do dziennika Write-Ahead Log (WAL) z wymuszoną synchronizacją dyskową (fsync).
    pub fn append_wal(&self, path: &Path, file_basename: &str, id: usize, vector: &[f32]) -> Result<(), String> {
        use std::io::Write;
        use std::fs::OpenOptions;

        if !path.exists() {
            std::fs::create_dir_all(path).map_err(|e| e.to_string())?;
        }

        let wal_path = path.join(format!("{}.hnsw.wal", file_basename));
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&wal_path)
            .map_err(|e| format!("Błąd otwierania pliku WAL: {}", e))?;

        // Format rekordu: ID:v1,v2,v3...
        let vec_str: Vec<String> = vector.iter().map(|v| v.to_string()).collect();
        let record = format!("{}:{}\n", id, vec_str.join(","));

        file.write_all(record.as_bytes()).map_err(|e| format!("Błąd zapisu do WAL: {}", e))?;
        file.sync_all().map_err(|e| format!("Błąd fsync dla WAL: {}", e))?;

        Ok(())
    }

    /// Bezpieczne wstawienie wektora z synchronicznym wpisem do WAL.
    pub fn insert_with_wal(&self, path: &Path, file_basename: &str, id: usize, vector: &[f32]) -> Result<(), String> {
        self.append_wal(path, file_basename, id, vector)?;
        self.insert(id, vector)
    }

    /// Zapisuje indeks atomowo (temp-then-rename), generuje kryptograficzną sumę SHA-256 oraz rotuje 2 generacje kopii (.prev).
    pub fn file_dump(&self, path: &Path, file_basename: &str) -> Result<String, String> {
        if !path.exists() {
            std::fs::create_dir_all(path).map_err(|e| e.to_string())?;
        }

        let tmp_basename = format!("{}_tmp", file_basename);

        // 1. Zapis do plików tymczasowych
        let dump_res = self.hnsw.file_dump(path, &tmp_basename).map_err(|e| e.to_string())?;

        let tmp_graph = path.join(format!("{}.hnsw.graph", tmp_basename));
        let tmp_data = path.join(format!("{}.hnsw.data", tmp_basename));

        if !tmp_graph.exists() || !tmp_data.exists() {
            return Err("Nie utworzono tymczasowych plików dump HNSW.".into());
        }

        // 2. Obliczenie kryptograficznej sumy kontrolnej SHA-256
        let graph_hash = compute_file_checksum(&tmp_graph)?;
        let data_hash = compute_file_checksum(&tmp_data)?;
        let checksum_content = format!("graph:{}\ndata:{}", graph_hash, data_hash);

        // 3. Rotacja poprzedniej generacji (.prev)
        let target_graph = path.join(format!("{}.hnsw.graph", file_basename));
        let target_data = path.join(format!("{}.hnsw.data", file_basename));
        let target_checksum = path.join(format!("{}.checksum", file_basename));

        let prev_graph = path.join(format!("{}.prev.hnsw.graph", file_basename));
        let prev_data = path.join(format!("{}.prev.hnsw.data", file_basename));
        let prev_checksum = path.join(format!("{}.prev.checksum", file_basename));

        if target_graph.exists() {
            let _ = std::fs::rename(&target_graph, &prev_graph);
        }
        if target_data.exists() {
            let _ = std::fs::rename(&target_data, &prev_data);
        }
        if target_checksum.exists() {
            let _ = std::fs::rename(&target_checksum, &prev_checksum);
        }

        // 4. Atomowa podmiana (atomic rename)
        std::fs::rename(&tmp_graph, &target_graph).map_err(|e| e.to_string())?;
        std::fs::rename(&tmp_data, &target_data).map_err(|e| e.to_string())?;
        std::fs::write(&target_checksum, checksum_content).map_err(|e| e.to_string())?;

        // 5. Wyczyszczenie pliku WAL (wszystkie wektory utrwalone w grafie)
        let wal_path = path.join(format!("{}.hnsw.wal", file_basename));
        if wal_path.exists() {
            let _ = std::fs::write(&wal_path, "");
        }

        Ok(dump_res)
    }

    /// Wczytuje indeks wektorowy z weryfikacją sumy kontrolnej SHA-256, automatycznym fallbackiem (.prev) oraz odtworzeniem wpisów z WAL.
    pub fn load_hnsw(path: &Path, file_basename: &str, dimension: usize) -> Result<Self, String> {
        // Próba załadowania z głównego zestawu plików
        let index = match Self::try_load_single(path, file_basename, dimension) {
            Ok(idx) => idx,
            Err(primary_err) => {
                println!("⚠️ [HNSW LOAD]: Błąd wczytywania głównego indeksu: {}. Próba przywrócenia z generacji .prev...", primary_err);
                let prev_basename = format!("{}.prev", file_basename);
                Self::try_load_single(path, &prev_basename, dimension).map_err(|prev_err| {
                    format!("Wszystkie generacje indeksu uszkodzone/niedostępne. Główny: {}; Fallback: {}", primary_err, prev_err)
                })?
            }
        };

        // Odtworzenie wpisów z dziennika WAL (jeśli istniały wpisy po ostatnim zrzucie)
        let wal_path = path.join(format!("{}.hnsw.wal", file_basename));
        if wal_path.exists() {
            if let Ok(content) = std::fs::read_to_string(&wal_path) {
                let mut replayed_count = 0;
                for line in content.lines() {
                    let trimmed = line.trim();
                    if trimmed.is_empty() {
                        continue;
                    }
                    if let Some((id_str, vec_str)) = trimmed.split_once(':') {
                        if let Ok(id) = id_str.parse::<usize>() {
                            let floats: Result<Vec<f32>, _> = vec_str.split(',').map(|s| s.parse::<f32>()).collect();
                            if let Ok(vec) = floats {
                                if vec.len() == dimension {
                                    let _ = index.insert(id, &vec);
                                    replayed_count += 1;
                                }
                            }
                        }
                    }
                }
                if replayed_count > 0 {
                    println!("✓ [HNSW WAL REPLAY]: Odtworzono {} wektorów z dziennika WAL.", replayed_count);
                }
            }
        }

        Ok(index)
    }

    fn try_load_single(path: &Path, file_basename: &str, dimension: usize) -> Result<Self, String> {
        let graph_path = path.join(format!("{}.hnsw.graph", file_basename));
        let data_path = path.join(format!("{}.hnsw.data", file_basename));

        if !graph_path.exists() || !data_path.exists() {
            return Err(format!("Brak wymaganych plików HNSW dla {}", file_basename));
        }

        // Weryfikacja sumy kontrolnej jeśli plik .checksum istnieje
        let checksum_path = path.join(format!("{}.checksum", file_basename));
        if checksum_path.exists() {
            if let Ok(content) = std::fs::read_to_string(&checksum_path) {
                let lines: Vec<&str> = content.lines().collect();
                if lines.len() >= 2 {
                    let expected_graph = lines[0].trim_start_matches("graph:");
                    let expected_data = lines[1].trim_start_matches("data:");

                    let actual_graph = compute_file_checksum(&graph_path)?;
                    let actual_data = compute_file_checksum(&data_path)?;

                    if expected_graph != actual_graph || expected_data != actual_data {
                        return Err(format!("Suma kontrolna SHA-256 plików HNSW nie zgadza się dla {}", file_basename));
                    }
                }
            }
        }

        let mut reloader = Box::new(HnswIo::new(path, file_basename));
        let reloader_ptr: *mut HnswIo = &mut *reloader;
        let hnsw: Hnsw<'static, f32, DistCosine> = unsafe {
            (*reloader_ptr).load_hnsw::<f32, DistCosine>().map_err(|e| e.to_string())?
        };

        let loaded_count = hnsw.get_nb_point();

        Ok(Self {
            hnsw,
            dimension,
            max_elements: 100_000,
            current_count: AtomicUsize::new(loaded_count),
            _reloader: Some(reloader),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_vector_insert_and_search() {
        let index = SparkleVectorIndex::default_256d();
        let vec_a = vec![1.0; 256];
        assert!(index.insert(1, &vec_a).is_ok());

        let results = index.search(&vec_a, 1);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].d_id, 1);
    }

    #[test]
    fn test_vector_capacity_guard() {
        let index = SparkleVectorIndex::new(4, 2);
        let v = vec![0.5, 0.5, 0.5, 0.5];

        assert!(index.insert(1, &v).is_ok());
        assert!(index.insert(2, &v).is_ok());
        
        let overflow = index.insert(3, &v);
        assert!(overflow.is_err());
        assert!(overflow.unwrap_err().contains("Przekroczono maksymalną pojemność"));
    }

    #[test]
    fn test_vector_dump_and_load_with_checksum() {
        let temp_dir = std::env::temp_dir().join("sparkle_test_dump_checksum");
        let _ = std::fs::create_dir_all(&temp_dir);
        let basename = "test_dump_cs";

        let index = SparkleVectorIndex::new(4, 100);
        let v1 = vec![1.0, 0.0, 0.0, 0.0];
        let v2 = vec![0.0, 1.0, 0.0, 0.0];

        assert!(index.insert(10, &v1).is_ok());
        assert!(index.insert(20, &v2).is_ok());

        // 1. Zrzut do pliku z sumą kontrolną
        let dump_result = index.file_dump(&temp_dir, basename);
        assert!(dump_result.is_ok());

        // Sprawdzamy czy plik .checksum istnieje
        let checksum_file = temp_dir.join(format!("{}.checksum", basename));
        assert!(checksum_file.exists(), "Plik .checksum musi istnieć");

        // 2. Wczytanie z dysku
        let loaded_index = SparkleVectorIndex::load_hnsw(&temp_dir, basename, 4)
            .expect("Ładowanie poprawnego indeksu musi się powieść");
        assert_eq!(loaded_index.len(), 2);

        let search_res = loaded_index.search(&v1, 1);
        assert_eq!(search_res[0].d_id, 10);

        // 3. Test naruszenia spójności (modyfikacja pliku .hnsw.data)
        let data_file = temp_dir.join(format!("{}.hnsw.data", basename));
        let mut data_bytes = std::fs::read(&data_file).unwrap();
        if !data_bytes.is_empty() {
            data_bytes[0] ^= 0xFF; // Uszkadzamy 1 bajt
            std::fs::write(&data_file, data_bytes).unwrap();
        }

        // 4. Próba załadowania uszkodzonego indeksu powinna wykryć błąd sumy kontrolnej
        let corrupted_load = SparkleVectorIndex::load_hnsw(&temp_dir, basename, 4);
        assert!(corrupted_load.is_err(), "Wczytanie uszkodzonego pliku bez kopii .prev musi zwrócić błąd");

        // Sprzątanie
        let _ = std::fs::remove_dir_all(&temp_dir);
    }

    #[test]
    fn test_hnsw_wal_crash_recovery() {
        let temp_dir = std::env::temp_dir().join("sparkle_test_wal_recovery");
        let _ = std::fs::create_dir_all(&temp_dir);
        let basename = "test_wal_rec";
        let dimension = 4;

        let index = SparkleVectorIndex::new(dimension, 100);
        let initial_vec = vec![1.0, 0.0, 0.0, 0.0];
        assert!(index.insert(100, &initial_vec).is_ok());

        // 1. Utrwalenie stanu początkowego na dysku
        assert!(index.file_dump(&temp_dir, basename).is_ok());

        // 2. Symulacja niespodziewanego zapisu do WAL bez pełnego zrzutu grafu
        let uncommitted_vec = vec![0.0, 1.0, 0.0, 0.0];
        assert!(index.append_wal(&temp_dir, basename, 200, &uncommitted_vec).is_ok());

        // 3. Załadowanie indeksu z dysku — musi odtworzyć wektor 200 z WAL
        let loaded = SparkleVectorIndex::load_hnsw(&temp_dir, basename, dimension)
            .expect("Ładowanie z WAL powinno się udać");

        assert_eq!(loaded.len(), 2, "Indeks po odtworzeniu WAL powinien zawierać 2 wektory");

        let search_res = loaded.search(&[0.0, 0.9, 0.0, 0.0], 1);
        assert_eq!(search_res[0].d_id, 200, "Wektor z WAL powinien być poprawnie odnaleziony");

        // Sprzątanie
        let _ = std::fs::remove_file(temp_dir.join(format!("{}.hnsw.graph", basename)));
        let _ = std::fs::remove_file(temp_dir.join(format!("{}.hnsw.data", basename)));
        let _ = std::fs::remove_file(temp_dir.join(format!("{}.checksum", basename)));
        let _ = std::fs::remove_file(temp_dir.join(format!("{}.hnsw.wal", basename)));
    }
}
