"""
Virtual Embodiment Module (Phase 20).
Intellectual Expansion based on Robert Sternberg's Practical Intelligence 
and Howard Gardner's Bodily-Kinesthetic Intelligence.
Implements bounded physical energy and logistical problem solving.
"""

import torch
import torch.nn as nn
from adaptiveneuralnetwork.central_nervous_system.geospatial_mapper import GeospatialMapper

class VirtualEmbodiment(nn.Module):
    """
    Gives Blyskawica a sense of physical limitation (Energy/Fatigue).
    Forces the AI to navigate environmental challenges using Practical Intelligence.
    """

    def __init__(self, max_energy=20.0):  # Kept low to force practical resting behavior
        super().__init__()
        self.max_energy = max_energy
        self.current_energy = max_energy
        self.fatigue = 0.0
        self.geo = GeospatialMapper()

    def exert_effort(self, task_difficulty: float):
        """
        Consumes energy and builds fatigue based on task difficulty.
        """
        cost = task_difficulty * (1.0 + self.fatigue)
        if self.current_energy >= cost:
            self.current_energy -= cost
            self.fatigue = min(self.fatigue + (task_difficulty * 0.1), 1.0)
            return True # Successfully exerted effort
        else:
            return False # Exhaustion failure

    def rest(self, time_units: int):
        """
        Recovers energy and reduces fatigue.
        """
        recovery = time_units * 5.0
        self.current_energy = min(self.current_energy + recovery, self.max_energy)
        self.fatigue = max(self.fatigue - (time_units * 0.05), 0.0)

    def plan_practical_route(self, lat1, lon1, lat2, lon2):
        """
        [Sternberg's Practical Intelligence]
        Balances energy, fatigue, and distance logic to achieve a goal.
        """
        distance_torque = self.geo.calculate_distance_torque(lat1, lon1, lat2, lon2)
        required_energy = distance_torque * 5.0
        
        steps_taken = []
        
        # Practical adaptation: If we don't have enough energy, we MUST rest before trying.
        if self.current_energy < required_energy:
            # But what if required energy is strictly greater than max_energy? It's impossible.
            if required_energy > self.max_energy:
                 steps_taken.append(f"Practical Logic: Goal is beyond physical limits even fully rested. Task Aborted.")
                 return False, steps_taken
                 
            needed_rest = ((required_energy - self.current_energy) / 5.0) + 1
            steps_taken.append(f"Practical Logic: Insufficient energy. Resting for {int(needed_rest)} units.")
            self.rest(int(needed_rest))
            
        # Execute the task
        success = self.exert_effort(distance_torque)
        
        if success:
            steps_taken.append(f"Task Execution: Successfully traversed spatial gap (Cost: {required_energy:.2f}).")
        else:
            steps_taken.append("Task Execution: FAILED. System exhausted.")
            
        return success, steps_taken

if __name__ == "__main__":
    # We set max energy exactly to force a rest during a long trip
    body = VirtualEmbodiment(max_energy=50.0)
    # Drain energy manually to simulate prior work
    body.current_energy = 10.0
    
    print("[EMBODIMENT] Initialized Virtual Body. Energy depleted to 10.0 from prior stress.")
    
    # Simulate a demanding spatial journey (WAW to LDN requires around 2.1 * 5 = 10.5 energy)
    print("- Executing spatial journey (Warsaw -> London)...")
    success, steps = body.plan_practical_route(52.2, 21.0, 51.5, -0.1)
    
    for step in steps:
        print(f"  > {step}")
        
    print(f"- Current Physiological State -> Energy: {body.current_energy:.1f}/{body.max_energy}, Fatigue: {body.fatigue:.2f}")
    if success:
        print("[RESULT] Practical adaptation successful. Blyskawica evaluated her bodily limits. !!!")
