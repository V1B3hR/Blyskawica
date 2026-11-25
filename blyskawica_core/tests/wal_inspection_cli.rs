use blyskawica_core::anomaly_loop::AnomalyQueueItem;
use blyskawica_core::vector_index::{IndexLease, SparkleVectorIndex};
use std::io::Write;
use std::sync::Arc;

#[test]
fn cli_reports_truncated_tail_without_disclosing_or_changing_data() {
    let root = std::env::temp_dir().join(format!("blysk-cli-wal-{:016x}", rand::random::<u64>()));
    std::fs::create_dir_all(&root).unwrap();
    let dir = root.join("db");
    let lease = Arc::new(IndexLease::acquire(&root.join("sparkle-index.lock")).unwrap());
    let index = SparkleVectorIndex::new(4, 10)
        .with_storage(&dir, lease.clone())
        .unwrap();
    index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
    index.file_dump(&dir, "index").unwrap();
    index
        .enqueue_durable(
            &dir,
            "index",
            AnomalyQueueItem {
                id: 2,
                vector: vec![0.0, 1.0, 0.0, 0.0],
                metadata: "synthetic-private-test-value".into(),
                queue_id: None,
            },
        )
        .unwrap();
    drop(index);
    drop(lease);
    let wal = dir.join("index.hnsw.wal");
    std::fs::OpenOptions::new()
        .append(true)
        .open(&wal)
        .unwrap()
        .write_all(b"v3:partial")
        .unwrap();
    let before = std::fs::read(&wal).unwrap();
    let output = std::process::Command::new(env!("CARGO_BIN_EXE_inspect_memory_wal"))
        .arg(&dir)
        .args(["index", "4"])
        .output()
        .unwrap();
    assert!(!output.status.success());
    let stdout = String::from_utf8(output.stdout).unwrap();
    let report: serde_json::Value = serde_json::from_str(&stdout).unwrap();
    assert_eq!(report["issue"]["kind"], "incomplete_tail");
    assert_eq!(report["pending_items"], 1);
    assert!(!stdout.contains("synthetic-private-test-value"));
    assert_eq!(std::fs::read(&wal).unwrap(), before);
    std::fs::remove_dir_all(root).unwrap();
}

#[test]
fn candidate_cli_requires_acknowledgement_and_keeps_the_original() {
    let root = std::env::temp_dir().join(format!(
        "blysk-cli-candidate-{:016x}",
        rand::random::<u64>()
    ));
    std::fs::create_dir_all(&root).unwrap();
    let dir = root.join("db");
    let lease = Arc::new(IndexLease::acquire(&root.join("sparkle-index.lock")).unwrap());
    let index = SparkleVectorIndex::new(4, 10)
        .with_storage(&dir, lease.clone())
        .unwrap();
    index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
    index.file_dump(&dir, "index").unwrap();
    index
        .enqueue_durable(
            &dir,
            "index",
            AnomalyQueueItem {
                id: 2,
                vector: vec![0.0, 1.0, 0.0, 0.0],
                metadata: "synthetic-private-candidate".into(),
                queue_id: None,
            },
        )
        .unwrap();
    drop(index);
    drop(lease);
    let wal = dir.join("index.hnsw.wal");
    std::fs::OpenOptions::new()
        .append(true)
        .open(&wal)
        .unwrap()
        .write_all(b"v3:partial")
        .unwrap();
    let before = std::fs::read(&wal).unwrap();
    let exe = env!("CARGO_BIN_EXE_prepare_memory_wal_candidate");
    let refused = std::process::Command::new(exe)
        .arg(&dir)
        .args(["index", "4"])
        .output()
        .unwrap();
    assert!(!refused.status.success());
    assert_eq!(std::fs::read(&wal).unwrap(), before);
    let result = std::process::Command::new(exe)
        .arg(&dir)
        .args(["index", "4", "--accept-possible-loss"])
        .output()
        .unwrap();
    assert!(
        result.status.success(),
        "{}",
        String::from_utf8_lossy(&result.stderr)
    );
    let stdout = String::from_utf8(result.stdout).unwrap();
    let report: serde_json::Value = serde_json::from_str(&stdout).unwrap();
    assert_eq!(report["possible_loss"], true);
    assert_eq!(report["pending_items"], 1);
    assert_eq!(report["excluded_tail_bytes"], 10);
    assert!(!stdout.contains("synthetic-private-candidate"));
    let candidate = dir.join(report["candidate_directory"].as_str().unwrap());
    assert!(candidate.join("recovery-candidate.json").is_file());
    assert_eq!(std::fs::read(&wal).unwrap(), before);
    let verify = |name: &str| {
        std::process::Command::new(env!("CARGO_BIN_EXE_verify_memory_wal_candidate"))
            .arg(&dir)
            .args(["index", "4", name])
            .output()
            .unwrap()
    };
    let name = report["candidate_directory"].as_str().unwrap();
    let verified = verify(name);
    assert!(
        verified.status.success(),
        "{}",
        String::from_utf8_lossy(&verified.stderr)
    );
    assert!(!String::from_utf8_lossy(&verified.stdout).contains("synthetic-private-candidate"));
    assert!(!verify("../db").status.success());
    let candidate_wal = candidate.join("index.hnsw.wal");
    let clean_copy = std::fs::read(&candidate_wal).unwrap();
    std::fs::write(&candidate_wal, b"tampered\n").unwrap();
    assert!(!verify(name).status.success());
    std::fs::write(&candidate_wal, clean_copy).unwrap();
    std::fs::OpenOptions::new()
        .append(true)
        .open(&wal)
        .unwrap()
        .write_all(b"changed")
        .unwrap();
    assert!(!verify(name).status.success());
    assert_eq!(
        std::fs::read(&wal).unwrap(),
        [before.as_slice(), b"changed"].concat()
    );
    std::fs::remove_dir_all(root).unwrap();
}

#[test]
fn maintenance_cli_requires_confirmation_and_operates_on_one_candidate() {
    let root = std::env::temp_dir().join(format!(
        "blysk-cli-maintenance-{:016x}",
        rand::random::<u64>()
    ));
    std::fs::create_dir_all(&root).unwrap();
    let dir = root.join("db");
    let lease = Arc::new(IndexLease::acquire(&root.join("sparkle-index.lock")).unwrap());
    let index = SparkleVectorIndex::new(4, 10)
        .with_storage(&dir, lease.clone())
        .unwrap();
    index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
    index.file_dump(&dir, "index").unwrap();
    index
        .enqueue_durable(
            &dir,
            "index",
            AnomalyQueueItem {
                id: 2,
                vector: vec![0.0, 1.0, 0.0, 0.0],
                metadata: "private-synthetic".into(),
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
    let before = std::fs::read(&wal).unwrap();
    let first =
        SparkleVectorIndex::prepare_wal_recovery_candidate(&dir, "index", 4, lease.clone(), true)
            .unwrap();
    let second =
        SparkleVectorIndex::prepare_wal_recovery_candidate(&dir, "index", 4, lease.clone(), true)
            .unwrap();
    drop(lease);
    let run = |mode: &str,
               report: &blyskawica_core::vector_index::RecoveryCandidateReport,
               flag: &str| {
        std::process::Command::new(env!("CARGO_BIN_EXE_manage_memory_recovery"))
            .arg(mode)
            .arg(&dir)
            .args([
                "index",
                "4",
                &report.candidate_directory,
                &report.original_wal_sha256,
                &report.candidate_wal_sha256,
                flag,
            ])
            .output()
            .unwrap()
    };
    assert!(
        !run("delete-candidate", &first, "--accept-possible-loss")
            .status
            .success()
    );
    let deletion = run("delete-candidate", &first, "--confirm-delete");
    assert!(
        deletion.status.success(),
        "{}",
        String::from_utf8_lossy(&deletion.stderr)
    );
    assert!(!dir.join(&first.candidate_directory).exists());
    assert!(dir.join(&second.candidate_directory).is_dir());
    assert!(
        !run("activate", &second, "--confirm-delete")
            .status
            .success()
    );
    let activation = run("activate", &second, "--accept-possible-loss");
    assert!(
        activation.status.success(),
        "{}",
        String::from_utf8_lossy(&activation.stderr)
    );
    assert!(!String::from_utf8_lossy(&activation.stdout).contains("private-synthetic"));
    assert_eq!(std::fs::read(&wal).unwrap(), before);
    let lease = Arc::new(IndexLease::acquire(&root.join("sparkle-index.lock")).unwrap());
    let restored = SparkleVectorIndex::load_hnsw(&dir, "index", 4, lease.clone()).unwrap();
    assert_eq!(restored.pending_queue().unwrap().len(), 1);
    drop(restored);
    drop(lease);
    std::fs::remove_dir_all(root).unwrap();
}

#[test]
fn generation_retention_cli_requires_review_and_confirmation() {
    let root = std::env::temp_dir().join(format!(
        "blysk-cli-retention-{:016x}",
        rand::random::<u64>()
    ));
    std::fs::create_dir_all(&root).unwrap();
    let dir = root.join("db");
    let lease = Arc::new(IndexLease::acquire(&root.join("sparkle-index.lock")).unwrap());
    let index = SparkleVectorIndex::new(4, 10)
        .with_storage(&dir, lease.clone())
        .unwrap();
    index.insert(1, &[1.0, 0.0, 0.0, 0.0]).unwrap();
    index.file_dump(&dir, "index").unwrap();
    for _ in 0..3 {
        index.checkpoint(&dir, "index").unwrap();
    }
    drop(index);
    drop(lease);
    let exe = env!("CARGO_BIN_EXE_manage_memory_retention");
    let run = |arguments: &[&str]| {
        std::process::Command::new(exe)
            .arg(arguments[0])
            .arg(&dir)
            .args(&arguments[1..])
            .output()
            .unwrap()
    };
    let review = run(&["review", "index", "4", "1"]);
    assert!(
        review.status.success(),
        "{}",
        String::from_utf8_lossy(&review.stderr)
    );
    let report: serde_json::Value = serde_json::from_slice(&review.stdout).unwrap();
    let fingerprint = report["fingerprint_sha256"].as_str().unwrap();
    assert!(
        !run(&["delete", "index", "4", "1", fingerprint, "--wrong"])
            .status
            .success()
    );
    assert!(
        !run(&["delete", "index", "4", "1", "wrong", "--confirm-delete"])
            .status
            .success()
    );
    let deleted = run(&["delete", "index", "4", "1", fingerprint, "--confirm-delete"]);
    assert!(
        deleted.status.success(),
        "{}",
        String::from_utf8_lossy(&deleted.stderr)
    );
    assert!(!dir.join(report["directory"].as_str().unwrap()).exists());
    assert!(dir.join("index.commit.00000000000000000002").exists());
    assert!(dir.join("index.commit.00000000000000000003").exists());
    std::fs::remove_dir_all(root).unwrap();
}
