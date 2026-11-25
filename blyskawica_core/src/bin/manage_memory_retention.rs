//! Review and explicitly remove one eligible old generation.
use blyskawica_core::vector_index::{IndexLease, SparkleVectorIndex};
use std::{path::PathBuf, sync::Arc};

fn run() -> Result<(), String> {
    let args: Vec<_> = std::env::args_os().skip(1).collect();
    if args.len() != 5 && args.len() != 7 {
        return Err("Użycie: manage_memory_retention review <db> <indeks> <wymiar> <generacja> | delete <db> <indeks> <wymiar> <generacja> <fingerprint_sha256> --confirm-delete".into());
    }
    let mode = args[0].to_str().ok_or("Nieprawidłowa operacja")?;
    let path = PathBuf::from(&args[1]);
    let basename = args[2].to_str().ok_or("Nieprawidłowy indeks")?;
    let dimension: usize = args[3]
        .to_str()
        .ok_or("Nieprawidłowy wymiar")?
        .parse()
        .map_err(|_| "Nieprawidłowy wymiar")?;
    let number: u64 = args[4]
        .to_str()
        .ok_or("Nieprawidłowy numer")?
        .parse()
        .map_err(|_| "Nieprawidłowy numer")?;
    if dimension == 0 || dimension > 65_536 {
        return Err("Wymiar poza zakresem 1–65536".into());
    }
    if !((mode == "review" && args.len() == 5)
        || (mode == "delete" && args.len() == 7 && args[6] == "--confirm-delete"))
    {
        return Err("Nieprawidłowa operacja lub brak potwierdzenia".into());
    }
    let parent = path
        .parent()
        .ok_or("Katalog DB musi mieć katalog nadrzędny")?;
    let lease = Arc::new(IndexLease::acquire(&parent.join("sparkle-index.lock"))?);
    if mode == "review" {
        let report = SparkleVectorIndex::review_generation_retention(
            &path, basename, dimension, number, lease,
        )?;
        println!(
            "{}",
            serde_json::to_string_pretty(&report).map_err(|e| e.to_string())?
        );
    } else {
        let fingerprint = args[5].to_str().ok_or("Nieprawidłowa suma")?;
        SparkleVectorIndex::delete_reviewed_generation(
            &path,
            basename,
            dimension,
            number,
            fingerprint,
            lease,
            true,
        )?;
        println!("{{\"generation_deleted\":{number}}}");
    }
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        std::process::exit(1);
    }
}
