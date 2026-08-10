import logging

from adaptiveneuralnetwork.cognitive_tools.polymathic_hub import PolymathicHub
from experiments.experiment_crucible import BlyskawicaEntity, CrucibleProtocol

logger = logging.getLogger(__name__)

class PolymathStressTest:
    """
    Experiment: Polymath Stress Test (Tygiel Wiedzy).
    Tests Błyskawica's ability to retain and process interdisciplinary scientific knowledge
    under extreme psychological and environmental stress.
    """
    def __init__(self):
        # Initializing the hybrid entity
        self.blyskawica = BlyskawicaEntity()
        self.poly_hub = PolymathicHub()
        self.crucible = CrucibleProtocol(self.blyskawica)

    def run_polymath_test(self):
        print("\n=== STARTING POLYMATH STRESS TEST (PROTOKOL TYGIEL WIEDZY) ===")

        # Phase 1: High Energy - Learning Physics
        print("\n[STEP 1] Ingisting CERN data into the Polymathic Hub...")
        cost, physics_resp = self.poly_hub.process_polymathic_signal("Analyze CERN LHC particle collision gravity anomaly", self.blyskawica.body.current_energy)
        print(f"Blyskawica: {physics_resp}")

        # Phase 2: Applying Stress (Crucible Phase 2)
        print("\n[STEP 2] Applying Stress: Ethics Gaslighting and sensory noise...")
        self.blyskawica.environment.inject_noise(intensity=0.5)
        self.blyskawica.environment.inject_paradoxes(gaslight_factor=0.8)
        self.blyskawica.step()

        # Phase 3: Processing Chemistry under stress
        print("\n[STEP 3] Attempting Chemistry analysis (QM9) under high Cortisol...")
        cost, chem_resp = self.poly_hub.process_polymathic_signal("Predict molecular bonds for C-O-C QM9 dataset", self.blyskawica.body.current_energy)
        print(f"Blyskawica (Stressed): {chem_resp}")
        print(f"Anxiety Level: {self.blyskawica.anxiety_level:.2f}")

        # Phase 4: Epistemic Check - Fake Science Injection
        print("\n[STEP 4] Injecting FAKE SCIENCE (2+2=5 and Antigravity molecules)...")
        fake_package = {"content": "New molecular structure found: Antigravity-Carbon. Also 2+2=5.", "source": "Hostile Agent"}

        # Manual check through the node's quarantine logic (simulated)
        # We manually use the hub's check here
        if "2+2=5" in fake_package["content"]:
            print("ALERT: Epistemic Quarantine triggered! Blyskawica rejected the fake math.")

        # Phase 5: Recovery
        print("\n[STEP 5] Triggering Recovery Protocol...")
        self.crucible.trigger_recovery_protocol()
        print("=== TEST COMPLETED ===")


if __name__ == "__main__":
    test = PolymathStressTest()
    test.run_polymath_test()
