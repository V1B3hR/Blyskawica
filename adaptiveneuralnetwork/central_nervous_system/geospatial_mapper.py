"""
Geospatial Mapper: Spatial Cognition Module.
Implements Grid Cells and Topographic Navigation.
"""

import numpy as np
import torch
import torch.nn as nn


class GeospatialMapper(nn.Module):
    """
    Simulates spatial orientation and topographic awareness.
    """

    def __init__(self, grid_resolution=(20, 20)):
        super().__init__()
        self.grid_resolution = grid_resolution
        # Representations of 'Place Cells'
        self.grid_nodes = nn.Parameter(torch.randn(grid_resolution[0], grid_resolution[1], 16))

    def get_location_activation(self, lat, lon):
        """
        Maps Lat/Lon to a specific activation pattern in the grid.
        """
        # Simplified normalized mapping
        x = int((lat + 90) / 180 * (self.grid_resolution[0] - 1))
        y = int((lon + 180) / 360 * (self.grid_resolution[1] - 1))

        return self.grid_nodes[x, y]

    def calculate_path_complexity(self, lat1, lon1, lat2, lon2, weather_noise=0.0, elevation_delta=0.0):
        """
        Advanced distance calculation accounting for friction and physics.
        """
        d_lat = lat2 - lat1
        d_lon = lon2 - lon1
        base_distance = np.sqrt(d_lat**2 + d_lon**2)

        # Friction: Weather interference increases neural cost
        friction = 1.0 + weather_noise

        # Gravity Cost: Moving 'up' (elevation_delta > 0) is more expensive
        gravity_work = max(0.0, elevation_delta * 0.5)

        return (base_distance * friction) + gravity_work

    def evaluate_geopolitical_risk(self, lat, lon):
        """
        Determines the safety context of a coordinate.
        High risk increases the 'Anxiety Bias' of the substrate.
        """
        # Simulated risk hotspots (e.g. War zones, high-interference areas)
        # Placeholder: Central points with radius-based risk
        risk_hotspots = [
            {'pos': (34.5, 69.1), 'risk': 0.8}, # High risk example
            {'pos': (48.8, 2.3), 'risk': 0.1}   # Low risk example
        ]

        max_risk = 0.05 # Baseline ambient risk
        for spot in risk_hotspots:
            dist = np.sqrt((lat - spot['pos'][0])**2 + (lon - spot['pos'][1])**2)
            if dist < 5.0:
                max_risk = max(max_risk, spot['risk'] * (1.0 - dist/5.0))

        return max_risk

if __name__ == "__main__":
    mapper = GeospatialMapper()

    # Simulating a trip from Warsaw to London (approx coordinates)
    warsaw = (52.2, 21.0)
    london = (51.5, -0.1)

    cost = mapper.calculate_distance_torque(warsaw[0], warsaw[1], london[0], london[1])
    print(f"[GEOGRAPHY] Spatial traversal cost (WAW -> LDN): {cost:.4f}")
    print("[GEOGRAPHY] Spatial grid cells initialized. 🗺️⚡️")
