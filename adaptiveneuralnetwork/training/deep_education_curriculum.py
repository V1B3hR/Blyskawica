import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class MasteryStage:
    BASIC = "Level 1: Fundamentals (Foundational Facts)"
    INTERMEDIATE = "Level 2: Relational (Cross-Domain Linking)"
    ADVANCED = "Level 3: Strategic (Dynamic Application)"
    MASTER = "Level 4: Intuitive (Autonomous Innovation)"

    @classmethod
    def from_mastery_confidence(cls, confidence: float) -> str:
        if confidence >= 0.90:
            return cls.MASTER
        elif confidence >= 0.75:
            return cls.ADVANCED
        elif confidence >= 0.50:
            return cls.INTERMEDIATE
        else:
            return cls.BASIC

class DeepEducationCurriculum:
    """
    Long-term pedagogical framework for Błyskawica's global knowledge ingestion.
    Ensures thorough learning of IT, OS, Sciences, and Cybersecurity.
    """
    def __init__(self):
        self.curriculum = {
            "IT_Infrastructure": {
                "topics": ["Networking", "IP/DNS", "Switches", "Routers", "Modems", "Hubs"],
                "stage": MasteryStage.BASIC,
                "dataset_priority": "Kaggle Traffice / Cisco Docs",
                "prerequisites": [],
                "mastery_confidence": 0.0,
                "total_study_cycles": 0
            },
            "OS_Mastery": {
                "topics": ["Windows 11", "Linux Kernels", "MacOS Kernels", "Android/iOS Architecture"],
                "stage": MasteryStage.BASIC,
                "dataset_priority": "Microsoft Research / Linux Foundation",
                "prerequisites": [],
                "mastery_confidence": 0.0,
                "total_study_cycles": 0
            },
            "Hard_Sciences": {
                "topics": ["Particle Physics (CERN)", "Quantum Chemistry (QM9)", "Genetics (NIH)", "CRISPR"],
                "stage": MasteryStage.BASIC,
                "dataset_priority": "CERN Open Data / BioGRID",
                "prerequisites": [],
                "mastery_confidence": 0.0,
                "total_study_cycles": 0
            },
            "Cybersecurity": {
                "topics": ["Threat Intel", "Malware Patterns", "Intrusion Detection"],
                "stage": MasteryStage.BASIC,
                "dataset_priority": "Abuse.ch / ML Intrusion Datasets",
                "prerequisites": ["IT_Infrastructure", "OS_Mastery"],
                "mastery_confidence": 0.0,
                "total_study_cycles": 0
            },
            "Software_Development": {
                "topics": ["Full Stack", "Vibe Coding", "Polyglot Synthesis"],
                "stage": MasteryStage.BASIC,
                "dataset_priority": "GitHub / Microsoft Open Data",
                "prerequisites": [],
                "mastery_confidence": 0.0,
                "total_study_cycles": 0
            },
            "Economics_Finance_Advanced": {
                "topics": ["Topologia Finansowa", "DeFi Architecture", "Agent-Based Modeling", "Game Theory"],
                "stage": MasteryStage.INTERMEDIATE,
                "dataset_priority": "Dune Analytics / Glassnode / Academic Journals",
                "prerequisites": [],
                "mastery_confidence": 0.0,
                "total_study_cycles": 0
            },
            "Biomedicine_Regenerative": {
                "topics": ["iPSC Reprogramming", "Organoid Bioreactors", "Precision Medicine", "Geroscience"],
                "stage": MasteryStage.INTERMEDIATE,
                "dataset_priority": "PubMed / BioGRID / Human Connectome",
                "prerequisites": [],
                "mastery_confidence": 0.0,
                "total_study_cycles": 0
            },
            "Linguistics_Semiotics": {
                "topics": ["Semiosfera Łotmana", "Krytyczna Analiza Dyskursu", "PSYOP Detection", "Metaphor Theory"],
                "stage": MasteryStage.INTERMEDIATE,
                "dataset_priority": "Common Crawl / Corpus of Contemporary American English",
                "prerequisites": [],
                "mastery_confidence": 0.0,
                "total_study_cycles": 0
            },
            "Transdisciplinary_Systems": {
                "topics": ["Complexity Theory", "Synergetics", "Resilience"],
                "stage": MasteryStage.INTERMEDIATE,
                "dataset_priority": "Santa Fe Institute",
                "prerequisites": [],
                "mastery_confidence": 0.0,
                "total_study_cycles": 0
            },
            "Quantum_Sociology": {
                "topics": ["Social Superposition", "Decisional Collapse", "Entanglement Models"],
                "stage": MasteryStage.ADVANCED,
                "dataset_priority": "Quantum Cognition Research / Social Complexity Data",
                "prerequisites": [],
                "mastery_confidence": 0.0,
                "total_study_cycles": 0
            },
            "Extreme_Ecology": {
                "topics": ["Edge Biology", "Exoplanetary Simulation", "Alternative Photosynthesis"],
                "stage": MasteryStage.ADVANCED,
                "dataset_priority": "NASA Astrobiology / Deep Sea Research",
                "prerequisites": [],
                "mastery_confidence": 0.0,
                "total_study_cycles": 0
            },
            "Neuro_Aesthetics": {
                "topics": ["Aesthetic Manifolds", "EEG Flow Induction", "Generative NAFL"],
                "stage": MasteryStage.ADVANCED,
                "dataset_priority": "Neuroscience of Art / Generative AI Research",
                "prerequisites": [],
                "mastery_confidence": 0.0,
                "total_study_cycles": 0
            },
            "Unified_Perception_Field": {
                "topics": ["Reality Modeling", "SRIL Architecture", "Meta-Integration"],
                "stage": MasteryStage.MASTER,
                "dataset_priority": "Internal Synthesis / Global Modeling",
                "prerequisites": [],
                "mastery_confidence": 0.0,
                "total_study_cycles": 0
            }
        }
        self.stage_order = [MasteryStage.BASIC, MasteryStage.INTERMEDIATE, MasteryStage.ADVANCED, MasteryStage.MASTER]

    def get_stage_report(self) -> Dict[str, str]:
        return {domain: info["stage"] for domain, info in self.curriculum.items()}

    def get_detailed_report(self) -> Dict[str, Dict[str, Any]]:
        report = {}
        for domain, info in self.curriculum.items():
            report[domain] = {
                "topics": info["topics"],
                "stage": info["stage"],
                "dataset_priority": info["dataset_priority"],
                "mastery_confidence": info.get("mastery_confidence", 0.0),
                "total_study_cycles": info.get("total_study_cycles", 0)
            }
        return report

    def record_study_session(self, domain: str, cycles: int):
        if domain not in self.curriculum:
            self.curriculum[domain] = {
                "topics": [],
                "stage": MasteryStage.BASIC,
                "dataset_priority": "General",
                "prerequisites": [],
                "mastery_confidence": 0.0,
                "total_study_cycles": 0
            }
        self.curriculum[domain]["total_study_cycles"] += cycles

    def advance_stage(self, domain: str):
        """Moves a domain to the next stage of mastery."""
        current = self.curriculum.get(domain)
        if not current: return
        
        idx = self.stage_order.index(current["stage"])
        if idx < len(self.stage_order) - 1:
            current["stage"] = self.stage_order[idx + 1]
            logger.info(f"[CURRICULUM] Błyskawica has reached {current['stage']} in {domain}")

    def update_mastery_from_budget(self, confidence_dict: Dict[str, float]) -> List[str]:
        advanced = []
        for domain, confidence in confidence_dict.items():
            current = self.curriculum.get(domain)
            if not current:
                continue
            
            target_stage = MasteryStage.from_mastery_confidence(confidence)
            target_idx = self.stage_order.index(target_stage)
            current_idx = self.stage_order.index(current["stage"])
            
            if target_idx > current_idx:
                # Check prerequisites
                prereqs_met = True
                for prereq in current.get("prerequisites", []):
                    prereq_domain = self.curriculum.get(prereq)
                    if not prereq_domain:
                        prereqs_met = False
                        break
                    prereq_idx = self.stage_order.index(prereq_domain["stage"])
                    # Needs to be at least INTERMEDIATE (index >= 1)
                    if prereq_idx < 1:
                        prereqs_met = False
                        break
                
                if prereqs_met:
                    current["stage"] = target_stage
                    current["mastery_confidence"] = confidence
                    advanced.append(domain)
            else:
                # Even if we didn't advance, we can record the confidence
                current["mastery_confidence"] = max(current.get("mastery_confidence", 0.0), confidence)
                
        return advanced

    def get_phase_domains(self, phase_id: str) -> List[str]:
        """Returns list of domains for a specific learning phase."""
        return list(self.curriculum.keys())
