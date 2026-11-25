//! Read-only WAL structure inspection. No records or vectors are printed.
use blyskawica_core::vector_index::{IndexLease, SparkleVectorIndex};
use std::path::PathBuf;
use std::sync::Arc;

fn run() -> Result<(), String> {
    let args: Vec<_> = std::env::args_os().skip(1).collect();
    if args.len() != 3 {
        return Err("Użycie: inspect_memory_wal <katalog-db> <nazwa-indeksu> <wymiar>".into());
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
    let report = SparkleVectorIndex::inspect_wal(&path, basename, dimension, lease)?;
    println!(
        "{}",
        serde_json::to_string_pretty(&report).map_err(|e| e.to_string())?
    );
    if report.issue.is_some() {
        return Err("WAL wymaga analizy; pliku nie zmieniono".into());
    }
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        std::process::exit(1);
    }
}
