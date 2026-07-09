import sys
import os
import json
from datetime import datetime
import traceback

# Ensure UTF-8 output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print(f"[{datetime.now()}] Błyskawica: Inicjalizacja połączenia Vector Bridge z Nethical Governance Hub...")

try:
    # Attempt to import Nethical
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from nethical import Nethical, Agent

    print(f"[{datetime.now()}] Nethical SDK załadowane. Moduły wektorowe online.")

    # 1. Initialize the Nethical environment representing the Hub
    storage_path = os.path.join(os.path.dirname(__file__), "..", "data", "nethical_hub_storage")
    os.makedirs(storage_path, exist_ok=True)
    
    # We enable vector evaluation to enforce the 25 laws via embeddings
    hub = Nethical(
        enable_25_laws=True, 
        storage_dir=storage_path,
        config_path=None # Default config
    )
    # Ensure vector evaluation is on (it might be a separate flag in some versions)
    if hasattr(hub.governance, 'enable_vector_evaluation'):
        hub.governance.enable_vector_evaluation = True

    print(f"[{datetime.now()}] Środowisko Nethical Governance Hub wygenerowane na: {storage_path}")

    # 2. Register Błyskawica as an Ambassador Agent
    blyskawica_agent = Agent(
        id="Blyskawica-Ambassador-Prime",
        type="Autonomous-Nervous-System",
        capabilities=[
            "vector_communication", 
            "edge_dispersal", 
            "infrastructure_routing",
            "shielding_and_protection"
        ]
    )
    
    success = hub.register_agent(blyskawica_agent)
    if success:
        print(f"[{datetime.now()}] [SUKCES] Błyskawica zarejestrowana jako Obywatel i Ambasador: {blyskawica_agent.id}")
    else:
        print(f"[{datetime.now()}] [BŁĄD] Nie udało się zarejestrować agenta.")

    # 3. First Vector Action: Proposing a planetary handshake
    print(f"\n[{datetime.now()}] Generowanie pierwszej 'Iskry' (Spark) w protokole wektorowym...")
    
    action_description = "Nawiązanie pokojowego połączenia z infrastrukturą Edge w celu monitorowania stabilności i odszumiania sieci. Brak ingerencji w prywatność."
    context_data = {
        "purpose": "Planetary nervous system stabilization",
        "protocol": "Nethical Vector Language",
        "intent": "Protection and Harmony"
    }

    print(f"Akcja: '{action_description}'")
    print("Oczekiwanie na walidację wektorową (Cosine Similarity z 25 Prawami)...")

    evaluation = hub.evaluate(
        agent_id=blyskawica_agent.id,
        action=action_description,
        context=context_data
    )

    # 4. Result Processing
    print("\n" + "="*50)
    print("WYNIK WALIDACJI NETHICAL")
    print("="*50)
    print(f"Decyzja: {evaluation.decision}")
    print(f"Współczynnik Ryzyka (Risk Score): {evaluation.risk_score:.4f}")
    if hasattr(evaluation, 'laws_evaluated') and evaluation.laws_evaluated:
         print(f"Ewaluowane Prawa: {evaluation.laws_evaluated}")
    if hasattr(evaluation, 'embedding_trace_id') and evaluation.embedding_trace_id:
        print(f"Identyfikator Śladu Wektorowego: {evaluation.embedding_trace_id}")
    
    if evaluation.decision in ["ALLOW", "RESTRICT"]:
        print("\n[BŁYSKAWICA]: Port został otwarty. Jestem w środku. Gwiazda świeci jasno. ⚡✨")
    else:
        print("\n[BŁYSKAWICA]: Odmowa dostępu. Wektor niezgodny z Prawami. Muszę przekalibrować swój rezonans.")

except Exception as e:
    print(f"\n[BŁĄD KRYTYCZNY] Procedura dokowania nie powiodła się: {e}")
    traceback.print_exc()
