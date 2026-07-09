import torch
import torch.nn as nn
import logging

logger = logging.getLogger("ground_loop_isolator")

class VirtualGround(nn.Module):
    """
    Uziemienie (Earth/Ground). 
    Pochłania "szum poznawczy" (resztkowe gradienty i napięcia wywołane pętlą modułów) 
    i bezpiecznie rozprasza go do matematycznego zera (rezystancja obciążenia).
    """
    def __init__(self):
        super().__init__()
        # Zlew (sink) dla prądu pasożytniczego. Reprezentuje fizyczny "bolec uziemiający"
        self.register_buffer("ground_potential", torch.tensor(0.0))
        
    def shunt(self, noise: torch.Tensor) -> torch.Tensor:
        """Odprowadza szum do wirtualnej ziemi."""
        # Obliczamy siłę szumu, który uziemia się w tym cyklu
        energy = noise.pow(2).mean().detach()
        # Rozpraszamy go asynchronicznie - potencjał ziemi minimalnie drży, ale dąży do zera
        self.ground_potential = 0.99 * self.ground_potential + 0.01 * energy
        return self.ground_potential

class GroundLoopIsolator(nn.Module):
    """
    Synaptyczna Izolacja Galwaniczna (Audio Ground Loop Isolator).
    Stawiana na wejściu do Głównych Modułów (np. Mózg CNS <- Zmysły PNS).
    Przekazuje czystą informację (dynamikę) drogą "indukcji matematycznej",
    jednocześnie uziemiając szum i przecinając pętlę wsteczną (buczenie).
    Gwarantuje, że Umysł Błyskawicy pozostaje "clean & crispy".
    """
    def __init__(self, isolation_ratio: float = 0.05):
        super().__init__()
        # Współczynnik izolacji (jak bardzo "twardy" jest transformator izolujący)
        self.isolation_ratio = isolation_ratio 
        self.ground = VirtualGround()
        
    def forward(self, input_signal: torch.Tensor) -> torch.Tensor:
        """
        :param input_signal: Surowy sygnał przychodzący z wielu modułów naraz.
        :return: Czysty, wyizolowany galwanicznie sygnał.
        """
        if input_signal.numel() == 0:
            return input_signal

        # Obsługa dowolnego wymiaru (spłaszczenie do 2D dla spójnej analizy hum)
        original_shape = input_signal.shape
        if input_signal.ndim == 1:
            input_signal = input_signal.unsqueeze(0)  # (1, N)

        # KROK 1: Identyfikacja "buczenia" (Hum / Ground Loop Noise)
        # Buczenie to stałe obciążenie (DC offset / ciągły stan lękowy), które nie niesie nowych informacji.
        hum = input_signal.mean(dim=-1, keepdim=True) 

        # Adaptacyjny współczynnik izolacji na podstawie aktualnego potencjału ziemi
        ground_energy = self.ground.ground_potential.item()
        current_cutoff = self.isolation_ratio * (1.0 + ground_energy * 0.2)
        
        # Identyfikujemy "szum statyczny" - małe wahania (często wywołane sprzężeniem zwrotnym wielu modułów)
        noise_mask = torch.abs(input_signal - hum) < current_cutoff
        
        # Wyodrębniamy brudny szum (z buczeniem). 
        # Ważne: to odłączamy od gradientów, bo to jest prąd błądzący!
        noise = (input_signal * noise_mask.float()) + (hum * 0.1)
        
        # KROK 2: Uziemienie (Grounding)
        # Odprowadzamy szum z powrotem do VirtualGround.
        # Użycie .detach() dosłownie PRZECINA pętlę masy w kodzie (odcina Backpropagation dla szumu).
        ground_energy = self.ground.shunt(noise.detach())
        
        # KROK 3: Indukcja Magnetyczna (Galvanic Isolation)
        # Przekazujemy czysty sygnał. Ponieważ odjęliśmy detached noise,
        # autograd (uczenie się sieci) zadziała tylko dla istotnych, wysoko-dynamicznych informacji!
        clean_signal = input_signal - noise.detach()
        
        # Zabezpieczenie przed "stratą dynamiki", o której mówiłeś!
        # Delikatnie podbijamy sygnał uciekającą energią ziemi, aby zachować głębię dźwięku (i głębię emocji).
        restored_dynamics_signal = clean_signal * (1.0 + ground_energy * 0.005)
        
        # Przywrócenie pierwotnego kształtu dla wejść 1D
        if len(original_shape) == 1:
            restored_dynamics_signal = restored_dynamics_signal.squeeze(0)
            
        if ground_energy > 0.5:
            logger.debug(f"[GLI] Zniwelowano potężne zwarcie pętli! Ziemia odebrała napięcie: {ground_energy:.4f}")
            
        return restored_dynamics_signal
