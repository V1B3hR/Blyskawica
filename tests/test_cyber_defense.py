import unittest
import torch
from torch.utils.data import DataLoader
from adaptiveneuralnetwork.training.datasets.cyber_defense import CyberDefenseDataset
from blyskawica_start import build_model, build_trainer


class TestCyberDefenseModule(unittest.TestCase):
    """Verifies Błyskawica V9 Module 3 (Cyber-Intelligence & Intrusion Awareness) dataset and model integrity."""

    def test_cyber_defense_dataset_shapes(self):
        """Weryfikuje poprawność wymiarów danych wyjściowych z CyberDefenseDataset."""
        num_samples = 120
        input_dim = 768
        num_classes = 6
        
        dataset = CyberDefenseDataset(num_samples=num_samples, input_dim=input_dim, num_classes=num_classes)
        self.assertEqual(len(dataset), num_samples)
        
        data_item, target_item = dataset[0]
        self.assertEqual(data_item.shape, torch.Size([input_dim]))
        self.assertIsInstance(target_item.item(), int)
        self.assertTrue(0 <= target_item.item() < num_classes)

    def test_threat_distribution(self):
        """Weryfikuje równomierny podział klas w syntetycznym zbiorze danych."""
        num_samples = 600
        dataset = CyberDefenseDataset(num_samples=num_samples)
        dist = dataset.get_threat_distribution()
        
        # Sprawdź obecność wszystkich 6 klas
        self.assertEqual(len(dist), 6)
        # Ponieważ 600 dzieli się przez 6 bez reszty, każda klasa powinna mieć dokładnie 100 próbek
        for class_name, count in dist.items():
            self.assertEqual(count, 100)

    def test_model_inference_with_cyber_data(self):
        """Weryfikuje, czy model Błyskawicy przyjmuje wektory cyber-zagrożeń i zwraca 6 klas wyjściowych."""
        input_dim = 768
        output_dim = 6
        batch_size = 16
        
        # Tworzenie modelu z wymiarem wyjściowym 6 (zgodnie z Module 3)
        from torch.utils.data._utils.collate import default_collate
        model = build_model(output_dim=output_dim)
        dataset = CyberDefenseDataset(num_samples=32, input_dim=input_dim, num_classes=output_dim)
        loader = DataLoader(dataset, batch_size=batch_size, collate_fn=default_collate)
        
        data_batch, target_batch = next(iter(loader))
        
        # Forward pass
        # model.forward() zwraca słownik lub tensor. Zobaczmy jak zachowuje się model w blyskawica_start.py
        # Zazwyczaj trainer wywołuje model i liczy stratę. Zweryfikujmy wyjście bezpośrednie.
        output = model(data_batch)
        
        # Jeśli to kognitywny system multimodalny, wyjściem z forward jest tensor logits
        # Sprawdźmy typ i kształt
        if isinstance(output, dict):
            self.assertIn("logits", output)
            logits = output["logits"]
        else:
            logits = output
            
        self.assertEqual(logits.shape, torch.Size([batch_size, output_dim]))
        
        # Sprawdź czy wartości straty są obliczalne
        criterion = torch.nn.CrossEntropyLoss()
        loss = criterion(logits, target_batch)
        self.assertTrue(torch.isfinite(loss))
        self.assertGreater(loss.item(), 0.0)
