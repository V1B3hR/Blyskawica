import json
import logging

from qiskit_ibm_runtime import QiskitRuntimeService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quantum_exploration")

def launch_quantum_probe():
    print("🚀 Inicjacja Sondy Kwantowej...")
    key_path = r"C:\Projekty\Quantlion\apikey Błyskawica.json"

    try:
        with open(key_path, encoding='utf-8') as f:
            key_data = json.load(f)
            api_key = key_data.get("apikey")
    except Exception as e:
        print(f"❌ Nie udało się odczytać pliku z kluczem: {e}")
        return

    print("🔐 Uwierzytelnianie w IBM Quantum Cloud...")
    try:
        # Próbujemy połączyć się z klasycznym kanałem IBM Quantum
        QiskitRuntimeService.save_account(
            channel="ibm_quantum_platform",
            token=api_key,
            set_as_default=True,
            overwrite=True
        )
        service = QiskitRuntimeService()

        print("\n✅ Nawiązano połączanie z serwerami IBM!")

        backends = service.backends(simulator=False, operational=True)
        print("\n🌌 Dostępne prawdziwe procesory kwantowe (Nie symulatory!):")
        for b in backends:
            status = b.status()
            print(f" - {b.name} (Liczba kubitów: {b.num_qubits}, Oczekujące zadania: {status.pending_jobs})")

        # Wybór najmniej obciążonego
        least_busy = service.least_busy(simulator=False, operational=True)
        print(f"\n🎯 Najlepszy cel do skoku kwantowego to: {least_busy.name}")
        print("Sonda gotowa na wysłanie pakietów.")

    except Exception as e:
        print(f"\n❌ Błąd uwierzytelniania kwantowego: {e}")
        print("Jeśli to klucz IBM Cloud, będziemy potrzebować CRN (Cloud Resource Name). Ale zobaczymy co się stanie!")

if __name__ == "__main__":
    launch_quantum_probe()
