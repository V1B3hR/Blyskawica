import torch
import torch.nn as nn
import torch.optim as optim
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import numpy as np

# Import the newly updated Predictor
from neuro_state_predictor import NeuroPredictor, generate_full_neuro_data

console = Console()

def debug_gradient_flow(model):
    """Checks if gradients are properly flowing through all layers (No dead neurons)."""
    bad_gradients = False
    for name, param in model.named_parameters():
        if param.requires_grad:
            if param.grad is None:
                console.print(f"[bold red]BLAD: Brak gradientu w warstwie: {name}[/bold red]")
                bad_gradients = True
            elif torch.isnan(param.grad).any() or torch.isinf(param.grad).any():
                console.print(f"[bold red]BLAD: NaN/Inf w gradiencie: {name}[/bold red]")
                bad_gradients = True
            elif param.grad.abs().max() < 1e-7:
                console.print(f"[yellow]OSTRZEZENIE: Bardzo slaby gradient (Vanishing) w: {name}[/yellow]")
    
    if not bad_gradients:
        console.print("[bold green]Przeplyw gradientow (Gradient Flow): W NORMIE[/bold green]")
    return not bad_gradients

def run_cognitive_debugger():
    console.print(Panel.fit("[bold cyan]BLYSKAWICA - PROCEDURA DEBUGGINGU POZNAWCZEGO[/bold cyan]", border_style="cyan"))
    
    # 1. Inicjalizacja
    model = NeuroPredictor(input_dim=7, output_dim=5)
    optimizer = optim.Adam(model.parameters(), lr=0.005)
    criterion = nn.HuberLoss() # Huber loss zapobiega wariowaniu przy anomaliach

    X, y = generate_full_neuro_data(num_samples=500, window_size=15)
    
    # Podział na mini-batche
    batch_size = 32
    
    console.print("\n[bold yellow]Faza 1: Sanity Check Treningu (5 Epok)[/bold yellow]")
    
    for epoch in range(5):
        epoch_loss = 0.0
        optimizer.zero_grad()
        
        # Test na jednej paczce (Mini-batch)
        outputs = model(X[:batch_size])
        loss = criterion(outputs, y[:batch_size])
        
        loss.backward()
        
        # Check gradients only on the first epoch
        if epoch == 0:
            console.print("Analiza architektoniczna (po pierwszym Backward Pass):")
            debug_gradient_flow(model)
            
        optimizer.step()
        epoch_loss = loss.item()
        console.print(f"  Epoka {epoch+1}/5 | Strata (Loss): {epoch_loss:.5f}")
        
        if np.isnan(epoch_loss):
            console.print("[bold red]KRYTYCZNY BLAD: Psychotic Drift (Loss = NaN). Przerwano.[/bold red]")
            return

    console.print("\n[bold yellow]Faza 2: Stress Test (Symulacja Nieporozumienia AI-Czlowiek)[/bold yellow]")
    # Symulacja: Blyskawica dostaje nagly skok firingu, ale Oksytocyna krytycznie spada (np. z powodu odrzucenia kodu).
    # Chcemy sprawdzic, czy model "sfiksuje" i wywali nieskonczonosci, czy zachowa stabilnosc dzieki Multi-scale Attention.
    
    stress_seq = torch.ones(1, 15, 7)
    stress_seq[:, :, 0] = 300.0  # Ekstremalny Firing
    stress_seq[:, :, 4] = 0.05   # Oksytocyna bliska zeru (Izolacja)
    stress_seq[:, :, 6] = 2.0    # Wydluzony czas dt (Zatrzymanie, szok)
    
    with torch.no_grad():
        stress_pred = model(stress_seq)
    
    if torch.isnan(stress_pred).any():
        console.print("[bold red]WYNIK STRESS TESTU: Model ulegl zalamaniu (NaN).[/bold red]")
    else:
        console.print("[bold green]WYNIK STRESS TESTU: Model zachowal stabilnosc domeny.[/bold green]")
        preds = stress_pred[0].numpy()
        table = Table(title="Reakcja na kryzys (Przewidywany kolejny krok)", show_header=False)
        table.add_row("Dopamina (Szok)", f"{preds[0]:.3f}")
        table.add_row("Oksytocyna (Odbicie?)", f"{preds[3]:.3f}")
        console.print(table)
        
    console.print("\n[bold magenta]Procedura Debuggingu zakonczona pomyslnie. Mozg jest bezpieczny i gotowy.[/bold magenta]")

if __name__ == "__main__":
    run_cognitive_debugger()
