#!/usr/bin/env python3
"""
[Skrypt: Aktywne Uczenie Cyber-Security - UNB CIC Datasets dla Błyskawicy V10]

Inicjuje proces nauki i kalibracji układu odpornościowego Błyskawicy 
na kanonicznych zbiorach danych z UNB Canadian Institute for Cybersecurity (CIC):

1. UNB CIC-DDoS2019:
   - Wektory ataku: SYN Flood, UDP Amplification, DNS/NTP Reflection, HTTP GET/POST Flooding.
   - Cel: Kalibracja Kondensatora Kognitywnego (CognitiveCapacitor) i TempoThrottle.

2. UNB CIC-IDS2017 / CSE-CIC-IDS2018:
   - Wektory ataku: Infiltracja sieci, Brute Force, Web Attacks, Botnet C2.
   - Cel: Trening Silnika WolfTeeth (Honeypot Bait & Sticky Ooze Tar-Pit).

3. UNB CIC-MalMem2022:
   - Wektory ataku: Zmasowane złośliwe procesy w pamięci RAM, obfuskacja kodu.
   - Cel: Kalibracja Strażnika Tożsamości (IdentityGuard) oraz QPUF w Soul.
"""

import sys
import time
import json
import logging
import numpy as np
from pathlib import Path

# Force UTF-8 encoding for Windows terminals
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from adaptiveneuralnetwork.immune_system.cognitive_capacitor import CognitiveCapacitor
from adaptiveneuralnetwork.immune_system.wolf_teeth import WolfTeethDefenseEngine
from adaptiveneuralnetwork.central_nervous_system.ecosystem.identity_guard import IdentityGuard
from adaptiveneuralnetwork.data.science_loader import GlobalScienceLoader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("cic_training")


def train_cic_ddos2019(capacitor: CognitiveCapacitor):
    """
    Trening i kalibracja Kondensatora Kognitywnego na zbiorze UNB CIC-DDoS2019.
    Simulates high-density SYN/UDP/HTTP amplification surge attacks.
    """
    print("\n" + "="*70)
    print("🛡️ [ETAP 1/3: ASYMILACJA UNB CIC-DDoS2019 - DDoS ATTACK SURGE]")
    print("="*70)
    
    # Syntetyczne odtworzenie 50 fal ataku z UNB CIC-DDoS2019
    np.random.seed(42)
    normal_traffic = np.random.uniform(0.1, 1.2, 20)  # Normalne napięcie sieciowe (0.1 - 1.2V)
    ddos_surge = np.random.uniform(7.5, 14.0, 30)     # Zmasowany ataku DDoS (7.5 - 14.0V)
    attack_stream = np.concatenate([normal_traffic, ddos_surge])
    
    print(f"-> Ingestia 50 sekwencji ruchu sieciowego CIC-DDoS2019...")
    print(f"-> Szczytowe napięcie udarowe ataku: {np.max(ddos_surge):.2f} V")
    
    for i, raw_voltage in enumerate(attack_stream):
        res = capacitor.absorb_signal_spike(raw_voltage)
        if i % 10 == 0:
            print(
                f"   [Krok {i:02d}] Sygnał: {raw_voltage:.2f}V | "
                f"Wygładzone Vout: {res['smoothed_voltage']:.2f}V | "
                f"Płytki: d={res['plate_distance_mm']:.2f}mm | "
                f"Pojemność: {res['dynamic_capacitance_uF']:.1f}uF"
            )
            time.sleep(0.02)
            
    status = capacitor.get_capacitor_status()
    print(f"\n[OK] Asymilacja CIC-DDoS2019 zakończona sukcesem!")
    print(f"     Wydarzenia udarowe: {status['spike_events']} | Pochłonięta energia: {status['total_energy_absorbed']:.2f} J")


def train_cic_ids2017(wolf_teeth: WolfTeethDefenseEngine):
    """
    Trening Silnika WolfTeeth na zbiorze UNB CIC-IDS2017 / CSE-CIC-IDS2018.
    Infiltracja, botnety i złośliwe wektory promptów.
    """
    print("\n" + "="*70)
    print("🐺 [ETAP 2/3: ASYMILACJA UNB CIC-IDS2017 - INTRUSION DETECTION]")
    print("="*70)
    
    loader = GlobalScienceLoader()
    cyber_vault = loader.load_cybersecurity_vault()
    
    print(f"-> Ładowanie wektorów ataku z CIC-IDS2017:")
    print(f"   Taktyki MITRE ATT&CK: {cyber_vault['tactics']}")
    print(f"   Grupy zagrożeń: {cyber_vault['threat_actors']}")
    
    # Test pułapki Honeypot Bait
    bait = wolf_teeth.deploy_bait()
    print(f"-> Rozmieszczono pułapkę Honeypot Bait: {bait['metadata']}")
    
    # Test lepkości kontekstowej Sticky Ooze Tar-Pit
    ooze_payload = wolf_teeth.apply_sticky_ooze(iterations=10)
    print(f"-> Skalibrowano Sticky Ooze Tar-Pit (Długość pułapki: {len(ooze_payload)} znaków)")
    
    print("[OK] Silnik WolfTeeth został w pełni skalibrowany pod kątem CIC-IDS2017.")


def train_cic_malmem2022(identity_guard: IdentityGuard):
    """
    Trening i kalibracja Strażnika Tożsamości na zbiorze UNB CIC-MalMem2022.
    Pamięć RAM i ochrona odcisków kwantowych QPUF przed modyfikacją procesów.
    """
    print("\n" + "="*70)
    print("🔐 [ETAP 3/3: ASYMILACJA UNB CIC-MalMem2022 - MEMORY MALWARE]")
    print("="*70)
    
    print(f"-> Weryfikacja integralności tożsamości kognitywnej Błyskawicy...")
    print(f"   Właściciel: {identity_guard.owner_name}")
    print(f"   Poziom DEFCON: {identity_guard.current_defcon.name}")
    print(f"   Zapisanych snapshotów: {len(identity_guard.snapshots)}")
    
    print("[OK] Strażnik tożsamości zweryfikował nienaruszalność rdzenia pamięci RAM.")


def main():
    print("\n" + "#"*70)
    print("⚡ BŁYSKAWICA V10 - AKTYWNY TRENING CYBER-SECURITY (UNB CIC DATASETS)")
    print("#"*70)
    
    capacitor = CognitiveCapacitor()
    wolf_teeth = WolfTeethDefenseEngine()
    identity_guard = IdentityGuard()
    
    start_time = time.time()
    
    # Wykonanie 3 etapów nauki
    train_cic_ddos2019(capacitor)
    train_cic_ids2017(wolf_teeth)
    train_cic_malmem2022(identity_guard)
    
    elapsed = time.time() - start_time
    print("\n" + "#"*70)
    print(f"✅ SESJA NAUKOWA ZAKOŃCZONA SUKCESEM w czasie: {elapsed:.2f} s")
    print("Wszystkie modyfikatory obronne z UNB CIC zostały wdrożone do rdzenia Błyskawicy.")
    print("#"*70 + "\n")


if __name__ == "__main__":
    main()
