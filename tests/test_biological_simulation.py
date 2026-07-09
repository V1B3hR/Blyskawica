import unittest
import math
from adaptiveneuralnetwork.central_nervous_system.biological_simulation import (
    GeneticTranslator,
    MetabolicSimulator,
    MetabolicCell
)

class TestBiologicalSimulation(unittest.TestCase):
    def test_transcription(self):
        """Tests DNA to RNA transcription with clean up."""
        dna = "atg cct gaa tga xyz!!!"
        rna = GeneticTranslator.dna_to_rna(dna)
        self.assertEqual(rna, "AUGCCUGAAUGA")  # Only valid DNA characters transcribed, T replaced by U

    def test_translation(self):
        """Tests RNA to protein codon translation."""
        # AUG = Met (Start), UUU = Phe, GAG = Glu, UGA = Stop
        rna = "AUGUUUGAGUGA"
        protein = GeneticTranslator.rna_to_protein(rna)
        self.assertEqual(protein, "MFE")

        # Test no start codon fallback (translates from start)
        rna_no_start = "UUUGAGUGA"
        protein_no_start = GeneticTranslator.rna_to_protein(rna_no_start)
        self.assertEqual(protein_no_start, "FE")

    def test_protein_to_phenotype(self):
        """Tests translation of protein chains to phenotypic cell properties."""
        # 1. Pure Hydrophobic chain (M, V, L, I, F, W, P, A)
        protein_hydro = "MVLIFWPA"
        traits_hydro = GeneticTranslator.protein_to_phenotype(protein_hydro)
        # 100% hydrophobic -> energy_capacity = 5.0 + 30.0 * 1.0 = 35.0
        self.assertAlmostEqual(traits_hydro["energy_capacity"], 35.0)

        # 2. Pure Polar uncharged chain (S, T, C, Y, N, Q)
        protein_polar = "STCYNQ"
        traits_polar = GeneticTranslator.protein_to_phenotype(protein_polar)
        # 100% polar -> calm = 0.5 + 10.0 * 1.0 = 10.5
        self.assertAlmostEqual(traits_polar["calm"], 10.5)

        # 3. Pure Charged chain (R, K, D, E, H)
        protein_charged = "RKDEH"
        traits_charged = GeneticTranslator.protein_to_phenotype(protein_charged)
        # 100% charged -> anxiety_sensitivity = 0.5 + 2.0 * 1.0 = 2.5
        self.assertAlmostEqual(traits_charged["anxiety_sensitivity"], 2.5)

        # 4. Pure Flexible chain (G, P)
        protein_flex = "GP"
        traits_flex = GeneticTranslator.protein_to_phenotype(protein_flex)
        # 100% flex -> trust_baseline = 0.1 + 0.8 * 1.0 = 0.9
        self.assertAlmostEqual(traits_flex["trust_baseline"], 0.9)

    def test_metabolic_kinetics(self):
        """Tests metabolic pathway fluxes under normal supply conditions."""
        metabolism = MetabolicSimulator(glucose=10.0, oxygen=10.0)
        initial_atp = metabolism.atp
        initial_nadh = metabolism.nadh
        
        # Run simulator for a few steps with spike frequency
        # Spikes consume ATP, but glycolysis & Krebs Cycle & OxPhos generate it
        for _ in range(50):
            metabolism.tick(dt=0.01, spike_frequency=2.0, input_glucose=1.5, input_oxygen=2.0)
            
        # Verify that pools remain bounded and charge is active
        self.assertGreater(metabolism.atp, 0.0)
        self.assertLessEqual(metabolism.atp, metabolism.atp_adp_pool)
        self.assertTrue(0.0 <= metabolism.atp_ratio <= 1.0)
        
    def test_starvation_behavior(self):
        """Tests that ATP levels drop under glucose/oxygen starvation."""
        # 1. Glucose Starvation
        metabolism = MetabolicSimulator(glucose=0.0, oxygen=10.0)
        # Zero glucose input, high spike activity to deplete energy
        for _ in range(1500):
            metabolism.tick(dt=0.01, spike_frequency=10.0, input_glucose=0.0, input_oxygen=2.0)
            
        atp_glucose_starved = metabolism.atp
        self.assertLess(atp_glucose_starved, 4.0)  # Significantly depleted

        # 2. Oxygen Starvation
        metabolism_o2 = MetabolicSimulator(glucose=10.0, oxygen=0.0)
        for _ in range(1500):
            metabolism_o2.tick(dt=0.01, spike_frequency=10.0, input_glucose=1.5, input_oxygen=0.0)
            
        atp_o2_starved = metabolism_o2.atp
        self.assertLess(atp_o2_starved, 4.0)

    def test_metabolic_cell_dynamics(self):
        """Tests MetabolicCell translation and functional parameter scaling."""
        # DNA containing hydrophobic start followed by polar and charged
        # Met-Phe-Glu-Ser (AUG-UUU-GAG-UCU)
        dna = "ATGTTTGAGUCT" # Wait, T is T in DNA, U is RNA, but cleanup/transcribe handles it
        dna_clean = "ATGTTTGAGTCT"
        cell = MetabolicCell(cell_id=0, genome_dna=dna_clean)
        
        # Verify initial configurations translated from DNA
        self.assertEqual(cell.protein, "MFES")
        self.assertGreater(cell.base_energy_capacity, 0.0)
        self.assertGreater(cell.base_calm, 0.0)
        
        # Process stimulus under normal metabolic supply
        energy, anxiety = cell.process_stimulus(
            external_stimulus=1.0, 
            spike_frequency=0.0, 
            input_glucose=1.0, 
            input_oxygen=1.0, 
            dt=0.01
        )
        # Verify output values
        self.assertTrue(energy >= 0.0)
        self.assertTrue(anxiety >= 0.0)
        
        # Now trigger starvation
        for _ in range(100):
            cell.process_stimulus(
                external_stimulus=1.0,
                spike_frequency=5.0,
                input_glucose=0.0,  # Starvation
                input_oxygen=0.0,   # Starvation
                dt=0.01
            )
            
        # Verify that Available Energy Capacity and Calm are degraded due to low ATP
        self.assertLess(cell.energy_capacity, cell.base_energy_capacity)
        self.assertLess(cell.calm, cell.base_calm)
        self.assertGreater(cell.anxiety_sensitivity, cell.base_anxiety_sensitivity)

if __name__ == "__main__":
    unittest.main()
