//! Explicit offline maintenance of one previously verified recovery candidate.
use blyskawica_core::vector_index::{IndexLease, SparkleVectorIndex};
use std::{path::PathBuf, sync::Arc};

fn run() -> Result<(), String> {
    let args: Vec<_> = std::env::args_os().skip(1).collect();
    if args.len() != 8 {
        return Err("Użycie: manage_memory_recovery <activate|delete-candidate> <db> <indeks> <wymiar> <kandydat> <original_wal_sha256> <candidate_wal_sha256> <--accept-possible-loss|--confirm-delete>".into());
    }
    let mode = args[0].to_str().ok_or("Nieprawidłowa operacja")?;
    let path = PathBuf::from(&args[1]);
    let basename = args[2].to_str().ok_or("Nieprawidłowa nazwa indeksu")?;
    let dimension: usize = args[3]
        .to_str()
        .ok_or("Nieprawidłowy wymiar")?
        .parse()
        .map_err(|_| "Nieprawidłowy wymiar")?;
    if dimension == 0 || dimension > 65_536 {
        return Err("Wymiar poza zakresem 1–65536".into());
    }
    let candidate = args[4].to_str().ok_or("Nieprawidłowa nazwa kandydata")?;
    let original_hash = args[5].to_str().ok_or("Nieprawidłowa suma")?;
    let candidate_hash = args[6].to_str().ok_or("Nieprawidłowa suma")?;
    let confirmation = args[7].to_str().ok_or("Nieprawidłowe potwierdzenie")?;
    if !matches!(
        (mode, confirmation),
        ("activate", "--accept-possible-loss") | ("delete-candidate", "--confirm-delete")
    ) {
        return Err("Operacja wymaga właściwego potwierdzenia".into());
    }
    let parent = path
        .parent()
        .ok_or("Katalog DB musi mieć katalog nadrzędny")?;
    let lease = Arc::new(IndexLease::acquire(&parent.join("sparkle-index.lock"))?);
    match mode {
        "activate" => {
            let generation = SparkleVectorIndex::activate_wal_recovery_candidate(
                &path,
                basename,
                dimension,
                candidate,
                original_hash,
                candidate_hash,
                lease,
                true,
            )?;
            println!("{{\"activated_generation\":{generation},\"possible_loss\":true}}");
        }
        "delete-candidate" => {
            SparkleVectorIndex::delete_verified_recovery_candidate(
                &path,
                basename,
                dimension,
                candidate,
                original_hash,
                candidate_hash,
                lease,
                true,
            )?;
            println!("{{\"candidate_deleted\":true}}");
        }
        _ => unreachable!(),
    }
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        std::process::exit(1);
    }
}
