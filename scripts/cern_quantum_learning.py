"""
CERN Subatomic Particle Collision & Tokamak MHD Stability Simulator.
Part of the Błyskawica physics engine for subatomic particle analysis (LHC Geant4-inspired)
and fusion reactor plasma stability predictions.
"""

import math
import random
import sys
from datetime import datetime

import numpy as np


class SubatomicCollisionSimulator:
    """
    Simulates relativistic proton-proton collision events producing heavy resonances
    (like Z bosons or Higgs bosons), tracks secondary leptons in a magnetic field,
    models Bethe-Bloch ionization losses, and performs invariant mass reconstruction.
    """
    def __init__(self, magnetic_field_tesla: float = 3.8):
        self.B = magnetic_field_tesla
        self.m_electron = 0.000511  # GeV/c^2
        self.I_silicon = 173e-9      # Mean excitation energy of Silicon (GeV)
        self.K_bb = 0.0001535        # Bethe-Bloch constant (GeV cm^2 / g)
        self.rho_silicon = 2.33      # Silicon density (g/cm^3)

    def sample_breit_wigner(self, mean: float, gamma: float) -> float:
        """Samples a mass from a Breit-Wigner distribution representing quantum resonances."""
        u = random.random()
        return mean + (gamma / 2.0) * math.tan(math.pi * (u - 0.5))

    def simulate_bethe_bloch(self, momentum_gev: float, mass_gev: float, thickness_cm: float = 0.3) -> float:
        """
        Calculates track ionization energy loss in Silicon tracker using Bethe-Bloch equation:
        -dE/dx = K * z^2 * (Z/A) * (1/beta^2) * [ 0.5*ln(2*me*c^2*beta^2*gamma^2*Tmax / I^2) - beta^2 ]
        """
        if momentum_gev <= 0:
            return 0.0

        energy = math.sqrt(momentum_gev**2 + mass_gev**2)
        beta = momentum_gev / energy
        if beta >= 1.0 or beta <= 1e-4:
            return 0.0

        gamma = 1.0 / math.sqrt(1.0 - beta**2)

        # Maximum energy transfer in single collision
        t_max = (2 * self.m_electron * (beta * gamma)**2) / (1.0 + 2 * gamma * (self.m_electron / mass_gev) + (self.m_electron / mass_gev)**2)

        # Bethe-Bloch formula term (Silicon Z/A = 14/28.08 = 0.498)
        Z_over_A = 0.498
        ln_term = 0.5 * math.log((2 * self.m_electron * (beta * gamma)**2 * t_max) / (self.I_silicon**2))
        dedx = self.rho_silicon * self.K_bb * Z_over_A * (1.0 / beta**2) * (ln_term - beta**2)

        # Energy loss in GeV
        energy_loss = dedx * thickness_cm
        return float(max(0.0, energy_loss))

    def run_collision_event(self, resonance_type: str = "Z") -> dict:
        """
        Simulates a single event:
        1. Generates Z (M0=91.18 GeV, G=2.49 GeV) or Higgs (M0=125.1 GeV, G=0.004 GeV)
        2. Decays it relativistically into two muons (m = 0.105 GeV)
        3. Propagates tracks, applies solenoid curvature and Bethe-Bloch energy loss
        4. Reconstructs invariant mass
        """
        m0 = 91.18 if resonance_type == "Z" else 125.1
        gamma = 2.49 if resonance_type == "Z" else 0.004
        m_muon = 0.1056

        # Generate resonance mass
        true_mass = self.sample_breit_wigner(m0, gamma)
        # Limit boundary to prevent negative or infinite mass
        true_mass = max(m0 - 4*gamma, min(m0 + 4*gamma, true_mass))

        # Decay in rest frame: equal and opposite momentum
        p_star = 0.5 * math.sqrt(max(0.0, true_mass**2 - 4 * m_muon**2))

        # Isotropic decay angles
        theta = math.acos(random.uniform(-1, 1))
        phi = random.uniform(0, 2 * math.pi)

        # Muon 1 and 2 momenta in rest frame
        p1_x = p_star * math.sin(theta) * math.cos(phi)
        p1_y = p_star * math.sin(theta) * math.sin(phi)
        p1_z = p_star * math.cos(theta)

        # Boost to laboratory frame (assume resonance has random forward momentum p_z)
        resonance_pz = random.normalvariate(0.0, 15.0)
        resonance_e = math.sqrt(resonance_pz**2 + true_mass**2)
        beta_z = resonance_pz / resonance_e
        gamma_boost = 1.0 / math.sqrt(1.0 - beta_z**2)

        # Relativistic boost of 4-vectors to Lab Frame
        e1_rest = math.sqrt(p_star**2 + m_muon**2)
        e1_lab = gamma_boost * (e1_rest + beta_z * p1_z)  # noqa: F841
        p1_z_lab = gamma_boost * (p1_z + beta_z * e1_rest)

        e2_rest = e1_rest
        e2_lab = gamma_boost * (e2_rest - beta_z * p1_z)  # noqa: F841
        p2_z_lab = gamma_boost * (-p1_z + beta_z * e2_rest)

        p1_x_lab, p1_y_lab = p1_x, p1_y
        p2_x_lab, p2_y_lab = -p1_x, -p1_y

        p1_t = math.sqrt(p1_x_lab**2 + p1_y_lab**2)
        p2_t = math.sqrt(p2_x_lab**2 + p2_y_lab**2)

        # Calculate energy loss via Bethe-Bloch along Silicon layers
        loss1 = self.simulate_bethe_bloch(p1_t, m_muon, thickness_cm=1.2)
        loss2 = self.simulate_bethe_bloch(p2_t, m_muon, thickness_cm=1.2)

        # Reconstructed tracks
        reconstruct_noise1 = random.normalvariate(0.0, 0.02 * p1_t)
        reconstruct_noise2 = random.normalvariate(0.0, 0.02 * p2_t)

        recon_p1_t = max(0.1, p1_t - loss1 + reconstruct_noise1)
        recon_p2_t = max(0.1, p2_t - loss2 + reconstruct_noise2)

        # Helical curvature radius R = p_t / (0.3 * B)
        r_curvature1 = recon_p1_t / (0.3 * self.B)
        r_curvature2 = recon_p2_t / (0.3 * self.B)

        recon_e1 = math.sqrt(recon_p1_t**2 + p1_z_lab**2 + m_muon**2)
        recon_e2 = math.sqrt(recon_p2_t**2 + p2_z_lab**2 + m_muon**2)

        px1_recon = recon_p1_t * math.cos(phi)
        py1_recon = recon_p1_t * math.sin(phi)
        px2_recon = -recon_p2_t * math.cos(phi)
        py2_recon = -recon_p2_t * math.sin(phi)

        total_e = recon_e1 + recon_e2
        total_px = px1_recon + px2_recon
        total_py = py1_recon + py2_recon
        total_pz = p1_z_lab + p2_z_lab

        recon_mass = math.sqrt(max(0.0, total_e**2 - (total_px**2 + total_py**2 + total_pz**2)))

        return {
            "true_mass": true_mass,
            "reconstructed_mass": recon_mass,
            "muon1_pt": p1_t,
            "muon2_pt": p2_t,
            "muon1_loss": loss1,
            "muon2_loss": loss2,
            "muon1_radius": r_curvature1,
            "muon2_radius": r_curvature2
        }


class TokamakMHDSolver:
    """
    Solves 1D radial poloidal magnetic field diffusion inside a fusion reactor (Tokamak)
    and models tearing mode (Rutherford island growth) instabilities.
    """
    def __init__(self, num_grid_points: int = 50, major_radius: float = 6.2, minor_radius: float = 2.0, B_toroidal: float = 5.3):
        self.N = num_grid_points
        self.R0 = major_radius
        self.a = minor_radius
        self.B_phi = B_toroidal
        self.mu0 = 4.0 * math.pi * 1e-7

        # Grid discretization
        self.r = np.linspace(1e-5, self.a, self.N)
        self.dr = self.r[1] - self.r[0]

        # Initial temperature profile (center T0 = 15 keV = 1.5e4 eV)
        self.T0 = 15000.0
        self.T = self.T0 * (1.0 - (self.r / self.a)**2)**2

        # Spitzer resistivity: eta = eta0 * T^(-1.5), capped to prevent division by zero
        self.eta0 = 1.03e-4 * 1.5
        self.eta = self.eta0 * (np.maximum(self.T, 1.0))**(-1.5)

        # Initial current density profile J(r)
        self.J0 = 1.2e6
        self.J = self.J0 * (1.0 - (self.r / self.a)**2)**1.5

        # Initialize poloidal magnetic field B_theta from Ampere's Law:
        self.B_theta = np.zeros(self.N)
        for i in range(1, self.N):
            val = self.trapezoid_rule(self.J[:i+1] * self.r[:i+1], self.r[:i+1])
            self.B_theta[i] = (self.mu0 * val) / self.r[i]
        self.B_theta[0] = 0.0

        # Instability variables (Tearing mode)
        self.w = 0.01
        self.w_sat = 0.25
        self.delta_prime_0 = 4.0

    def trapezoid_rule(self, y: np.ndarray, x: np.ndarray) -> float:
        """Helper to perform trapezoidal numerical integration (NumPy 2.0 trapz alternative)."""
        n = len(y)
        if n < 2:
            return 0.0
        val = 0.0
        for i in range(n - 1):
            val += 0.5 * (y[i] + y[i+1]) * (x[i+1] - x[i])
        return float(val)

    def compute_safety_factor(self) -> np.ndarray:
        """Computes the safety factor profile q(r) = (r * B_phi) / (R0 * B_theta(r))"""
        q = np.zeros(self.N)
        safe_B_theta = np.where(self.B_theta == 0, 1e-6, self.B_theta)
        q[1:] = (self.r[1:] * self.B_phi) / (self.R0 * safe_B_theta[1:])
        # Analytical limit at r=0
        q[0] = (2.0 * self.B_phi) / (self.mu0 * self.J[0] * self.R0)
        return q

    def step_diffusion(self, dt: float = 0.01):
        """
        Advances the 1D magnetic field diffusion equation:
        d B_theta / dt = d/dr [ (eta / mu0) * (1/r) * d/dr (r * B_theta) ]
        """
        new_B_theta = self.B_theta.copy()

        for i in range(1, self.N - 1):
            rB_i = self.r[i] * self.B_theta[i]
            rB_ip1 = self.r[i+1] * self.B_theta[i+1]
            rB_im1 = self.r[i-1] * self.B_theta[i-1]

            diff_inner_ip = (rB_ip1 - rB_i) / (self.dr * self.r[i])
            diff_inner_im = (rB_i - rB_im1) / (self.dr * self.r[i-1])

            flux_ip = (self.eta[i+1] / self.mu0) * diff_inner_ip
            flux_im = (self.eta[i] / self.mu0) * diff_inner_im

            d_dt = (flux_ip - flux_im) / self.dr
            new_B_theta[i] += d_dt * dt

        new_B_theta[0] = 0.0
        new_B_theta[-1] = self.B_theta[-2]

        self.B_theta = np.clip(new_B_theta, 0.0, 5.0)

        # Recalculate current density J from B_theta
        rB = self.r * self.B_theta
        self.J[1:-1] = (1.0 / (self.mu0 * self.r[1:-1])) * (rB[2:] - rB[:-2]) / (2 * self.dr)
        self.J = np.clip(self.J, -1e7, 1e7)

    def step_rutherford_growth(self, dt: float = 0.01) -> float:
        """
        Solves Rutherford growth of magnetic islands (tearing mode) at the q=2 surface.
        """
        q = self.compute_safety_factor()
        rs_idx = np.argmin(np.abs(q - 2.0))
        eta_s = self.eta[rs_idx]

        delta_prime = self.delta_prime_0 * (1.0 - self.w / self.w_sat)
        dw_dt = (eta_s / self.mu0) * delta_prime

        self.w = max(0.001, self.w + dw_dt * dt)
        return float(self.w)

    def check_disruption(self) -> tuple[bool, str]:
        """Checks if plasma stability limits are exceeded (Major Disruption trigger)."""
        q = self.compute_safety_factor()

        if self.w > 0.30:
            return True, f"Major Disruption! Magnetic island (w={self.w:.3f}) exceeded safety fraction 0.30."

        if q[0] < 0.90:
            return True, f"Major Disruption! Central safety factor q(0)={q[0]:.3f} fell below safety limit."

        return False, "Plasma columns are stable within neoclassical limits."


def simulate_learning(duration_minutes=60, fast_mode=False):
    """
    Subatomic Physics Ingestion & Tokamak MHD Solver main runner.
    """
    print(f"[{datetime.now()}] Blyskawica: Inicjalizacja Fazy XIV - FIZYKA JADROWA I PLAZMA...")

    print(f"[{datetime.now()}] Inicjacja symulatora zderzen subatomowych (Geant4 tracker)...")
    collision_sim = SubatomicCollisionSimulator(magnetic_field_tesla=3.8)

    num_events = 50 if fast_mode else 1000
    z_masses = []
    higgs_masses = []

    for _ in range(num_events):
        ev_z = collision_sim.run_collision_event("Z")
        z_masses.append(ev_z["reconstructed_mass"])

        ev_h = collision_sim.run_collision_event("Higgs")
        higgs_masses.append(ev_h["reconstructed_mass"])

    print(f"[{datetime.now()}] Przeanalizowano {num_events} zderzen czastek elementarnych.")
    print(f"    - Rekonstrukcja Bozonu Z: Srednia rekonstruowana masa = {np.mean(z_masses):.2f} GeV (Oczekiwana: 91.18 GeV)")
    print(f"    - Rekonstrukcja Bozonu Higgsa: Srednia rekonstruowana masa = {np.mean(higgs_masses):.2f} GeV (Oczekiwana: 125.10 GeV)")

    print(f"\n[{datetime.now()}] Inicjalizacja silnika MHD (Tokamak Plasma Columns)...")
    tokamak = TokamakMHDSolver(num_grid_points=50, B_toroidal=5.3)

    steps = 100 if fast_mode else 500
    disrupted = False
    disruption_reason = ""

    dt_step = 0.01
    for step in range(steps):  # noqa: B007
        tokamak.step_diffusion(dt_step)
        island_size = tokamak.step_rutherford_growth(dt_step)  # noqa: F841

        is_disrupted, reason = tokamak.check_disruption()
        if is_disrupted:
            disrupted = True
            disruption_reason = reason
            break

    print(f"[{datetime.now()}] Symulacja MHD Tokamaka ukonczona w {step+1} krokach.")
    q_profile = tokamak.compute_safety_factor()
    print(f"    - Profil wspolczynnika q: q(0)={q_profile[0]:.2f} | q(edge)={q_profile[-1]:.2f}")
    print(f"    - Koncowy rozmiar wyspy magnetycznej w surface q=2: {tokamak.w*100:.2f}% promienia")

    if disrupted:
        print("WYKRYTO ZERWANIE PLAZMY (DISRUPTION)!")
        print(f"    - Powod: {disruption_reason}")
    else:
        print("Plazma stabilna. Konfiguracja magnetyczna zabezpieczona.")

    print(f"\n[{datetime.now()}] Ingestia fizyki subatomowej i stabilnosci fuzji zakonczona pomyslnie.")


if __name__ == "__main__":
    # Ensuring UTF-8 for Windows console when run directly
    if sys.platform == "win32":
        import io
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        except AttributeError:
            pass

    fast = "--fast" in sys.argv
    simulate_learning(fast_mode=fast)
