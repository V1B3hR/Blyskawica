use hnsw_rs::hnswio::HnswIo;
use hnsw_rs::prelude::*;
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};

/// Cooperative exclusive lease. The lock file must live outside the data tree
/// so deleting the tree cannot invalidate the lock while it is held.
pub struct IndexLease {
    _file: std::fs::File,
    lock_path: PathBuf,
    bound: std::sync::atomic::AtomicBool,
}

impl IndexLease {
    pub fn acquire(lock_path: &Path) -> Result<Self, String> {
        let file = std::fs::OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .truncate(false)
            .open(lock_path)
            .map_err(|e| format!("Nie można otworzyć blokady pamięci: {e}"))?;
        file.try_lock()
            .map_err(|e| format!("Pamięć jest zajęta albo nie można jej zablokować: {e}"))?;
        let lock_path = lock_path
            .canonicalize()
            .map_err(|e| format!("Nie można ustalić ścieżki blokady: {e}"))?;
        Ok(Self {
            _file: file,
            lock_path,
            bound: std::sync::atomic::AtomicBool::new(false),
        })
    }

    fn verify_storage(&self, path: &Path) -> Result<(), String> {
        let parent = path
            .parent()
            .ok_or("Katalog indeksu musi mieć katalog nadrzędny")?;
        let expected = parent
            .join("sparkle-index.lock")
            .canonicalize()
            .map_err(|e| format!("Nie można ustalić blokady katalogu indeksu: {e}"))?;
        if self.lock_path != expected {
            return Err("Blokada nie należy do katalogu indeksu".into());
        }
        Ok(())
    }
}
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};

const MAX_WAL_BYTES: u64 = 64 * 1024 * 1024;
const MAX_PENDING_ITEMS: usize = 10_000;
const MAX_QUEUE_METADATA_BYTES: usize = 4096;
const MAX_CHECKPOINT_STORE_BYTES: u64 = 4 * 1024 * 1024 * 1024;
const MAX_CHECKPOINT_STORE_ENTRIES: usize = 10_000;

// Never delete history automatically. Refuse new checkpoints if the bounded
// scan is incomplete or storage has reached the configured safety limits.
fn check_checkpoint_storage(root: &Path, max_bytes: u64, max_entries: usize) -> Result<(), String> {
    let mut directories = vec![root.to_path_buf()];
    let mut total = 0u64;
    let mut count = 0usize;
    while let Some(directory) = directories.pop() {
        for entry in std::fs::read_dir(directory)
            .map_err(|e| format!("Nie można sprawdzić rozmiaru pamięci: {e}"))?
        {
            let entry = entry.map_err(|e| format!("Nie można sprawdzić rozmiaru pamięci: {e}"))?;
            count = count
                .checked_add(1)
                .ok_or("Przekroczono limit wpisów pamięci")?;
            if count > max_entries {
                return Err(
                    "Checkpoint wstrzymano: przekroczono limit 10000 wpisów pamięci".into(),
                );
            }
            let metadata = std::fs::symlink_metadata(entry.path())
                .map_err(|e| format!("Nie można sprawdzić danych pamięci: {e}"))?;
            let kind = metadata.file_type();
            if kind.is_symlink() {
                return Err("Checkpoint wstrzymano: pamięć zawiera dowiązanie symboliczne".into());
            }
            #[cfg(windows)]
            {
                use std::os::windows::fs::MetadataExt;
                const FILE_ATTRIBUTE_REPARSE_POINT: u32 = 0x400;
                if metadata.file_attributes() & FILE_ATTRIBUTE_REPARSE_POINT != 0 {
                    return Err("Checkpoint wstrzymano: pamięć zawiera punkt przekierowania".into());
                }
            }
            if kind.is_dir() {
                directories.push(entry.path());
            } else if kind.is_file() {
                let size = metadata.len();
                total = total
                    .checked_add(size)
                    .ok_or("Przekroczono limit rozmiaru pamięci")?;
                if total > max_bytes {
                    return Err("Checkpoint wstrzymano: przekroczono limit 4 GiB pamięci".into());
                }
            } else {
                return Err(
                    "Checkpoint wstrzymano: pamięć zawiera nieobsługiwany typ pliku".into(),
                );
            }
        }
    }
    Ok(())
}

fn recovery_plain_file(path: &Path) -> Result<std::fs::Metadata, String> {
    let meta =
        std::fs::symlink_metadata(path).map_err(|e| format!("Nie można sprawdzić pliku: {e}"))?;
    if !meta.file_type().is_file() || meta.file_type().is_symlink() {
        return Err("Odmowa kopiowania nietypowego pliku indeksu".into());
    }
    #[cfg(windows)]
    {
        use std::os::windows::fs::MetadataExt;
        if meta.file_attributes() & 0x400 != 0 {
            return Err("Odmowa kopiowania punktu przekierowania".into());
        }
    }
    Ok(meta)
}

// Unix file sync alone does not persist its directory entry. No equivalent is
// implemented here on Windows, so Windows power-loss durability is unverified.
#[cfg(unix)]
fn sync_directory_if_supported(path: &Path) -> Result<(), String> {
    std::fs::File::open(path)
        .and_then(|directory| directory.sync_all())
        .map_err(|e| format!("Nie można zsynchronizować katalogu: {e}"))
}

#[cfg(not(unix))]
fn sync_directory_if_supported(_path: &Path) -> Result<(), String> {
    Ok(())
}

fn durable_write_options(options: &mut std::fs::OpenOptions) -> &mut std::fs::OpenOptions {
    #[cfg(windows)]
    {
        use std::os::windows::fs::OpenOptionsExt;
        const FILE_FLAG_WRITE_THROUGH: u32 = 0x8000_0000;
        options.custom_flags(FILE_FLAG_WRITE_THROUGH);
    }
    options
}

#[cfg(windows)]
fn publish_marker(source: &Path, destination: &Path) -> Result<(), String> {
    use std::os::windows::ffi::OsStrExt;
    #[link(name = "kernel32")]
    unsafe extern "system" {
        fn MoveFileExW(existing: *const u16, new: *const u16, flags: u32) -> i32;
    }
    let source: Vec<u16> = source.as_os_str().encode_wide().chain(Some(0)).collect();
    let destination: Vec<u16> = destination
        .as_os_str()
        .encode_wide()
        .chain(Some(0))
        .collect();
    // The destination is unique and must not be replaced. This asks Windows
    // for write-through, but does not prove durability of all directory metadata.
    let result = unsafe { MoveFileExW(source.as_ptr(), destination.as_ptr(), 0x8) };
    if result == 0 {
        return Err(format!(
            "Nie można opublikować znacznika: {}",
            std::io::Error::last_os_error()
        ));
    }
    Ok(())
}

#[cfg(not(windows))]
fn publish_marker(source: &Path, destination: &Path) -> Result<(), String> {
    std::fs::rename(source, destination)
        .map_err(|e| format!("Nie można opublikować znacznika: {e}"))
}

#[derive(serde::Serialize, serde::Deserialize)]
#[serde(tag = "kind")]
enum QueueRecord {
    Enqueue {
        item: crate::anomaly_loop::AnomalyQueueItem,
    },
    Consolidate {
        queue_id: String,
    },
}

#[derive(serde::Serialize, Debug, PartialEq, Eq)]
pub struct WalInspection {
    pub format: &'static str,
    pub bytes: usize,
    pub complete_records: usize,
    pub pending_items: usize,
    pub issue: Option<WalInspectionIssue>,
}

#[derive(serde::Serialize, Debug, PartialEq, Eq)]
pub struct WalInspectionIssue {
    pub kind: &'static str,
    pub line: usize,
    pub byte_offset: usize,
}

#[derive(serde::Serialize, serde::Deserialize, Debug)]
pub struct RecoveryCandidateReport {
    pub format: String,
    pub candidate_directory: String,
    pub retained_bytes: usize,
    pub excluded_tail_bytes: usize,
    pub original_wal_sha256: String,
    pub candidate_wal_sha256: String,
    pub pending_items: usize,
    pub possible_loss: bool,
}

#[derive(serde::Serialize, Debug)]
pub struct RetentionReview {
    pub generation: u64,
    pub directory: String,
    pub fingerprint_sha256: String,
    pub bytes: u64,
}

#[derive(Debug, PartialEq, Eq)]
pub enum AutosaveOutcome {
    NoChanges,
    PendingQueue,
    CheckpointPublished,
}

struct StorageBinding {
    path: PathBuf,
    lease: Arc<IndexLease>,
}

impl Drop for StorageBinding {
    fn drop(&mut self) {
        self.lease.bound.store(false, Ordering::Release);
    }
}

impl IndexLease {
    fn bind(self: &Arc<Self>, path: &Path, create: bool) -> Result<StorageBinding, String> {
        self.verify_storage(path)?;
        if create {
            std::fs::create_dir_all(path)
                .map_err(|e| format!("Nie można utworzyć katalogu indeksu: {e}"))?;
        }
        let path = path.canonicalize().map_err(|e| e.to_string())?;
        self.bound
            .compare_exchange(false, true, Ordering::AcqRel, Ordering::Acquire)
            .map_err(|_| "Blokada jest już powiązana z aktywnym indeksem")?;
        Ok(StorageBinding {
            path,
            lease: self.clone(),
        })
    }
}

pub struct SparkleVectorIndex {
    hnsw: Hnsw<'static, f32, DistCosine>,
    dimension: usize,
    max_elements: usize,
    current_count: AtomicUsize,
    wal_failed: AtomicBool,
    journal_only_pending: AtomicBool,
    generation: Mutex<Option<(u64, PathBuf)>>,
    pending: Mutex<Vec<crate::anomaly_loop::AnomalyQueueItem>>,
    write_lock: Mutex<()>,
    _reloader: Option<Box<HnswIo>>,
    // Keep the lease until after the HNSW and reloader fields are dropped.
    storage: Option<StorageBinding>,
}

fn compute_file_checksum(file_path: &Path) -> Result<String, String> {
    use sha2::{Digest, Sha256};
    use std::fs::File;
    use std::io::Read;

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

fn wal_record(id: usize, vector: &[f32]) -> String {
    use sha2::{Digest, Sha256};
    let values = vector
        .iter()
        .map(|v| v.to_string())
        .collect::<Vec<_>>()
        .join(",");
    let body = format!("v2:{id}:{values}");
    format!("{body}:{:x}\n", Sha256::digest(body.as_bytes()))
}

fn queue_record(record: &QueueRecord) -> Result<String, String> {
    use sha2::{Digest, Sha256};
    let payload = serde_json::to_string(record).map_err(|e| e.to_string())?;
    let body = format!("v3:{payload}");
    Ok(format!("{body}:{:x}\n", Sha256::digest(body.as_bytes())))
}

fn parse_queue_record(line: &str) -> Result<QueueRecord, String> {
    use sha2::{Digest, Sha256};
    let (body, checksum) = line.rsplit_once(':').ok_or("Brak sumy rekordu kolejki")?;
    if checksum != format!("{:x}", Sha256::digest(body.as_bytes())) {
        return Err("Nieprawidłowa suma rekordu kolejki".into());
    }
    let payload = body
        .strip_prefix("v3:")
        .ok_or("Nieprawidłowa wersja rekordu kolejki")?;
    serde_json::from_str(payload).map_err(|e| format!("Nieprawidłowy rekord kolejki: {e}"))
}

fn parse_wal_record(line: &str, dimension: usize) -> Result<(usize, Vec<f32>), String> {
    use sha2::{Digest, Sha256};
    let payload = if line.starts_with("v2:") {
        let (body, checksum) = line.rsplit_once(':').ok_or("Brak sumy kontrolnej WAL")?;
        let actual = format!("{:x}", Sha256::digest(body.as_bytes()));
        if checksum != actual {
            return Err("Suma kontrolna rekordu WAL nie zgadza się".into());
        }
        body.strip_prefix("v2:").ok_or("Nieprawidłowa wersja WAL")?
    } else {
        line
    };
    let (id, values) = payload.split_once(':').ok_or("Brak identyfikatora WAL")?;
    let id = id
        .parse::<usize>()
        .map_err(|_| "Nieprawidłowy identyfikator WAL")?;
    let vector = values
        .split(',')
        .map(|value| {
            value
                .parse::<f32>()
                .map_err(|_| "Nieprawidłowa wartość WAL")
        })
        .collect::<Result<Vec<_>, _>>()?;
    if vector.len() != dimension || vector.iter().any(|value| !value.is_finite()) {
        return Err("Nieprawidłowy wymiar lub wartość wektora WAL".into());
    }
    Ok((id, vector))
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
            wal_failed: AtomicBool::new(false),
            journal_only_pending: AtomicBool::new(false),
            generation: Mutex::new(None),
            pending: Mutex::new(Vec::new()),
            write_lock: Mutex::new(()),
            storage: None,
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

        let hnsw = Hnsw::new(max_nb_connection, 100_000, nb_layer, ef_c, DistCosine {});

        Self {
            hnsw,
            dimension: 256,
            max_elements: 100_000,
            current_count: AtomicUsize::new(0),
            wal_failed: AtomicBool::new(false),
            journal_only_pending: AtomicBool::new(false),
            generation: Mutex::new(None),
            pending: Mutex::new(Vec::new()),
            write_lock: Mutex::new(()),
            storage: None,
            _reloader: None,
        }
    }

    /// Bind a memory-only index to one storage directory for its lifetime.
    pub fn with_storage(mut self, path: &Path, lease: Arc<IndexLease>) -> Result<Self, String> {
        if self.storage.is_some() {
            return Err("Indeks jest już powiązany z magazynem".into());
        }
        self.storage = Some(lease.bind(path, true)?);
        Ok(self)
    }

    fn require_storage(&self, path: &Path) -> Result<(), String> {
        let storage = self
            .storage
            .as_ref()
            .ok_or("Indeks nie posiada blokady trwałego magazynu")?;
        storage.lease.verify_storage(path)?;
        let actual = path
            .canonicalize()
            .map_err(|e| format!("Nie można ustalić katalogu indeksu: {e}"))?;
        if actual != storage.path {
            return Err("Indeks jest przypisany do innego katalogu".into());
        }
        Ok(())
    }

    fn validate_basename(name: &str) -> Result<(), String> {
        if name.is_empty()
            || !name
                .bytes()
                .all(|byte| byte.is_ascii_alphanumeric() || byte == b'_' || byte == b'-')
        {
            return Err("Nieprawidłowa nazwa indeksu".into());
        }
        Ok(())
    }

    fn active_dir(&self, root: &Path) -> Result<PathBuf, String> {
        let generation = self
            .generation
            .lock()
            .map_err(|_| "Blokada generacji jest uszkodzona")?;
        Ok(generation
            .as_ref()
            .map_or_else(|| root.to_path_buf(), |(_, dir)| dir.clone()))
    }

    fn latest_generation(root: &Path, basename: &str) -> Result<Option<(u64, PathBuf)>, String> {
        let prefix = format!("{basename}.commit.");
        let generation_prefix = format!("{basename}.gen.");
        let mut latest: Option<(u64, PathBuf)> = None;
        let mut generation_dirs = Vec::new();
        for entry in std::fs::read_dir(root).map_err(|e| e.to_string())? {
            let entry = entry.map_err(|e| e.to_string())?;
            let name = entry.file_name();
            let name = name.to_string_lossy();
            if let Some(suffix) = name.strip_prefix(&generation_prefix) {
                let (number, nonce) = suffix
                    .split_once('.')
                    .ok_or("Nieprawidłowa nazwa katalogu generacji")?;
                if number.len() != 20
                    || !number.bytes().all(|b| b.is_ascii_digit())
                    || nonce.len() != 16
                    || !nonce.bytes().all(|b| b.is_ascii_hexdigit())
                {
                    return Err("Nieprawidłowa nazwa katalogu generacji".into());
                }
                if !entry.file_type().map_err(|e| e.to_string())?.is_dir() {
                    return Err("Nieprawidłowy typ katalogu generacji".into());
                }
                generation_dirs.push((
                    number
                        .parse::<u64>()
                        .map_err(|_| "Nieprawidłowy numer generacji")?,
                    entry.path(),
                ));
                continue;
            }
            let Some(suffix) = name.strip_prefix(&prefix) else {
                continue;
            };
            if suffix.len() != 20 || !suffix.bytes().all(|b| b.is_ascii_digit()) {
                return Err("Nieprawidłowy identyfikator generacji".into());
            }
            let number = suffix
                .parse::<u64>()
                .map_err(|_| "Nieprawidłowy numer generacji")?;
            if latest
                .as_ref()
                .is_none_or(|(previous, _)| number > *previous)
            {
                latest = Some((number, entry.path()));
            }
        }
        let selected = if let Some((number, marker)) = latest {
            let meta = std::fs::symlink_metadata(&marker).map_err(|e| e.to_string())?;
            if !meta.file_type().is_file() || meta.len() > 256 {
                return Err("Nieprawidłowy znacznik generacji".into());
            }
            let dir_name = std::fs::read_to_string(marker).map_err(|e| e.to_string())?;
            let expected = format!("{basename}.gen.{number:020}.");
            let random = dir_name
                .strip_prefix(&expected)
                .ok_or("Nieprawidłowa ścieżka generacji")?;
            if random.len() != 16 || !random.bytes().all(|byte| byte.is_ascii_hexdigit()) {
                return Err("Nieprawidłowa ścieżka generacji".into());
            }
            let dir = root.join(dir_name);
            if !std::fs::symlink_metadata(&dir)
                .map_err(|e| e.to_string())?
                .file_type()
                .is_dir()
            {
                return Err("Nieprawidłowy katalog generacji".into());
            }
            Some((number, dir))
        } else {
            None
        };

        // An unpublished generation cannot receive WAL writes. A non-empty WAL
        // in an unselected same/newer generation can indicate a lost marker.
        // Refuse to silently roll back acknowledged records.
        for (number, dir) in generation_dirs {
            if selected
                .as_ref()
                .is_some_and(|(current, selected_dir)| number < *current || dir == *selected_dir)
            {
                continue;
            }
            let wal = dir.join(format!("{basename}.hnsw.wal"));
            match std::fs::symlink_metadata(wal) {
                Ok(meta) if meta.file_type().is_file() && meta.len() == 0 => {}
                Ok(_) => return Err("Znaleziono nowszą lub niejednoznaczną generację z danymi WAL bez znacznika; odczyt wstrzymano".into()),
                Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
                Err(error) => return Err(format!("Nie można sprawdzić WAL generacji: {error}")),
            }
        }
        Ok(selected)
    }

    /// Bezpieczne dodawanie wektora z weryfikacją wymiarowości oraz limitu max_elements.
    pub fn insert(&self, id: usize, vector: &[f32]) -> Result<(), String> {
        let _guard = self
            .write_lock
            .lock()
            .map_err(|_| "Blokada indeksu jest uszkodzona")?;
        self.validate_insert(vector)?;
        self.insert_validated(id, vector);
        Ok(())
    }

    fn validate_insert(&self, vector: &[f32]) -> Result<(), String> {
        if vector.len() != self.dimension {
            return Err(format!(
                "Wektor musi mieć wymiar równy wymiarowi indeksu (oczekiwano {}, otrzymano {}).",
                self.dimension,
                vector.len()
            ));
        }

        if vector.iter().any(|value| !value.is_finite()) {
            return Err("Wektor zawiera wartości niefinitywne".to_string());
        }

        let current = self.current_count.load(Ordering::Relaxed);
        if current >= self.max_elements {
            return Err(format!(
                "Przekroczono maksymalną pojemność indeksu wektorowego ({}/{}).",
                current, self.max_elements
            ));
        }

        Ok(())
    }

    fn insert_validated(&self, id: usize, vector: &[f32]) {
        let v = vector.to_vec();
        self.hnsw.parallel_insert(&[(&v, id)]);
        self.current_count.fetch_add(1, Ordering::Relaxed);
    }

    pub fn search(&self, query: &[f32], k: usize) -> Vec<Neighbour> {
        assert_eq!(
            query.len(),
            self.dimension,
            "Wektor zapytania musi mieć wymiar równy wymiarowi indeksu."
        );
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
    pub fn append_wal(
        &self,
        path: &Path,
        file_basename: &str,
        id: usize,
        vector: &[f32],
    ) -> Result<(), String> {
        self.require_storage(path)?;
        Self::validate_basename(file_basename)?;
        let _guard = self
            .write_lock
            .lock()
            .map_err(|_| "Blokada indeksu jest uszkodzona")?;
        self.validate_insert(vector)?;
        let active = self.active_dir(path)?;
        self.append_wal_locked(&active, file_basename, id, vector)?;
        self.journal_only_pending.store(true, Ordering::Release);
        Ok(())
    }

    fn append_wal_locked(
        &self,
        path: &Path,
        file_basename: &str,
        id: usize,
        vector: &[f32],
    ) -> Result<(), String> {
        self.append_wal_locked_with_hook(path, file_basename, id, vector, || Ok(()))
    }

    fn append_wal_locked_with_hook(
        &self,
        path: &Path,
        file_basename: &str,
        id: usize,
        vector: &[f32],
        hook: impl FnOnce() -> std::io::Result<()>,
    ) -> Result<(), String> {
        self.append_encoded_locked(path, file_basename, &wal_record(id, vector), hook)
    }

    fn append_encoded_locked(
        &self,
        path: &Path,
        file_basename: &str,
        record: &str,
        hook: impl FnOnce() -> std::io::Result<()>,
    ) -> Result<(), String> {
        use std::fs::OpenOptions;
        use std::io::Write;

        if self.wal_failed.load(Ordering::Acquire) {
            return Err("Poprzedni zapis WAL zakończył się błędem; wymagane jest ponowne otwarcie i weryfikacja pamięci".into());
        }

        for suffix in [".hnsw.graph", ".hnsw.data", ".checksum"] {
            if !path.join(format!("{file_basename}{suffix}")).is_file() {
                return Err("Nie można dopisać WAL bez kompletnej generacji bazowej".into());
            }
        }

        if !path.exists() {
            std::fs::create_dir_all(path).map_err(|e| e.to_string())?;
        }

        let wal_path = path.join(format!("{}.hnsw.wal", file_basename));
        let mut options = OpenOptions::new();
        let mut file = durable_write_options(&mut options)
            .create(true)
            .append(true)
            .open(&wal_path)
            .map_err(|e| format!("Błąd otwierania pliku WAL: {}", e))?;
        let len = file
            .metadata()
            .map_err(|e| format!("Błąd sprawdzania WAL: {e}"))?
            .len();
        if len
            .checked_add(record.len() as u64)
            .is_none_or(|total| total > MAX_WAL_BYTES)
        {
            return Err("Osiągnięto limit 64 MiB dziennika WAL; zapis wstrzymano".into());
        }
        if let Err(error) = file
            .write_all(record.as_bytes())
            .and_then(|_| hook())
            .and_then(|_| file.sync_all())
        {
            self.wal_failed.store(true, Ordering::Release);
            return Err(format!(
                "Błąd zapisu WAL; stan rekordu jest niepewny, zapis wstrzymano: {error}"
            ));
        }

        if let Err(error) = sync_directory_if_supported(path) {
            self.wal_failed.store(true, Ordering::Release);
            return Err(format!(
                "Zapis WAL może być niepełny; wstrzymano dalsze zapisy: {error}"
            ));
        }

        Ok(())
    }

    /// Bezpieczne wstawienie wektora z synchronicznym wpisem do WAL.
    pub fn insert_with_wal(
        &self,
        path: &Path,
        file_basename: &str,
        id: usize,
        vector: &[f32],
    ) -> Result<(), String> {
        self.require_storage(path)?;
        Self::validate_basename(file_basename)?;
        let _guard = self
            .write_lock
            .lock()
            .map_err(|_| "Blokada indeksu jest uszkodzona")?;
        self.validate_insert(vector)?;
        let active = self.active_dir(path)?;
        self.append_wal_locked(&active, file_basename, id, vector)?;
        self.insert_validated(id, vector);
        Ok(())
    }

    pub fn pending_queue(&self) -> Result<Vec<crate::anomaly_loop::AnomalyQueueItem>, String> {
        self.pending
            .lock()
            .map(|items| items.clone())
            .map_err(|_| "Blokada kolejki jest uszkodzona".into())
    }

    pub fn enqueue_durable(
        &self,
        path: &Path,
        basename: &str,
        item: crate::anomaly_loop::AnomalyQueueItem,
    ) -> Result<crate::anomaly_loop::AnomalyQueueItem, String> {
        self.enqueue_durable_with_hook(path, basename, item, || {})
    }

    fn enqueue_durable_with_hook(
        &self,
        path: &Path,
        basename: &str,
        mut item: crate::anomaly_loop::AnomalyQueueItem,
        hook: impl FnOnce(),
    ) -> Result<crate::anomaly_loop::AnomalyQueueItem, String> {
        self.require_storage(path)?;
        Self::validate_basename(basename)?;
        let _guard = self
            .write_lock
            .lock()
            .map_err(|_| "Blokada indeksu jest uszkodzona")?;
        if item.vector.len() != self.dimension
            || item.vector.iter().any(|x| !x.is_finite())
            || item.metadata.len() > MAX_QUEUE_METADATA_BYTES
        {
            return Err(
                "Nieprawidłowa pozycja kolejki albo metadane przekraczają 4096 bajtów".into(),
            );
        }
        let mut pending = self
            .pending
            .lock()
            .map_err(|_| "Blokada kolejki jest uszkodzona")?;
        if pending.len() >= MAX_PENDING_ITEMS {
            return Err("Osiągnięto limit kolejki".into());
        }
        let id = format!("{:032x}", rand::random::<u128>());
        if pending
            .iter()
            .any(|existing| existing.queue_id.as_ref() == Some(&id))
        {
            return Err("Kolizja identyfikatora kolejki".into());
        }
        item.queue_id = Some(id);
        let encoded = queue_record(&QueueRecord::Enqueue { item: item.clone() })?;
        let active = self.active_dir(path)?;
        self.append_encoded_locked(&active, basename, &encoded, || Ok(()))?;
        hook();
        pending.push(item.clone());
        Ok(item)
    }

    pub fn consolidate_queued(
        &self,
        path: &Path,
        basename: &str,
        queue_id: &str,
    ) -> Result<(), String> {
        self.consolidate_queued_with_hook(path, basename, queue_id, || {})
    }

    fn consolidate_queued_with_hook(
        &self,
        path: &Path,
        basename: &str,
        queue_id: &str,
        hook: impl FnOnce(),
    ) -> Result<(), String> {
        self.require_storage(path)?;
        Self::validate_basename(basename)?;
        let _guard = self
            .write_lock
            .lock()
            .map_err(|_| "Blokada indeksu jest uszkodzona")?;
        let mut pending = self
            .pending
            .lock()
            .map_err(|_| "Blokada kolejki jest uszkodzona")?;
        let position = pending
            .iter()
            .position(|item| item.queue_id.as_deref() == Some(queue_id))
            .ok_or("Brak pozycji w trwałej kolejce")?;
        let item = &pending[position];
        self.validate_insert(&item.vector)?;
        let encoded = queue_record(&QueueRecord::Consolidate {
            queue_id: queue_id.to_string(),
        })?;
        let active = self.active_dir(path)?;
        self.append_encoded_locked(&active, basename, &encoded, || Ok(()))?;
        hook();
        self.insert_validated(item.id, &item.vector);
        pending.remove(position);
        Ok(())
    }

    /// Zapisuje pliki indeksu i sumy kontrolne. Zapis wielu plików nie jest atomowy.
    pub fn file_dump(&self, path: &Path, file_basename: &str) -> Result<String, String> {
        self.file_dump_with_hook(path, file_basename, |_| Ok(()))
    }

    /// Publish a new immutable baseline and an empty WAL using a final marker.
    /// Previous generations and WAL files are retained for recovery.
    pub fn checkpoint(&self, path: &Path, basename: &str) -> Result<(), String> {
        self.checkpoint_with_hook(path, basename, |_| Ok(()))
    }

    /// Best-effort compaction of already journaled entries. The WAL itself is
    /// synced on each acknowledged enqueue/consolidation, independent of this.
    /// `checkpoint` rechecks all invariants under the write lock.
    pub fn autosave_if_needed(
        &self,
        path: &Path,
        basename: &str,
    ) -> Result<AutosaveOutcome, String> {
        self.require_storage(path)?;
        Self::validate_basename(basename)?;
        if self.wal_failed.load(Ordering::Acquire)
            || self.journal_only_pending.load(Ordering::Acquire)
        {
            return Err(
                "Niepewny lub niewłączony do indeksu WAL; automatyczny checkpoint wstrzymano"
                    .into(),
            );
        }
        if !self
            .pending
            .lock()
            .map_err(|_| "Blokada kolejki jest uszkodzona")?
            .is_empty()
        {
            return Ok(AutosaveOutcome::PendingQueue);
        }
        let active = self.active_dir(path)?;
        let wal = active.join(format!("{basename}.hnsw.wal"));
        match std::fs::metadata(wal) {
            Ok(meta) if meta.len() == 0 => return Ok(AutosaveOutcome::NoChanges),
            Ok(_) => {}
            Err(error)
                if error.kind() == std::io::ErrorKind::NotFound
                    && self
                        .generation
                        .lock()
                        .map_err(|_| "Blokada generacji jest uszkodzona")?
                        .is_none() =>
            {
                return Ok(AutosaveOutcome::NoChanges);
            }
            Err(error) => return Err(format!("Nie można sprawdzić WAL: {error}")),
        }
        self.checkpoint(path, basename)?;
        Ok(AutosaveOutcome::CheckpointPublished)
    }

    fn checkpoint_with_hook(
        &self,
        path: &Path,
        basename: &str,
        hook: impl FnMut(&str) -> Result<(), String>,
    ) -> Result<(), String> {
        self.checkpoint_with_limits(
            path,
            basename,
            MAX_CHECKPOINT_STORE_BYTES,
            MAX_CHECKPOINT_STORE_ENTRIES,
            hook,
        )
    }

    fn checkpoint_with_limits(
        &self,
        path: &Path,
        basename: &str,
        max_bytes: u64,
        max_entries: usize,
        mut hook: impl FnMut(&str) -> Result<(), String>,
    ) -> Result<(), String> {
        use std::io::Write;
        self.require_storage(path)?;
        Self::validate_basename(basename)?;
        let _guard = self
            .write_lock
            .lock()
            .map_err(|_| "Blokada indeksu jest uszkodzona")?;
        if self.wal_failed.load(Ordering::Acquire)
            || self.journal_only_pending.load(Ordering::Acquire)
        {
            return Err("Niepewny lub niewłączony do indeksu WAL; checkpoint wstrzymano".into());
        }
        if !self
            .pending
            .lock()
            .map_err(|_| "Blokada kolejki jest uszkodzona")?
            .is_empty()
        {
            return Err("Trwała kolejka nie jest pusta; checkpoint wstrzymano".into());
        }
        check_checkpoint_storage(path, max_bytes, max_entries)?;
        let active = self.active_dir(path)?;
        // Require a readable and structurally complete baseline and journal.
        let baseline = Self::try_load_single(&active, basename, self.dimension)?;
        drop(baseline);
        let wal_path = active.join(format!("{basename}.hnsw.wal"));
        if wal_path.try_exists().map_err(|e| e.to_string())? {
            if std::fs::metadata(&wal_path)
                .map_err(|e| e.to_string())?
                .len()
                > MAX_WAL_BYTES
            {
                return Err("WAL przekracza limit; checkpoint wstrzymano".into());
            }
            let bytes = std::fs::read(&wal_path).map_err(|e| e.to_string())?;
            if bytes.len() as u64 > MAX_WAL_BYTES || (!bytes.is_empty() && !bytes.ends_with(b"\n"))
            {
                return Err("Nieprawidłowy WAL; checkpoint wstrzymano".into());
            }
            let text = std::str::from_utf8(&bytes).map_err(|e| e.to_string())?;
            for line in text.lines().filter(|line| !line.trim().is_empty()) {
                if line.trim().starts_with("v3:") {
                    parse_queue_record(line.trim())?;
                } else {
                    parse_wal_record(line.trim(), self.dimension)?;
                }
            }
        }
        let previous = self
            .generation
            .lock()
            .map_err(|_| "Blokada generacji jest uszkodzona")?
            .as_ref()
            .map_or(0, |(number, _)| *number);
        let number = previous
            .checked_add(1)
            .ok_or("Przekroczono numer generacji")?;
        let dir_name = format!("{basename}.gen.{number:020}.{:016x}", rand::random::<u64>());
        let dir = path.join(&dir_name);
        std::fs::create_dir(&dir).map_err(|e| format!("Nie można utworzyć generacji: {e}"))?;
        sync_directory_if_supported(path)?;
        hook("created_dir")?;
        self.hnsw
            .file_dump(&dir, basename)
            .map_err(|e| e.to_string())?;
        let graph = dir.join(format!("{basename}.hnsw.graph"));
        let data = dir.join(format!("{basename}.hnsw.data"));
        for file in [&graph, &data] {
            std::fs::OpenOptions::new()
                .write(true)
                .open(file)
                .and_then(|f| f.sync_all())
                .map_err(|e| e.to_string())?;
        }
        hook("snapshot")?;
        let checksum = format!(
            "graph:{}\ndata:{}",
            compute_file_checksum(&graph)?,
            compute_file_checksum(&data)?
        );
        let mut checksum_options = std::fs::OpenOptions::new();
        let mut checksum_file = durable_write_options(&mut checksum_options)
            .write(true)
            .create_new(true)
            .open(dir.join(format!("{basename}.checksum")))
            .map_err(|e| e.to_string())?;
        checksum_file
            .write_all(checksum.as_bytes())
            .and_then(|_| checksum_file.sync_all())
            .map_err(|e| e.to_string())?;
        let mut wal_options = std::fs::OpenOptions::new();
        let new_wal = durable_write_options(&mut wal_options)
            .write(true)
            .create_new(true)
            .open(dir.join(format!("{basename}.hnsw.wal")))
            .map_err(|e| e.to_string())?;
        new_wal.sync_all().map_err(|e| e.to_string())?;
        sync_directory_if_supported(&dir)?;
        check_checkpoint_storage(path, max_bytes, max_entries)?;
        hook("prepared")?;
        let check = Self::try_load_single(&dir, basename, self.dimension)?;
        if check.len() != self.len() {
            return Err("Generacja ma niezgodną liczbę wektorów".into());
        }
        drop(check);
        let marker = path.join(format!("{basename}.commit.{number:020}"));
        let pending = path.join(format!(
            "{basename}.commit_tmp_{:016x}",
            rand::random::<u64>()
        ));
        let mut marker_options = std::fs::OpenOptions::new();
        let mut marker_file = durable_write_options(&mut marker_options)
            .write(true)
            .create_new(true)
            .open(&pending)
            .map_err(|e| e.to_string())?;
        marker_file
            .write_all(dir_name.as_bytes())
            .and_then(|_| marker_file.sync_all())
            .map_err(|e| e.to_string())?;
        drop(marker_file);
        hook("marker_ready")?;
        // No other writer may use the directory while the storage lease is held.
        if marker.try_exists().map_err(|e| e.to_string())? {
            return Err("Znacznik generacji już istnieje".into());
        }
        if let Err(error) = publish_marker(&pending, &marker) {
            self.wal_failed.store(true, Ordering::Release);
            return Err(format!(
                "Wynik publikacji generacji jest niepewny; uruchom ponownie: {error}"
            ));
        }
        // Once published, any failure must stop writes until restart selects the marker.
        if let Err(error) = hook("marker_moved") {
            self.wal_failed.store(true, Ordering::Release);
            return Err(error);
        }
        if let Err(error) = sync_directory_if_supported(path) {
            self.wal_failed.store(true, Ordering::Release);
            return Err(format!(
                "Znacznik opublikowany, ale synchronizacja katalogu nie powiodła się; uruchom ponownie: {error}"
            ));
        }
        if let Err(error) = hook("published") {
            self.wal_failed.store(true, Ordering::Release);
            return Err(error);
        }
        match self.generation.lock() {
            Ok(mut current) => *current = Some((number, dir)),
            Err(_) => {
                self.wal_failed.store(true, Ordering::Release);
                return Err(
                    "Znacznik opublikowany, lecz nie można przełączyć generacji; uruchom ponownie"
                        .into(),
                );
            }
        }
        Ok(())
    }

    fn file_dump_with_hook(
        &self,
        path: &Path,
        file_basename: &str,
        mut hook: impl FnMut(&str) -> Result<(), String>,
    ) -> Result<String, String> {
        self.require_storage(path)?;
        Self::validate_basename(file_basename)?;
        let _guard = self
            .write_lock
            .lock()
            .map_err(|_| "Blokada indeksu jest uszkodzona")?;
        if self.wal_failed.load(Ordering::Acquire) {
            return Err("Poprzedni zapis WAL zakończył się błędem; checkpoint wstrzymano".into());
        }
        if self
            .generation
            .lock()
            .map_err(|_| "Blokada generacji jest uszkodzona")?
            .is_some()
        {
            return Err("Użyj checkpointu generacyjnego zamiast zapisu starszego formatu".into());
        }
        if !path.exists() {
            std::fs::create_dir_all(path).map_err(|e| e.to_string())?;
        }

        // A non-empty WAL cannot be discarded safely without a transactional
        // checkpoint protocol. Preserve it and refuse this checkpoint instead.
        let wal_path = path.join(format!("{}.hnsw.wal", file_basename));
        match std::fs::metadata(&wal_path) {
            Ok(metadata) if metadata.len() > 0 => {
                return Err(
                    "Zapis indeksu wstrzymany: WAL nie jest pusty i wymaga bezpiecznego odzyskania"
                        .into(),
                );
            }
            Ok(_) => {}
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => {}
            Err(e) => return Err(format!("Nie można sprawdzić WAL: {e}")),
        }

        let tmp_basename = format!("{}_tmp_{:016x}", file_basename, rand::random::<u64>());

        // 1. Zapis do plików tymczasowych
        let dump_res = self
            .hnsw
            .file_dump(path, &tmp_basename)
            .map_err(|e| e.to_string())?;

        let tmp_graph = path.join(format!("{}.hnsw.graph", tmp_basename));
        let tmp_data = path.join(format!("{}.hnsw.data", tmp_basename));

        if !tmp_graph.exists() || !tmp_data.exists() {
            return Err("Nie utworzono tymczasowych plików dump HNSW.".into());
        }
        for staged in [&tmp_graph, &tmp_data] {
            std::fs::OpenOptions::new()
                .write(true)
                .open(staged)
                .and_then(|file| file.sync_all())
                .map_err(|e| format!("Nie można zsynchronizować pliku indeksu: {e}"))?;
        }

        // 2. Obliczenie kryptograficznej sumy kontrolnej SHA-256
        let graph_hash = compute_file_checksum(&tmp_graph)?;
        let data_hash = compute_file_checksum(&tmp_data)?;
        let checksum_content = format!("graph:{}\ndata:{}", graph_hash, data_hash);

        // Preserve a verified copy before changing any current-generation file.
        let target_graph = path.join(format!("{}.hnsw.graph", file_basename));
        let target_data = path.join(format!("{}.hnsw.data", file_basename));
        let target_checksum = path.join(format!("{}.checksum", file_basename));
        let targets = [&target_graph, &target_data, &target_checksum];
        let present: Vec<bool> = targets
            .iter()
            .map(|p| p.try_exists())
            .collect::<Result<_, _>>()
            .map_err(|e| e.to_string())?;
        if present.iter().any(|p| *p) {
            if !present.iter().all(|p| *p) {
                return Err(
                    "Niekompletna poprzednia generacja; pliki pozostawiono bez zmian".into(),
                );
            }
            // Validate the current generation before using it as a recovery copy.
            let previous = Self::try_load_single(path, file_basename, self.dimension)?;
            drop(previous);
            let backup_dir = path.join(format!(
                "{}.backup_{:016x}",
                file_basename,
                rand::random::<u64>()
            ));
            std::fs::create_dir(&backup_dir)
                .map_err(|e| format!("Nie można utworzyć kopii indeksu: {e}"))?;
            sync_directory_if_supported(path)?;
            for source in targets {
                let destination =
                    backup_dir.join(source.file_name().ok_or("Nieprawidłowa nazwa pliku")?);
                std::fs::copy(source, &destination)
                    .map_err(|e| format!("Nie można skopiować indeksu: {e}"))?;
                std::fs::OpenOptions::new()
                    .write(true)
                    .open(&destination)
                    .and_then(|f| f.sync_all())
                    .map_err(|e| format!("Nie można zsynchronizować kopii indeksu: {e}"))?;
                if compute_file_checksum(source)? != compute_file_checksum(&destination)? {
                    return Err("Kopia indeksu nie zgadza się z oryginałem".into());
                }
            }
            sync_directory_if_supported(&backup_dir)?;
            hook("backup")?;
            for (step, target) in ["remove_graph", "remove_data", "remove_checksum"]
                .into_iter()
                .zip(targets)
            {
                std::fs::remove_file(target)
                    .map_err(|e| format!("Nie można zastąpić indeksu; kopię zachowano: {e}"))?;
                hook(step)?;
            }
        }

        // Several filesystem operations are required; the backup permits manual
        // recovery if the process stops between them, but this is not atomic.
        std::fs::rename(&tmp_graph, &target_graph).map_err(|e| e.to_string())?;
        hook("publish_graph")?;
        std::fs::rename(&tmp_data, &target_data).map_err(|e| e.to_string())?;
        hook("publish_data")?;
        std::fs::write(&target_checksum, checksum_content).map_err(|e| e.to_string())?;
        std::fs::OpenOptions::new()
            .write(true)
            .open(&target_checksum)
            .and_then(|file| file.sync_all())
            .map_err(|e| format!("Nie można zsynchronizować sum kontrolnych: {e}"))?;
        sync_directory_if_supported(path)?;
        hook("publish_checksum")?;

        Ok(dump_res)
    }

    /// Read-only inspection, without exposing WAL contents or deciding whether
    /// an incomplete tail was previously acknowledged.
    pub fn inspect_wal(
        path: &Path,
        basename: &str,
        dimension: usize,
        lease: Arc<IndexLease>,
    ) -> Result<WalInspection, String> {
        use std::io::Read;
        Self::validate_basename(basename)?;
        let _binding = lease.bind(path, false)?;
        let generation = Self::latest_generation(path, basename)?;
        let active = generation.as_ref().map_or(path, |(_, dir)| dir.as_path());
        let wal_path = active.join(format!("{basename}.hnsw.wal"));
        let file = match std::fs::File::open(&wal_path) {
            Ok(file) => file,
            Err(error) if error.kind() == std::io::ErrorKind::NotFound && generation.is_none() => {
                return Ok(WalInspection {
                    format: "wal-inspection-v1",
                    bytes: 0,
                    complete_records: 0,
                    pending_items: 0,
                    issue: None,
                });
            }
            Err(error) => return Err(format!("Nie można otworzyć WAL: {error}")),
        };
        let mut bytes = Vec::new();
        file.take(MAX_WAL_BYTES + 1)
            .read_to_end(&mut bytes)
            .map_err(|e| format!("Nie można odczytać WAL: {e}"))?;
        if bytes.len() as u64 > MAX_WAL_BYTES {
            return Err("Dziennik WAL przekracza limit 64 MiB".into());
        }
        Ok(Self::inspect_wal_bytes(&bytes, dimension))
    }

    fn inspect_wal_bytes(bytes: &[u8], dimension: usize) -> WalInspection {
        let mut report = WalInspection {
            format: "wal-inspection-v1",
            bytes: bytes.len(),
            complete_records: 0,
            pending_items: 0,
            issue: None,
        };
        let mut pending = std::collections::HashSet::new();
        let mut seen = std::collections::HashSet::new();
        let mut offset = 0;
        for (position, record) in bytes.split_inclusive(|byte| *byte == b'\n').enumerate() {
            let line = position + 1;
            if !record.ends_with(b"\n") {
                report.issue = Some(WalInspectionIssue {
                    kind: "incomplete_tail",
                    line,
                    byte_offset: offset,
                });
                break;
            }
            let parsed = std::str::from_utf8(&record[..record.len() - 1])
                .ok()
                .map(str::trim);
            let valid = match parsed {
                Some("") => true,
                Some(text) if text.starts_with("v3:") => match parse_queue_record(text) {
                    Ok(QueueRecord::Enqueue { item }) => {
                        if let Some(id) = item.queue_id {
                            id.len() == 32
                                && id.bytes().all(|b| b.is_ascii_hexdigit())
                                && item.vector.len() == dimension
                                && item.vector.iter().all(|v| v.is_finite())
                                && item.metadata.len() <= MAX_QUEUE_METADATA_BYTES
                                && pending.len() < MAX_PENDING_ITEMS
                                && seen.insert(id.clone())
                                && pending.insert(id)
                        } else {
                            false
                        }
                    }
                    Ok(QueueRecord::Consolidate { queue_id }) => pending.remove(&queue_id),
                    Err(_) => false,
                },
                Some(text) => parse_wal_record(text, dimension).is_ok(),
                None => false,
            };
            if !valid {
                report.issue = Some(WalInspectionIssue {
                    kind: "invalid_record",
                    line,
                    byte_offset: offset,
                });
                break;
            }
            if parsed != Some("") {
                report.complete_records += 1;
            }
            offset += record.len();
        }
        report.pending_items = pending.len();
        report
    }

    /// Build an isolated candidate from an intact snapshot and the validated
    /// WAL prefix. The original is never modified and the candidate is never
    /// selected automatically. An incomplete tail may contain acknowledged data.
    pub fn prepare_wal_recovery_candidate(
        path: &Path,
        basename: &str,
        dimension: usize,
        lease: Arc<IndexLease>,
        accept_possible_loss: bool,
    ) -> Result<RecoveryCandidateReport, String> {
        Self::prepare_wal_recovery_candidate_with_hook(
            path,
            basename,
            dimension,
            lease,
            accept_possible_loss,
            |_| Ok(()),
        )
    }

    fn prepare_wal_recovery_candidate_with_hook(
        path: &Path,
        basename: &str,
        dimension: usize,
        lease: Arc<IndexLease>,
        accept_possible_loss: bool,
        mut hook: impl FnMut(&str) -> Result<(), String>,
    ) -> Result<RecoveryCandidateReport, String> {
        use sha2::{Digest, Sha256};
        use std::io::{Read, Write};
        if !accept_possible_loss {
            return Err("Wymagana jawna akceptacja możliwej utraty danych z końcówki WAL".into());
        }
        Self::validate_basename(basename)?;
        let _binding = lease.bind(path, false)?;
        let generation = Self::latest_generation(path, basename)?;
        let active = generation.as_ref().map_or(path, |(_, dir)| dir.as_path());
        let wal_path = active.join(format!("{basename}.hnsw.wal"));
        recovery_plain_file(&wal_path)?;
        let mut input_wal = Vec::new();
        std::fs::File::open(&wal_path)
            .map_err(|e| format!("Nie można odczytać WAL: {e}"))?
            .take(MAX_WAL_BYTES + 1)
            .read_to_end(&mut input_wal)
            .map_err(|e| e.to_string())?;
        if input_wal.len() as u64 > MAX_WAL_BYTES {
            return Err("WAL przekracza limit 64 MiB".into());
        }
        let inspection = Self::inspect_wal_bytes(&input_wal, dimension);
        let issue = inspection
            .issue
            .as_ref()
            .ok_or("WAL nie ma niekompletnej końcówki; nie utworzono kandydata")?;
        if issue.kind != "incomplete_tail" {
            return Err("WAL zawiera niepoprawny pełny rekord; nie utworzono kandydata".into());
        }
        let retained = issue.byte_offset;
        let original_hash = format!("{:x}", Sha256::digest(&input_wal));
        let candidate_hash = format!("{:x}", Sha256::digest(&input_wal[..retained]));
        let suffixes = [".hnsw.graph", ".hnsw.data", ".checksum"];
        let mut total = retained as u64;
        for suffix in suffixes {
            let source = active.join(format!("{basename}{suffix}"));
            let meta = recovery_plain_file(&source)?;
            total = total
                .checked_add(meta.len())
                .ok_or("Przekroczono limit rozmiaru kandydata")?;
            if total > MAX_CHECKPOINT_STORE_BYTES {
                return Err("Kandydat przekracza 4 GiB".into());
            }
        }
        // Validate the original baseline before producing any candidate files.
        let original = Self::try_load_single(active, basename, dimension)?;
        drop(original);
        let candidate_name = format!(
            "{basename}.recovery_candidate.{:016x}",
            rand::random::<u64>()
        );
        let candidate = path.join(&candidate_name);
        #[cfg(unix)]
        {
            use std::os::unix::fs::DirBuilderExt;
            std::fs::DirBuilder::new()
                .mode(0o700)
                .create(&candidate)
                .map_err(|e| format!("Nie można utworzyć katalogu kandydata: {e}"))?;
        }
        #[cfg(not(unix))]
        std::fs::create_dir(&candidate)
            .map_err(|e| format!("Nie można utworzyć katalogu kandydata: {e}"))?;
        sync_directory_if_supported(path)?;
        hook("created")?;
        let mut remaining = MAX_CHECKPOINT_STORE_BYTES - retained as u64;
        for suffix in suffixes {
            let name = format!("{basename}{suffix}");
            let source = active.join(&name);
            let destination = candidate.join(name);
            let mut input = std::fs::File::open(&source).map_err(|e| e.to_string())?;
            let mut options = std::fs::OpenOptions::new();
            #[cfg(unix)]
            {
                use std::os::unix::fs::OpenOptionsExt;
                options.mode(0o600);
            }
            let mut output = durable_write_options(&mut options)
                .write(true)
                .create_new(true)
                .open(&destination)
                .map_err(|e| e.to_string())?;
            let copied = std::io::copy(
                &mut Read::by_ref(&mut input).take(remaining + 1),
                &mut output,
            )
            .map_err(|e| e.to_string())?;
            if copied > remaining {
                return Err("Kopiowane pliki przekraczają limit kandydata".into());
            }
            remaining -= copied;
            output.sync_all().map_err(|e| e.to_string())?;
            if compute_file_checksum(&source)? != compute_file_checksum(&destination)? {
                return Err("Źródło lub kopia zmieniły się podczas odczytu".into());
            }
        }
        hook("baseline_copied")?;
        let mut options = std::fs::OpenOptions::new();
        #[cfg(unix)]
        {
            use std::os::unix::fs::OpenOptionsExt;
            options.mode(0o600);
        }
        let mut output = durable_write_options(&mut options)
            .write(true)
            .create_new(true)
            .open(candidate.join(format!("{basename}.hnsw.wal")))
            .map_err(|e| e.to_string())?;
        output
            .write_all(&input_wal[..retained])
            .and_then(|_| output.sync_all())
            .map_err(|e| e.to_string())?;
        drop(output);
        hook("wal_copied")?;
        if compute_file_checksum(&candidate.join(format!("{basename}.hnsw.wal")))? != candidate_hash
        {
            return Err("Nieprawidłowa suma WAL kandydata".into());
        }
        if compute_file_checksum(&wal_path)? != original_hash {
            return Err("WAL zmienił się podczas przygotowania kandydata".into());
        }
        let restored = Self::load_active_with_wal(&candidate, basename, dimension, true)?;
        if restored.pending_queue()?.len() != inspection.pending_items {
            return Err("Niezgodny stan kolejki kandydata".into());
        }
        drop(restored);
        hook("validated")?;
        let report = RecoveryCandidateReport {
            format: "wal-recovery-candidate-v1".into(),
            candidate_directory: candidate_name,
            retained_bytes: retained,
            excluded_tail_bytes: input_wal.len() - retained,
            original_wal_sha256: original_hash,
            candidate_wal_sha256: candidate_hash,
            pending_items: inspection.pending_items,
            possible_loss: true,
        };
        let manifest = serde_json::to_vec_pretty(&report).map_err(|e| e.to_string())?;
        let mut options = std::fs::OpenOptions::new();
        #[cfg(unix)]
        {
            use std::os::unix::fs::OpenOptionsExt;
            options.mode(0o600);
        }
        let mut file = durable_write_options(&mut options)
            .write(true)
            .create_new(true)
            .open(candidate.join("recovery-candidate.pending"))
            .map_err(|e| e.to_string())?;
        file.write_all(&manifest)
            .and_then(|_| file.sync_all())
            .map_err(|e| e.to_string())?;
        drop(file);
        hook("manifest_ready")?;
        publish_marker(
            &candidate.join("recovery-candidate.pending"),
            &candidate.join("recovery-candidate.json"),
        )?;
        sync_directory_if_supported(&candidate)?;
        Ok(report)
    }

    /// Recheck a candidate against the still-present source. This does not
    /// authenticate either copy, activate it, or establish that loss is safe.
    pub fn verify_wal_recovery_candidate(
        path: &Path,
        basename: &str,
        dimension: usize,
        candidate_name: &str,
        lease: Arc<IndexLease>,
    ) -> Result<RecoveryCandidateReport, String> {
        let _binding = lease.bind(path, false)?;
        Self::verify_candidate_locked(path, basename, dimension, candidate_name)
    }

    fn verify_candidate_locked(
        path: &Path,
        basename: &str,
        dimension: usize,
        candidate_name: &str,
    ) -> Result<RecoveryCandidateReport, String> {
        use sha2::{Digest, Sha256};
        use std::io::Read;
        Self::validate_basename(basename)?;
        let suffix = candidate_name
            .strip_prefix(&format!("{basename}.recovery_candidate."))
            .ok_or("Nieprawidłowa nazwa kandydata")?;
        if suffix.len() != 16 || !suffix.bytes().all(|b| b.is_ascii_hexdigit()) {
            return Err("Nieprawidłowa nazwa kandydata".into());
        }
        let candidate = path.join(candidate_name);
        let meta = std::fs::symlink_metadata(&candidate).map_err(|e| e.to_string())?;
        if !meta.file_type().is_dir() || meta.file_type().is_symlink() {
            return Err("Nieprawidłowy katalog kandydata".into());
        }
        #[cfg(windows)]
        {
            use std::os::windows::fs::MetadataExt;
            if meta.file_attributes() & 0x400 != 0 {
                return Err("Katalog kandydata jest punktem przekierowania".into());
            }
        }
        let expected = [
            format!("{basename}.hnsw.graph"),
            format!("{basename}.hnsw.data"),
            format!("{basename}.checksum"),
            format!("{basename}.hnsw.wal"),
            "recovery-candidate.json".to_owned(),
        ];
        let mut entries = 0;
        for entry in std::fs::read_dir(&candidate).map_err(|e| e.to_string())? {
            let entry = entry.map_err(|e| e.to_string())?;
            entries += 1;
            if entries > expected.len()
                || !expected
                    .iter()
                    .any(|name| entry.file_name() == name.as_str())
            {
                return Err("Katalog kandydata zawiera nieoczekiwany wpis".into());
            }
        }
        if entries != expected.len() {
            return Err("Katalog kandydata jest niekompletny".into());
        }
        let manifest_path = candidate.join("recovery-candidate.json");
        let manifest_meta = recovery_plain_file(&manifest_path)?;
        if manifest_meta.len() > 16 * 1024 {
            return Err("Manifest kandydata przekracza limit".into());
        }
        let mut manifest = Vec::new();
        std::fs::File::open(manifest_path)
            .map_err(|e| e.to_string())?
            .take(16 * 1024 + 1)
            .read_to_end(&mut manifest)
            .map_err(|e| e.to_string())?;
        if manifest.len() > 16 * 1024 {
            return Err("Manifest kandydata przekracza limit".into());
        }
        let report: RecoveryCandidateReport = serde_json::from_slice(&manifest)
            .map_err(|e| format!("Nieprawidłowy manifest kandydata: {e}"))?;
        if report.format != "wal-recovery-candidate-v1"
            || report.candidate_directory != candidate_name
            || !report.possible_loss
        {
            return Err("Manifest nie opisuje wskazanego kandydata".into());
        }
        let generation = Self::latest_generation(path, basename)?;
        let active = generation.as_ref().map_or(path, |(_, dir)| dir.as_path());
        let source_wal = active.join(format!("{basename}.hnsw.wal"));
        let candidate_wal = candidate.join(format!("{basename}.hnsw.wal"));
        let read_wal = |file: &Path| -> Result<Vec<u8>, String> {
            if recovery_plain_file(file)?.len() > MAX_WAL_BYTES {
                return Err("WAL przekracza limit".into());
            }
            let mut bytes = Vec::new();
            std::fs::File::open(file)
                .map_err(|e| e.to_string())?
                .take(MAX_WAL_BYTES + 1)
                .read_to_end(&mut bytes)
                .map_err(|e| e.to_string())?;
            if bytes.len() as u64 > MAX_WAL_BYTES {
                return Err("WAL przekracza limit".into());
            }
            Ok(bytes)
        };
        let source_bytes = read_wal(&source_wal)?;
        let candidate_bytes = read_wal(&candidate_wal)?;
        let inspection = Self::inspect_wal_bytes(&source_bytes, dimension);
        let issue = inspection
            .issue
            .as_ref()
            .ok_or("Źródłowy WAL nie ma niekompletnej końcówki")?;
        if issue.kind != "incomplete_tail"
            || issue.byte_offset != report.retained_bytes
            || source_bytes.len() - issue.byte_offset != report.excluded_tail_bytes
            || inspection.pending_items != report.pending_items
            || candidate_bytes != source_bytes[..issue.byte_offset]
            || format!("{:x}", Sha256::digest(&source_bytes)) != report.original_wal_sha256
            || format!("{:x}", Sha256::digest(&candidate_bytes)) != report.candidate_wal_sha256
        {
            return Err("Kandydat lub źródłowy WAL nie zgadza się z manifestem".into());
        }
        let mut total = candidate_bytes.len() as u64;
        for suffix in [".hnsw.graph", ".hnsw.data", ".checksum"] {
            let name = format!("{basename}{suffix}");
            let original = active.join(&name);
            let copy = candidate.join(&name);
            let source_meta = recovery_plain_file(&original)?;
            let copy_meta = recovery_plain_file(&copy)?;
            total = total
                .checked_add(copy_meta.len())
                .ok_or("Przekroczono limit kandydata")?;
            if total > MAX_CHECKPOINT_STORE_BYTES
                || source_meta.len() != copy_meta.len()
                || compute_file_checksum(&original)? != compute_file_checksum(&copy)?
            {
                return Err("Pliki kandydata lub źródła nie zgadzają się".into());
            }
        }
        let restored = Self::load_active_with_wal(&candidate, basename, dimension, true)?;
        if restored.pending_queue()?.len() != report.pending_items {
            return Err("Niezgodny stan kolejki kandydata".into());
        }
        Ok(report)
    }

    /// Explicitly publish a verified copy as a new generation. The source and
    /// candidate are retained; an incomplete tail may have contained data.
    #[allow(clippy::too_many_arguments)]
    pub fn activate_wal_recovery_candidate(
        path: &Path,
        basename: &str,
        dimension: usize,
        candidate_name: &str,
        expected_original_hash: &str,
        expected_candidate_hash: &str,
        lease: Arc<IndexLease>,
        accept_possible_loss: bool,
    ) -> Result<u64, String> {
        Self::activate_candidate_with_hook(
            path,
            basename,
            dimension,
            candidate_name,
            expected_original_hash,
            expected_candidate_hash,
            lease,
            accept_possible_loss,
            |_| Ok(()),
        )
    }

    #[allow(clippy::too_many_arguments)]
    fn activate_candidate_with_hook(
        path: &Path,
        basename: &str,
        dimension: usize,
        candidate_name: &str,
        expected_original_hash: &str,
        expected_candidate_hash: &str,
        lease: Arc<IndexLease>,
        accept_possible_loss: bool,
        mut hook: impl FnMut(&str) -> Result<(), String>,
    ) -> Result<u64, String> {
        use std::io::{Read, Write};
        if !accept_possible_loss {
            return Err("Wymagana akceptacja możliwej utraty danych".into());
        }
        let _binding = lease.bind(path, false)?;
        let report = Self::verify_candidate_locked(path, basename, dimension, candidate_name)?;
        if report.original_wal_sha256 != expected_original_hash
            || report.candidate_wal_sha256 != expected_candidate_hash
        {
            return Err("Sumy nie odpowiadają zatwierdzonemu raportowi".into());
        }
        check_checkpoint_storage(
            path,
            MAX_CHECKPOINT_STORE_BYTES,
            MAX_CHECKPOINT_STORE_ENTRIES,
        )?;
        let previous = Self::latest_generation(path, basename)?.map_or(0, |(n, _)| n);
        let number = previous
            .checked_add(1)
            .ok_or("Przekroczono numer generacji")?;
        let marker = path.join(format!("{basename}.commit.{number:020}"));
        if marker.try_exists().map_err(|e| e.to_string())? {
            return Err("Znacznik już istnieje".into());
        }
        let nonce = rand::random::<u64>();
        let staging = path.join(format!("{basename}.recovery_stage.{nonce:016x}"));
        let name = format!("{basename}.gen.{number:020}.{nonce:016x}");
        let destination = path.join(&name);
        #[cfg(unix)]
        {
            use std::os::unix::fs::DirBuilderExt;
            std::fs::DirBuilder::new()
                .mode(0o700)
                .create(&staging)
                .map_err(|e| e.to_string())?;
        }
        #[cfg(not(unix))]
        std::fs::create_dir(&staging).map_err(|e| e.to_string())?;
        sync_directory_if_supported(path)?;
        hook("created")?;
        let candidate = path.join(candidate_name);
        let mut remaining = MAX_CHECKPOINT_STORE_BYTES;
        for suffix in [".hnsw.graph", ".hnsw.data", ".checksum", ".hnsw.wal"] {
            let filename = format!("{basename}{suffix}");
            let source = candidate.join(&filename);
            recovery_plain_file(&source)?;
            let mut input = std::fs::File::open(&source).map_err(|e| e.to_string())?;
            let copy = staging.join(filename);
            let mut options = std::fs::OpenOptions::new();
            #[cfg(unix)]
            {
                use std::os::unix::fs::OpenOptionsExt;
                options.mode(0o600);
            }
            let mut output = durable_write_options(&mut options)
                .write(true)
                .create_new(true)
                .open(&copy)
                .map_err(|e| e.to_string())?;
            let copied = std::io::copy(
                &mut Read::by_ref(&mut input).take(remaining + 1),
                &mut output,
            )
            .map_err(|e| e.to_string())?;
            if copied > remaining {
                return Err("Kopia przekracza limit".into());
            }
            remaining -= copied;
            output.sync_all().map_err(|e| e.to_string())?;
            if compute_file_checksum(&source)? != compute_file_checksum(&copy)? {
                return Err("Kopia generacji nie zgadza się z kandydatem".into());
            }
        }
        sync_directory_if_supported(&staging)?;
        hook("copied")?;
        let restored = Self::load_active_with_wal(&staging, basename, dimension, true)?;
        if restored.pending_queue()?.len() != report.pending_items {
            return Err("Niezgodny stan kolejki".into());
        }
        drop(restored);
        // Recheck immediately before publication while the cooperative lease is held.
        let rechecked = Self::verify_candidate_locked(path, basename, dimension, candidate_name)?;
        if rechecked.original_wal_sha256 != expected_original_hash
            || rechecked.candidate_wal_sha256 != expected_candidate_hash
        {
            return Err("Kandydat lub źródło zmieniły się podczas aktywacji".into());
        }
        for suffix in [".hnsw.graph", ".hnsw.data", ".checksum", ".hnsw.wal"] {
            let filename = format!("{basename}{suffix}");
            if compute_file_checksum(&candidate.join(&filename))?
                != compute_file_checksum(&staging.join(filename))?
            {
                return Err("Kopia generacji zmieniła się przed publikacją".into());
            }
        }
        check_checkpoint_storage(
            path,
            MAX_CHECKPOINT_STORE_BYTES,
            MAX_CHECKPOINT_STORE_ENTRIES,
        )?;
        hook("validated")?;
        let pending = path.join(format!("{basename}.commit_tmp_{nonce:016x}"));
        let mut options = std::fs::OpenOptions::new();
        let mut file = durable_write_options(&mut options)
            .write(true)
            .create_new(true)
            .open(&pending)
            .map_err(|e| e.to_string())?;
        file.write_all(name.as_bytes())
            .and_then(|_| file.sync_all())
            .map_err(|e| e.to_string())?;
        drop(file);
        hook("marker_ready")?;
        // The no-replace directory name is random; a collision is an error.
        if destination.try_exists().map_err(|e| e.to_string())? {
            return Err("Generacja już istnieje".into());
        }
        std::fs::rename(&staging, &destination).map_err(|e| e.to_string())?;
        sync_directory_if_supported(path)?;
        hook("generation_renamed")?;
        if marker.try_exists().map_err(|e| e.to_string())? {
            return Err("Znacznik już istnieje".into());
        }
        publish_marker(&pending, &marker).map_err(|e| {
            format!("Niepewny wynik publikacji; zachowaj pliki i sprawdź po restarcie: {e}")
        })?;
        hook("marker_published")?;
        sync_directory_if_supported(path).map_err(|e| {
            format!("Znacznik może być aktywny; zachowaj pliki i sprawdź po restarcie: {e}")
        })?;
        Ok(number)
    }

    /// Delete exactly one verified redundant candidate after explicit review.
    /// If interrupted, an incomplete candidate is deliberately not trusted.
    #[allow(clippy::too_many_arguments)]
    pub fn delete_verified_recovery_candidate(
        path: &Path,
        basename: &str,
        dimension: usize,
        candidate_name: &str,
        expected_original_hash: &str,
        expected_candidate_hash: &str,
        lease: Arc<IndexLease>,
        confirm_delete: bool,
    ) -> Result<(), String> {
        Self::delete_candidate_with_hook(
            path,
            basename,
            dimension,
            candidate_name,
            expected_original_hash,
            expected_candidate_hash,
            lease,
            confirm_delete,
            |_| Ok(()),
        )
    }

    #[allow(clippy::too_many_arguments)]
    fn delete_candidate_with_hook(
        path: &Path,
        basename: &str,
        dimension: usize,
        candidate_name: &str,
        expected_original_hash: &str,
        expected_candidate_hash: &str,
        lease: Arc<IndexLease>,
        confirm_delete: bool,
        mut hook: impl FnMut(&str) -> Result<(), String>,
    ) -> Result<(), String> {
        if !confirm_delete {
            return Err("Wymagane potwierdzenie usunięcia kandydata".into());
        }
        let _binding = lease.bind(path, false)?;
        let report = Self::verify_candidate_locked(path, basename, dimension, candidate_name)?;
        if report.original_wal_sha256 != expected_original_hash
            || report.candidate_wal_sha256 != expected_candidate_hash
        {
            return Err("Sumy nie odpowiadają zatwierdzonemu raportowi".into());
        }
        let dir = path.join(candidate_name);
        // Remove the readiness marker first. Never recursively traverse data.
        std::fs::remove_file(dir.join("recovery-candidate.json")).map_err(|e| e.to_string())?;
        sync_directory_if_supported(&dir)?;
        hook("manifest_removed")?;
        for suffix in [".hnsw.graph", ".hnsw.data", ".checksum", ".hnsw.wal"] {
            let file = dir.join(format!("{basename}{suffix}"));
            recovery_plain_file(&file)?;
            std::fs::remove_file(file)
                .map_err(|e| format!("Usuwanie przerwane; kandydat nie jest gotowy: {e}"))?;
            hook(suffix)?;
        }
        std::fs::remove_dir(&dir).map_err(|e| format!("Usuwanie przerwane: {e}"))?;
        sync_directory_if_supported(path)?;
        Ok(())
    }

    /// Inspect one old generation for explicitly confirmed removal. Retain the
    /// newest two generations and reject ambiguous or unfinished recovery work.
    pub fn review_generation_retention(
        path: &Path,
        basename: &str,
        dimension: usize,
        generation: u64,
        lease: Arc<IndexLease>,
    ) -> Result<RetentionReview, String> {
        let _binding = lease.bind(path, false)?;
        Self::review_generation_locked(path, basename, dimension, generation)
    }

    fn review_generation_locked(
        path: &Path,
        basename: &str,
        dimension: usize,
        generation: u64,
    ) -> Result<RetentionReview, String> {
        use sha2::{Digest, Sha256};
        Self::validate_basename(basename)?;
        let mut markers = Vec::new();
        let mut dirs = Vec::new();
        let mut count = 0usize;
        for item in std::fs::read_dir(path).map_err(|e| e.to_string())? {
            let item = item.map_err(|e| e.to_string())?;
            count += 1;
            if count > MAX_CHECKPOINT_STORE_ENTRIES {
                return Err("Zbyt wiele wpisów do przeglądu".into());
            }
            let name = item
                .file_name()
                .into_string()
                .map_err(|_| "Nieprawidłowa nazwa pliku")?;
            if name.starts_with(&format!("{basename}.recovery_candidate."))
                || name.starts_with(&format!("{basename}.recovery_stage."))
                || name.starts_with(&format!("{basename}.commit_tmp_"))
            {
                return Err(
                    "Niedokończone lub istniejące odzyskiwanie; przegląd retencji wstrzymano"
                        .into(),
                );
            }
            if let Some(suffix) = name.strip_prefix(&format!("{basename}.commit.")) {
                if suffix.len() != 20 || !suffix.bytes().all(|b| b.is_ascii_digit()) {
                    return Err("Nieprawidłowy znacznik".into());
                }
                let n: u64 = suffix
                    .parse()
                    .map_err(|_| "Nieprawidłowy numer generacji")?;
                let marker = item.path();
                if recovery_plain_file(&marker)?.len() > 256 {
                    return Err("Znacznik jest za duży".into());
                }
                let name = std::fs::read_to_string(&marker).map_err(|e| e.to_string())?;
                let prefix = format!("{basename}.gen.{n:020}.");
                let nonce = name.strip_prefix(&prefix).ok_or("Błędny znacznik")?;
                if nonce.len() != 16 || !nonce.bytes().all(|b| b.is_ascii_hexdigit()) {
                    return Err("Błędny znacznik".into());
                }
                markers.push((n, name));
            } else if name.starts_with(&format!("{basename}.gen.")) {
                dirs.push(name);
            }
        }
        markers.sort_by_key(|(number, _)| *number);
        if markers.len() < 3 || markers[markers.len() - 2].0 <= generation {
            return Err("Należy zachować dwie najnowsze generacje".into());
        }
        if dirs.len() != markers.len()
            || dirs
                .iter()
                .any(|dir| !markers.iter().any(|(_, name)| name == dir))
        {
            return Err(
                "Niejednoznaczna lub nieopublikowana generacja; retencję wstrzymano".into(),
            );
        }
        let (_, target_name) = markers
            .iter()
            .find(|(n, _)| *n == generation)
            .ok_or("Nie znaleziono generacji")?;
        let latest = Self::latest_generation(path, basename)?.ok_or("Brak aktywnej generacji")?;
        if latest.0 != markers.last().unwrap().0 {
            return Err("Niezgodna aktywna generacja".into());
        }
        // Ensure both retained generations and the target are readable, and
        // refuse any unusual files, links or non-empty target journal.
        let check = |name: &str, require_empty_wal: bool| -> Result<(u64, Vec<String>), String> {
            let dir = path.join(name);
            let meta = std::fs::symlink_metadata(&dir).map_err(|e| e.to_string())?;
            if !meta.file_type().is_dir() || meta.file_type().is_symlink() {
                return Err("Nietypowy katalog generacji".into());
            }
            #[cfg(windows)]
            {
                use std::os::windows::fs::MetadataExt;
                if meta.file_attributes() & 0x400 != 0 {
                    return Err("Punkt przekierowania generacji".into());
                }
            }
            let names = [
                format!("{basename}.hnsw.graph"),
                format!("{basename}.hnsw.data"),
                format!("{basename}.checksum"),
                format!("{basename}.hnsw.wal"),
            ];
            let mut count = 0;
            for item in std::fs::read_dir(&dir).map_err(|e| e.to_string())? {
                let item = item.map_err(|e| e.to_string())?;
                count += 1;
                if count > names.len() || !names.iter().any(|n| item.file_name() == n.as_str()) {
                    return Err("Nietypowa zawartość generacji".into());
                }
            }
            if count != names.len() {
                return Err("Niekompletna generacja".into());
            }
            let mut size = 0u64;
            let mut hashes = Vec::new();
            for name in names {
                let file = dir.join(&name);
                let meta = recovery_plain_file(&file)?;
                size = size.checked_add(meta.len()).ok_or("Przekroczono limit")?;
                if size > MAX_CHECKPOINT_STORE_BYTES {
                    return Err("Generacja przekracza limit".into());
                }
                if name.ends_with(".hnsw.wal") && require_empty_wal && meta.len() != 0 {
                    return Err("Historyczny WAL nie jest pusty".into());
                }
                hashes.push(compute_file_checksum(&file)?);
            }
            let restored = Self::load_active_with_wal(&dir, basename, dimension, true)?;
            drop(restored);
            Ok((size, hashes))
        };
        for (_, name) in markers.iter().rev().take(2) {
            check(name, false)?;
        }
        let (bytes, hashes) = check(target_name, true)?;
        let mut digest = Sha256::new();
        digest.update(b"retention-review-v1\0");
        digest.update(basename.as_bytes());
        digest.update([0]);
        digest.update(generation.to_be_bytes());
        digest.update(target_name.as_bytes());
        digest.update([0]);
        for hash in hashes {
            digest.update(hash.as_bytes());
        }
        Ok(RetentionReview {
            generation,
            directory: target_name.clone(),
            fingerprint_sha256: format!("{:x}", digest.finalize()),
            bytes,
        })
    }

    pub fn delete_reviewed_generation(
        path: &Path,
        basename: &str,
        dimension: usize,
        generation: u64,
        fingerprint: &str,
        lease: Arc<IndexLease>,
        confirm_delete: bool,
    ) -> Result<(), String> {
        Self::delete_generation_with_hook(
            path,
            basename,
            dimension,
            generation,
            fingerprint,
            lease,
            confirm_delete,
            |_| Ok(()),
        )
    }

    #[allow(clippy::too_many_arguments)]
    fn delete_generation_with_hook(
        path: &Path,
        basename: &str,
        dimension: usize,
        generation: u64,
        fingerprint: &str,
        lease: Arc<IndexLease>,
        confirm_delete: bool,
        mut hook: impl FnMut(&str) -> Result<(), String>,
    ) -> Result<(), String> {
        if !confirm_delete {
            return Err("Wymagane potwierdzenie usunięcia generacji".into());
        }
        let _binding = lease.bind(path, false)?;
        let report = Self::review_generation_locked(path, basename, dimension, generation)?;
        if report.fingerprint_sha256 != fingerprint {
            return Err("Generacja nie odpowiada zatwierdzonemu przeglądowi".into());
        }
        let dir = path.join(&report.directory);
        // Retired marker first: interruption never selects a partially removed tree.
        std::fs::remove_file(path.join(format!("{basename}.commit.{generation:020}")))
            .map_err(|e| e.to_string())?;
        sync_directory_if_supported(path)?;
        hook("marker_removed")?;
        for suffix in [".hnsw.graph", ".hnsw.data", ".checksum", ".hnsw.wal"] {
            let file = dir.join(format!("{basename}{suffix}"));
            recovery_plain_file(&file)?;
            std::fs::remove_file(file)
                .map_err(|e| format!("Usuwanie przerwane; zachowaj pozostałości: {e}"))?;
            hook(suffix)?;
        }
        std::fs::remove_dir(dir).map_err(|e| format!("Usuwanie przerwane: {e}"))?;
        sync_directory_if_supported(path)?;
        Ok(())
    }

    /// Wczytuje zweryfikowaną generację główną i odtwarza wpisy WAL.
    /// Starsza generacja nie jest automatycznie używana: WAL mógł już zostać
    /// wyczyszczony po nowszym zrzucie i taki fallback mógłby ukryć utratę danych.
    pub fn load_hnsw(
        path: &Path,
        file_basename: &str,
        dimension: usize,
        lease: Arc<IndexLease>,
    ) -> Result<Self, String> {
        Self::validate_basename(file_basename)?;
        let binding = lease.bind(path, false)?;
        let generation = Self::latest_generation(path, file_basename)?;
        let active = generation.as_ref().map_or(path, |(_, dir)| dir.as_path());
        let mut index =
            Self::load_active_with_wal(active, file_basename, dimension, generation.is_some())?;
        index.storage = Some(binding);
        *index
            .generation
            .lock()
            .map_err(|_| "Blokada generacji jest uszkodzona")? = generation;
        Ok(index)
    }

    fn load_active_with_wal(
        active: &Path,
        file_basename: &str,
        dimension: usize,
        require_wal: bool,
    ) -> Result<Self, String> {
        let index = Self::try_load_single(active, file_basename, dimension)?;
        // Odtworzenie wpisów z dziennika WAL (jeśli istniały wpisy po ostatnim zrzucie)
        let wal_path = active.join(format!("{}.hnsw.wal", file_basename));
        if require_wal && !wal_path.is_file() {
            return Err("Brak dziennika opublikowanej generacji".into());
        }
        if wal_path.try_exists().map_err(|e| e.to_string())? {
            if std::fs::metadata(&wal_path)
                .map_err(|e| e.to_string())?
                .len()
                > MAX_WAL_BYTES
            {
                return Err("Dziennik WAL przekracza limit 64 MiB".into());
            }
            let content = std::fs::read_to_string(&wal_path)
                .map_err(|e| format!("Nie można odczytać WAL: {e}"))?;
            if !content.is_empty() && !content.ends_with('\n') {
                return Err("Niekompletny ostatni rekord WAL".to_string());
            }
            let mut replayed_count = 0;
            let mut seen_queue_ids = std::collections::HashSet::new();
            for (line_number, line) in content.lines().enumerate() {
                let trimmed = line.trim();
                if trimmed.is_empty() {
                    continue;
                }
                let invalid = || format!("Nieprawidłowy rekord WAL w linii {}", line_number + 1);
                if trimmed.starts_with("v3:") {
                    let record =
                        parse_queue_record(trimmed).map_err(|e| format!("{}: {e}", invalid()))?;
                    let mut pending = index
                        .pending
                        .lock()
                        .map_err(|_| "Blokada kolejki jest uszkodzona")?;
                    match record {
                        QueueRecord::Enqueue { item } => {
                            let id = item.queue_id.as_deref().ok_or_else(invalid)?;
                            if id.len() != 32
                                || !id.bytes().all(|b| b.is_ascii_hexdigit())
                                || !seen_queue_ids.insert(id.to_owned())
                                || item.vector.len() != dimension
                                || item.vector.iter().any(|v| !v.is_finite())
                                || item.metadata.len() > MAX_QUEUE_METADATA_BYTES
                                || pending.len() >= MAX_PENDING_ITEMS
                            {
                                return Err(invalid());
                            }
                            pending.push(item);
                        }
                        QueueRecord::Consolidate { queue_id } => {
                            let position = pending
                                .iter()
                                .position(|item| item.queue_id.as_deref() == Some(&queue_id))
                                .ok_or_else(invalid)?;
                            let item = pending.remove(position);
                            index
                                .insert(item.id, &item.vector)
                                .map_err(|e| format!("{}: {e}", invalid()))?;
                            replayed_count += 1;
                        }
                    }
                } else {
                    let (id, vector) = parse_wal_record(trimmed, dimension)
                        .map_err(|e| format!("{}: {e}", invalid()))?;
                    index
                        .insert(id, &vector)
                        .map_err(|e| format!("{}: {e}", invalid()))?;
                    replayed_count += 1;
                }
            }
            if replayed_count > 0 {
                eprintln!(
                    "✓ [HNSW WAL REPLAY]: Odtworzono {} wektorów z dziennika WAL.",
                    replayed_count
                );
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

        // An absent, unreadable or malformed checksum cannot establish integrity.
        let checksum_path = path.join(format!("{}.checksum", file_basename));
        let content = std::fs::read_to_string(&checksum_path)
            .map_err(|e| format!("Nie można odczytać sum kontrolnych {file_basename}: {e}"))?;
        let mut lines = content.lines();
        let expected_graph = lines.next().and_then(|line| line.strip_prefix("graph:"));
        let expected_data = lines.next().and_then(|line| line.strip_prefix("data:"));
        if lines.next().is_some()
            || expected_graph != Some(compute_file_checksum(&graph_path)?.as_str())
            || expected_data != Some(compute_file_checksum(&data_path)?.as_str())
        {
            return Err(format!(
                "Nieprawidłowe lub niezgodne sumy kontrolne SHA-256 dla {file_basename}"
            ));
        }

        let mut reloader = Box::new(HnswIo::new(path, file_basename));
        let reloader_ptr: *mut HnswIo = &mut *reloader;
        let hnsw: Hnsw<'static, f32, DistCosine> = unsafe {
            (*reloader_ptr)
                .load_hnsw::<f32, DistCosine>()
                .map_err(|e| e.to_string())?
        };

        let loaded_count = hnsw.get_nb_point();

        Ok(Self {
            hnsw,
            dimension,
            max_elements: 100_000,
            current_count: AtomicUsize::new(loaded_count),
            wal_failed: AtomicBool::new(false),
            journal_only_pending: AtomicBool::new(false),
            generation: Mutex::new(None),
            pending: Mutex::new(Vec::new()),
            write_lock: Mutex::new(()),
            storage: None,
            _reloader: Some(reloader),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::{SystemTime, UNIX_EPOCH};

    fn fresh_temp_dir(test_name: &str) -> std::path::PathBuf {
        let unique_suffix = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("system clock should be after the Unix epoch")
            .as_nanos();
        let directory = std::env::temp_dir()
            .join(format!(
                "blyskawica-{test_name}-{}-{unique_suffix}",
                std::process::id()
            ))
            .join("db");
        std::fs::create_dir_all(&directory).expect("test directory should be created");
        directory
    }

    fn lease_for(dir: &Path) -> Arc<IndexLease> {
        Arc::new(IndexLease::acquire(&dir.parent().unwrap().join("sparkle-index.lock")).unwrap())
    }

    #[test]
    fn lease_child_helper() {
        if let Some(path) = std::env::var_os("BLYSK_TEST_LEASE_PATH") {
            let expected = std::env::var("BLYSK_TEST_LEASE_EXPECT").unwrap();
            let acquired = IndexLease::acquire(Path::new(&path)).is_ok();
            assert_eq!(acquired, expected == "free");
        }
    }

    #[test]
    fn crash_simulation_child() {
        let Some(path) = std::env::var_os("BLYSK_TEST_CRASH_DB") else {
            return;
        };
        let path = PathBuf::from(path);
        let lease = lease_for(&path);
        let index = SparkleVectorIndex::load_hnsw(&path, "index", 4, lease).unwrap();
        match std::env::var("BLYSK_TEST_CRASH_ACTION").unwrap().as_str() {
            "wal" => {
                index
                    .insert_with_wal(&path, "index", 2, &[0.0, 1.0, 0.0, 0.0])
                    .unwrap();
                std::process::exit(42);
            }
            "enqueue" => {
                index
                    .enqueue_durable_with_hook(
                        &path,
                        "index",
                        crate::anomaly_loop::AnomalyQueueItem {
                            id: 2,
                            vector: vec![0.0, 1.0, 0.0, 0.0],
                            metadata: "synthetic queue".into(),
                            queue_id: None,
                        },
                        || std::process::exit(42),
                    )
                    .unwrap();
                panic!("expected interruption");
            }
            "consolidate" => {
                let pending = index.pending_queue().unwrap();
                index
                    .consolidate_queued_with_hook(
                        &path,
                        "index",
                        pending[0].queue_id.as_deref().unwrap(),
                        || std::process::exit(42),
                    )
                    .unwrap();
                panic!("expected interruption");
            }
            "snapshot" => {
                index.insert(2, &[0.0, 1.0, 0.0, 0.0]).unwrap();
                let _ = index.file_dump_with_hook(&path, "index", |step| {
                    if step == "remove_data" {
                        std::process::exit(42);
                    }
                    Ok(())
                });
                panic!("expected interruption");
            }
            action if action.starts_with("checkpoint_") => {
                let stop = action.strip_prefix("checkpoint_").unwrap();
                let _ = index.checkpoint_with_hook(&path, "index", |step| {
                    if step == stop {
                        std::process::exit(42);
                    }
                    Ok(())
                });
                panic!("expected interruption");
            }
            _ => panic!("unknown crash scenario"),
        }
    }

    #[test]
    fn abrupt_process_exit_keeps_wal_or_prior_generation() {
        for action in ["wal", "snapshot"] {
            let dir = fresh_temp_dir("abrupt-exit");
            let lease = lease_for(&dir);
            let index = SparkleVectorIndex::new(4, 10)
                .with_storage(&dir, lease.clone())
                .unwrap();
            index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
            index.file_dump(&dir, "index").unwrap();
            drop(index);
            drop(lease);
            let status = std::process::Command::new(std::env::current_exe().unwrap())
                .args(["--exact", "vector_index::tests::crash_simulation_child"])
                .env("BLYSK_TEST_CRASH_DB", &dir)
                .env("BLYSK_TEST_CRASH_ACTION", action)
                .status()
                .unwrap();
            assert_eq!(status.code(), Some(42));
            let lease = lease_for(&dir);
            if action == "wal" {
                let recovered =
                    SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
                assert_eq!(recovered.len(), 2);
                assert_eq!(recovered.search(&[0.0, 1.0, 0.0, 0.0], 1)[0].d_id, 2);
                drop(recovered);
            } else {
                assert!(SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).is_err());
                let backup = std::fs::read_dir(&dir)
                    .unwrap()
                    .map(|entry| entry.unwrap().path())
                    .find(|path| {
                        path.file_name()
                            .unwrap()
                            .to_string_lossy()
                            .starts_with("index.backup_")
                    })
                    .unwrap();
                let recovered = SparkleVectorIndex::try_load_single(&backup, "index", 4).unwrap();
                assert_eq!(recovered.len(), 1);
                drop(recovered);
            }
            drop(lease);
            std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
        }
    }

    #[test]
    fn lease_excludes_other_process_until_released() {
        let dir = fresh_temp_dir("process-lock");
        let lock = dir.join("index.lock");
        let lease = IndexLease::acquire(&lock).unwrap();
        let run_child = |expected: &str| {
            std::process::Command::new(std::env::current_exe().unwrap())
                .args(["--exact", "vector_index::tests::lease_child_helper"])
                .env("BLYSK_TEST_LEASE_PATH", &lock)
                .env("BLYSK_TEST_LEASE_EXPECT", expected)
                .status()
                .unwrap()
                .success()
        };
        assert!(run_child("busy"));
        drop(lease);
        assert!(run_child("free"));
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn durable_operations_require_lease_for_the_matching_storage() {
        let first = fresh_temp_dir("lease-storage-a");
        let second = fresh_temp_dir("lease-storage-b");
        let lease = lease_for(&first);
        let unbound = SparkleVectorIndex::new(4, 10);
        assert!(unbound.file_dump(&first, "index").is_err());
        assert!(
            unbound
                .append_wal(&first, "index", 1, &[1.0, 0.0, 0.0, 0.0])
                .is_err()
        );
        assert!(
            SparkleVectorIndex::new(4, 10)
                .with_storage(&second, lease.clone())
                .is_err()
        );
        let index = unbound.with_storage(&first, lease.clone()).unwrap();
        assert!(
            SparkleVectorIndex::new(4, 10)
                .with_storage(&first, lease.clone())
                .is_err()
        );
        assert!(index.file_dump(&second, "index").is_err());
        assert!(index.file_dump(&first, "../escape").is_err());
        assert!(std::fs::read_dir(&first).unwrap().next().is_none());
        drop(index);
        let rebound = SparkleVectorIndex::new(4, 10)
            .with_storage(&first, lease.clone())
            .unwrap();
        drop(rebound);
        drop(lease);
        std::fs::remove_dir_all(first.parent().unwrap()).unwrap();
        std::fs::remove_dir_all(second.parent().unwrap()).unwrap();
    }

    #[test]
    fn persistent_index_keeps_lease_until_it_is_dropped() {
        let dir = fresh_temp_dir("lease-lifetime");
        let lock = dir.parent().unwrap().join("sparkle-index.lock");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        drop(lease);
        let run_child = |expected: &str| {
            std::process::Command::new(std::env::current_exe().unwrap())
                .args(["--exact", "vector_index::tests::lease_child_helper"])
                .env("BLYSK_TEST_LEASE_PATH", &lock)
                .env("BLYSK_TEST_LEASE_EXPECT", expected)
                .status()
                .unwrap()
                .success()
        };
        assert!(run_child("busy"));
        drop(index);
        assert!(run_child("free"));
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

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
        assert!(
            overflow
                .unwrap_err()
                .contains("Przekroczono maksymalną pojemność")
        );
    }

    #[test]
    fn test_vector_dump_and_load_with_checksum() {
        let temp_dir = fresh_temp_dir("vector-dump-checksum");
        let lease = lease_for(&temp_dir);
        let basename = "test_dump_cs";

        let index = SparkleVectorIndex::new(4, 100)
            .with_storage(&temp_dir, lease.clone())
            .unwrap();
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
        drop(index);
        let loaded_index = SparkleVectorIndex::load_hnsw(&temp_dir, basename, 4, lease.clone())
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
        drop(loaded_index);
        let corrupted_load = SparkleVectorIndex::load_hnsw(&temp_dir, basename, 4, lease.clone());
        assert!(
            corrupted_load.is_err(),
            "Wczytanie uszkodzonego pliku bez kopii .prev musi zwrócić błąd"
        );

        drop(lease);
        std::fs::remove_dir_all(temp_dir.parent().unwrap())
            .expect("test directory should be removed");
    }

    #[test]
    fn test_hnsw_wal_crash_recovery() {
        let temp_dir = fresh_temp_dir("vector-wal-recovery");
        let lease = lease_for(&temp_dir);
        let basename = "test_wal_rec";
        let dimension = 4;

        let index = SparkleVectorIndex::new(dimension, 100)
            .with_storage(&temp_dir, lease.clone())
            .unwrap();
        let initial_vec = vec![1.0, 0.0, 0.0, 0.0];
        assert!(index.insert(100, &initial_vec).is_ok());

        // 1. Utrwalenie stanu początkowego na dysku
        assert!(index.file_dump(&temp_dir, basename).is_ok());

        // 2. Symulacja niespodziewanego zapisu do WAL bez pełnego zrzutu grafu
        let uncommitted_vec = vec![0.0, 1.0, 0.0, 0.0];
        assert!(
            index
                .append_wal(&temp_dir, basename, 200, &uncommitted_vec)
                .is_ok()
        );

        // 3. Załadowanie indeksu z dysku — musi odtworzyć wektor 200 z WAL
        drop(index);
        let loaded = SparkleVectorIndex::load_hnsw(&temp_dir, basename, dimension, lease.clone())
            .expect("Ładowanie z WAL powinno się udać");

        assert_eq!(
            loaded.len(),
            2,
            "Indeks po odtworzeniu WAL powinien zawierać 2 wektory"
        );

        let search_res = loaded.search(&[0.0, 0.9, 0.0, 0.0], 1);
        assert_eq!(
            search_res[0].d_id, 200,
            "Wektor z WAL powinien być poprawnie odnaleziony"
        );

        drop(loaded);
        drop(lease);
        std::fs::remove_dir_all(temp_dir.parent().unwrap())
            .expect("test directory should be removed");
    }

    #[test]
    fn missing_or_malformed_checksum_and_wal_fail_closed() {
        let dir = fresh_temp_dir("integrity-fail-closed");
        let lease = lease_for(&dir);
        let name = "index";
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, name).unwrap();
        let checksum = dir.join("index.checksum");
        let valid_checksum = std::fs::read(&checksum).unwrap();
        drop(index);

        std::fs::remove_file(&checksum).unwrap();
        assert!(SparkleVectorIndex::load_hnsw(&dir, name, 4, lease.clone()).is_err());
        std::fs::write(&checksum, b"graph:invalid").unwrap();
        assert!(SparkleVectorIndex::load_hnsw(&dir, name, 4, lease.clone()).is_err());
        std::fs::write(&checksum, valid_checksum).unwrap();
        std::fs::write(dir.join("index.hnsw.wal"), b"2:0,1,broken,0\n").unwrap();
        assert!(SparkleVectorIndex::load_hnsw(&dir, name, 4, lease.clone()).is_err());
        std::fs::write(dir.join("index.hnsw.wal"), b"2:0,1,0,0").unwrap();
        assert!(SparkleVectorIndex::load_hnsw(&dir, name, 4, lease.clone()).is_err());

        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn wal_checksums_reject_valid_looking_corruption_and_accept_legacy() {
        let dir = fresh_temp_dir("wal-record-integrity");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        index
            .insert_with_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
            .unwrap();
        drop(index);
        let wal = dir.join("index.hnsw.wal");
        let valid = std::fs::read_to_string(&wal).unwrap();
        assert!(valid.starts_with("v2:2:"));
        let altered = valid.replacen("v2:2:0,1,0,0:", "v2:2:0,2,0,0:", 1);
        assert_ne!(valid, altered);
        std::fs::write(&wal, &altered).unwrap();
        assert!(SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).is_err());
        std::fs::write(&wal, "2:0,1,0,0\n").unwrap();
        let legacy = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
        assert_eq!(legacy.len(), 2);
        drop(legacy);
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn durable_queue_survives_restart_and_consolidates_exactly_once() {
        let dir = fresh_temp_dir("queue-lifecycle");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        let item = |id, vector| crate::anomaly_loop::AnomalyQueueItem {
            id,
            vector,
            metadata: format!("synthetic-{id}"),
            queue_id: None,
        };
        let first = index
            .enqueue_durable(&dir, "index", item(2, vec![0.0, 1.0, 0.0, 0.0]))
            .unwrap();
        index
            .enqueue_durable(&dir, "index", item(3, vec![0.0, 0.0, 1.0, 0.0]))
            .unwrap();
        assert_eq!(index.len(), 1);
        assert!(index.checkpoint(&dir, "index").is_err());
        drop(index);
        let index = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
        assert_eq!(index.pending_queue().unwrap().len(), 2);
        index
            .consolidate_queued(&dir, "index", first.queue_id.as_deref().unwrap())
            .unwrap();
        drop(index);
        let index = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
        assert_eq!(index.len(), 2);
        let remaining = index.pending_queue().unwrap();
        assert_eq!(remaining.len(), 1);
        assert_eq!(remaining[0].metadata, "synthetic-3");
        assert!(
            index
                .consolidate_queued(&dir, "index", first.queue_id.as_deref().unwrap())
                .is_err()
        );
        index
            .consolidate_queued(&dir, "index", remaining[0].queue_id.as_deref().unwrap())
            .unwrap();
        index.checkpoint(&dir, "index").unwrap();
        drop(index);
        let index = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
        assert_eq!(index.len(), 3);
        assert!(index.pending_queue().unwrap().is_empty());
        drop(index);
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn queue_journal_recovers_after_abrupt_process_exits() {
        let dir = fresh_temp_dir("queue-process-exit");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        drop(index);
        drop(lease);
        for action in ["enqueue", "consolidate"] {
            let status = std::process::Command::new(std::env::current_exe().unwrap())
                .args(["--exact", "vector_index::tests::crash_simulation_child"])
                .env("BLYSK_TEST_CRASH_DB", &dir)
                .env("BLYSK_TEST_CRASH_ACTION", action)
                .status()
                .unwrap();
            assert_eq!(status.code(), Some(42));
            let lease = lease_for(&dir);
            let index = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
            if action == "enqueue" {
                assert_eq!(index.pending_queue().unwrap().len(), 1);
                assert_eq!(index.len(), 1);
            } else {
                assert!(index.pending_queue().unwrap().is_empty());
                assert_eq!(index.len(), 2);
            }
            drop(index);
            drop(lease);
        }
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn invalid_or_tampered_queue_records_fail_closed() {
        let dir = fresh_temp_dir("queue-corrupt");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        let bad = crate::anomaly_loop::AnomalyQueueItem {
            id: 2,
            vector: vec![0.0, 1.0, 0.0, 0.0],
            metadata: "x".repeat(MAX_QUEUE_METADATA_BYTES + 1),
            queue_id: None,
        };
        assert!(index.enqueue_durable(&dir, "index", bad).is_err());
        assert!(!dir.join("index.hnsw.wal").exists());
        let good = crate::anomaly_loop::AnomalyQueueItem {
            id: 2,
            vector: vec![0.0, 1.0, 0.0, 0.0],
            metadata: "synthetic".into(),
            queue_id: None,
        };
        index.enqueue_durable(&dir, "index", good).unwrap();
        drop(index);
        let wal = dir.join("index.hnsw.wal");
        let original = std::fs::read_to_string(&wal).unwrap();
        let changed = original.replace("synthetic", "altered--");
        assert_ne!(original, changed);
        std::fs::write(&wal, changed).unwrap();
        assert!(SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).is_err());
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn wal_inspection_reports_tail_without_mutating_or_exposing_contents() {
        use std::io::Write;
        let dir = fresh_temp_dir("inspect-tail");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        index
            .enqueue_durable(
                &dir,
                "index",
                crate::anomaly_loop::AnomalyQueueItem {
                    id: 2,
                    vector: vec![0.0, 1.0, 0.0, 0.0],
                    metadata: "private-synthetic-content".into(),
                    queue_id: None,
                },
            )
            .unwrap();
        drop(index);
        let path = dir.join("index.hnsw.wal");
        let offset = std::fs::metadata(&path).unwrap().len() as usize;
        std::fs::OpenOptions::new()
            .append(true)
            .open(&path)
            .unwrap()
            .write_all(b"v3:partial")
            .unwrap();
        let before = std::fs::read(&path).unwrap();
        let report = SparkleVectorIndex::inspect_wal(&dir, "index", 4, lease.clone()).unwrap();
        assert_eq!(report.complete_records, 1);
        assert_eq!(report.pending_items, 1);
        assert_eq!(
            report.issue,
            Some(WalInspectionIssue {
                kind: "incomplete_tail",
                line: 2,
                byte_offset: offset
            })
        );
        assert!(
            !serde_json::to_string(&report)
                .unwrap()
                .contains("private-synthetic-content")
        );
        assert_eq!(std::fs::read(&path).unwrap(), before);
        assert!(SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).is_err());
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn wal_inspection_rejects_unmatched_consolidation() {
        let dir = fresh_temp_dir("inspect-order");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        drop(index);
        let invalid = queue_record(&QueueRecord::Consolidate {
            queue_id: "0123456789abcdef0123456789abcdef".into(),
        })
        .unwrap();
        std::fs::write(dir.join("index.hnsw.wal"), invalid).unwrap();
        let report = SparkleVectorIndex::inspect_wal(&dir, "index", 4, lease.clone()).unwrap();
        assert_eq!(
            report.issue,
            Some(WalInspectionIssue {
                kind: "invalid_record",
                line: 1,
                byte_offset: 0
            })
        );
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn recovery_candidate_preserves_source_and_replays_valid_prefix() {
        use std::io::Write;
        let dir = fresh_temp_dir("candidate-recovery");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        let first = index
            .enqueue_durable(
                &dir,
                "index",
                crate::anomaly_loop::AnomalyQueueItem {
                    id: 2,
                    vector: vec![0.0, 1.0, 0.0, 0.0],
                    metadata: "synthetic-first".into(),
                    queue_id: None,
                },
            )
            .unwrap();
        index
            .consolidate_queued(&dir, "index", first.queue_id.as_deref().unwrap())
            .unwrap();
        index
            .enqueue_durable(
                &dir,
                "index",
                crate::anomaly_loop::AnomalyQueueItem {
                    id: 3,
                    vector: vec![0.0, 0.0, 1.0, 0.0],
                    metadata: "synthetic-pending".into(),
                    queue_id: None,
                },
            )
            .unwrap();
        drop(index);
        let wal = dir.join("index.hnsw.wal");
        std::fs::OpenOptions::new()
            .append(true)
            .open(&wal)
            .unwrap()
            .write_all(b"v3:partial")
            .unwrap();
        let original = std::fs::read(&wal).unwrap();
        assert!(
            SparkleVectorIndex::prepare_wal_recovery_candidate(
                &dir,
                "index",
                4,
                lease.clone(),
                false
            )
            .is_err()
        );
        let report = SparkleVectorIndex::prepare_wal_recovery_candidate(
            &dir,
            "index",
            4,
            lease.clone(),
            true,
        )
        .unwrap();
        assert!(report.possible_loss);
        assert_eq!(report.excluded_tail_bytes, b"v3:partial".len());
        assert_eq!(report.pending_items, 1);
        assert_eq!(std::fs::read(&wal).unwrap(), original);
        assert!(SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).is_err());
        let candidate = dir.join(&report.candidate_directory);
        let restored =
            SparkleVectorIndex::load_active_with_wal(&candidate, "index", 4, true).unwrap();
        assert_eq!(restored.len(), 2);
        assert_eq!(
            restored.pending_queue().unwrap()[0].metadata,
            "synthetic-pending"
        );
        assert!(candidate.join("recovery-candidate.json").is_file());
        drop(restored);
        let verify = || {
            SparkleVectorIndex::verify_wal_recovery_candidate(
                &dir,
                "index",
                4,
                &report.candidate_directory,
                lease.clone(),
            )
        };
        assert!(verify().is_ok());
        let graph = candidate.join("index.hnsw.graph");
        let graph_original = std::fs::read(&graph).unwrap();
        std::fs::write(&graph, b"corrupt graph").unwrap();
        assert!(verify().is_err());
        std::fs::write(&graph, graph_original).unwrap();
        let manifest = candidate.join("recovery-candidate.json");
        let manifest_original = std::fs::read(&manifest).unwrap();
        std::fs::write(&manifest, b"{}").unwrap();
        assert!(verify().is_err());
        std::fs::write(&manifest, manifest_original).unwrap();
        assert!(verify().is_ok());
        let extra = candidate.join("unexpected");
        std::fs::write(&extra, b"extra").unwrap();
        assert!(verify().is_err());
        std::fs::remove_file(extra).unwrap();
        assert_eq!(std::fs::read(&wal).unwrap(), original);
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn autosave_only_checkpoints_applied_changes_and_preserves_pending_queue() {
        let dir = fresh_temp_dir("autosave");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        assert_eq!(
            index.autosave_if_needed(&dir, "index").unwrap(),
            AutosaveOutcome::NoChanges
        );
        let item = index
            .enqueue_durable(
                &dir,
                "index",
                crate::anomaly_loop::AnomalyQueueItem {
                    id: 2,
                    vector: vec![0.0, 1.0, 0.0, 0.0],
                    metadata: "synthetic".into(),
                    queue_id: None,
                },
            )
            .unwrap();
        let original_wal = std::fs::read(dir.join("index.hnsw.wal")).unwrap();
        assert_eq!(
            index.autosave_if_needed(&dir, "index").unwrap(),
            AutosaveOutcome::PendingQueue
        );
        assert_eq!(
            std::fs::read(dir.join("index.hnsw.wal")).unwrap(),
            original_wal
        );
        drop(index);
        let index = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
        assert_eq!(index.pending_queue().unwrap().len(), 1);
        index
            .consolidate_queued(&dir, "index", item.queue_id.as_deref().unwrap())
            .unwrap();
        assert_eq!(
            index.autosave_if_needed(&dir, "index").unwrap(),
            AutosaveOutcome::CheckpointPublished
        );
        assert_eq!(
            index.autosave_if_needed(&dir, "index").unwrap(),
            AutosaveOutcome::NoChanges
        );
        assert!(!dir.join("index.commit.00000000000000000002").exists());
        drop(index);
        let reopened = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
        assert_eq!(reopened.len(), 2);
        assert!(reopened.pending_queue().unwrap().is_empty());
        drop(reopened);
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn retention_reviews_only_old_empty_wal_generations_and_keeps_two_newest() {
        let dir = fresh_temp_dir("retention");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        for _ in 0..3 {
            index.checkpoint(&dir, "index").unwrap();
        }
        drop(index);
        let review =
            |n| SparkleVectorIndex::review_generation_retention(&dir, "index", 4, n, lease.clone());
        assert!(review(2).is_err());
        assert!(review(3).is_err());
        let report = review(1).unwrap();
        let target = dir.join(&report.directory);
        let wal = target.join("index.hnsw.wal");
        std::fs::write(&wal, b"unsafe").unwrap();
        assert!(review(1).is_err());
        std::fs::write(&wal, b"").unwrap();
        let stray = dir.join("index.recovery_stage.0000000000000000");
        std::fs::create_dir(&stray).unwrap();
        assert!(review(1).is_err());
        std::fs::remove_dir(stray).unwrap();
        assert!(
            SparkleVectorIndex::delete_reviewed_generation(
                &dir,
                "index",
                4,
                1,
                "wrong",
                lease.clone(),
                true
            )
            .is_err()
        );
        assert!(
            SparkleVectorIndex::delete_reviewed_generation(
                &dir,
                "index",
                4,
                1,
                &report.fingerprint_sha256,
                lease.clone(),
                false
            )
            .is_err()
        );
        SparkleVectorIndex::delete_reviewed_generation(
            &dir,
            "index",
            4,
            1,
            &report.fingerprint_sha256,
            lease.clone(),
            true,
        )
        .unwrap();
        assert!(!target.exists());
        assert!(!dir.join("index.commit.00000000000000000001").exists());
        assert!(dir.join("index.commit.00000000000000000002").exists());
        assert!(dir.join("index.commit.00000000000000000003").exists());
        let restored = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
        assert_eq!(restored.len(), 1);
        drop(restored);
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn interrupted_generation_retention_never_deletes_or_selects_active_data() {
        for stage in [
            "marker_removed",
            ".hnsw.graph",
            ".hnsw.data",
            ".checksum",
            ".hnsw.wal",
        ] {
            let dir = fresh_temp_dir("retention-interrupt");
            let lease = lease_for(&dir);
            let index = SparkleVectorIndex::new(4, 10)
                .with_storage(&dir, lease.clone())
                .unwrap();
            index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
            index.file_dump(&dir, "index").unwrap();
            for _ in 0..3 {
                index.checkpoint(&dir, "index").unwrap();
            }
            drop(index);
            let report =
                SparkleVectorIndex::review_generation_retention(&dir, "index", 4, 1, lease.clone())
                    .unwrap();
            let result = SparkleVectorIndex::delete_generation_with_hook(
                &dir,
                "index",
                4,
                1,
                &report.fingerprint_sha256,
                lease.clone(),
                true,
                |at| {
                    if at == stage {
                        Err("injected".into())
                    } else {
                        Ok(())
                    }
                },
            );
            assert!(result.is_err());
            assert!(dir.join("index.commit.00000000000000000003").exists());
            assert!(
                SparkleVectorIndex::review_generation_retention(&dir, "index", 4, 1, lease.clone())
                    .is_err()
            );
            let reopened = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
            assert_eq!(reopened.len(), 1);
            drop(reopened);
            drop(lease);
            std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
        }
    }

    #[test]
    fn recovery_activation_crash_child() {
        let Some(path) = std::env::var_os("BLYSK_TEST_RECOVERY_DB") else {
            return;
        };
        let path = PathBuf::from(path);
        let candidate = std::env::var("BLYSK_TEST_RECOVERY_CANDIDATE").unwrap();
        let original = std::env::var("BLYSK_TEST_RECOVERY_ORIGINAL_HASH").unwrap();
        let copy = std::env::var("BLYSK_TEST_RECOVERY_COPY_HASH").unwrap();
        let stop = std::env::var("BLYSK_TEST_RECOVERY_STAGE").unwrap();
        let lease = lease_for(&path);
        let _ = SparkleVectorIndex::activate_candidate_with_hook(
            &path,
            "index",
            4,
            &candidate,
            &original,
            &copy,
            lease,
            true,
            |step| {
                if step == stop {
                    std::process::exit(42);
                }
                Ok(())
            },
        );
        panic!("expected process interruption");
    }

    #[test]
    fn recovery_activation_survives_abrupt_process_exit() {
        use std::io::Write;
        for stage in ["marker_ready", "generation_renamed", "marker_published"] {
            let dir = fresh_temp_dir("activate-process");
            let lease = lease_for(&dir);
            let index = SparkleVectorIndex::new(4, 10)
                .with_storage(&dir, lease.clone())
                .unwrap();
            index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
            index.file_dump(&dir, "index").unwrap();
            index
                .enqueue_durable(
                    &dir,
                    "index",
                    crate::anomaly_loop::AnomalyQueueItem {
                        id: 2,
                        vector: vec![0.0, 1.0, 0.0, 0.0],
                        metadata: "synthetic".into(),
                        queue_id: None,
                    },
                )
                .unwrap();
            drop(index);
            let wal = dir.join("index.hnsw.wal");
            std::fs::OpenOptions::new()
                .append(true)
                .open(&wal)
                .unwrap()
                .write_all(b"partial")
                .unwrap();
            let original = std::fs::read(&wal).unwrap();
            let report = SparkleVectorIndex::prepare_wal_recovery_candidate(
                &dir,
                "index",
                4,
                lease.clone(),
                true,
            )
            .unwrap();
            drop(lease);
            let status = std::process::Command::new(std::env::current_exe().unwrap())
                .args([
                    "--exact",
                    "vector_index::tests::recovery_activation_crash_child",
                    "--nocapture",
                ])
                .env("BLYSK_TEST_RECOVERY_DB", &dir)
                .env("BLYSK_TEST_RECOVERY_CANDIDATE", &report.candidate_directory)
                .env(
                    "BLYSK_TEST_RECOVERY_ORIGINAL_HASH",
                    &report.original_wal_sha256,
                )
                .env(
                    "BLYSK_TEST_RECOVERY_COPY_HASH",
                    &report.candidate_wal_sha256,
                )
                .env("BLYSK_TEST_RECOVERY_STAGE", stage)
                .status()
                .unwrap();
            assert_eq!(status.code(), Some(42));
            assert_eq!(std::fs::read(&wal).unwrap(), original);
            let lease = lease_for(&dir);
            let reopened = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone());
            if stage == "marker_published" {
                assert_eq!(reopened.unwrap().pending_queue().unwrap().len(), 1);
            } else {
                assert!(reopened.is_err());
            }
            drop(lease);
            std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
        }
    }

    #[test]
    fn recovery_activation_preserves_source_through_each_publication_stage() {
        use std::io::Write;
        for stage in [
            "created",
            "copied",
            "validated",
            "marker_ready",
            "generation_renamed",
            "marker_published",
            "success",
        ] {
            let dir = fresh_temp_dir(&format!("activate-{stage}"));
            let lease = lease_for(&dir);
            let index = SparkleVectorIndex::new(4, 10)
                .with_storage(&dir, lease.clone())
                .unwrap();
            index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
            index.file_dump(&dir, "index").unwrap();
            index
                .enqueue_durable(
                    &dir,
                    "index",
                    crate::anomaly_loop::AnomalyQueueItem {
                        id: 2,
                        vector: vec![0.0, 1.0, 0.0, 0.0],
                        metadata: "synthetic".into(),
                        queue_id: None,
                    },
                )
                .unwrap();
            drop(index);
            let wal = dir.join("index.hnsw.wal");
            std::fs::OpenOptions::new()
                .append(true)
                .open(&wal)
                .unwrap()
                .write_all(b"partial")
                .unwrap();
            let original = std::fs::read(&wal).unwrap();
            let report = SparkleVectorIndex::prepare_wal_recovery_candidate(
                &dir,
                "index",
                4,
                lease.clone(),
                true,
            )
            .unwrap();
            assert!(
                SparkleVectorIndex::activate_wal_recovery_candidate(
                    &dir,
                    "index",
                    4,
                    &report.candidate_directory,
                    &report.original_wal_sha256,
                    &report.candidate_wal_sha256,
                    lease.clone(),
                    false
                )
                .is_err()
            );
            assert!(
                SparkleVectorIndex::activate_wal_recovery_candidate(
                    &dir,
                    "index",
                    4,
                    &report.candidate_directory,
                    "wrong",
                    &report.candidate_wal_sha256,
                    lease.clone(),
                    true
                )
                .is_err()
            );
            let result = SparkleVectorIndex::activate_candidate_with_hook(
                &dir,
                "index",
                4,
                &report.candidate_directory,
                &report.original_wal_sha256,
                &report.candidate_wal_sha256,
                lease.clone(),
                true,
                |at| {
                    if at == stage {
                        Err("injected".into())
                    } else {
                        Ok(())
                    }
                },
            );
            assert_eq!(result.is_ok(), stage == "success");
            assert_eq!(std::fs::read(&wal).unwrap(), original);
            assert!(
                dir.join(&report.candidate_directory)
                    .join("recovery-candidate.json")
                    .is_file()
            );
            let reopened = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone());
            if stage == "marker_published" || stage == "success" {
                let restored = reopened.unwrap();
                assert_eq!(restored.len(), 1);
                assert_eq!(restored.pending_queue().unwrap().len(), 1);
                drop(restored);
            } else {
                assert!(reopened.is_err());
            }
            drop(lease);
            std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
        }
    }

    #[test]
    fn selective_candidate_deletion_requires_review_and_preserves_source() {
        use std::io::Write;
        let dir = fresh_temp_dir("selective-delete");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        drop(index);
        let wal = dir.join("index.hnsw.wal");
        std::fs::write(&wal, b"partial").unwrap();
        let report = SparkleVectorIndex::prepare_wal_recovery_candidate(
            &dir,
            "index",
            4,
            lease.clone(),
            true,
        )
        .unwrap();
        let target = dir.join(&report.candidate_directory);
        let attempt = |hash: &str, confirm| {
            SparkleVectorIndex::delete_verified_recovery_candidate(
                &dir,
                "index",
                4,
                &report.candidate_directory,
                hash,
                &report.candidate_wal_sha256,
                lease.clone(),
                confirm,
            )
        };
        assert!(attempt(&report.original_wal_sha256, false).is_err());
        assert!(attempt("wrong", true).is_err());
        let extra = target.join("extra");
        std::fs::File::create(&extra)
            .unwrap()
            .write_all(b"data")
            .unwrap();
        assert!(attempt(&report.original_wal_sha256, true).is_err());
        std::fs::remove_file(extra).unwrap();
        assert!(attempt(&report.original_wal_sha256, true).is_ok());
        assert!(!target.exists());
        assert_eq!(std::fs::read(wal).unwrap(), b"partial");
        assert!(dir.join("index.hnsw.graph").is_file());
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn interrupted_candidate_deletion_preserves_source_and_never_marks_copy_ready() {
        for stage in [
            "manifest_removed",
            ".hnsw.graph",
            ".hnsw.data",
            ".checksum",
            ".hnsw.wal",
        ] {
            let dir = fresh_temp_dir("delete-interrupt");
            let lease = lease_for(&dir);
            let index = SparkleVectorIndex::new(4, 10)
                .with_storage(&dir, lease.clone())
                .unwrap();
            index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
            index.file_dump(&dir, "index").unwrap();
            drop(index);
            let wal = dir.join("index.hnsw.wal");
            std::fs::write(&wal, b"partial").unwrap();
            let report = SparkleVectorIndex::prepare_wal_recovery_candidate(
                &dir,
                "index",
                4,
                lease.clone(),
                true,
            )
            .unwrap();
            let result = SparkleVectorIndex::delete_candidate_with_hook(
                &dir,
                "index",
                4,
                &report.candidate_directory,
                &report.original_wal_sha256,
                &report.candidate_wal_sha256,
                lease.clone(),
                true,
                |at| {
                    if at == stage {
                        Err("injected".into())
                    } else {
                        Ok(())
                    }
                },
            );
            assert!(result.is_err());
            assert_eq!(std::fs::read(&wal).unwrap(), b"partial");
            assert!(dir.join("index.hnsw.graph").is_file());
            assert!(
                !dir.join(&report.candidate_directory)
                    .join("recovery-candidate.json")
                    .exists()
            );
            assert!(
                SparkleVectorIndex::verify_wal_recovery_candidate(
                    &dir,
                    "index",
                    4,
                    &report.candidate_directory,
                    lease.clone()
                )
                .is_err()
            );
            drop(lease);
            std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
        }
    }

    #[test]
    fn recovery_candidate_refuses_complete_or_corrupt_full_records() {
        let dir = fresh_temp_dir("candidate-refusal");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        index
            .insert_with_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
            .unwrap();
        drop(index);
        let wal = dir.join("index.hnsw.wal");
        let before = std::fs::read(&wal).unwrap();
        assert!(
            SparkleVectorIndex::prepare_wal_recovery_candidate(
                &dir,
                "index",
                4,
                lease.clone(),
                true
            )
            .is_err()
        );
        std::fs::write(&wal, b"bad:record\nv3:partial").unwrap();
        let corrupt = std::fs::read(&wal).unwrap();
        assert!(
            SparkleVectorIndex::prepare_wal_recovery_candidate(
                &dir,
                "index",
                4,
                lease.clone(),
                true
            )
            .is_err()
        );
        assert_eq!(std::fs::read(&wal).unwrap(), corrupt);
        assert_ne!(before, corrupt);
        assert!(!std::fs::read_dir(&dir).unwrap().any(|entry| {
            entry
                .unwrap()
                .file_name()
                .to_string_lossy()
                .contains("recovery_candidate")
        }));
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn recovery_candidate_uses_published_generation_not_legacy_snapshot() {
        use std::io::Write;
        let dir = fresh_temp_dir("candidate-generation");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        index
            .insert_with_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
            .unwrap();
        index.checkpoint(&dir, "index").unwrap();
        index
            .enqueue_durable(
                &dir,
                "index",
                crate::anomaly_loop::AnomalyQueueItem {
                    id: 3,
                    vector: vec![0.0, 0.0, 1.0, 0.0],
                    metadata: "synthetic-new".into(),
                    queue_id: None,
                },
            )
            .unwrap();
        let wal = index.active_dir(&dir).unwrap().join("index.hnsw.wal");
        drop(index);
        std::fs::OpenOptions::new()
            .append(true)
            .open(&wal)
            .unwrap()
            .write_all(b"partial")
            .unwrap();
        let before = std::fs::read(&wal).unwrap();
        let report = SparkleVectorIndex::prepare_wal_recovery_candidate(
            &dir,
            "index",
            4,
            lease.clone(),
            true,
        )
        .unwrap();
        let candidate = SparkleVectorIndex::load_active_with_wal(
            &dir.join(report.candidate_directory),
            "index",
            4,
            true,
        )
        .unwrap();
        assert_eq!(candidate.len(), 2);
        assert_eq!(candidate.pending_queue().unwrap()[0].id, 3);
        assert_eq!(std::fs::read(wal).unwrap(), before);
        drop(candidate);
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn interrupted_candidate_creation_never_changes_source_or_marks_incomplete_copy_ready() {
        use std::io::Write;
        let dir = fresh_temp_dir("candidate-interruption");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        index
            .insert_with_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
            .unwrap();
        drop(index);
        let wal = dir.join("index.hnsw.wal");
        std::fs::OpenOptions::new()
            .append(true)
            .open(&wal)
            .unwrap()
            .write_all(b"v2:partial")
            .unwrap();
        let original_wal = std::fs::read(&wal).unwrap();
        let original_graph = std::fs::read(dir.join("index.hnsw.graph")).unwrap();
        for stop in [
            "created",
            "baseline_copied",
            "wal_copied",
            "validated",
            "manifest_ready",
        ] {
            let result = SparkleVectorIndex::prepare_wal_recovery_candidate_with_hook(
                &dir,
                "index",
                4,
                lease.clone(),
                true,
                |stage| {
                    if stage == stop {
                        Err("simulated failure".into())
                    } else {
                        Ok(())
                    }
                },
            );
            assert!(result.is_err(), "{stop}");
            assert_eq!(std::fs::read(&wal).unwrap(), original_wal);
            assert_eq!(
                std::fs::read(dir.join("index.hnsw.graph")).unwrap(),
                original_graph
            );
            assert!(SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).is_err());
        }
        let candidates: Vec<_> = std::fs::read_dir(&dir)
            .unwrap()
            .map(|entry| entry.unwrap().path())
            .filter(|path| {
                path.file_name()
                    .unwrap()
                    .to_string_lossy()
                    .starts_with("index.recovery_candidate.")
            })
            .collect();
        assert_eq!(candidates.len(), 5);
        assert!(
            candidates
                .iter()
                .all(|path| !path.join("recovery-candidate.json").exists())
        );
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn invalid_and_over_capacity_vectors_do_not_enter_wal() {
        let dir = fresh_temp_dir("invalid-wal-insert");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 2)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(100, &[0.0, 0.0, 1.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        assert!(index.insert_with_wal(&dir, "index", 1, &[1.0]).is_err());
        assert!(
            index
                .insert_with_wal(&dir, "index", 1, &[f32::NAN; 4])
                .is_err()
        );
        assert!(!dir.join("index.hnsw.wal").exists());
        index
            .insert_with_wal(&dir, "index", 1, &[1.0, 0.0, 0.0, 0.0])
            .unwrap();
        let original = std::fs::read(dir.join("index.hnsw.wal")).unwrap();
        assert!(
            index
                .insert_with_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
                .is_err()
        );
        assert_eq!(std::fs::read(dir.join("index.hnsw.wal")).unwrap(), original);
        drop(index);
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn checkpoint_refuses_nonempty_wal_without_changing_snapshot() {
        let dir = fresh_temp_dir("checkpoint-wal");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        let graph = std::fs::read(dir.join("index.hnsw.graph")).unwrap();
        let data = std::fs::read(dir.join("index.hnsw.data")).unwrap();
        index
            .append_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
            .unwrap();
        let wal = std::fs::read(dir.join("index.hnsw.wal")).unwrap();
        assert!(index.file_dump(&dir, "index").is_err());
        assert_eq!(std::fs::read(dir.join("index.hnsw.graph")).unwrap(), graph);
        assert_eq!(std::fs::read(dir.join("index.hnsw.data")).unwrap(), data);
        assert_eq!(std::fs::read(dir.join("index.hnsw.wal")).unwrap(), wal);
        drop(index);
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn generation_checkpoint_recovers_without_duplicate_wal_entries_at_each_stage() {
        for stop in [
            "created_dir",
            "snapshot",
            "prepared",
            "marker_ready",
            "marker_moved",
            "published",
        ] {
            let dir = fresh_temp_dir("generation-interrupt");
            let lease = lease_for(&dir);
            let index = SparkleVectorIndex::new(4, 10)
                .with_storage(&dir, lease.clone())
                .unwrap();
            index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
            index.file_dump(&dir, "index").unwrap();
            index
                .insert_with_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
                .unwrap();
            assert!(
                index
                    .checkpoint_with_hook(&dir, "index", |stage| {
                        if stage == stop {
                            Err("simulated interruption".into())
                        } else {
                            Ok(())
                        }
                    })
                    .is_err()
            );
            if stop == "marker_moved" || stop == "published" {
                assert!(
                    index
                        .insert_with_wal(&dir, "index", 4, &[0.0, 0.0, 0.0, 1.0])
                        .is_err()
                );
            }
            drop(index);
            let loaded = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
            assert_eq!(loaded.len(), 2, "{stop}");
            assert_eq!(loaded.search(&[0.0, 1.0, 0.0, 0.0], 1)[0].d_id, 2);
            loaded
                .insert_with_wal(&dir, "index", 3, &[0.0, 0.0, 1.0, 0.0])
                .unwrap();
            loaded.checkpoint(&dir, "index").unwrap();
            drop(loaded);
            let reopened = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
            assert_eq!(reopened.len(), 3, "{stop}");
            drop(reopened);
            drop(lease);
            std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
        }
    }

    #[test]
    fn generation_checkpoint_rejects_unapplied_wal() {
        let dir = fresh_temp_dir("generation-unapplied");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        index
            .append_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
            .unwrap();
        assert!(index.checkpoint(&dir, "index").is_err());
        drop(index);
        let recovered = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
        assert_eq!(recovered.len(), 2);
        recovered.checkpoint(&dir, "index").unwrap();
        drop(recovered);
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn generation_checkpoint_survives_abrupt_process_exit() {
        for stage in [
            "created_dir",
            "snapshot",
            "prepared",
            "marker_ready",
            "marker_moved",
            "published",
        ] {
            let dir = fresh_temp_dir("generation-process-exit");
            let lease = lease_for(&dir);
            let index = SparkleVectorIndex::new(4, 10)
                .with_storage(&dir, lease.clone())
                .unwrap();
            index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
            index.file_dump(&dir, "index").unwrap();
            index
                .insert_with_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
                .unwrap();
            drop(index);
            drop(lease);
            let status = std::process::Command::new(std::env::current_exe().unwrap())
                .args(["--exact", "vector_index::tests::crash_simulation_child"])
                .env("BLYSK_TEST_CRASH_DB", &dir)
                .env("BLYSK_TEST_CRASH_ACTION", format!("checkpoint_{stage}"))
                .status()
                .unwrap();
            assert_eq!(status.code(), Some(42), "{stage}");
            let lease = lease_for(&dir);
            let recovered = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
            assert_eq!(recovered.len(), 2, "{stage}");
            assert_eq!(recovered.search(&[0.0, 1.0, 0.0, 0.0], 1)[0].d_id, 2);
            drop(recovered);
            drop(lease);
            std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
        }
    }

    #[test]
    fn corrupt_latest_generation_is_not_silently_rolled_back() {
        let dir = fresh_temp_dir("generation-corrupt");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        index
            .insert_with_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
            .unwrap();
        index.checkpoint(&dir, "index").unwrap();
        drop(index);
        std::fs::write(dir.join("index.commit.00000000000000000001"), "../outside").unwrap();
        assert!(SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).is_err());
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn missing_latest_marker_with_newer_wal_refuses_silent_rollback() {
        let dir = fresh_temp_dir("missing-marker-new-wal");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        index
            .insert_with_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
            .unwrap();
        index.checkpoint(&dir, "index").unwrap();
        index
            .insert_with_wal(&dir, "index", 3, &[0.0, 0.0, 1.0, 0.0])
            .unwrap();
        index.checkpoint(&dir, "index").unwrap();
        index
            .insert_with_wal(&dir, "index", 4, &[0.0, 0.0, 0.0, 1.0])
            .unwrap();
        let newest = index.active_dir(&dir).unwrap();
        let wal = newest.join("index.hnsw.wal");
        let before = std::fs::read(&wal).unwrap();
        drop(index);
        std::fs::remove_file(dir.join("index.commit.00000000000000000002")).unwrap();
        let error = match SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()) {
            Ok(_) => panic!("silent rollback accepted"),
            Err(error) => error,
        };
        assert!(error.contains("WAL bez znacznika"));
        assert_eq!(std::fs::read(&wal).unwrap(), before);
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn missing_only_marker_with_nonempty_wal_does_not_revert_to_legacy() {
        let dir = fresh_temp_dir("missing-only-marker");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        index
            .insert_with_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
            .unwrap();
        index.checkpoint(&dir, "index").unwrap();
        index
            .insert_with_wal(&dir, "index", 3, &[0.0, 0.0, 1.0, 0.0])
            .unwrap();
        let wal = index.active_dir(&dir).unwrap().join("index.hnsw.wal");
        let before = std::fs::read(&wal).unwrap();
        drop(index);
        std::fs::remove_file(dir.join("index.commit.00000000000000000001")).unwrap();
        assert!(SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).is_err());
        assert_eq!(std::fs::read(&wal).unwrap(), before);
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn uncertain_wal_write_disables_further_writes_and_checkpoints() {
        let dir = fresh_temp_dir("wal-uncertain");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        let error =
            index.append_wal_locked_with_hook(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0], || {
                Err(std::io::Error::other("simulated flush failure"))
            });
        assert!(error.is_err());
        let wal = std::fs::read(dir.join("index.hnsw.wal")).unwrap();
        assert!(
            index
                .insert_with_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
                .is_err()
        );
        assert!(index.file_dump(&dir, "index").is_err());
        assert_eq!(std::fs::read(dir.join("index.hnsw.wal")).unwrap(), wal);
        drop(index);
        let restored = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
        assert_eq!(restored.len(), 2);
        drop(restored);
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn full_wal_refuses_new_records_without_truncation() {
        let dir = fresh_temp_dir("wal-capacity");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        let wal_path = dir.join("index.hnsw.wal");
        let file = std::fs::File::create(&wal_path).unwrap();
        file.set_len(MAX_WAL_BYTES).unwrap();
        drop(file);
        assert!(
            index
                .insert_with_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
                .is_err()
        );
        assert_eq!(std::fs::metadata(&wal_path).unwrap().len(), MAX_WAL_BYTES);
        assert_eq!(index.len(), 1);
        drop(index);
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn checkpoint_capacity_scan_preserves_files_and_fails_closed() {
        let dir = fresh_temp_dir("storage-limits");
        std::fs::create_dir(dir.join("history")).unwrap();
        std::fs::write(dir.join("history").join("data"), b"synthetic").unwrap();
        assert!(check_checkpoint_storage(&dir, 9, 2).is_ok());
        assert!(check_checkpoint_storage(&dir, 8, 2).is_err());
        assert!(check_checkpoint_storage(&dir, 9, 1).is_err());
        assert_eq!(
            std::fs::read(dir.join("history").join("data")).unwrap(),
            b"synthetic"
        );
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn checkpoint_capacity_failures_preserve_journal_before_publication() {
        let dir = fresh_temp_dir("storage-checkpoint-limit");
        let lease = lease_for(&dir);
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, "index").unwrap();
        index
            .insert_with_wal(&dir, "index", 2, &[0.0, 1.0, 0.0, 0.0])
            .unwrap();
        let wal = dir.join("index.hnsw.wal");
        let before = std::fs::read(&wal).unwrap();
        let baseline_size: u64 = std::fs::read_dir(&dir)
            .unwrap()
            .map(|entry| entry.unwrap().metadata().unwrap().len())
            .sum();
        assert!(
            index
                .checkpoint_with_limits(&dir, "index", 1, 10_000, |_| Ok(()))
                .is_err()
        );
        assert!(
            index
                .checkpoint_with_limits(&dir, "index", baseline_size + 1, 10_000, |_| Ok(()))
                .is_err()
        );
        assert_eq!(std::fs::read(&wal).unwrap(), before);
        assert!(!dir.join("index.commit.00000000000000000001").exists());
        drop(index);
        let recovered = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
        assert_eq!(recovered.len(), 2);
        drop(recovered);
        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }

    #[test]
    fn interrupted_replacement_preserves_original_generation() {
        for stop in [
            "backup",
            "remove_graph",
            "remove_data",
            "remove_checksum",
            "publish_graph",
            "publish_data",
            "publish_checksum",
        ] {
            let dir = fresh_temp_dir("interrupt-checkpoint");
            let lease = lease_for(&dir);
            let index = SparkleVectorIndex::new(4, 10)
                .with_storage(&dir, lease.clone())
                .unwrap();
            index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
            index.file_dump(&dir, "index").unwrap();
            let names = ["index.hnsw.graph", "index.hnsw.data", "index.checksum"];
            let originals: Vec<_> = names
                .iter()
                .map(|name| std::fs::read(dir.join(name)).unwrap())
                .collect();
            index.insert(2, &[0.0, 1.0, 0.0, 0.0]).unwrap();
            let result = index.file_dump_with_hook(&dir, "index", |step| {
                if step == stop {
                    Err("simulated interruption".into())
                } else {
                    Ok(())
                }
            });
            assert!(result.is_err(), "{stop}");
            let backup = std::fs::read_dir(&dir)
                .unwrap()
                .map(|entry| entry.unwrap().path())
                .find(|path| {
                    path.file_name()
                        .unwrap()
                        .to_string_lossy()
                        .starts_with("index.backup_")
                })
                .unwrap();
            for (name, original) in names.iter().zip(originals) {
                assert_eq!(
                    std::fs::read(backup.join(name)).unwrap(),
                    original,
                    "{stop}: {name}"
                );
            }
            drop(index);
            drop(lease);
            std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
        }
    }

    #[test]
    fn concurrent_insertions_respect_capacity() {
        let index = std::sync::Arc::new(SparkleVectorIndex::new(4, 1));
        let threads: Vec<_> = (0..8)
            .map(|id| {
                let index = index.clone();
                std::thread::spawn(move || index.insert(id, &[1.0, 0.0, 0.0, 0.0]).is_ok())
            })
            .collect();
        assert_eq!(
            threads
                .into_iter()
                .map(|thread| thread.join().unwrap())
                .filter(|ok| *ok)
                .count(),
            1
        );
        assert_eq!(index.len(), 1);
    }

    #[test]
    fn corrupted_primary_does_not_silently_fall_back_to_older_generation() {
        let dir = fresh_temp_dir("stale-fallback");
        let lease = lease_for(&dir);
        let name = "index";
        let index = SparkleVectorIndex::new(4, 10)
            .with_storage(&dir, lease.clone())
            .unwrap();
        index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, name).unwrap();
        index.insert(2, &[0.0, 1.0, 0.0, 0.0]).unwrap();
        index.file_dump(&dir, name).unwrap();
        assert!(std::fs::read_dir(&dir).unwrap().any(|entry| {
            entry
                .unwrap()
                .file_name()
                .to_string_lossy()
                .starts_with("index.backup_")
        }));
        std::fs::write(dir.join("index.checksum"), b"corrupt").unwrap();
        drop(index);
        assert!(SparkleVectorIndex::load_hnsw(&dir, name, 4, lease.clone()).is_err());

        drop(lease);
        std::fs::remove_dir_all(dir.parent().unwrap()).unwrap();
    }
}
