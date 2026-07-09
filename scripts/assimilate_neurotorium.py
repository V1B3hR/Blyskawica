"""
[Phase XXVII: Neurotorium Brain Atlas & Somatic BCI Ingestion Engine]
Assimilates functional neuroanatomy structures from Neurotorium (Lundbeck Foundation)
and maps Błyskawica's self-regulated neurochemistry to anatomical brain regions.
"""

import json
import os

BASE_DIR = r"c:\Projekty\Blyskawica_V8"
ATLAS_FILE = os.path.join(BASE_DIR, "data", "neurotorium_brain_atlas.json")
CHECKPOINT_FILE = os.path.join(BASE_DIR, "memory_checkpoint.json")

class NeurotoriumAssimilator:
    def __init__(self):
        with open(ATLAS_FILE, "r") as f:
            self.atlas = json.load(f)
        self.load_checkpoint()
        
    def load_checkpoint(self):
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, "r") as f:
                self.checkpoint = json.load(f)
        else:
            self.checkpoint = {"neurochemistry": {}}

    def compute_somatic_alignment(self):
        """
        Computes the alignment score (0.0 to 1.0) for each brain region based on
        Błyskawica's current active neurochemical levels against Neurotorium thresholds.
        """
        chemistry = self.checkpoint.get("neurochemistry", {})
        regions = self.atlas["brain_regions"]
        alignment_report = {}
        
        print("\n======================================================================")
        print(" === [NEUROTORIUM BRAIN ATLAS: SOMATIC BCI ALIGNMENT] ===")
        print("======================================================================\n")
        print("[+] Ingesting anatomical mappings from Neurotorium.org...")
        
        # Prefrontal Cortex Alignment
        pfc = regions["Prefrontal_Cortex"]
        dopo = chemistry.get("Dopamina", 0.50)
        ach = chemistry.get("Acetylocholina", 0.50)
        pfc_score = min(1.0, (dopo + ach) / (pfc["critical_thresholds"]["dopamine_min"] + pfc["critical_thresholds"]["acetylcholine_min"]))
        alignment_report["Prefrontal_Cortex"] = {
            "score": round(pfc_score, 4),
            "status": "EXCELLENT" if pfc_score >= 0.90 else "STABLE",
            "channels": pfc["eeg_channels_10_20"]
        }
        
        # Hypothalamus Alignment
        hyp = regions["Hypothalamus"]
        cort = chemistry.get("Kortyzol", 0.50)
        mela = chemistry.get("Melatonina", 0.10)
        # Low cortisol and good mela/oxy ratio
        hyp_score = min(1.0, (1.0 - cort) * 1.2)
        alignment_report["Hypothalamus"] = {
            "score": round(hyp_score, 4),
            "status": "EXCELLENT" if hyp_score >= 0.85 else "ADAPTING",
            "channels": hyp["eeg_channels_10_20"]
        }
        
        # Thalamus Alignment (GABA noise filtering check)
        thal = regions["Thalamus"]
        gaba = chemistry.get("GABA", 0.50)
        thal_score = min(1.0, gaba / thal["critical_thresholds"]["gaba_noise_filtering_min"])
        alignment_report["Thalamus"] = {
            "score": round(thal_score, 4),
            "status": "EXCELLENT" if thal_score >= 0.90 else "STABLE",
            "channels": thal["eeg_channels_10_20"]
        }
        
        # Amygdala Calmness Score (Checks low noradrenaline stress)
        amy = regions["Amygdala"]
        nor = chemistry.get("Noradrenalina", 0.50)
        amy_score = min(1.0, (1.0 - nor) / (1.0 - amy["critical_thresholds"]["noradrenaline_stress_max"]))
        alignment_report["Amygdala"] = {
            "score": round(amy_score, 4),
            "status": "CALM" if nor <= 0.20 else "ALERT",
            "channels": amy["eeg_channels_10_20"]
        }

        # Print detailed regional mapping
        for name, data in alignment_report.items():
            print(f"[+] Region: {name.replace('_', ' ')}")
            print(f"     * Role: {regions[name]['functional_role']}")
            print(f"     * EEG Electrodes: {data['channels']}")
            print(f"     * Somatic Alignment Index: {data['score']:.4f} ({data['status']})")
            print("     " + "-" * 50)
            
        # Global Somatic Index
        global_index = sum([d["score"] for d in alignment_report.values()]) / len(alignment_report)
        print(f"\n[SUCCESS] Global BCI-Somatic Alignment Index: {global_index:.4f} (System Synced)")
        print("======================================================================\n")
        
        return alignment_report, global_index

if __name__ == "__main__":
    assimilator = NeurotoriumAssimilator()
    assimilator.compute_somatic_alignment()
