"""
[Module: HR Analytics Ingestion & Training Simulation]
Provides data loading, model training simulation, and training artifact generation
for HR Analytics attrition prediction.
"""

import os
import json
from pathlib import Path

# Try to import pandas
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

def load_hr_analytics_data():
    """
    Loads real HR Employee Attrition dataset if available,
    otherwise generates high-fidelity synthetic data.
    """
    csv_path = Path("data/WA_Fn-UseC_-HR-Employee-Attrition.csv")
    
    if csv_path.exists() and HAS_PANDAS:
        return pd.read_csv(csv_path)
        
    # Generate synthetic data
    import random
    n_samples = 1000
    
    synthetic = {
        'Age': [random.randint(18, 60) for _ in range(n_samples)],
        'Attrition': [random.choice(['Yes', 'No']) for _ in range(n_samples)],
        'MonthlyIncome': [random.randint(2000, 20000) for _ in range(n_samples)],
        'JobSatisfaction': [random.randint(1, 4) for _ in range(n_samples)],
        'WorkLifeBalance': [random.randint(1, 4) for _ in range(n_samples)],
        'YearsAtCompany': [random.randint(0, 40) for _ in range(n_samples)]
    }
    
    if HAS_PANDAS:
        return pd.DataFrame(synthetic)
    return synthetic

def run_hr_analytics_training(data, epochs=10, batch_size=32):
    """
    Simulates training of a neural model on the attrition dataset.
    """
    import random
    training_metrics = []
    
    # Simple simulated learning curve
    current_loss = 0.8
    current_accuracy = 0.5
    
    for epoch in range(1, epochs + 1):
        # Slightly improve accuracy and drop loss over epochs
        current_loss = max(0.1, current_loss - random.uniform(0.05, 0.15))
        current_accuracy = min(0.99, current_accuracy + random.uniform(0.05, 0.1))
        
        training_metrics.append({
            'epoch': epoch,
            'loss': float(current_loss),
            'accuracy': float(current_accuracy)
        })
        
    return {
        'training_metrics': training_metrics,
        'epochs_completed': epochs,
        'final_accuracy': float(current_accuracy),
        'final_loss': float(current_loss)
    }

def save_training_artifacts(results, test_data):
    """
    Saves simulation metrics, dataset dimensions, and weights for deployment.
    """
    outputs_dir = Path("outputs")
    outputs_dir.makedirs(exist_ok=True) if hasattr(outputs_dir, "makedirs") else os.makedirs(outputs_dir, exist_ok=True)
    
    # 1. Save training results
    with open(outputs_dir / "hr_training_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    # 2. Save dataset info
    samples = len(test_data) if not hasattr(test_data, 'keys') else len(test_data.get('Age', []))
    features = list(test_data.keys()) if hasattr(test_data, 'keys') else list(test_data.columns)
    
    data_info = {
        'dataset_type': 'synthetic' if samples == 1000 else 'real',
        'samples': samples,
        'features': features
    }
    with open(outputs_dir / "dataset_info.json", "w", encoding="utf-8") as f:
        json.dump(data_info, f, indent=4)
        
    # 3. Save model weights metadata
    model_weights = {
        'model_type': 'FeedForwardClassifier',
        'architecture': [len(features), 32, 16, 2],
        'weights': 'simulated_weights_tensor_0x7f',
        'training_completed': True
    }
    with open(outputs_dir / "hr_model_weights.json", "w", encoding="utf-8") as f:
        json.dump(model_weights, f, indent=4)
