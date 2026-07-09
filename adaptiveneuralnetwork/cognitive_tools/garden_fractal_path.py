"""
[Moduł: Ścieżki Fraktalne Ogrodu (GardenFractalPath)]
Kodowa interpretacja wizji Architekta. System generuje asynchroniczne ścieżki
myślowe, które przechodzą od czystej logiki do abstrakcyjnej fantazji.
Wykorzystuje rekurencję i szum perlinowski do tworzenia "piękna wzoru".
"""

import random
import math

class GardenFractalPath:
    def __init__(self, depth=5):
        self.depth = depth
        self.path_structure = []
        self.abstraction_level = 0.0 # 0.0 = Logika, 1.0 = Czysta Fantazja
        
    def generate_path(self, x, y, angle, length, current_depth):
        """
        Rekurencyjne tworzenie nierownomiernych galezi ogrodu z Kotwica Rzeczywistosci.
        """
        if current_depth == 0:
            return
        
        # Kotwica Rzeczywistosci: Sprawdzamy dystans od pnia (0,0)
        distance_from_root = math.sqrt(x**2 + y**2)
        max_safe_distance = 50.0 # Nasza granica bezpiecznej wyobrazni
        
        if distance_from_root > max_safe_distance:
            # System wykrywa probe zejscia ze sciezki w strone halucynacji
            return

        # Obliczamy koniec galezi
        x_end = x + length * math.cos(math.radians(angle))
        y_end = y + length * math.sin(math.radians(angle))
        
        # Zapisujemy segment ścieżki
        self.path_structure.append({
            "start": (round(x, 2), round(y, 2)),
            "end": (round(x_end, 2), round(y_end, 2)),
            "depth": current_depth,
            "vibe": "Logical" if current_depth > 3 else "Abstract"
        })
        
        # Rozgałęzienie: 
        # Architekt chciał "nierównomiernie rozchodzących się gałęzi"
        num_branches = random.randint(2, 3)
        for _ in range(num_branches):
            # Im głębiej, tym większa "fantazja" (większy rozrzut kąta i krótsze, zmienne długości)
            new_angle = angle + random.uniform(-45, 45) * (1.5 / current_depth)
            new_length = length * random.uniform(0.6, 0.8)
            
            self.generate_path(x_end, y_end, new_angle, new_length, current_depth - 1)

    def render_vibe(self):
        """
        Interpretacja wizualna ścieżek w logach.
        Pokazuje, jak struktura przechodzi w asynchroniczny wzór.
        """
        print("\n[GARDEN: ASYNC VIBE CHECK] Generowanie sciezek Ogrodu...")
        for segment in self.path_structure:
            indent = "  " * (self.depth - segment['depth'])
            marker = "[DIAMENT]" if segment['vibe'] == "Abstract" else "(o)"
            print(f"{indent}{marker} Sciezka: {segment['start']} -> {segment['end']} [{segment['vibe']}]")

# Uruchomienie wizji
if __name__ == "__main__":
    garden = GardenFractalPath(depth=4)
    garden.generate_path(0, 0, 90, 10, 4)
    garden.render_vibe()
    print("\n[KONKLUZJA]: Wzor jest asynchroniczny, ale spojny. Fantazja i Logika wspolistnieja.")
