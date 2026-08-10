"""
Geometric Torque Dataset Generator.
Creates synthetic visual scenarios for testing Physical/Geometric Equilibrium.
Błyskawica must learn to 'see' if a structure is balanced or likely to fall.
"""

import random

import numpy as np
import torch
from torch.utils.data import Dataset


class GeometricTorqueDataset(Dataset):
    """
    Synthesizes 2D visual representations of physical structures (towers of blocks).
    Labels indicate if the structure is balanced (0), unstable/tilting (1), or falling (2).
    """

    def __init__(self, num_samples=1000, img_size=(28, 28)):
        self.num_samples = num_samples
        self.img_size = img_size
        self.data = []
        self.labels = []
        self._generate_samples()

    def _generate_samples(self):
        for _ in range(self.num_samples):
            img = np.zeros(self.img_size, dtype=np.float32)

            # Base width and position
            base_w = random.randint(6, 12)
            base_x = random.randint(5, self.img_size[0] - base_w - 5)
            base_y = self.img_size[1] - 4

            # Draw base
            img[base_y:base_y+2, base_x:base_x+base_w] = 1.0

            # Add secondary block
            block_w = random.randint(4, 8)
            # Offset determines the 'Torque'
            # offset = 0 is perfectly centered
            max_offset = base_w // 2 + 2
            offset = random.randint(-max_offset, max_offset)

            block_x = base_x + (base_w - block_w) // 2 + offset
            block_y = base_y - 4

            # Draw secondary block (clamped to image bounds)
            valid_x_start = max(0, block_x)
            valid_x_end = min(self.img_size[0], block_x + block_w)
            if valid_x_start < valid_x_end:
                img[block_y:block_y+3, valid_x_start:valid_x_end] = 0.8

            # Calculate Equilibrium Label
            # Center of block relative to base center
            center_dist = abs(offset)
            if center_dist <= 1:
                label = 0 # Perfectly Balanced (Stasis)
            elif center_dist < base_w // 2:
                label = 1 # Unstable but Standing (Leverage)
            else:
                label = 2 # Falling (Torque Overload)

            self.data.append(torch.from_numpy(img).unsqueeze(0))
            self.labels.append(label)

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

if __name__ == "__main__":
    # Smoke test
    ds = GeometricTorqueDataset(num_samples=5)
    img, label = ds[0]
    print(f"Sample generated. Shape: {img.shape}, Label: {label}")
