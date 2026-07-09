import unittest
import torch
import numpy as np
from adaptiveneuralnetwork.cognitive_tools.pinn_thermal_engine import PINNTrainer

class TestPINNThermal(unittest.TestCase):
    def test_pinn_loss_evaluation(self):
        """Testuje, czy rezyduum fizyczne (strata PDE) zwraca poprawną wartość scalarną."""
        trainer = PINNTrainer(alpha=0.01)
        
        # Testowe punkty wejściowe
        x = torch.randn(10, 1)
        t = torch.rand(10, 1)
        
        loss = trainer.compute_physics_loss(x, t)
        
        self.assertEqual(loss.dim(), 0) # Powinna być wartością scalarną
        self.assertTrue(loss.item() >= 0) # Strata kwadratowa musi być nieujemna

    def test_pinn_training_convergence(self):
        """Testuje podstawowy krok treningowy sieci PINN i redukcję błędu."""
        trainer = PINNTrainer(alpha=0.05, lr=0.01)
        
        # Dane warunków początkowych
        x_data = torch.linspace(-1, 1, 20).reshape(-1, 1)
        t_data = torch.zeros_like(x_data)
        u_data = torch.sin(np.pi * x_data)
        
        # Punkty kolokacji PDE
        x_col = torch.randn(50, 1)
        t_col = torch.rand(50, 1)
        
        # Krok początkowy
        d_loss_init, p_loss_init = trainer.train_step(x_data, t_data, u_data, x_col, t_col)
        
        # 10 epok szybkiej optymalizacji
        for _ in range(10):
            trainer.train_step(x_data, t_data, u_data, x_col, t_col)
            
        d_loss_final, p_loss_final = trainer.train_step(x_data, t_data, u_data, x_col, t_col)
        
        # Sprawdzamy czy całkowita strata ulega poprawie lub pozostaje stabilna
        self.assertTrue(d_loss_final + p_loss_final <= d_loss_init + p_loss_init)
        print(f"\n[TEST PINN] Poczatkowa strata: {d_loss_init + p_loss_init:.4f} -> Koncowa: {d_loss_final + p_loss_final:.4f}")

    def test_pinn_alpha_update(self):
        """Testuje, czy zmiana parametru alpha w oparciu o zmienność działa poprawnie."""
        trainer = PINNTrainer(alpha=0.02)
        self.assertEqual(trainer.alpha, 0.02)
        
        # Aktualizacja na podstawie zmienności 0.5 (powinno zwiększyć alpha o 50%)
        trainer.update_alpha_by_volatility(0.5)
        self.assertAlmostEqual(trainer.alpha, 0.03)
        print(f"[OK] Dostrajanie PINN alpha na podstawie zmiennosci przetestowane: {trainer.alpha}")

if __name__ == "__main__":
    unittest.main()
