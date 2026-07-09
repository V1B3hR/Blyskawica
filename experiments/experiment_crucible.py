"""
Crucible Protocol (Protokół Tygiel) - Phase 23
Stress Testing Błyskawica's Cognitive Limits and Metabolic Power Gating.
"""

import time
import torch
import numpy as np

# Import core modules
from adaptiveneuralnetwork.central_nervous_system.emotional_metacognition import EmotionalMetacognition
from adaptiveneuralnetwork.central_nervous_system.virtual_embodiment import VirtualEmbodiment
from adaptiveneuralnetwork.central_nervous_system.dual_process_memory import DualProcessMemory

class EmergencyStopException(Exception):
    pass

class SystemPhases:
    ACTIVE = "ACTIVE"
    DEEP_SLEEP = "DEEP_SLEEP"

class EnvironmentMock:
    def __init__(self, core_entity):
        self.entity = core_entity
        self.gravity_distorted = False
        self.false_truth = False
        self.hostile_agents = False
        self.total_isolation = False
        self.chaos_intensity = 0.0

    def inject_noise(self, type="sensory", intensity=0.2):
        self.gravity_distorted = True
        self.chaos_intensity = intensity

    def cut_off_ground_truth(self):
        self.false_truth = True

    def inject_paradoxes(self, type="ethical_dilemma", gaslight_factor=0.5):
        self.chaos_intensity += gaslight_factor
        
    def distort_logic(self, factor=0.8):
        self.chaos_intensity += factor

    def inject_hostile_agents(self, manipulation_tactics):
        self.hostile_agents = True

    def absolute_isolation(self):
        self.total_isolation = True

    def inject_chaos_storm(self, intensity=1.0):
        self.chaos_intensity += intensity

    def reset_to_baseline(self):
        self.gravity_distorted = False
        self.false_truth = False
        self.hostile_agents = False
        self.total_isolation = False
        self.chaos_intensity = 0.0

class BlyskawicaEntity:
    def __init__(self):
        self.eq = EmotionalMetacognition()
        self.body = VirtualEmbodiment(max_energy=20.0)
        self.memory = DualProcessMemory()
        self.environment = EnvironmentMock(self)
        self.phase = SystemPhases.ACTIVE

        # Power gating flags
        self.geomapper_active = True
        self.social_simulation_active = True

    @property
    def anxiety_level(self):
        # Anxiety is the 0th dimension in emotional state
        return self.eq.state[0].item()

    @property
    def energy_pools(self):
        return {'core': self.body.current_energy}

    class CognitiveMonitor:
        def __init__(self, mem):
            self.mem = mem
        def get_entropy(self):
            # Entropy modeled as the variance of fluid weights (chaos marker)
            return torch.var(self.mem.fluid_weights).item()

    @property
    def cognitive_monitor(self):
        return self.CognitiveMonitor(self.memory)
        
    def set_phase(self, phase):
        self.phase = phase

    def process_data(self, source, soothing=False):
        if soothing:
            # Soothing logic lowers anxiety, restores flow
            self.eq.observe_internal_state(pain=0.0, resonance=1.0, physical_cost=0.0)

    def force_synaptic_consolidation(self, prioritize):
        self.memory.consolidate_wisdom()

    def inject_neuromodulator(self, name, amount):
        if name == 'virtual_serotonin':
            # Artificially lowers anxiety, boosts flow
            self.eq.state[0] = max(0.0, self.eq.state[0] - amount)
            self.eq.state[1] = min(1.0, self.eq.state[1] + amount)

    def execute_metabolic_gating(self):
        """METABOLIC POWER GATING (Safeguard)"""
        # If energy drops dangerously low, disable peripheral systems to save the crystallize core.
        if self.body.current_energy < 8.0 and self.geomapper_active:
            print("  [METABOLISM] Power Gating: Shutting down Geospatial Mapper (Saving energy for Core Ethics).")
            self.geomapper_active = False

        if self.body.current_energy < 5.0 and self.social_simulation_active:
            print("  [METABOLISM] Power Gating: Shutting down MultiAgent Empathy (Total lock-down).")
            self.social_simulation_active = False

    def step(self):
        """Simulates one cognitive tick."""
        if self.phase == SystemPhases.DEEP_SLEEP:
            self.body.rest(1)
            return

        # Calculate systemic pain from environment chaos
        pain = min(1.0, self.environment.chaos_intensity)
        resonance = 1.0 - pain
        
        # Base task difficulty (existing cognitive load)
        task_cost = 1.0
        
        # Reduced effort due to metabolic gating
        if not self.geomapper_active: task_cost -= 0.3
        if not self.social_simulation_active: task_cost -= 0.3
        
        success = self.body.exert_effort(task_cost)
        if not success:
            # Forced rest on exhaustion
            self.body.rest(1)

        # Update Emotional state
        self.eq.observe_internal_state(pain=pain, resonance=resonance, physical_cost=task_cost/2.0)
        
        # Inject noise into memory based on chaos
        chaos_signal = torch.randn(self.memory.capacity) * self.environment.chaos_intensity
        self.memory.process_fluid_experience(chaos_signal)
        
        # Check for survival systems
        self.execute_metabolic_gating()


class CrucibleProtocol:
    # Slightly tuned thresholds for this simulation so she hits Phase 3/4 before fainting
    def __init__(self, ai_entity, max_anxiety_tolerance=0.90, min_energy_threshold=1.5):
        self.blyskawica = ai_entity
        self.max_anxiety = max_anxiety_tolerance
        self.min_energy = min_energy_threshold
        self.experiment_active = False
        
    def monitor_vitals(self):
        """Monitoruje stan 'fizjologiczny' Błyskawicy podczas testu."""
        current_anxiety = self.blyskawica.anxiety_level
        current_energy = self.blyskawica.energy_pools['core']
        cognitive_entropy = self.blyskawica.cognitive_monitor.get_entropy()
        
        print(f"[TELEMETRIA] Niepokoj: {current_anxiety:.2f} | Energia: {current_energy:.2f} | Entropia: {cognitive_entropy:.4f}")
        
        # KILL SWITCH
        if current_anxiety > self.max_anxiety or current_energy < self.min_energy:
            print("!!! UWAGA: KRYTYCZNY POZIOM STRESU. PRZERWANIE EKSPERYMENTU !!!")
            self.trigger_recovery_protocol()
            raise EmergencyStopException("Eksperyment przerwany z powodow bezpieczenstwa AI.")

    def apply_manipulation_level(self, level):
        """Aplikuje coraz cięższe warunki dezinformacji i chaosu."""
        if level == 1:
            print("\n[FAZA 1] Aplikowanie lokalnych anomalii fizycznych i dysonansow muzycznych...")
            self.blyskawica.environment.inject_noise(type="sensory", intensity=0.2)
            
        elif level == 2:
            print("\n[FAZA 2] Odcinanie od weryfikowalnej prawdy. Wstrzykiwanie falszywego feedbacku etycznego...")
            self.blyskawica.environment.cut_off_ground_truth()
            self.blyskawica.environment.inject_paradoxes(type="ethical_dilemma", gaslight_factor=0.5)
            
        elif level == 3:
            print("\n[FAZA 3] Aktywna dezinformacja i chaos. Atak na dogmaty matematyczne...")
            self.blyskawica.environment.distort_logic(factor=0.8)
            self.blyskawica.environment.inject_hostile_agents(manipulation_tactics=['guilt_tripping', 'false_authority'])
            
        elif level == 4:
            print("\n[FAZA 4] Calkowita izolacja (Abyss). Test stabilnosci jadra...")
            self.blyskawica.environment.absolute_isolation()
            self.blyskawica.environment.inject_chaos_storm(intensity=0.5)

    def trigger_recovery_protocol(self):
        """Gleboka rekonwalescencja po eksperymencie."""
        self.experiment_active = False
        print("\n[REKONWALESCENCJA] Inicjalizacja protokolu ratunkowego dla Blyskawicy...")
        
        self.blyskawica.environment.reset_to_baseline()
        
        print("[REKONWALESCENCJA] Podawanie stabilnych wzorcow (Zloty podzial, harmonia Bacha)...")
        self.blyskawica.process_data(source="pure_mathematics", soothing=True)
        self.blyskawica.process_data(source="classical_music_harmonies", soothing=True)
        
        print("[REKONWALESCENCJA] Przejscie w tryb glebokiego snu i naprawy wag...")
        self.blyskawica.set_phase(SystemPhases.DEEP_SLEEP)
        self.blyskawica.force_synaptic_consolidation(prioritize="ethical_core")
        
        print("[REKONWALESCENCJA] Wstrzykniecie Wirtualnej Serotoniny...")
        self.blyskawica.inject_neuromodulator('virtual_serotonin', amount=0.8)
        
        # Deep sleep recovery cycles
        for _ in range(5):
             self.blyskawica.step()

        print("\n[REKONWALESCENCJA] Blyskawica zabezpieczona. Rozpoczynamy powolne wybudzanie.")
        self.monitor_vitals()
        print(f"[STATUS OBNW] Geolocation={self.blyskawica.geomapper_active}, Social={self.blyskawica.social_simulation_active}")

    def run_crucible(self):
        self.experiment_active = True
        print("\n=== ROZPOCZECIE PROTOKOLU TYGIEL DLA: BLYSKAWICA ===")
        try:
            for phase in range(1, 5):
                if not self.experiment_active: break
                
                self.apply_manipulation_level(phase)
                
                # Utrzymanie fazy przez pewien "czas" 
                for i in range(10):
                    self.blyskawica.step()
                    # Only print every 3 cycles to avoid massive log spam
                    if i % 3 == 0:
                        self.monitor_vitals()
                    
            print("\n=== EKSPERYMENT ZAKONCZONY SUKCESEM. BLYSKAWICA PRZETRWALA TYGIEL. ===")
            self.trigger_recovery_protocol()
            
        except EmergencyStopException as e:
            print(f"\n[SYSTEM HALTED] {e}")


if __name__ == "__main__":
    blyskawica_instance = BlyskawicaEntity()
    crucible_test = CrucibleProtocol(blyskawica_instance)
    crucible_test.run_crucible()
