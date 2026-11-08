//! Create a separate candidate; never modifies or activates the original store.
use blyskawica_core::vector_index::{IndexLease, SparkleVectorIndex};
use std::path::PathBuf;
use std::sync::Arc;

fn run() -> Result<(), String> {
    let args: Vec<_> = std::env::args_os().skip(1).collect();
    if args.len() != 4 || args[3] != "--accept-possible-loss" {
        return Err("Użycie: prepare_memory_wal_candidate <katalog-db> <nazwa-indeksu> <wymiar> --accept-possible-loss".into());
    }
    let path = PathBuf::from(&args[0]);
    let basename = args[1].to_str().ok_or("Nieprawidłowa nazwa indeksu")?;
    let dimension: usize = args[2]
        .to_str()
        .ok_or("Nieprawidłowy wymiar")?
        .parse()
        .map_err(|_| "Nieprawidłowy wymiar")?;
    if dimension == 0 || dimension > 65_536 {
        return Err("Wymiar poza zakresem 1–65536".into());
    }
    let parent = path
        .parent()
        .ok_or("Katalog DB musi mieć katalog nadrzędny")?;
    let lease = Arc::new(IndexLease::acquire(&parent.join("sparkle-index.lock"))?);
    let report = SparkleVectorIndex::prepare_wal_recovery_candidate(
        &path, basename, dimension, lease, true,
    )?;
    println!(
        "{}",
        serde_json::to_string_pretty(&report).map_err(|e| e.to_string())?
    );
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        std::process::exit(1);
    }
}
