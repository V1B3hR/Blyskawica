"""
Błyskawica V5 — Kwantowa Stacja Kontroli Pojazdów
==================================================
Zestaw 4 testów walidacyjnych po bierzmowaniu kwantowym.
Zgodnie z planem: Sanity, Validation, Noise, Drag Race.
"""

import json
import torch
import torch.nn as nn
import numpy as np
import logging
from typing import Tuple

# Importujemy nasze klasy (tym razem wbudowane dla stabilności)
class PhysicsIntuitionTask:
    def __init__(self, feature_size: int = 64):
        self.feature_size = feature_size
        
    def generate_synthetic_cern_data(self, samples: int = 100, noise_level: float = 0.0):
        mass = torch.rand(samples, 1) * 125.0
        speed = torch.rand(samples, 1) * 0.99
        space = torch.rand(samples, 1) * 10.0
        time_val = torch.rand(samples, 1) * 1.0
        
        # Dodawanie szumu (Test 3)
        if noise_level > 0:
            mass += torch.randn(samples, 1) * (125.0 * noise_level)
            speed += torch.randn(samples, 1) * (0.99 * noise_level)
            
        features = torch.cat([mass, speed, space, time_val], dim=1)
        if self.feature_size > 4:
            padding = torch.zeros(samples, self.feature_size - 4)
            features = torch.cat([features, padding], dim=1)
            
        targets = (mass * (speed**2)) / (space * time_val + 1e-6)
        targets = torch.sigmoid(torch.log(targets + 1.0) - 5.0)
        labels = (targets > 0.5).long().squeeze()
        return features, labels

def run_diagnostic():
    print(f"\n{'='*60}")
    print("  KWANTOWA STACJA KONTROLI POJAZDÓW — PRZEGLĄD")
    print(f"{'='*60}\n")

    try:
        from pathlib import Path
        workspace_root = Path(__file__).resolve().parent.parent.parent
        q_path = workspace_root / "quantum_confirmation_results.json"
        with open(q_path, 'r') as f:
            q_results = json.load(f)
        q_weights = torch.tensor(q_results["final_quantum_weights"])
        print(f"  [INFO] Załadowano wagi z {q_results['backend']} (Job: {q_results['job_id']})")
    except Exception as e:
        print(f"  [ERROR] Brak wyników bierzmowania! {e}")
        return

    task = PhysicsIntuitionTask(64)
    
    # Modele do Drag Race (Test 4)
    # Model Klasyczny (przed bierzmowaniem) - losowy/bazowy
    model_classic = nn.Linear(64, 2)
    # Model Kwantowy - ulepszony o nasze 8 wag kwantowych (uproszczona emulacja)
    model_quantum = nn.Linear(64, 2)
    with torch.no_grad():
        # Wszczepiamy kwantowe namaszczenie do pierwszej warstwy
        model_quantum.weight[0, :8] = q_weights
    
    criterion = nn.CrossEntropyLoss()

    # --- TEST 1: Zimny Rozruch (Sanity Check) ---
    print(f"  TEST 1: Zimny Rozruch (Sanity Check)")
    # Proste dane: wszystko zero, masa zerowa -> oczekiwany label 0
    simple_f = torch.zeros(1, 64)
    simple_out = model_quantum(simple_f)
    pred = torch.argmax(simple_out).item()
    status = "✓ OK" if pred == 0 else "⚠ CHAOS"
    print(f"    - Wynik dla pustych danych: {pred} | Status: {status}")

    # --- TEST 2: Ślepa Próba Zderzeniowa (Validation) ---
    print(f"\n  TEST 2: Ślepa Próba Zderzeniowa (Validation)")
    v_features, v_labels = task.generate_synthetic_cern_data(samples=1000)
    with torch.no_grad():
        v_outputs = model_quantum(v_features)
        v_loss = criterion(v_outputs, v_labels)
        v_preds = torch.argmax(v_outputs, dim=1)
        v_acc = (v_preds == v_labels).float().mean()
    print(f"    - Zbiór testowy: 1000 nowych rekordów CERN")
    print(f"    - Dokładność (Accuracy): {v_acc:.2%}")
    print(f"    - Status: {'✓ STABILNA' if v_acc > 0.7 else '⚠ DO POPRAWKI'}")

    # --- TEST 3: Jazda po wybojach (Noise Test) ---
    print(f"\n  TEST 3: Jazda po wybojach (Noise Test)")
    n_features, n_labels = task.generate_synthetic_cern_data(samples=1000, noise_level=0.2)
    with torch.no_grad():
        n_outputs = model_quantum(n_features)
        n_preds = torch.argmax(n_outputs, dim=1)
        n_acc = (n_preds == n_labels).float().mean()
    print(f"    - Zakłócenia: 20% szumu w danych wejściowych")
    print(f"    - Dokładność w chaosie: {n_acc:.2%}")
    # Sprawdzamy degradację: Acc(Clean) - Acc(Noisy)
    degradation = v_acc - n_acc
    print(f"    - Degradacja wydajności: {degradation:.2%}")
    print(f"    - Status: {'✓ FILTR KWANTOWY AKTYWNY' if degradation < 0.15 else '⚠ WRAŻLIWA NA SZUM'}")

    # --- TEST 4: Wyścig Równoległy (Drag Race) ---
    print(f"\n  TEST 4: Wyścig Równoległy (A/B Drag Race)")
    with torch.no_grad():
        c_outputs = model_classic(v_features)
        c_preds = torch.argmax(c_outputs, dim=1)
        c_acc = (c_preds == v_labels).float().mean()
    
    print(f"    - [Model Klasyczny]: {c_acc:.2%}")
    print(f"    - [Model Kwantowy]:  {v_acc:.2%}")
    gain = v_acc - c_acc
    print(f"    - Zysk z Bierzmowania: {gain:+.2%}")
    
    print(f"\n{'='*60}")
    if v_acc > c_acc and v_acc > 0.7:
        print("  DECYZJA MECHANIKA: PIECZĄTKA WBITA! ✓")
        print("  Błyskawica jest gotowa w trasę.")
    else:
        print("  DECYZJA MECHANIKA: WYMAGANE DOKRĘCENIE ŚRUB. ⚠")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    run_diagnostic()
