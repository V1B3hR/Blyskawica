#!/usr/bin/env python3
"""
Comprehensive test script to verify all Quick Start features.

This script validates that all features listed in the problem statement work correctly:
1. Run smoke tests for quick validation
2. Run benchmarks for full evaluation
3. Use local CSV files or Kaggle datasets
4. Configure output directories and subset sizes
5. Access trained models and detailed metrics
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Configure stdout encoding if available
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptiveneuralnetwork.training.models.text_baseline import TextClassificationBaseline
from adaptiveneuralnetwork.training.scripts.run_bitext_training import (
    run_benchmark,
    run_smoke_test,
)


class TestQuickstartFeatures(unittest.TestCase):
    """Test suite verifying all quickstart training features."""

    def test_1_smoke_test_default(self):
        """Test 1: Run smoke tests for quick validation (default settings)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_smoke_test(output_dir=tmpdir)

            self.assertTrue(result['success'], f"Smoke test failed: {result.get('error')}")
            self.assertEqual(result['mode'], 'smoke')
            self.assertGreater(result['runtime_seconds'], 0)
            self.assertGreater(result['dataset_info']['train_samples'], 0)
            self.assertIn('train_accuracy', result['train_metrics'])
            self.assertIn('accuracy', result['eval_metrics'])

            # Verify output files exist
            self.assertTrue(Path(tmpdir, 'smoke_test_results.json').exists())
            self.assertTrue(Path(tmpdir, 'smoke_test_model.pkl').exists())

    def test_2_smoke_test_custom(self):
        """Test 2: Smoke test with custom subset size and output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir) / "custom_output"
            result = run_smoke_test(
                subset_size=50,
                output_dir=str(custom_dir)
            )

            self.assertTrue(result['success'], f"Custom smoke test failed: {result.get('error')}")
            self.assertLessEqual(result['dataset_info']['train_samples'], 50)
            self.assertTrue(custom_dir.exists())
            self.assertTrue((custom_dir / 'smoke_test_results.json').exists())
            self.assertTrue((custom_dir / 'smoke_test_model.pkl').exists())

    def test_3_benchmark_mode(self):
        """Test 3: Run benchmarks for full evaluation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_benchmark(
                subset_size=200,
                output_dir=tmpdir
            )

            self.assertTrue(result['success'], f"Benchmark failed: {result.get('error')}")
            self.assertEqual(result['mode'], 'benchmark')
            self.assertIn('eval_metrics', result)
            self.assertIn('accuracy', result['eval_metrics'])
            self.assertIn('precision', result['eval_metrics'])
            self.assertIn('recall', result['eval_metrics'])
            self.assertIn('f1_score', result['eval_metrics'])

            # Verify detailed metrics
            self.assertIn('feature_importance', result)
            self.assertIn('classification_report', result['eval_metrics'])

            # Verify output files
            self.assertTrue(Path(tmpdir, 'benchmark_results.json').exists())
            self.assertTrue(Path(tmpdir, 'benchmark_model.pkl').exists())

    def test_4_local_csv(self):
        """Test 4: Use local CSV files"""
        try:
            import pandas as pd
        except (ImportError, AttributeError):
            self.skipTest("Pandas is not available or broken on this environment")
            return

        # Create test CSV
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_data.csv"

            # Generate test data
            data = {
                'text': [
                    f"positive sample {i} with good quality" for i in range(50)
                ] + [
                    f"negative sample {i} with poor quality" for i in range(50)
                ],
                'label': [1] * 50 + [0] * 50
            }
            df = pd.DataFrame(data)
            df.to_csv(csv_path, index=False)

            # Run training with local CSV
            output_dir = Path(tmpdir) / "output"
            result = run_smoke_test(
                local_path=str(csv_path),
                output_dir=str(output_dir)
            )

            self.assertTrue(result['success'], f"Local CSV test failed: {result.get('error')}")
            self.assertEqual(result['dataset_info']['data_source'], 'real')
            self.assertGreater(result['dataset_info']['train_samples'], 0)

    def test_5_access_trained_model(self):
        """Test 5: Access trained models and make predictions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Train model
            result = run_smoke_test(output_dir=tmpdir)
            self.assertTrue(result['success'])

            model_path = Path(tmpdir) / 'smoke_test_model.pkl'
            self.assertTrue(model_path.exists())

            # Load model
            model = TextClassificationBaseline()
            model.load_model(str(model_path))

            # Make predictions
            test_texts = [
                "machine learning is great",
                "artificial intelligence example",
                "hello world test"
            ]
            predictions = model.predict(test_texts)
            probabilities = model.predict_proba(test_texts)

            self.assertEqual(len(predictions), len(test_texts))
            self.assertEqual(len(probabilities), len(test_texts))
            self.assertTrue(all(len(p) == 2 for p in probabilities))  # Binary classification

    def test_6_access_detailed_metrics(self):
        """Test 6: Access detailed metrics from results JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Run benchmark
            result = run_benchmark(
                subset_size=200,
                output_dir=tmpdir
            )
            self.assertTrue(result['success'], f"Benchmark failed: {result.get('error')}")

            # Load JSON results
            results_path = Path(tmpdir) / 'benchmark_results.json'
            self.assertTrue(results_path.exists())

            with open(results_path) as f:
                metrics = json.load(f)

            # Verify all required metrics are present
            required_fields = [
                'mode', 'runtime_seconds', 'dataset_info',
                'model_info', 'train_metrics', 'eval_metrics'
            ]
            for field in required_fields:
                self.assertIn(field, metrics, f"Missing field: {field}")

            # Verify detailed evaluation metrics
            eval_metrics = metrics['eval_metrics']
            self.assertIn('accuracy', eval_metrics)
            self.assertIn('precision', eval_metrics)
            self.assertIn('recall', eval_metrics)
            self.assertIn('f1_score', eval_metrics)
            self.assertIn('confusion_matrix', eval_metrics)
            self.assertIn('classification_report', eval_metrics)

            # Verify model info
            model_info = metrics['model_info']
            self.assertIn('num_features', model_info)
            self.assertIn('num_classes', model_info)

            # Verify feature importance
            self.assertIn('feature_importance', metrics)

    def test_7_configure_subset_sizes(self):
        """Test 7: Configure different subset sizes"""
        subset_sizes = [50, 100, 200]

        for size in subset_sizes:
            with tempfile.TemporaryDirectory() as tmpdir:
                result = run_smoke_test(
                    subset_size=size,
                    output_dir=tmpdir
                )

                self.assertTrue(result['success'], f"Failed with subset_size={size}")
                total_samples = (
                    result['dataset_info']['train_samples'] +
                    result['dataset_info']['val_samples']
                )
                self.assertLessEqual(
                    total_samples, size, f"Generated {total_samples} samples, expected <= {size}"
                )


if __name__ == "__main__":
    unittest.main()
