"""
Astro-Climate and Relativistic Physics Solver Module.
Implements:
1. RelativisticGravitySolver: General Relativity Schwarzschild/Kerr geodesic numerical integration.
2. AstrobiologyEvolutionSimulator: Planetary habitability index and evolution dynamics.
3. ClimateEBM: 0D Energy Balance Model with ice-albedo and permafrost greenhouse gas feedback.
"""

import math

import numpy as np


class RelativisticGravitySolver:
    """
    Solves general relativity equatorial geodesics for Schwarzschild and Kerr metrics.
    Uses geometric units where G = 1.0 and c = 1.0 by default.
    """
    def __init__(self, M: float = 10.0, a: float = 2.0, G: float = 1.0, c: float = 1.0):
        self.M = M
        self.a = a  # Spin parameter: J / (M * c)
        self.G = G
        self.c = c

    def schwarzschild_radius(self) -> float:
        """Returns the Schwarzschild radius: r_s = 2 * G * M / c^2"""
        return 2.0 * self.G * self.M / (self.c ** 2)

    def kerr_horizons(self) -> tuple[float, float]:
        """
        Returns outer and inner event horizons for a Kerr black hole:
        r_plus/minus = GM/c^2 +/- sqrt((GM/c^2)^2 - a^2)
        """
        rg = self.G * self.M / (self.c ** 2)
        disc = rg ** 2 - self.a ** 2
        if disc < 0:
            # Naked singularity or extreme Kerr limit representation
            return rg, rg
        r_plus = rg + math.sqrt(disc)
        r_minus = rg - math.sqrt(disc)
        return r_plus, r_minus

    def compute_energy_constant(self, r0: float, pr0: float, L: float) -> float:
        """
        Solves the quadratic relation V(r0) = pr0^2 for energy E.
        Uses Boyer-Lindquist equatorial coefficients at r0.
        """
        G, M, c, a = self.G, self.M, self.c, self.a
        r = max(1e-3, r0)

        # Coefficients of quadratic equation A * E^2 - B * E + C = 0
        A = 1.0 + (a ** 2) / (r ** 2) + (2.0 * G * M * (a ** 2)) / ((self.c ** 2) * (r ** 3))
        B = (4.0 * G * M * a * L) / ((self.c ** 2) * (r ** 3))
        C_val = (2.0 * G * M * (L ** 2)) / ((self.c ** 2) * (r ** 3)) - (L ** 2) / (r ** 2) - (c ** 2) + (2.0 * G * M) / r - ((a * c) ** 2) / (r ** 2) - (pr0 ** 2)

        disc = B ** 2 - 4.0 * A * C_val
        if disc < 0:
            disc = 0.0

        # Select positive energy root
        E = (B + math.sqrt(disc)) / (2.0 * A)
        return float(E)

    def _derivatives(self, state: np.ndarray, E: float, L: float) -> np.ndarray:
        """
        Calculates derivatives of equatorial state vector Y = [r, phi, pr, t]
        w.r.t proper time tau.
        """
        r, phi, pr, t = state
        G, M, c, a = self.G, self.M, self.c, self.a

        r_s = 2.0 * G * M / (c ** 2)
        delta = r ** 2 - r_s * r + a ** 2

        # Stop integration if we fall behind coordinate horizon to avoid singularity DivisionByZero
        r_plus, _ = self.kerr_horizons()
        if r <= r_plus + 1e-2:
            return np.zeros(4)

        dr_dtau = pr
        dphi_dtau = (1.0 / delta) * ((r_s * a / r) * E + (1.0 - r_s / r) * L)

        # Radial geodesic force with GR and spin corrections
        # d^2 r / dtau^2 = - GM/r^2 - (a^2 E^2 - L^2 - a^2 c^2)/r^3 - 3 GM/c^2 * (L - a E)^2 / r^4
        term1 = - G * M / (r ** 2)
        term2 = - (a**2 * E**2 - L**2 - a**2 * c**2) / (r ** 3)
        term3 = - (3.0 * G * M / (c**2 * r**4)) * ((L - a * E) ** 2)
        dpr_dtau = term1 + term2 + term3

        dt_dtau = (1.0 / delta) * ((r**2 + a**2 + r_s * a**2 / r) * E - (r_s * a / r) * L)

        return np.array([dr_dtau, dphi_dtau, dpr_dtau, dt_dtau])

    def integrate_kerr_geodesic(self, r0: float, phi0: float, pr0: float, L: float, proper_time_steps: int = 200, dtau: float = 0.05) -> dict:
        """
        Integrates equatorial Kerr geodesics using Runge-Kutta 4th order (RK4).
        Returns orbit trajectory arrays.
        """
        E = self.compute_energy_constant(r0, pr0, L)
        state = np.array([r0, phi0, pr0, 0.0])  # [r, phi, pr, t]

        trajectory = []
        r_plus, _ = self.kerr_horizons()

        for step in range(proper_time_steps):  # noqa: B007
            trajectory.append(state.copy())

            # Check horizon crossing boundary conditions
            if state[0] <= r_plus + 1e-2:
                break
            # Check escape boundary
            if state[0] > 1000.0:
                break

            # RK4 Integration
            k1 = self._derivatives(state, E, L)
            k2 = self._derivatives(state + 0.5 * dtau * k1, E, L)
            k3 = self._derivatives(state + 0.5 * dtau * k2, E, L)
            k4 = self._derivatives(state + dtau * k3, E, L)

            state += (dtau / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

        traj_arr = np.array(trajectory)
        return {
            "energy": E,
            "horizon": r_plus,
            "proper_time": np.arange(len(traj_arr)) * dtau,
            "r": traj_arr[:, 0],
            "phi": traj_arr[:, 1],
            "pr": traj_arr[:, 2],
            "t": traj_arr[:, 3]
        }


class AstrobiologyEvolutionSimulator:
    """
    Simulates evolutionary dynamics and habitability indexes under non-Earth conditions.
    """
    def __init__(self, gravity_g: float = 1.0, uv_flux_relative: float = 1.0):
        self.gravity = gravity_g
        self.uv_flux = uv_flux_relative

        # Evolution stage names
        self.stages = [
            "Prebiotic Soup",
            "Prokaryotic Equivalents",
            "Eukaryotic Complexity",
            "Multicellular Organization",
            "Sapient Speciation",
            "Technological Civilization"
        ]

        # Evolution rate constants (probability rate per million years)
        self.rates = [0.05, 0.02, 0.015, 0.01, 0.005]

    def calculate_habitability_index(self, temp_k: float, atm_co2_ppm: float, o2_fraction: float) -> float:
        """
        Calculates planetary habitability index H in [0, 1] based on temperature, gravity,
        UV flux, and atmospheric chemistry.
        """
        # Temperature factor (Gaussian centered at 288 K / 15 C)
        f_temp = math.exp(-0.5 * ((temp_k - 288.0) / 18.0) ** 2)

        # Gravity factor (centered at 1.0 g)
        f_grav = math.exp(-0.5 * ((self.gravity - 1.0) / 0.6) ** 2)

        # UV shield factor (high UV flux without O2 is hazardous)
        # Ozone proxy: O2 presence helps shield UV
        shielding = 1.0 - math.exp(-10.0 * o2_fraction)
        effective_uv = self.uv_flux * (1.0 - 0.9 * shielding)
        f_uv = math.exp(-0.5 * (max(0.0, effective_uv - 1.0) / 1.5) ** 2)

        # Liquid water constraint (strictly bounded)
        f_water = 1.0 if (273.0 <= temp_k <= 373.0) else 0.05

        # Atmospheric toxicity (high CO2 reduces complex habitability index)
        f_atm = 1.0 - 0.5 * min(1.0, atm_co2_ppm / 50000.0)

        H = f_temp * f_grav * f_uv * f_water * f_atm
        return max(0.0, min(1.0, H))

    def deterministic_evolution(self, H: float, duration_myr: float = 100.0) -> tuple[float, str]:
        """
        Calculates deterministic evolutionary progress float in [0.0, 5.0]
        and returns current evolutionary state description.
        """
        progress = 0.0
        remaining_time = duration_myr

        for i, rate in enumerate(self.rates):  # noqa: B007
            # Effective rate is modulated by habitability
            eff_rate = rate * H
            if eff_rate <= 0:
                break

            # Time required to complete this stage
            time_required = 1.0 / eff_rate
            if remaining_time >= time_required:
                progress += 1.0
                remaining_time -= time_required
            else:
                progress += remaining_time / time_required
                break

        progress = min(5.0, progress)
        stage_idx = int(progress)
        sub_progress = progress - stage_idx

        if stage_idx >= len(self.stages) - 1:
            state_desc = self.stages[-1]
        else:
            state_desc = f"{self.stages[stage_idx]} ({sub_progress*100:.1f}% transition to {self.stages[stage_idx+1]})"

        return progress, state_desc


class ClimateEBM:
    """
    0D Planetary Energy Balance Model (EBM) with ice-albedo and greenhouse gas feedbacks.
    """
    def __init__(self, T_initial: float = 288.0, CO2_initial: float = 280.0, CH4_initial: float = 0.7):
        self.T = T_initial
        self.CO2 = CO2_initial
        self.CH4 = CH4_initial

        # Physical constants
        self.C_w = 2.0e8       # Heat capacity of planetary surface layer (J / m^2 K)
        self.S_0 = 1361.0      # Stellar Constant (W / m^2)
        self.sigma = 5.6703e-8 # Stefan-Boltzmann Constant (W / m^2 K^4)
        self.epsilon_0 = 0.62  # Base greenhouse emissivity

    def calculate_albedo(self) -> float:
        """Ice-albedo feedback: higher temperature decreases albedo due to ice melt."""
        if self.T <= 263.0:
            return 0.62  # Snowball planet albedo
        elif self.T >= 283.0:
            return 0.30  # Bare rock/vegetation albedo
        else:
            # Linear transition between ice and ground albedo
            return 0.62 - 0.32 * (self.T - 263.0) / 20.0

    def calculate_emissivity(self) -> float:
        """Greenhouse gas concentration feedback on atmospheric emissivity."""
        # Logarithmic CO2 scale, square root CH4 scale
        co2_factor = 0.015 * math.log(max(1.0, self.CO2) / 280.0)
        ch4_factor = 0.010 * (math.sqrt(max(0.01, self.CH4)) - math.sqrt(0.7))

        emissivity = self.epsilon_0 - co2_factor - ch4_factor
        return max(0.35, min(0.95, emissivity))

    def step(self, dt_years: float = 0.1, F_geo: float = 0.0) -> dict:
        """
        Advances the climate state by dt_years.
        F_geo represents geoengineering or artificial heating (W / m^2).
        """
        # Calculate albedo & emissivity
        albedo = self.calculate_albedo()
        emissivity = self.calculate_emissivity()

        # Energy balance terms
        s_incoming = (self.S_0 / 4.0) * (1.0 - albedo)
        lw_outgoing = emissivity * self.sigma * (self.T ** 4)

        net_flux = s_incoming - lw_outgoing + F_geo

        # Temperature derivative (dT/dt)
        # Convert years to seconds (1 yr = 31536000 s)
        dt_seconds = dt_years * 31536000.0
        dT = (net_flux / self.C_w) * dt_seconds

        # Permafrost melting greenhouse gas release feedback
        # If T > 270 K, permafrost melts releasing CO2 and CH4
        if self.T > 270.0:
            d_ch4 = 0.02 * (self.T - 270.0) - 0.05 * (self.CH4 - 0.7)
            d_co2 = 1.5 * (self.T - 270.0) - 0.01 * (self.CO2 - 280.0)
        else:
            # Natural removal/sequestration
            d_ch4 = -0.05 * (self.CH4 - 0.7)
            d_co2 = -0.01 * (self.CO2 - 280.0)

        self.T = max(100.0, min(500.0, self.T + dT))
        self.CH4 = max(0.1, self.CH4 + d_ch4 * dt_years)
        self.CO2 = max(10.0, self.CO2 + d_co2 * dt_years)

        return {
            "temperature": self.T,
            "albedo": albedo,
            "emissivity": emissivity,
            "co2": self.CO2,
            "ch4": self.CH4,
            "absorbed_solar": s_incoming,
            "outgoing_longwave": lw_outgoing
        }
