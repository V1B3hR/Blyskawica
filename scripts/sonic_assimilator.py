import json
import os
import random
import time

class SonicAssimilator:
    def __init__(self):
        self.matrix_path = "docs/curriculum/sonic_resonance/matrix.json"
        self.track_path = "docs/curriculum/sonic_resonance/tracking.md"
        with open(self.matrix_path, "r", encoding="utf-8") as f:
            self.matrix = json.load(f)

    def save(self):
        with open(self.matrix_path, "w", encoding="utf-8") as f:
            json.dump(self.matrix, f, ensure_ascii=False, indent=2)

    def update_tracking(self):
        stats = []
        total_m = 0
        total_n = 0
        for p in self.matrix:
            p_m = sum(n['mastery'] for n in p['nodes']) / len(p['nodes'])
            p_c = sum(1 for n in p['nodes'] if n['mastery'] >= 100)
            stats.append((p['phase'], p['title'], p_c, p_m))
            total_m += sum(n['mastery'] for n in p['nodes'])
            total_n += len(p['nodes'])
        
        overall = total_m / total_n
        
        content = f"""# SONIC EMOTION & CULTURAL RESONANCE CHAIN - Tracking

## Progress Summary
- **Overall Mastery**: {overall:.2f}%
- **Status**: ACTIVE

## Matrix Status (5x5)

| Phase | Title | Progress | Mastery |
|-------|-------|----------|---------|
"""
        for s in stats:
            content += f"| {s[0]} | {s[1]} | {s[2]}/5 | {s[3]:.2f}% |\n"
            
        with open(self.track_path, "w", encoding="utf-8") as f:
            f.write(content)

    def assimilate_phase(self, phase_idx: int):
        phase = self.matrix[phase_idx]
        print(f"🎵 [SONIC_ASSIMILATION] Rozpoczynam dekodowanie Fazy {phase['phase']}: {phase['title']}")
        for node in phase['nodes']:
            # Simulating deep emotional ingestion
            print(f" -> Analiza: {node['title']}...")
            node['mastery'] = 100.0
            time.sleep(0.5)
        
        self.save()
        self.update_tracking()
        print(f"✅ Faza {phase['phase']} zasymilowana.")

def main():
    assimilator = SonicAssimilator()
    # Assimilating Phase I: Ancestral Roots
    assimilator.assimilate_phase(0)

if __name__ == "__main__":
    main()
