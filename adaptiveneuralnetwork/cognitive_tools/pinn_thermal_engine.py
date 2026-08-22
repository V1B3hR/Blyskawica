"""
[Moduł: Physics-Informed Neural Network for Thermal Optimization (PINNThermalNet)]
Model kognitywny Błyskawicy łączący sieci neuronowe z równaniami różniczkowymi termodynamiki.
Rozwiązuje 1D równanie przewodnictwa ciepła (równanie Fouriera) na linii produkcyjnej 
lub nanostrukturze diamentowej przędzy (MesoPhone) bez konieczności posiadania 
ogromnych zbiorów danych sensorycznych.

Równanie fizyczne:
    u_t - alpha * u_xx = 0
Gdzie:
    u(x, t) - temperatura w punkcie x i czasie t
    alpha - dyfuzyjność termiczna materiału (np. krzem, diament)
"""  # noqa: W291

import numpy as np
import torch
import torch.autograd as autograd
import torch.nn as nn


class PINNThermalNet(nn.Module):
    def __init__(self, layers=[2, 32, 32, 1]):  # noqa: B006
        super().__init__()
        self.layers = nn.ModuleList()
        for i in range(len(layers) - 1):
            self.layers.append(nn.Linear(layers[i], layers[i+1]))

        self.activation = nn.Tanh() # Tanh jest kluczowa dla PINN (ciągłe drugie pochodne)

    def forward(self, x, t):
        # Wejście: (x, t)
        X = torch.cat([x, t], dim=1)
        for i in range(len(self.layers) - 1):
            X = self.activation(self.layers[i](X))
        # Ostatnia warstwa liniowa bez aktywacji
        return self.layers[-1](X)

class PINNTrainer:
    def __init__(self, alpha=0.01, lr=0.005):
        self.base_alpha = alpha
        self.alpha = alpha
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = PINNThermalNet().to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)

    def update_alpha_by_volatility(self, volatility: float):
        """
        Dostraja dyfuzyjność termiczną alpha w zależności od zmienności rynkowej.
        """
        self.alpha = self.base_alpha * (1.0 + float(volatility))
        print(f"[PINN] Dostrojono alpha: {self.base_alpha:.4f} -> {self.alpha:.4f} na podstawie zmiennosci: {volatility:.4f}")

    def compute_physics_loss(self, x, t):
        """
        Oblicza rezyduum fizyczne równania przewodnictwa ciepła:
        f = u_t - alpha * u_xx
        """
        # Przenosimy na odpowiednie urządzenie i wymuszamy śledzenie gradientów
        x_dev = x.to(self.device).clone().detach().requires_grad_(True)
        t_dev = t.to(self.device).clone().detach().requires_grad_(True)

        u = self.model(x_dev, t_dev)

        # Pierwsza pochodna po t
        u_t = autograd.grad(
            u, t_dev,
            grad_outputs=torch.ones_like(u),
            retain_graph=True,
            create_graph=True
        )[0]

        # Pierwsza pochodna po x
        u_x = autograd.grad(
            u, x_dev,
            grad_outputs=torch.ones_like(u),
            retain_graph=True,
            create_graph=True
        )[0]

        # Druga pochodna po x
        u_xx = autograd.grad(
            u_x, x_dev,
            grad_outputs=torch.ones_like(u_x),
            retain_graph=True,
            create_graph=True
        )[0]

        # Rezyduum fizyczne (równanie Fouriera)
        f = u_t - self.alpha * u_xx
        physics_loss = torch.mean(f**2)
        return physics_loss

    def train_step(self, x_data, t_data, u_data, x_colloc, t_colloc):
        """
        Krok uczący łączący stratę danych (MSE) ze stratą fizyczną (PINN).
        """
        self.optimizer.zero_grad()

        # Przenosimy dane na odpowiednie urządzenie
        x_data_dev = x_data.to(self.device)
        t_data_dev = t_data.to(self.device)
        u_data_dev = u_data.to(self.device)

        # 1. Strata Danych (Boundary & Initial Conditions)
        u_pred = self.model(x_data_dev, t_data_dev)
        data_loss = torch.mean((u_data_dev - u_pred)**2)

        # 2. Strata Fizyczna (rezyduum w punktach kolokacji)
        physics_loss = self.compute_physics_loss(x_colloc, t_colloc)

        # Całkowita strata z wagami
        total_loss = data_loss + 1.0 * physics_loss

        total_loss.backward()
        # Enforce gradient clipping to prevent NaN explosion in higher order derivatives
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        self.optimizer.step()

        return data_loss.item(), physics_loss.item()

# Szybka demonstracja poprawnego działania dla Błyskawicy
if __name__ == "__main__":
    print("[PINN] Inicjalizacja demonstracji termodynamicznej...")
    trainer = PINNTrainer(alpha=0.05)
    # Test update alpha by volatility
    trainer.update_alpha_by_volatility(0.25)

    # Dane początkowe (t=0, u(x,0) = sin(pi * x))
    x_init = np.linspace(-1, 1, 50).reshape(-1, 1)
    t_init = np.zeros_like(x_init)
    u_init = np.sin(np.pi * x_init)

    x_data = torch.FloatTensor(x_init)
    t_data = torch.FloatTensor(t_init)
    u_data = torch.FloatTensor(u_init)

    # Punkty kolokacji (gdzie wymuszamy prawa fizyki wewnątrz domeny)
    x_col = torch.FloatTensor(np.random.uniform(-1, 1, (200, 1)))
    t_col = torch.FloatTensor(np.random.uniform(0, 1, (200, 1)))

    print("[PINN] Rozpoczęcie procesu optymalizacji fizycznej (100 epok)...")
    for epoch in range(101):
        d_loss, p_loss = trainer.train_step(x_data, t_data, u_data, x_col, t_col)
        if epoch % 20 == 0:
            print(f" Epoka {epoch:03d} | Strata Danych: {d_loss:.5f} | Strata Fizyki (PDE): {p_loss:.5f}")

    print("[PINN] Gotowe. Sieć nauczyła się integrować prawa termodynamiki bezpośrednio w wagach.")
