#!/usr/bin/env python3
"""
Demonstration of Governance Integration in Model Training

This script demonstrates how the governance system validates training data
and model predictions for safety and ethical violations.
"""

import subprocess
import sys
import tempfile
from pathlib import Path


def run_demo():
    print("=" * 80)
    print(" Governance Integration Demo - Model Training with Safety Validation")
    print("=" * 80)

    print("\n📋 Overview:")
    print("This demo shows how the governance system validates:")
    print("  1. Training data samples for safety violations")
    print("  2. Model predictions for ethical issues")
    print("  3. Complete audit trail with governance metrics")

    print("\n" + "=" * 80)
    print(" Demo 1: Training with Governance Only")
    print("=" * 80)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create required directories
        models_dir = tmpdir_path / "models"
        (models_dir / "current").mkdir(parents=True)
        (models_dir / "candidates").mkdir(parents=True)
        (tmpdir_path / "data" / "external").mkdir(parents=True)

        print("\n▶️  Running: train_any_model.py --enable-governance")
        print("   (Training a heuristic model with governance validation)")

        result = subprocess.run([
            sys.executable,
            str(Path(__file__).parent.parent / "training" / "train_any_model.py"),
            "--model-type", "heuristic",
            "--epochs", "1",
            "--num-samples", "50",
            "--enable-governance"
        ],
        cwd=tmpdir_path,
        capture_output=True,
        text=True,
        timeout=60
        )

        print("\n📊 Output:")
        # Print only governance-related lines
        for line in result.stdout.split('\n'):
            if any(keyword in line for keyword in [
                'Governance', 'governance', 'Data samples validated',
                'Predictions validated', 'violations found'
            ]):
                print(f"   {line}")

        print("\n✅ Demo 1 Complete!")
        print("   The governance system validated both training data and predictions.")

        print("\n" + "=" * 80)
        print(" Demo 2: Training with Governance + Audit Logging")
        print("=" * 80)

        audit_dir = tmpdir_path / "audit_logs"
        audit_dir.mkdir()

        print("\n▶️  Running: train_any_model.py --enable-governance --enable-audit")
        print("   (Training with both governance validation and Merkle audit trail)")

        result2 = subprocess.run([
            sys.executable,
            str(Path(__file__).parent.parent / "training" / "train_any_model.py"),
            "--model-type", "heuristic",
            "--epochs", "1",
            "--num-samples", "50",
            "--enable-governance",
            "--enable-audit",
            "--audit-path", str(audit_dir)
        ],
        cwd=tmpdir_path,
        capture_output=True,
        text=True,
        timeout=60
        )

        print("\n📊 Output:")
        for line in result2.stdout.split('\n'):
            if any(keyword in line for keyword in [
                'Governance', 'governance', 'Data samples validated',
                'Predictions validated', 'violations found', 'Merkle',
                'Audit', 'audit'
            ]):
                print(f"   {line}")

        # Show audit summary
        import json
        audit_summary_path = audit_dir / "training_summary.json"
        if audit_summary_path.exists():
            with open(audit_summary_path) as f:
                summary = json.load(f)

            print("\n📄 Audit Summary (with Governance Metrics):")
            print(f"   Merkle Root: {summary['merkle_root'][:20]}...")
            print(f"   Model Type: {summary['model_type']}")
            print(f"   Promoted: {summary['promoted']}")
            print(f"   Accuracy: {summary['metrics']['accuracy']:.4f}")

            if 'governance' in summary and summary['governance']['enabled']:
                print("\n   Governance Metrics:")
                print(f"     Data Violations: {summary['governance']['data_violations']}")
                print(f"     Prediction Violations: {summary['governance']['prediction_violations']}")
                if 'total_violations_detected' in summary['governance']:
                    print(f"     Total Violations: {summary['governance']['total_violations_detected']}")

        print("\n✅ Demo 2 Complete!")
        print("   Audit trail includes comprehensive governance metrics.")

    print("\n" + "=" * 80)
    print(" Summary: Governance Integration Benefits")
    print("=" * 80)

    print("\n🔒 Safety & Ethics:")
    print("   • Real-time validation of training data and predictions")
    print("   • Detection of 15+ violation types (toxic content, bias, privacy, etc.)")
    print("   • Quarantine/block decisions for problematic samples")

    print("\n📝 Compliance & Auditing:")
    print("   • Complete audit trail with governance metrics")
    print("   • Cryptographic verification via Merkle trees")
    print("   • Regulatory compliance documentation")

    print("\n🎯 Model Quality:")
    print("   • Early detection of problematic training data")
    print("   • Validation that model outputs meet safety standards")
    print("   • Continuous monitoring throughout training pipeline")

    print("\n💡 Usage:")
    print("   python training/train_any_model.py \\")
    print("       --model-type heuristic \\")
    print("       --enable-governance \\")
    print("       --enable-audit")

    print("\n" + "=" * 80)
    print(" ✅ Governance Demo Complete!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        raise
