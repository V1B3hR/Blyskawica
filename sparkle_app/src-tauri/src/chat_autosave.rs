//! Local append-only chat history. Callers serialize access with the index lease.
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{
    io::{Read, Write},
    path::Path,
};

const MAX_BYTES: u64 = 16 * 1024 * 1024;
const MAX_RECORD_BYTES: usize = 256 * 1024;
const MAX_RECORDS: usize = 10_000;

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct ChatRecord {
    pub channel: String,
    pub sender: String,
    pub text: String,
    pub iso_time: String,
}

fn validate(record: &ChatRecord) -> Result<(), String> {
    if !matches!(record.channel.as_str(), "main" | "guest")
        || record.sender.is_empty()
        || record.sender.len() > 128
        || record.text.len() > 64 * 1024
        || record.iso_time.len() > 64
        || record.iso_time.is_empty()
    {
        return Err("Nieprawidłowa lub zbyt duża wiadomość historii".into());
    }
    Ok(())
}

fn plain(meta: &std::fs::Metadata, directory: bool) -> bool {
    if meta.file_type().is_symlink()
        || (directory && !meta.is_dir())
        || (!directory && !meta.is_file())
    {
        return false;
    }
    #[cfg(windows)]
    {
        use std::os::windows::fs::MetadataExt;
        if meta.file_attributes() & 0x400 != 0 {
            return false;
        }
    }
    true
}

fn check_directory(dir: &Path, create: bool) -> Result<bool, String> {
    match std::fs::symlink_metadata(dir) {
        Ok(meta) if plain(&meta, true) => Ok(true),
        Ok(_) => Err("Nieprawidłowy katalog pamięci rozmowy".into()),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound && !create => Ok(false),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => {
            #[cfg(unix)]
            {
                use std::os::unix::fs::DirBuilderExt;
                std::fs::DirBuilder::new()
                    .mode(0o700)
                    .create(dir)
                    .map_err(|e| e.to_string())?;
            }
            #[cfg(not(unix))]
            std::fs::create_dir(dir).map_err(|e| e.to_string())?;
            sync_parent(dir.parent().ok_or("Brak katalogu nadrzędnego")?)?;
            Ok(true)
        }
        Err(e) => Err(format!("Nie można sprawdzić katalogu pamięci: {e}")),
    }
}

#[cfg(unix)]
fn sync_parent(dir: &Path) -> Result<(), String> {
    std::fs::File::open(dir)
        .and_then(|f| f.sync_all())
        .map_err(|e| e.to_string())
}
#[cfg(not(unix))]
fn sync_parent(_: &Path) -> Result<(), String> {
    Ok(())
}

pub fn load(dir: &Path) -> Result<Vec<ChatRecord>, String> {
    if !check_directory(dir, false)? {
        return Ok(Vec::new());
    }
    let path = dir.join("chat-autosave.jsonl");
    let metadata = match std::fs::symlink_metadata(&path) {
        Ok(meta) if plain(&meta, false) => meta,
        Ok(_) => return Err("Nieprawidłowy plik historii rozmów".into()),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok(Vec::new()),
        Err(e) => return Err(format!("Nie można sprawdzić historii: {e}")),
    };
    if metadata.len() > MAX_BYTES {
        return Err("Historia rozmów przekracza limit 16 MiB".into());
    }
    let mut bytes = Vec::new();
    std::fs::File::open(path)
        .map_err(|e| e.to_string())?
        .take(MAX_BYTES + 1)
        .read_to_end(&mut bytes)
        .map_err(|e| e.to_string())?;
    if bytes.len() as u64 > MAX_BYTES || (!bytes.is_empty() && !bytes.ends_with(b"\n")) {
        return Err("Historia jest zbyt duża lub ma niekompletną końcówkę; plik zachowano".into());
    }
    let mut records = Vec::new();
    for entry in bytes.split_inclusive(|b| *b == b'\n') {
        let line = &entry[..entry.len() - 1];
        if line.is_empty() {
            return Err("Pusty rekord historii; plik zachowano".into());
        }
        if line.len() > MAX_RECORD_BYTES || records.len() >= MAX_RECORDS {
            return Err("Przekroczono limit historii".into());
        }
        let separator = line
            .iter()
            .position(|b| *b == b' ')
            .ok_or("Nieprawidłowy rekord historii")?;
        let (hash, remaining) = line.split_at(separator);
        let json = &remaining[1..];
        if hash != format!("{:x}", Sha256::digest(json)).as_bytes() {
            return Err("Nieprawidłowa suma historii; plik zachowano".into());
        }
        let record: ChatRecord =
            serde_json::from_slice(json).map_err(|_| "Nieprawidłowy rekord historii")?;
        validate(&record)?;
        records.push(record);
    }
    Ok(records)
}

pub fn append(dir: &Path, record: &ChatRecord) -> Result<(), String> {
    validate(record)?;
    check_directory(dir, true)?;
    let existing = load(dir)?;
    if existing.len() >= MAX_RECORDS {
        return Err("Osiągnięto limit liczby wiadomości".into());
    }
    let json = serde_json::to_vec(record).map_err(|_| "Nie można zakodować wiadomości")?;
    let mut line = format!("{:x} ", Sha256::digest(&json)).into_bytes();
    line.extend_from_slice(&json);
    line.push(b'\n');
    if line.len() > MAX_RECORD_BYTES {
        return Err("Wiadomość przekracza limit".into());
    }
    let path = dir.join("chat-autosave.jsonl");
    let existing_len = match std::fs::symlink_metadata(&path) {
        Ok(meta) if plain(&meta, false) => meta.len(),
        Ok(_) => return Err("Nieprawidłowy plik historii rozmów".into()),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => 0,
        Err(e) => return Err(e.to_string()),
    };
    if existing_len.saturating_add(line.len() as u64) > MAX_BYTES {
        return Err("Osiągnięto limit 16 MiB historii".into());
    }
    let mut options = std::fs::OpenOptions::new();
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        options.mode(0o600);
    }
    #[cfg(windows)]
    {
        use std::os::windows::fs::OpenOptionsExt;
        options.custom_flags(0x8000_0000);
    }
    let mut file = options
        .append(true)
        .create(true)
        .open(path)
        .map_err(|e| e.to_string())?;
    file.write_all(&line)
        .and_then(|_| file.sync_all())
        .map_err(|e| format!("Niepewny wynik zapisu historii; zachowaj plik: {e}"))?;
    sync_parent(dir)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::{SystemTime, UNIX_EPOCH};

    fn root() -> std::path::PathBuf {
        let unique = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let root =
            std::env::temp_dir().join(format!("sparkle-chat-{}-{unique}", std::process::id()));
        std::fs::create_dir(&root).unwrap();
        root
    }
    fn record(channel: &str, text: &str) -> ChatRecord {
        ChatRecord {
            channel: channel.into(),
            sender: "Użytkownik".into(),
            text: text.into(),
            iso_time: "2026-11-03T12:00:00.000Z".into(),
        }
    }

    #[test]
    fn chat_roundtrip_preserves_order_unicode_and_channel() {
        let root = root();
        let db = root.join("db");
        assert!(load(&db).unwrap().is_empty());
        let a = record("main", "Zażółć\n\"bezpiecznie\"");
        let b = record("guest", "odpowiedź");
        append(&db, &a).unwrap();
        append(&db, &b).unwrap();
        assert_eq!(load(&db).unwrap(), vec![a, b]);
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn truncated_or_tampered_history_is_preserved_and_refuses_append() {
        let root = root();
        let db = root.join("db");
        append(&db, &record("main", "oryginał")).unwrap();
        let file = db.join("chat-autosave.jsonl");
        let valid = std::fs::read(&file).unwrap();
        let mut corrupted = valid.clone();
        corrupted[0] = if corrupted[0] == b'0' { b'1' } else { b'0' };
        std::fs::write(&file, &corrupted).unwrap();
        assert!(load(&db).is_err());
        assert!(append(&db, &record("main", "nowa")).is_err());
        assert_eq!(std::fs::read(&file).unwrap(), corrupted);
        let truncated = &valid[..valid.len() - 1];
        std::fs::write(&file, truncated).unwrap();
        assert!(load(&db).is_err());
        assert!(append(&db, &record("guest", "nowa")).is_err());
        assert_eq!(std::fs::read(&file).unwrap(), truncated);
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn oversized_or_invalid_messages_do_not_modify_history() {
        let root = root();
        let db = root.join("db");
        append(&db, &record("main", "ok")).unwrap();
        let file = db.join("chat-autosave.jsonl");
        let before = std::fs::read(&file).unwrap();
        assert!(append(&db, &record("main", &"a".repeat(64 * 1024 + 1))).is_err());
        assert!(append(&db, &record("other", "x")).is_err());
        assert_eq!(std::fs::read(file).unwrap(), before);
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn chat_crash_child() {
        if let Some(path) = std::env::var_os("SPARKLE_TEST_CHAT_DB") {
            append(Path::new(&path), &record("main", "po restarcie")).unwrap();
            std::process::exit(42);
        }
    }

    #[test]
    fn acknowledged_chat_record_survives_abrupt_process_exit() {
        let root = root();
        let db = root.join("db");
        let status = std::process::Command::new(std::env::current_exe().unwrap())
            .args([
                "--exact",
                "chat_autosave::tests::chat_crash_child",
                "--nocapture",
            ])
            .env("SPARKLE_TEST_CHAT_DB", &db)
            .status()
            .unwrap();
        assert_eq!(status.code(), Some(42));
        assert_eq!(load(&db).unwrap(), vec![record("main", "po restarcie")]);
        std::fs::remove_dir_all(root).unwrap();
    }
}
