#!/usr/bin/env python3
"""
AI PoC Validation Demo

Demonstrates the three-pillar validation approach for AI Proof of Concepts:
1. Strategic Validation (The "Why")
2. Technical Validation (The "How" with Python) 
3. Operational Validation (The "What If")

This example follows the comprehensive methodology outlined in docs/AI_POC_VALIDATION_GUIDE.md
"""

import numpy as np
import pandas as pd
import time
import warnings
from typing import Dict, Any, Tuple
import os
import sys

# Add src directory to path for bioart imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Suppress warnings for cleaner demo output
warnings.filterwarnings('ignore')

def ensure_sklearn_available():
    """Check if scikit-learn is available for the demo"""
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import classification_report, confusion_matrix
        from sklearn.datasets import make_classification
        return True
    except ImportError:
        print("⚠️  scikit-learn not available. Installing minimal demo version...")
        return False

def create_synthetic_dataset():
    """Create a synthetic dataset for demonstration purposes"""
    print("📊 Creating synthetic customer churn dataset...")
    
    # Simulate customer data
    np.random.seed(42)  # For reproducibility
    n_samples = 1000
    
    # Features: tenure_months, monthly_charges, support_tickets
    tenure_months = np.random.exponential(24, n_samples)
    monthly_charges = np.random.normal(65, 20, n_samples)
    support_tickets = np.random.poisson(2, n_samples)
    total_charges = tenure_months * monthly_charges + np.random.normal(0, 100, n_samples)
    
    # Create churn based on logical rules (higher churn with short tenure, high charges, many tickets)
    churn_probability = (
        0.6 * (tenure_months < 12) +  # Short tenure increases churn
        0.3 * (monthly_charges > 80) +  # High charges increase churn
        0.4 * (support_tickets > 3) +  # Many tickets increase churn
        np.random.normal(0, 0.1, n_samples)  # Add noise
    )
    churn = (churn_probability > 0.7).astype(int)
    
    # Create DataFrame
    data = pd.DataFrame({
        'tenure_months': tenure_months,
        'monthly_charges': monthly_charges,
        'support_tickets': support_tickets,
        'total_charges': total_charges,
        'churn': churn
    })
    
    print(f"   Dataset created: {len(data)} samples")
    print(f"   Churn rate: {churn.mean():.1%}")
    print(f"   Features: {list(data.columns[:-1])}")
    
    return data

class MockModel:
    """Simple mock model for demonstration when sklearn is not available"""
    
    def __init__(self):
        self.is_fitted = False
        self.feature_names = None
        
    def fit(self, X, y):
        """Mock fit method"""
        self.is_fitted = True
        self.feature_names = X.columns.tolist() if hasattr(X, 'columns') else None
        # Simple rule-based prediction: churn if tenure < 12 months
        return self
        
    def predict(self, X):
        """Mock prediction using simple rules"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
            
        # Simple heuristic: predict churn for short tenure + high charges
        if hasattr(X, 'iloc'):
            predictions = ((X['tenure_months'] < 15) & (X['monthly_charges'] > 70)).astype(int)
        else:
            # Handle single prediction case
            predictions = np.array([1 if X[0] < 15 and X[1] > 70 else 0])
            
        return predictions
        
    def predict_proba(self, X):
        """Mock probability prediction"""
        predictions = self.predict(X)
        # Convert to probabilities
        probabilities = np.column_stack([1 - predictions, predictions])
        return probabilities

def pillar_1_strategic_validation():
    """
    Pillar 1: Strategic Validation (The "Why")
    Define success criteria, baseline, and data requirements
    """
    print("\n" + "="*60)
    print("🎯 PILLAR 1: STRATEGIC VALIDATION (The 'Why')")
    print("="*60)
    
    # 1.1 Define Crystal-Clear Success Criteria
    print("\n1.1 📋 Success Criteria Definition")
    print("-" * 40)
    
    success_criteria = {
        'precision': {
            'target': 0.70,
            'description': 'Of customers predicted to churn, 70% actually do',
            'business_impact': 'Minimizes wasted retention efforts'
        },
        'recall': {
            'target': 0.65, 
            'description': 'Catch 65% of customers who will actually churn',
            'business_impact': 'Identifies most at-risk customers'
        },
        'inference_time_ms': {
            'target': 500,
            'description': 'Prediction must complete within 500ms',
            'business_impact': 'Enables real-time customer scoring'
        }
    }
    
    print("✅ Success criteria defined:")
    for metric, details in success_criteria.items():
        print(f"   • {metric}: {details['target']} - {details['description']}")
    
    # 1.2 Establish Baseline
    print("\n1.2 📊 Baseline Establishment")
    print("-" * 40)
    
    baseline_metrics = {
        'current_process': {
            'method': 'Manual review by customer success team',
            'precision': 0.45,
            'recall': 0.60,
            'cost_per_prediction': 25.0,
            'description': 'Current manual process performance'
        },
        'simple_model': {
            'method': 'Rule-based system (tenure < 6 months = churn)',
            'precision': 0.55,
            'recall': 0.40,
            'cost_per_prediction': 0.10,
            'description': 'Simple automated baseline'
        }
    }
    
    print("✅ Baselines established:")
    for baseline, details in baseline_metrics.items():
        print(f"   • {baseline}: Precision {details['precision']:.2f}, "
              f"Recall {details['recall']:.2f}")
    
    # 1.3 Data Scoping
    print("\n1.3 🗃️  Data Scoping Assessment")
    print("-" * 40)
    
    data_requirements = {
        'minimum_samples': 1000,
        'minimum_positive_class': 100,
        'required_features': ['tenure_months', 'monthly_charges', 'support_tickets'],
        'data_quality_threshold': 0.95,
        'time_range': '12_months'
    }
    
    print("✅ Data requirements defined:")
    for requirement, value in data_requirements.items():
        print(f"   • {requirement}: {value}")
    
    return {
        'success_criteria': success_criteria,
        'baseline_metrics': baseline_metrics,
        'data_requirements': data_requirements
    }

def pillar_2_technical_validation(data: pd.DataFrame, strategic_results: Dict):
    """
    Pillar 2: Technical Validation (The "How" with Python)
    Model training, evaluation, and reproducibility
    """
    print("\n" + "="*60)
    print("🔬 PILLAR 2: TECHNICAL VALIDATION (The 'How')")
    print("="*60)
    
    # 2.1 Data Splitting and Preparation
    print("\n2.1 🔄 Data Preparation & Splitting")
    print("-" * 40)
    
    # Prepare features and target
    X = data.drop('churn', axis=1)
    y = data['churn']
    
    # Mock train_test_split if sklearn not available
    if ensure_sklearn_available():
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    else:
        # Simple manual split
        split_idx = int(0.8 * len(data))
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    print(f"✅ Data split completed:")
    print(f"   • Training set: {len(X_train)} samples")
    print(f"   • Test set: {len(X_test)} samples") 
    print(f"   • Train churn rate: {y_train.mean():.1%}")
    print(f"   • Test churn rate: {y_test.mean():.1%}")
    
    # 2.2 Model Training and Evaluation
    print("\n2.2 🤖 Model Training & Evaluation")
    print("-" * 40)
    
    # Train model
    if ensure_sklearn_available():
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import precision_score, recall_score, f1_score
        model = RandomForestClassifier(random_state=42, n_estimators=50)
    else:
        model = MockModel()
        
    print("🔧 Training model...")
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    if ensure_sklearn_available():
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
    else:
        # Calculate manually
        tp = np.sum((y_test == 1) & (y_pred == 1))
        fp = np.sum((y_test == 0) & (y_pred == 1))
        fn = np.sum((y_test == 1) & (y_pred == 0))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    metrics = {
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }
    
    print("📊 Model Performance:")
    print(f"   • Precision: {precision:.3f}")
    print(f"   • Recall: {recall:.3f}")
    print(f"   • F1-Score: {f1:.3f}")
    
    # 2.3 Success Criteria Validation
    print("\n2.3 🎯 Success Criteria Validation")
    print("-" * 40)
    
    success_criteria = strategic_results['success_criteria']
    validation_results = {}
    
    for metric in ['precision', 'recall']:
        achieved = metrics[metric]
        target = success_criteria[metric]['target']
        passed = achieved >= target
        
        validation_results[metric] = {
            'achieved': achieved,
            'target': target,
            'passed': passed
        }
        
        status = '✅ PASS' if passed else '❌ FAIL'
        print(f"   • {metric.upper()}: {achieved:.3f} (target: {target:.3f}) {status}")
    
    overall_technical_success = all(r['passed'] for r in validation_results.values())
    print(f"\n🏆 Technical Validation: {'✅ PASSED' if overall_technical_success else '❌ FAILED'}")
    
    return {
        'model': model,
        'X_test': X_test,
        'y_test': y_test,
        'y_pred': y_pred,
        'metrics': metrics,
        'validation_results': validation_results,
        'overall_success': overall_technical_success
    }

def pillar_3_operational_validation(technical_results: Dict, strategic_results: Dict):
    """
    Pillar 3: Operational Validation (The "What If") 
    Performance, robustness, and production readiness
    """
    print("\n" + "="*60)
    print("⚡ PILLAR 3: OPERATIONAL VALIDATION (The 'What If')")
    print("="*60)
    
    model = technical_results['model']
    X_test = technical_results['X_test']
    
    # 3.1 Performance Testing
    print("\n3.1 🚀 Performance & Resource Testing")
    print("-" * 40)
    
    # Test inference time
    sample_instance = X_test.iloc[[0]]
    
    # Warm up
    _ = model.predict(sample_instance)
    
    # Measure inference times
    times = []
    for _ in range(10):  # Smaller sample for demo
        start_time = time.time()
        _ = model.predict(sample_instance)
        end_time = time.time()
        times.append((end_time - start_time) * 1000)  # Convert to ms
    
    avg_inference_time = np.mean(times)
    target_time = strategic_results['success_criteria']['inference_time_ms']['target']
    
    performance_passed = avg_inference_time <= target_time
    
    print(f"📈 Performance Metrics:")
    print(f"   • Average inference time: {avg_inference_time:.2f}ms")
    print(f"   • Target time: {target_time}ms")
    print(f"   • Throughput: ~{1000/avg_inference_time:.0f} predictions/second")
    print(f"   • Performance: {'✅ PASS' if performance_passed else '❌ FAIL'}")
    
    # 3.2 Robustness Testing
    print("\n3.2 🛡️  Robustness Testing")
    print("-" * 40)
    
    robustness_results = {}
    
    # Test with missing values (simulate)
    print("Testing edge cases:")
    try:
        # Create edge case: very short tenure, very high charges
        edge_case = pd.DataFrame({
            'tenure_months': [1.0],
            'monthly_charges': [200.0],
            'support_tickets': [10],
            'total_charges': [200.0]
        })
        
        edge_prediction = model.predict(edge_case)
        robustness_results['handles_edge_cases'] = True
        print("   • Edge cases: ✅ Model handles gracefully")
        
    except Exception as e:
        robustness_results['handles_edge_cases'] = False
        print(f"   • Edge cases: ❌ Model fails - {str(e)[:50]}")
    
    # Error analysis
    y_test = technical_results['y_test']
    y_pred = technical_results['y_pred']
    
    misclassified_count = np.sum(y_pred != y_test)
    total_count = len(y_test)
    error_rate = misclassified_count / total_count
    
    print(f"   • Error rate: {error_rate:.1%} ({misclassified_count}/{total_count})")
    print(f"   • Robustness: {'✅ ACCEPTABLE' if error_rate < 0.4 else '❌ NEEDS IMPROVEMENT'}")
    
    # 3.3 Production Readiness Assessment
    print("\n3.3 🏭 Production Readiness")
    print("-" * 40)
    
    operational_score = 0
    max_score = 3
    
    if performance_passed:
        operational_score += 1
        print("   • Performance requirements: ✅")
    else:
        print("   • Performance requirements: ❌")
        
    if robustness_results.get('handles_edge_cases', False):
        operational_score += 1
        print("   • Edge case handling: ✅")
    else:
        print("   • Edge case handling: ❌")
        
    if error_rate < 0.35:  # Acceptable error rate
        operational_score += 1
        print("   • Error rate acceptable: ✅")  
    else:
        print("   • Error rate acceptable: ❌")
    
    operational_success = operational_score >= 2  # At least 2/3 criteria
    
    print(f"\n🏆 Operational Validation: {'✅ PASSED' if operational_success else '❌ FAILED'}")
    print(f"   Score: {operational_score}/{max_score}")
    
    return {
        'performance_results': {
            'avg_inference_time_ms': avg_inference_time,
            'target_time_ms': target_time,
            'performance_passed': performance_passed
        },
        'robustness_results': robustness_results,
        'error_rate': error_rate,
        'operational_success': operational_success
    }

def generate_final_recommendation(strategic_results: Dict, technical_results: Dict, 
                                operational_results: Dict):
    """Generate final PoC validation recommendation"""
    print("\n" + "="*60)
    print("🏆 FINAL POC VALIDATION SUMMARY")
    print("="*60)
    
    strategic_passed = True  # Strategic validation always passes in this demo
    technical_passed = technical_results['overall_success']
    operational_passed = operational_results['operational_success']
    
    print(f"✅ Strategic Validation:   {'✅ PASSED' if strategic_passed else '❌ FAILED'}")
    print(f"✅ Technical Validation:   {'✅ PASSED' if technical_passed else '❌ FAILED'}")
    print(f"✅ Operational Validation: {'✅ PASSED' if operational_passed else '❌ FAILED'}")
    
    overall_success = strategic_passed and technical_passed and operational_passed
    
    print("\n" + "="*60)
    if overall_success:
        print("🎉 RECOMMENDATION: PROCEED TO MVP DEVELOPMENT")
        print("✅ All validation pillars passed")
        print("✅ Success criteria met")
        print("✅ Technical feasibility confirmed")
        print("✅ Operational readiness validated")
        
        print("\n🎯 Next Steps:")
        print("1. Begin MVP development planning")
        print("2. Set up production infrastructure")
        print("3. Design A/B testing framework")
        print("4. Establish monitoring systems")
    else:
        print("⚠️  RECOMMENDATION: ADDITIONAL RESEARCH NEEDED")
        print("❌ One or more validation pillars failed")
        
        if not technical_passed:
            print("   • Address technical performance issues")
        if not operational_passed:
            print("   • Improve operational readiness")
            
        print("\n🔄 Next Steps:")
        print("1. Address failed criteria")
        print("2. Gather additional data if needed")
        print("3. Experiment with different approaches")
        print("4. Re-run validation after improvements")
    
    return {
        'overall_success': overall_success,
        'strategic_passed': strategic_passed,
        'technical_passed': technical_passed,
        'operational_passed': operational_passed,
        'recommendation': 'PROCEED_TO_MVP' if overall_success else 'ADDITIONAL_RESEARCH'
    }

def main():
    """Run the complete AI PoC validation demonstration"""
    print("🧬 AI PROOF OF CONCEPT VALIDATION DEMO")
    print("="*60)
    print("Demonstrating comprehensive 3-pillar validation methodology")
    print("Following guide: docs/AI_POC_VALIDATION_GUIDE.md")
    print("="*60)
    
    # Set random seed for reproducibility (following Bioart patterns)
    np.random.seed(42)
    print("🔒 Reproducibility locked with seed: 42")
    
    # Create demonstration dataset
    data = create_synthetic_dataset()
    
    # Run three-pillar validation
    try:
        # Pillar 1: Strategic Validation
        strategic_results = pillar_1_strategic_validation()
        
        # Pillar 2: Technical Validation  
        technical_results = pillar_2_technical_validation(data, strategic_results)
        
        # Pillar 3: Operational Validation
        operational_results = pillar_3_operational_validation(technical_results, strategic_results)
        
        # Final Recommendation
        final_results = generate_final_recommendation(
            strategic_results, technical_results, operational_results
        )
        
        print(f"\n📊 VALIDATION COMPLETED SUCCESSFULLY!")
        print(f"🕒 Demo executed with {len(data)} sample dataset")
        print(f"📚 Full methodology: docs/AI_POC_VALIDATION_GUIDE.md")
        
    except Exception as e:
        print(f"\n❌ Validation demo encountered an error: {e}")
        print("This is a demonstration script - in real validation, investigate and fix errors")
        
    print("\n" + "="*60)

if __name__ == "__main__":
    main()