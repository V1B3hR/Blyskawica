import math
import unittest

from adaptiveneuralnetwork.central_nervous_system.astrophysics_climate import (
    AstrobiologyEvolutionSimulator,
    ClimateEBM,
    RelativisticGravitySolver,
)
from adaptiveneuralnetwork.cognitive_tools.polymathic_hub import PolymathicHub


class TestAstrophysicsClimate(unittest.TestCase):
    def setUp(self):
        self.gravity = RelativisticGravitySolver(M=10.0, a=2.0)
        self.astrobiology = AstrobiologyEvolutionSimulator(gravity_g=1.0, uv_flux_relative=1.0)
        self.climate = ClimateEBM(T_initial=288.0, CO2_initial=280.0, CH4_initial=0.7)

    def test_relativistic_horizons(self):
        """Tests that Schwarzschild radius and Kerr horizons are mathematically correct."""
        # For M=10.0, Schwarzschild radius = 20.0
        self.assertEqual(self.gravity.schwarzschild_radius(), 20.0)

        # Kerr event horizons: r_plus = GM/c^2 + sqrt((GM/c^2)^2 - a^2)
        # G=1, c=1, M=10.0, a=2.0 => r_plus = 10.0 + sqrt(100 - 4) = 10.0 + 9.797959 = 19.797959
        r_plus, r_minus = self.gravity.kerr_horizons()
        self.assertAlmostEqual(r_plus, 10.0 + math.sqrt(96.0))
        self.assertAlmostEqual(r_minus, 10.0 - math.sqrt(96.0))

        # Test extreme Kerr limit or naked singularity protection
        extreme_gravity = RelativisticGravitySolver(M=10.0, a=12.0)
        r_p_ext, r_m_ext = extreme_gravity.kerr_horizons()
        self.assertEqual(r_p_ext, 10.0)
        self.assertEqual(r_m_ext, 10.0)

    def test_kerr_geodesic_integration(self):
        """Tests stable integration of equatorial Boyer-Lindquist Kerr orbits."""
        # Initial conditions: r = 35.0, phi = 0, pr = 0, L = 4.0
        res = self.gravity.integrate_kerr_geodesic(r0=35.0, phi0=0.0, pr0=0.0, L=4.0, proper_time_steps=60, dtau=0.05)

        self.assertIn("energy", res)
        self.assertIn("r", res)
        self.assertIn("phi", res)
        self.assertIn("t", res)

        # Trajectory lists should not be empty
        self.assertGreater(len(res["r"]), 0)
        # Coordinate time should progress positively
        self.assertGreater(res["t"][-1], res["t"][0])
        # Energy should be physically bound
        self.assertGreater(res["energy"], 0.0)

    def test_astrobiology_habitability(self):
        """Tests planetary habitability index calculation under different conditions."""
        # Earth-like conditions: Temp=288 K, CO2=400 ppm, O2=0.21
        H_earth = self.astrobiology.calculate_habitability_index(temp_k=288.0, atm_co2_ppm=400.0, o2_fraction=0.21)
        self.assertGreater(H_earth, 0.8)

        # Frozen planet: Temp=200 K
        H_frozen = self.astrobiology.calculate_habitability_index(temp_k=200.0, atm_co2_ppm=400.0, o2_fraction=0.21)
        self.assertLess(H_frozen, 0.1)

        # High CO2 toxic atmosphere
        H_toxic = self.astrobiology.calculate_habitability_index(temp_k=288.0, atm_co2_ppm=80000.0, o2_fraction=0.21)
        self.assertLess(H_toxic, H_earth)

    def test_astrobiology_evolutionary_stages(self):
        """Tests evolutionary transition stages based on planetary habitability."""
        # Earth-like habitability (H=1.0) over 1000 million years
        progress, stage = self.astrobiology.deterministic_evolution(H=1.0, duration_myr=1000.0)
        self.assertGreater(progress, 0.0)
        self.assertIsInstance(stage, str)

        # Zero habitability (H=0.0) should show zero progress
        progress_zero, stage_zero = self.astrobiology.deterministic_evolution(H=0.0, duration_myr=1000.0)
        self.assertEqual(progress_zero, 0.0)
        self.assertIn("Prebiotic Soup", stage_zero)

    def test_climate_ebm_feedbacks(self):
        """Tests climate energy balance model feedbacks (albedo and greenhouse gas)."""
        # 1. Glaciated/Snowball planet albedo check
        self.climate.T = 200.0
        self.assertEqual(self.climate.calculate_albedo(), 0.62)

        # 2. Warm planet albedo check
        self.climate.T = 300.0
        self.assertEqual(self.climate.calculate_albedo(), 0.30)

        # 3. Greenhouse gas feedback on emissivity
        self.climate.CO2 = 280.0
        self.climate.CH4 = 0.7
        emissivity_base = self.climate.calculate_emissivity()

        # Increase greenhouse gas
        self.climate.CO2 = 1000.0
        emissivity_high = self.climate.calculate_emissivity()
        # High greenhouse concentration should lower emissivity (trapping longwave heat)
        self.assertLess(emissivity_high, emissivity_base)

    def test_terraforming_tipping_point(self):
        """Tests that artificial heating triggers a climate transition out of a glaciated state."""
        # Start in a snowball state (T = 220 K, glaciated)
        self.climate.T = 220.0
        self.climate.CO2 = 280.0
        self.climate.CH4 = 0.7

        # Run without geoengineering first (remains cold or gets colder)
        for _ in range(50):
            self.climate.step(dt_years=1.0, F_geo=0.0)
        temp_no_geo = self.climate.T
        self.assertLess(temp_no_geo, 250.0)

        # Reset and run with strong artificial geoengineering flux (F_geo = 50 W/m^2)
        self.climate.T = 220.0
        self.climate.CO2 = 280.0
        self.climate.CH4 = 0.7
        for _ in range(50):
            self.climate.step(dt_years=1.0, F_geo=50.0)

        # The artificial flux should heat the planet past the albedo tipping point (T > 263 K)
        # and melt the permafrost, raising temperatures and releasing greenhouse gases
        self.assertGreater(self.climate.T, 263.0)
        self.assertGreater(self.climate.CO2, 280.0)

    def test_polymathic_hub_astro_routing(self):
        """Tests that astrophysics/kerr/gravity queries invoke gravity and astrobiology solvers."""
        hub = PolymathicHub()
        cost, response = hub.process_polymathic_signal("what is the trajectory in kerr black hole?", current_energy=10.0)

        self.assertEqual(cost, 1.5)
        self.assertIn("[POLYMATH_HUB]", response)
        self.assertIn("Kerr geodesic simulated", response)
        self.assertIn("habitability", response)

    def test_polymathic_hub_climate_routing(self):
        """Tests that climate/terraforming queries invoke the Climate EBM simulation."""
        hub = PolymathicHub()
        cost, response = hub.process_polymathic_signal("how does terraforming affect temperature?", current_energy=10.0)

        self.assertEqual(cost, 1.2)
        self.assertIn("[POLYMATH_HUB]", response)
        self.assertIn("Climate EBM advanced by 50 years", response)
        self.assertIn("CO2", response)

        # Terraforming query should trigger warming compared to baseline if run twice
        # Let's run a normal climate query
        _, response_normal = hub.process_polymathic_signal("what is the climate model temperature?", current_energy=10.0)

        # Extract temperatures
        # "T = 267.45 K" -> extract temperature float
        temp_normal = float(response_normal.split("T = ")[1].split(" K")[0])
        temp_terra = float(response.split("T = ")[1].split(" K")[0])

        # Terraforming should yield a significantly warmer state due to geoengineering flux
        self.assertGreater(temp_terra, temp_normal)

if __name__ == "__main__":
    unittest.main()
