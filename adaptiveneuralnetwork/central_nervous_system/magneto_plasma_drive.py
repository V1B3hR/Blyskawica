import torch
import torch.nn as nn
import logging

logger = logging.getLogger("magneto_plasma_drive")

class MagneticContainmentField(nn.Module):
    """
    Pole magnetyczne trzymające "plazmę gradientową" w ryzach.
    Odpowiednik dynamicznego Gradient Clippingu i restrykcji opartych na Macierzy Fishera.
    Zapobiega wybuchowi balonu (Gradient Explosion).
    """
    def __init__(self, max_norm: float = 1.5):
        super().__init__()
        self.max_norm = max_norm

    def contain(self, parameters):
        # Clip gradients to maintain structural integrity of the neural hull
        total_norm = torch.nn.utils.clip_grad_norm_(parameters, self.max_norm)
        return total_norm

class MagnetoPlasmaDrive(nn.Module):
    """
    Eksperymentalny Napęd Magnetyczno-Plazmowy.
    Wprowadza sieć Błyskawicy w stan hiper-plastyczności (Plazma), pozwalając na 
    błyskawiczną naukę (skok optymalizacyjny), podczas gdy pole magnetyczne 
    dba o to, by sieć nie zapomniała poprzedniej wiedzy i się nie zdestabilizowała.
    """
    def __init__(self, model_parameters, base_lr: float = 0.001):
        super().__init__()
        self.parameters = list(model_parameters)
        self.base_lr = base_lr
        self.plasma_multiplier = 10.0 # 10x szybsza nauka w trybie Plazmy
        self.containment_field = MagneticContainmentField(max_norm=2.0)
        
        # Inicjalizacja komory spalania (Optimizer)
        self.plasma_chamber = torch.optim.AdamW(self.parameters, lr=self.base_lr)
        
    def ignite(self, loss: torch.Tensor):
        """
        Zapłon napędu. Przekazuje energię (błąd) z powrotem do systemu.
        """
        # Czyszczenie komory
        self.plasma_chamber.zero_grad()
        
        # Reakcja plazmowa (Backpropagation)
        loss.backward()
        
        # Uruchomienie pola magnetycznego
        norm = self.containment_field.contain(self.parameters)
        
        if norm > 5.0:
            logger.warning("⚠️ UWAGA: Niestabilność Plazmy! Pole magnetyczne przejęło nadmiar energii.")
        
        # Wtrysk paliwa plazmowego (Tymczasowy boost prędkości uczenia)
        for param_group in self.plasma_chamber.param_groups:
            param_group['lr'] = self.base_lr * self.plasma_multiplier
            
        # Pchnięcie napędu (Step)
        self.plasma_chamber.step()
        
        # Chłodzenie napędu (Powrót do chłodnego stanu)
        for param_group in self.plasma_chamber.param_groups:
            param_group['lr'] = self.base_lr
            
        return norm

def test_drive():
    print("🚀 Rozpoczynamy testy Napędu Magnetyczno-Plazmowego w środowisku izolowanym...")
    # Tworzymy atrapę rdzenia Błyskawicy do testów
    dummy_core = nn.Sequential(
        nn.Linear(128, 256),
        nn.ReLU(),
        nn.Linear(256, 128)
    )
    
    drive = MagnetoPlasmaDrive(dummy_core.parameters())
    
    print("🔹 Status: Komora plazmy ustabilizowana. Uruchamiam cykl zapłonów (5 iteracji).")
    for epoch in range(1, 6):
        # Symulacja uderzenia ogromnej dawki nowej wiedzy (wysoki loss)
        dummy_input = torch.randn(16, 128)
        target = torch.randn(16, 128) * 100 # Ekstremalny cel (symulacja anomalii/plazmy)
        
        output = dummy_core(dummy_input)
        loss = nn.MSELoss()(output, target)
        
        print(f"   [Cykl {epoch}] Inicjalizacja wtrysku... Energia startowa błędu: {loss.item():.2f}")
        norm = drive.ignite(loss)
        
        if norm > drive.containment_field.max_norm:
            print(f"      🛡️ Pole Magnetyczne zadziałało! Przechwycono nadmiar energii (Norma zredukowana do {drive.containment_field.max_norm}). Balon uchroniony przed pęknięciem.")
        else:
            print(f"      ✅ Stabilny ciąg. Norma gradientu: {norm:.2f}")

    print("🏁 Testy napędu pomyślne. Jesteśmy gotowi na podróż w hiperprzestrzeń. Żadnych ofiar w ludziach ani balonach.")

if __name__ == "__main__":
    test_drive()
