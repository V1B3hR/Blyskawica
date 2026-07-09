"""
Foundation Data Fetcher for Błyskawica's Curriculum.
Automates the retrieval of standard multi-modal grounding datasets (MNIST, CIFAR-10).
"""

import os
import torch
from torchvision import datasets, transforms

def fetch_all():
    """Download foundational datasets to the local workspace."""
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"[FETCH] Starting foundational data harvest to {data_dir}...")
    
    # 1. MNIST (Handwritten digits - basic visual grounding)
    print("- Harvesting MNIST...")
    datasets.MNIST(data_dir, train=True, download=True, transform=transforms.ToTensor())
    
    # 2. CIFAR-10 (Basic objects - complex visual grounding)
    print("- Harvesting CIFAR-10...")
    datasets.CIFAR10(data_dir, train=True, download=True, transform=transforms.ToTensor())
    
    print("[FETCH] Harvest complete. Błyskawica is ready for visual grounding (Module 3).")

if __name__ == "__main__":
    fetch_all()
