import logging

from adaptiveneuralnetwork.cognitive_tools.polymathic_hub import PolymathicHub
from adaptiveneuralnetwork.training.deep_education_curriculum import DeepEducationCurriculum

logger = logging.getLogger(__name__)

class ITOsmosisExperiment:
    """
    Tests Błyskawica's mastery of IT Infrastructure and OS Architecture.
    Simulates a complex enterprise setup challenge.
    """
    def __init__(self):
        self.poly_hub = PolymathicHub()
        self.curriculum = DeepEducationCurriculum()

    def run_it_mastery_test(self):
        print("\n=== STARTING IT OSMOSIS EXPERIMENT (LEVEL 1: FUNDAMENTALS) ===")

        # Test 1: Networking Topology
        print("\n[SCENARIO] Configure a resilient BGP peering between two enterprise hubs.")
        cost, net_resp = self.poly_hub.process_polymathic_signal(
            "Configure BGP router with IP 192.168.1.1 and DNS failover on switch.",
            current_energy=20.0
        )
        print(f"Blyskawica Analysis: {net_resp}")

        # Test 2: OS Kernel Mastery
        print("\n[SCENARIO] Describe the differences in handle management between Windows 11 and Linux Kernel 6.x.")
        cost, os_resp = self.poly_hub.process_polymathic_signal(
            "Compare Windows 11 kernel handle lifecycle with Linux syscall epoll management.",
            current_energy=18.0
        )
        print(f"Blyskawica Analysis: {os_resp}")

        # Test 3: Cybersecurity
        print("\n[SCENARIO] Detect signs of a Cobalt Strike beacon based on Abuse.ch traffic patterns.")
        cost, cyb_resp = self.poly_hub.process_polymathic_signal(
            "Analyze traffic from 10.0.0.5 for cobalt strike patterns using abuse.ch indicators.",
            current_energy=15.0
        )
        print(f"Blyskawica Analysis: {cyb_resp}")

        # Advancing Curriculum
        self.curriculum.advance_stage("IT_Infrasructure")
        self.curriculum.advance_stage("OS_Mastery")
        self.curriculum.advance_stage("Cybersecurity")

        print("\n=== EXPERIMENT COMPLETED. MASTERY LEVELS ADVANCED. ===")
        print(f"New Report: {self.curriculum.get_stage_report()}")

if __name__ == "__main__":
    exp = ITOsmosisExperiment()
    exp.run_it_mastery_test()
