import os
import sys
import torch
import torch.nn.functional as F
import hashlib
import logging

# Dodanie ścieżki do głównego katalogu, aby widzieć pakiet adaptiveneuralnetwork
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from adaptiveneuralnetwork.applications.continual_learning import (
    ContinualLearningSystem,
    ContinualLearningConfig
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def text_to_tensor(text: str, dim: int = 784) -> torch.Tensor:
    """
    Symulacja Embeddingu. Zamienia tekst na deterministyczny wektor (Tensor).
    Używamy funkcji skrótu (hash) dla uproszczenia (zamiast prawdziwego modelu LLM).
    """
    # Haszowanie tekstu
    hash_obj = hashlib.sha256(text.encode('utf-8'))
    hash_bytes = hash_obj.digest()
    
    # Zamiana bajtów na liczby całkowite i normalizacja
    # Powtarzamy bajty, aby wypełnić wymiar 'dim'
    repeated_bytes = (hash_bytes * (dim // len(hash_bytes) + 1))[:dim]
    
    # Tworzenie tensora (wartości od 0.0 do 1.0)
    tensor = torch.tensor([b / 255.0 for b in repeated_bytes], dtype=torch.float32)
    return tensor

def parse_knowledge_base(filepath: str, label_id: int):
    """Odczytuje plik z bazą wiedzy i konwertuje na tensory treningowe."""
    data = []
    labels = []
    
    if not os.path.exists(filepath):
        logger.error(f"Nie znaleziono pliku: {filepath}")
        return None, None
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Prosty podział na koncepty
    concepts = [c for c in content.split('[CONCEPT:') if c.strip()]
    for i, concept in enumerate(concepts):
        text = concept.strip()
        tensor = text_to_tensor(text)
        data.append(tensor)
        # Każdy koncept dostaje unikalne ID
        labels.append(label_id + i)
        
    if not data:
        return None, None
        
    return torch.stack(data), torch.tensor(labels, dtype=torch.long)

def evaluate(system, data, labels, task_id, task_name):
    """Testuje wiedzę Błyskawicy z danego tematu."""
    system.eval()
    with torch.no_grad():
        # Move to device
        device_data = data.to(system.device)
        device_labels = labels.to(system.device)
        
        output = system(device_data, task_id=task_id)
        # Pobieramy przewidywaną klasę
        preds = torch.argmax(output, dim=1)
        accuracy = (preds == device_labels).float().mean().item()
        
    logger.info(f"[EWALUACJA] Temat: {task_name} | Skuteczność: {accuracy * 100:.1f}%")
    return accuracy

def run_experiment():
    print("="*80)
    print(" EKSPERYMENT: PRZYSWAJANIE WIEDZY O ŚWIECIE (PHASE 1)")
    print(" Cel: Udowodnić brak Katastroficznego Zapominania (Catastrophic Forgetting)")
    print("="*80)

    # 1. Inicjalizacja Systemu
    config = ContinualLearningConfig(
        num_tasks=2,
        input_size=784,
        output_size=512,  # Larger feature space
        hidden_layers=[512, 512],
        enable_metaplasticity=False,
        enable_homeostatic_scaling=False,
        enable_sparse_coding=False,
        consolidation_strength=0.01,
        threshold_adaptation=False,
        memory_replay_ratio=0.5
    )
    
    logger.info("Inicjalizacja Mózgu (Continual Learning System)...")
    blyskawica = ContinualLearningSystem(config)
    optimizer = torch.optim.Adam(blyskawica.parameters(), lr=0.01)
    
    # 2. Przygotowanie danych
    base_dir = os.path.dirname(os.path.abspath(__file__))
    physics_path = os.path.join(base_dir, '..', 'data', 'knowledge_base', 'physics.txt')
    biology_path = os.path.join(base_dir, '..', 'data', 'knowledge_base', 'biology.txt')
    
    physics_data, physics_labels = parse_knowledge_base(physics_path, label_id=0)
    biology_data, biology_labels = parse_knowledge_base(biology_path, label_id=3)
    
    if physics_data is None or biology_data is None:
        logger.error("Brak danych do eksperymentu. Przerwanie.")
        return

    from torch.utils.data import TensorDataset, DataLoader
    
    physics_dataset = TensorDataset(physics_data, physics_labels)
    physics_loader = DataLoader(physics_dataset, batch_size=len(physics_dataset), shuffle=True)
    
    biology_dataset = TensorDataset(biology_data, biology_labels)
    biology_loader = DataLoader(biology_dataset, batch_size=len(biology_dataset), shuffle=True)

    # 3. ZADANIE 1: NAUKA FIZYKI
    print("\n[FAZA 1] Błyskawica czyta o Fizyce...")
    # learn_task przyjmuje DataLoader, task_id, num_epochs i wykonuje pętlę wewnątrz!
    metrics_physics = blyskawica.learn_task(physics_loader, task_id=0, num_epochs=100, learning_rate=0.05)
    
    logger.info(f"Nauka fizyki zakończona. Ostatnia dokładność: {metrics_physics.get('accuracy', 0):.4f}")
    
    # Konsolidacja pamięci (Zapisanie Fizyki w Crystallized Intelligence)
    print("[KONSOLIDACJA] Zapisywanie praw fizyki w pamięci długotrwałej...")
    blyskawica.synaptic_consolidation.update_optimal_params()
    
    # Test z Fizyki
    acc_physics_before = evaluate(blyskawica, physics_data, physics_labels, task_id=0, task_name="Fizyka (Po nauce fizyki)")

    # 4. ZADANIE 2: NAUKA BIOLOGII
    print("\n[FAZA 2] Błyskawica czyta o Biologii...")
    metrics_biology = blyskawica.learn_task(biology_loader, task_id=1, num_epochs=100, learning_rate=0.05)
        
    logger.info(f"Nauka biologii zakończona. Ostatnia dokładność: {metrics_biology.get('accuracy', 0):.4f}")
    
    # Test z Biologii
    acc_biology = evaluate(blyskawica, biology_data, biology_labels, task_id=1, task_name="Biologia (Po nauce biologii)")

    # 5. SPRAWDZIAN OSTATECZNY: CZY ZAPOMNIAŁA FIZYKĘ?
    print("\n[FAZA 3] Sprawdzian ostateczny (Test Katastroficznego Zapominania)")
    acc_physics_after = evaluate(blyskawica, physics_data, physics_labels, task_id=0, task_name="Fizyka (PO NAUCE BIOLOGII)")
    
    drop = acc_physics_before - acc_physics_after
    
    print("\n" + "="*80)
    print(" WYNIKI EKSPERYMENTU")
    print("="*80)
    if drop <= 0.1:
        print("[SUKCES] Błyskawica zachowała pamięć! System ciągłego uczenia zadziałał perfekcyjnie.")
    else:
        print(f"[OSTRZEŻENIE] Wystąpiło katastroficzne zapominanie. Spadek o {drop*100:.1f}%. Wymagana rekalibracja pamięci.")
    print("="*80)


if __name__ == "__main__":
    run_experiment()
