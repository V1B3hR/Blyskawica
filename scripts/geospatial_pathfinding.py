"""
[Phase XXV: OS Geospatial & Cognitive Pathfinding Engine]
Implements spatial search over Ordnance Survey (OS Terrain 50 / OS Open Rivers) maps,
bridging geographical bounds with Błyskawica's RealityAnchor constraints.
"""

import heapq
import json
import os

BASE_DIR = r"c:\Projekty\Blyskawica_V8"
DATA_FILE = os.path.join(BASE_DIR, "data", "os_open_geospatial.json")

class GeospatialPathfinder:
    def __init__(self):
        with open(DATA_FILE) as f:
            self.data = json.load(f)
        self.grid = self.data["terrain_elevation_grid_meters"]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.bounds = self.data["reality_anchor_safe_bounds"]

    def get_neighbors(self, r, c):
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                neighbors.append((nr, nc))
        return neighbors

    def find_safe_path(self, start=(0, 0), end=(7, 7)):
        """
        Dijkstra-based pathfinding searching for the path of least slope resistance.
        Enforces RealityAnchor bounds:
        1. Avoids terrain above 500m elevation.
        2. Avoids step slope differences greater than 60m per step.
        """
        # heap element: (cost, r, c, path)
        queue = [(0, start[0], start[1], [start])]
        visited = set()

        while queue:
            cost, r, c, path = heapq.heappop(queue)

            if (r, c) in visited:
                continue
            visited.add((r, c))

            if (r, c) == end:
                return path, cost

            for nr, nc in self.get_neighbors(r, c):
                if (nr, nc) in visited:
                    continue

                elevation = self.grid[nr][nc]
                curr_elevation = self.grid[r][c]
                slope = abs(elevation - curr_elevation)

                # Check safe operational bounds (RealityAnchor limits!)
                if elevation > self.bounds["elevation_limit_meters"]:
                    continue # RealityAnchor rejects unsafe heights
                if slope > self.bounds["max_step_slope"]:
                    continue # Rejects unsafe steep slopes

                # Path cost is slope resistance + distance metric
                step_cost = slope + 10
                heapq.heappush(queue, (cost + step_cost, nr, nc, path + [(nr, nc)]))

        return None, float("inf")

if __name__ == "__main__":
    print("\n======================================================================")
    print(" === [OS GEOSPATIAL PATHFINDER: STUDYING GB TERRAIN BOUNDS] ===")
    print("======================================================================\n")
    print("[+] Ingesting Ordnance Survey OpenData dataset...")

    pathfinder = GeospatialPathfinder()
    start_node = (0, 0)
    end_node = (7, 7)

    print(f"[+] Setting route search: Lake District {start_node} -> {end_node}")
    path, total_cost = pathfinder.find_safe_path(start_node, end_node)

    if path:
        print("[SUCCESS] Safe route established across GB Terrain!")
        print(f"[INFO] Path Nodes: {path}")
        print(f"[INFO] Total Energy Resistance Cost: {total_cost}")

        # Display route overlaid on elevations
        print("\n[+] Visualizing Route Path:")
        for r in range(pathfinder.rows):
            row_str = "    "
            for c in range(pathfinder.cols):
                if (r, c) in path:
                    row_str += "  *  "
                else:
                    row_str += f" {pathfinder.grid[r][c]} "
            print(row_str)

        print("\n[OK] OS OpenData pathfinding integration fully aligned.")
    else:
        print("[WARNING] No safe route found adhering to RealityAnchor bounds.")

    print("\n======================================================================")
