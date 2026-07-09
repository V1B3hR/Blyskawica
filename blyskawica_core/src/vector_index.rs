use hnsw_rs::prelude::*;
use hnsw_rs::hnswio::HnswIo;
use std::path::Path;

pub struct SparkleVectorIndex {
    hnsw: Hnsw<'static, f32, DistCosine>,
    dimension: usize,
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

        Self { hnsw, dimension }
    }

    pub fn from_hnsw(hnsw: Hnsw<'static, f32, DistCosine>, dimension: usize) -> Self {
        Self { hnsw, dimension }
    }

    pub fn insert(&self, id: usize, vector: &Vec<f32>) {
        assert_eq!(vector.len(), self.dimension, "Wektor musi mieć wymiar równy wymiarowi indeksu.");
        // parallel_insert takes a slice of ( &Vec<f32>, usize )
        self.hnsw.parallel_insert(&[(vector, id)]);
        println!("📊 [HNSW INDEX]: Wstawiono wektor o ID: {} do indeksu.", id);
    }

    pub fn search(&self, query: &Vec<f32>, k: usize) -> Vec<Neighbour> {
        assert_eq!(query.len(), self.dimension, "Wektor zapytania musi mieć wymiar równy wymiarowi indeksu.");
        let ef_search = 50;
        let results = self.hnsw.search(query, k, ef_search);
        println!("📊 [HNSW INDEX]: Wyszukano najbliższych sąsiadów. Znaleziono: {}.", results.len());
        results
    }

    pub fn get_dimension(&self) -> usize {
        self.dimension
    }

    /// Zapisuje indeks wektorowy na dysk w wybranym katalogu z określoną nazwą bazową.
    pub fn file_dump(&self, path: &Path, file_basename: &str) -> Result<String, String> {
        if !path.exists() {
            std::fs::create_dir_all(path).map_err(|e| e.to_string())?;
        }
        self.hnsw.file_dump(path, file_basename).map_err(|e| e.to_string())
    }

    /// Wczytuje indeks wektorowy z dysku.
    pub fn load_hnsw(path: &Path, file_basename: &str, dimension: usize) -> Result<Self, String> {
        let reloader: &'static mut HnswIo = Box::leak(Box::new(HnswIo::new(path, file_basename)));
        let hnsw: Hnsw<'static, f32, DistCosine> = reloader.load_hnsw::<f32, DistCosine>().map_err(|e| e.to_string())?;
        Ok(Self::from_hnsw(hnsw, dimension))
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
        
        index.insert(1, &vec1);
        index.insert(2, &vec2);
        
        let query = vec![0.9, 0.1, 0.0, 0.0];
        let results = index.search(&query, 2);
        
        assert!(!results.is_empty());
        assert_eq!(results[0].d_id, 1);
    }

    #[test]
    fn test_vector_dump_and_load() {
        let dimension = 4;
        let index = SparkleVectorIndex::new(dimension, 10);
        
        let vec1 = vec![1.0, 0.0, 0.0, 0.0];
        index.insert(42, &vec1);
        
        let temp_dir = std::env::temp_dir();
        let basename = "test_sparkle_index_unique";
        
        // Zapis do pliku
        let dump_res = index.file_dump(&temp_dir, basename);
        assert!(dump_res.is_ok());
        
        // Odczyt z pliku
        let loaded_index_res = SparkleVectorIndex::load_hnsw(&temp_dir, basename, dimension);
        assert!(loaded_index_res.is_ok());
        
        let loaded_index = loaded_index_res.unwrap();
        let query = vec![0.9, 0.1, 0.0, 0.0];
        let results = loaded_index.search(&query, 1);
        
        assert!(!results.is_empty());
        assert_eq!(results[0].d_id, 42);

        // Opcjonalne usunięcie plików testowych
        let graph_file = temp_dir.join(format!("{}.hnsw.graph", basename));
        let data_file = temp_dir.join(format!("{}.hnsw.data", basename));
        let _ = std::fs::remove_file(graph_file);
        let _ = std::fs::remove_file(data_file);
    }
}
