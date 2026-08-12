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

fn compute_file_checksum(file_path: &Path) -> Result<u64, String> {
    use std::fs::File;
    use std::io::Read;
    use std::collections::hash_map::DefaultHasher;
    use std::hash::Hasher;

    let mut file = File::open(file_path).map_err(|e| e.to_string())?;
    let mut hasher = DefaultHasher::new();
    let mut buffer = [0u8; 8192];
    loop {
        let bytes_read = file.read(&mut buffer).map_err(|e| e.to_string())?;
        if bytes_read == 0 {
            break;
        }
        hasher.write(&buffer[..bytes_read]);
    }
    Ok(hasher.finish())
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
            DistCosine,
        );

        Self {
            hnsw,
            dimension,
            max_elements,
            current_count: AtomicUsize::new(0),
            _reloader: None,
        }
    }

    pub fn from_hnsw(hnsw: Hnsw<'static, f32, DistCosine>, dimension: usize) -> Self {
        Self {
            hnsw,
            dimension,
            max_elements: 100_000,
            current_count: AtomicUsize::new(0),
            _reloader: None,
        }
    }

    /// Bezpieczne dodawanie wektora z weryfikacją wymiarowości oraz limitu max_elements.
    pub fn insert(&self, id: usize, vector: &Vec<f32>) -> Result<(), String> {
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

        self.hnsw.parallel_insert(&[(vector, id)]);
        self.current_count.fetch_add(1, Ordering::Relaxed);
        Ok(())
    }

    pub fn search(&self, query: &Vec<f32>, k: usize) -> Vec<Neighbour> {
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

    /// Zapisuje indeks atomowo (temp-then-rename), generuje sumę kontrolną oraz rotuje 2 generacje kopii (.prev).
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

        // 2. Obliczenie sumy kontrolnej
        let graph_hash = compute_file_checksum(&tmp_graph)?;
        let data_hash = compute_file_checksum(&tmp_data)?;
        let checksum_content = format!("graph:{:x}\ndata:{:x}", graph_hash, data_hash);

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

        Ok(dump_res)
    }

    /// Wczytuje indeks wektorowy z weryfikacją sumy kontrolnej oraz automatycznym plikiem zapasowym (.prev).
    pub fn load_hnsw(path: &Path, file_basename: &str, dimension: usize) -> Result<Self, String> {
        // Próba załadowania z głównego zestawu plików
        match Self::try_load_single(path, file_basename, dimension) {
            Ok(index) => Ok(index),
            Err(primary_err) => {
                println!("⚠️ [HNSW LOAD]: Błąd wczytywania głównego indeksu: {}. Próba przywrócenia z generacji .prev...", primary_err);
                let prev_basename = format!("{}.prev", file_basename);
                Self::try_load_single(path, &prev_basename, dimension).map_err(|prev_err| {
                    format!("Wszystkie generacje indeksu uszkodzone/niedostępne. Główny: {}; Fallback: {}", primary_err, prev_err)
                })
            }
        }
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

                    let actual_graph = format!("{:x}", compute_file_checksum(&graph_path)?);
                    let actual_data = format!("{:x}", compute_file_checksum(&data_path)?);

                    if expected_graph != actual_graph || expected_data != actual_data {
                        return Err(format!("Suma kontrolna plików HNSW nie zgadza się dla {}", file_basename));
                    }
                }
            }
        }

        let mut reloader = Box::new(HnswIo::new(path, file_basename));
        let reloader_ptr: *mut HnswIo = &mut *reloader;
        let hnsw: Hnsw<'static, f32, DistCosine> = unsafe {
            (*reloader_ptr).load_hnsw::<f32, DistCosine>().map_err(|e| e.to_string())?
        };

        Ok(Self {
            hnsw,
            dimension,
            max_elements: 100_000,
            current_count: AtomicUsize::new(0),
            _reloader: Some(reloader),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_vector_insert_and_search() {
        let dimension = 4;
        let index = SparkleVectorIndex::new(dimension, 10);
        
        let vec1 = vec![1.0, 0.0, 0.0, 0.0];
        let vec2 = vec![0.0, 1.0, 0.0, 0.0];
        
        assert!(index.insert(1, &vec1).is_ok());
        assert!(index.insert(2, &vec2).is_ok());
        
        let query = vec![0.9, 0.1, 0.0, 0.0];
        let results = index.search(&query, 2);
        
        assert!(!results.is_empty());
        assert_eq!(results[0].d_id, 1);
    }

    #[test]
    fn test_vector_capacity_guard() {
        let dimension = 2;
        let max_elements = 2;
        let index = SparkleVectorIndex::new(dimension, max_elements);

        assert!(index.insert(1, &vec![1.0, 0.0]).is_ok());
        assert!(index.insert(2, &vec![0.0, 1.0]).is_ok());
        // Trzeci powinien zwrócić błąd z powodu limitu pojemności
        assert!(index.insert(3, &vec![0.5, 0.5]).is_err());
    }

    #[test]
    fn test_vector_dump_and_load_with_checksum() {
        let dimension = 4;
        let index = SparkleVectorIndex::new(dimension, 10);
        
        let vec1 = vec![1.0, 0.0, 0.0, 0.0];
        assert!(index.insert(42, &vec1).is_ok());
        
        let temp_dir = std::env::temp_dir();
        let basename = "test_sparkle_index_atomic_unique";
        
        // Zapis do pliku
        let dump_res = index.file_dump(&temp_dir, basename);
        assert!(dump_res.is_ok());
        
        // Odczyt z pliku z weryfikacją sumy kontrolnej
        let loaded_index_res = SparkleVectorIndex::load_hnsw(&temp_dir, basename, dimension);
        assert!(loaded_index_res.is_ok());
        
        let loaded_index = loaded_index_res.unwrap();
        let query = vec![0.9, 0.1, 0.0, 0.0];
        let results = loaded_index.search(&query, 1);
        
        assert!(!results.is_empty());
        assert_eq!(results[0].d_id, 42);

        // Opcjonalne usunięcie plików testowych
        let _ = std::fs::remove_file(temp_dir.join(format!("{}.hnsw.graph", basename)));
        let _ = std::fs::remove_file(temp_dir.join(format!("{}.hnsw.data", basename)));
        let _ = std::fs::remove_file(temp_dir.join(format!("{}.checksum", basename)));
    }
}
