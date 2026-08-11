"""
Biological Simulation Core for Błyskawica SNN.
Implements DNA-to-RNA genetic translation and cellular metabolism (Krebs Cycle / TCA, Glycolysis,
Oxidative Phosphorylation) to provide bio-energetically constrained cognitive cell dynamics.
"""

import logging

logger = logging.getLogger(__name__)

class GeneticTranslator:
    """
    Translates DNA nucleotide sequences into amino acid chains (proteins) using the standard
    codon translation table, and extracts phenotypic cell configurations.
    """
    # Standard codon translation map (RNA triplet -> 1-letter Amino Acid)
    CODON_TABLE = {
        'UUU': 'F', 'UUC': 'F', 'UUA': 'L', 'UUG': 'L',
        'CUU': 'L', 'CUC': 'L', 'CUA': 'L', 'CUG': 'L',
        'AUU': 'I', 'AUC': 'I', 'AUA': 'I', 'AUG': 'M', # AUG is Met / Start
        'GUU': 'V', 'GUC': 'V', 'GUA': 'V', 'GUG': 'V',
        'UCU': 'S', 'UCC': 'S', 'UCA': 'S', 'UCG': 'S',
        'CCU': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
        'ACU': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
        'GCU': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
        'UAU': 'Y', 'UAC': 'Y', 'UAA': 'Stop', 'UAG': 'Stop',
        'CAU': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
        'AAU': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
        'GAU': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
        'UGU': 'C', 'UGC': 'C', 'UGA': 'Stop', 'UGG': 'W',
        'CGU': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
        'AGU': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
        'GGU': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
    }

    # Bio-chemical property classifications of amino acid residues
    HYDROPHOBIC = set(['A', 'V', 'L', 'I', 'P', 'F', 'W', 'M'])  # noqa: C405
    CHARGED = set(['R', 'K', 'D', 'E', 'H'])  # noqa: C405
    POLAR_UNCHARGED = set(['S', 'T', 'C', 'Y', 'N', 'Q'])  # noqa: C405

    @staticmethod
    def dna_to_rna(dna: str) -> str:
        """Transcribes DNA to RNA (replacing T with U)."""
        clean_dna = "".join([c.upper() for c in dna if c.upper() in ['A', 'T', 'C', 'G']])
        return clean_dna.replace('T', 'U')

    @classmethod
    def rna_to_protein(cls, rna: str) -> str:
        """Translates RNA codons into an amino acid sequence starting from Met (AUG)."""
        start_idx = rna.find('AUG')
        if start_idx == -1:
            # Fallback if no start codon: translate from start of string
            start_idx = 0

        protein = []
        for i in range(start_idx, len(rna) - 2, 3):
            codon = rna[i:i+3]
            amino_acid = cls.CODON_TABLE.get(codon, 'X')
            if amino_acid == 'Stop':
                break
            protein.append(amino_acid)
        return "".join(protein)

    @classmethod
    def protein_to_phenotype(cls, protein: str) -> dict[str, float]:
        """
        Extracts structural SNN cell parameters based on amino acid residues:
        - Hydrophobic ratio -> fuels cell energy capacity.
        - Charged ratio -> determines sensitivity to stimulation (excitable states).
        - Polar ratio -> supports baseline calm (hydration/attenuation).
        - Glycine/Proline ratio -> determines trust (structural flexibility).
        """
        if not protein:
            return {
                "energy_capacity": 10.0,
                "anxiety_sensitivity": 1.0,
                "calm": 1.0,
                "trust_baseline": 0.5
            }

        total = len(protein)
        hydrophobic_count = sum(1 for aa in protein if aa in cls.HYDROPHOBIC)
        charged_count = sum(1 for aa in protein if aa in cls.CHARGED)
        polar_count = sum(1 for aa in protein if aa in cls.POLAR_UNCHARGED)
        flex_count = sum(1 for aa in protein if aa in ['G', 'P'])

        hydrophobic_ratio = hydrophobic_count / total
        charged_ratio = charged_count / total
        polar_ratio = polar_count / total
        flex_ratio = flex_count / total

        # Map to reasonable biological SNN ranges
        return {
            "energy_capacity": float(5.0 + 30.0 * hydrophobic_ratio),
            "anxiety_sensitivity": float(0.5 + 2.0 * charged_ratio),
            "calm": float(0.5 + 10.0 * polar_ratio),
            "trust_baseline": float(0.1 + 0.8 * flex_ratio)
        }


class MetabolicSimulator:
    """
    Simulates cellular metabolic fluxes of Glycolysis, Krebs Cycle (TCA),
    and Oxidative Phosphorylation to regulate ATP levels.
    """
    def __init__(self, glucose=5.0, oxygen=10.0):
        # Initial concentrations (in mM/arbitrary units)
        self.glucose = glucose
        self.oxygen = oxygen
        self.pyruvate = 1.0
        self.acetyl_coa = 0.5

        # ATP / ADP pool
        self.atp_adp_pool = 10.0
        self.atp = 8.0  # high initial charge
        self.adp = self.atp_adp_pool - self.atp

        # NAD+ / NADH pool
        self.nad_nadh_pool = 5.0
        self.nadh = 1.0
        self.nad = self.nad_nadh_pool - self.nadh

        # Kinetics constants
        self.k_gly = 0.05    # Glycolysis rate constant
        self.k_pdh = 0.08    # Pyruvate dehydrogenase rate constant
        self.k_tca = 0.06    # Krebs Cycle rate constant
        self.k_ox = 0.12     # Oxidative phosphorylation rate constant
        self.k_basal = 0.02  # Maintenance ATP consumption
        self.k_spike = 0.05  # Spiking ATP consumption

    def tick(self, dt: float = 0.001, spike_frequency: float = 0.0, input_glucose: float = 0.1, input_oxygen: float = 0.2):
        """
        Advances the cellular biochemical metabolic network.
        Equations track fluxes for Glycolysis, Krebs, OxPhos, and Consumption.
        """
        # Re-supply inputs
        self.glucose += input_glucose * dt
        self.oxygen += input_oxygen * dt

        # 1. Glycolysis: Glucose + 2 ADP + 2 NAD+ -> 2 Pyruvate + 2 ATP + 2 NADH
        r_gly = self.k_gly * self.glucose * self.adp * self.nad
        flux_gly = r_gly * dt

        self.glucose = max(0.0, self.glucose - flux_gly)
        self.pyruvate += 2.0 * flux_gly
        self.atp = min(self.atp_adp_pool, self.atp + 2.0 * flux_gly)
        self.nadh = min(self.nad_nadh_pool, self.nadh + 2.0 * flux_gly)

        # Sync pools
        self.adp = self.atp_adp_pool - self.atp
        self.nad = self.nad_nadh_pool - self.nadh

        # 2. PDH reaction: Pyruvate + NAD+ -> Acetyl-CoA + NADH
        r_pdh = self.k_pdh * self.pyruvate * self.nad
        flux_pdh = r_pdh * dt
        self.pyruvate = max(0.0, self.pyruvate - flux_pdh)
        self.acetyl_coa += flux_pdh
        self.nadh = min(self.nad_nadh_pool, self.nadh + flux_pdh)

        # Sync pool
        self.nad = self.nad_nadh_pool - self.nadh

        # 3. Krebs Cycle (TCA): Acetyl-CoA + ADP + 3 NAD+ -> 1 ATP + 3 NADH
        r_tca = self.k_tca * self.acetyl_coa * self.adp * self.nad
        flux_tca = r_tca * dt

        self.acetyl_coa = max(0.0, self.acetyl_coa - flux_tca)
        self.atp = min(self.atp_adp_pool, self.atp + flux_tca)
        self.nadh = min(self.nad_nadh_pool, self.nadh + 3.0 * flux_tca)

        # Sync pools
        self.adp = self.atp_adp_pool - self.atp
        self.nad = self.nad_nadh_pool - self.nadh

        # 4. Oxidative Phosphorylation: NADH + 0.5 O2 + 3 ADP -> NAD+ + 3 ATP
        r_ox = self.k_ox * self.nadh * self.oxygen * self.adp
        flux_ox = r_ox * dt

        self.nadh = max(0.0, self.nadh - flux_ox)
        self.oxygen = max(0.0, self.oxygen - 0.5 * flux_ox)
        self.atp = min(self.atp_adp_pool, self.atp + 3.0 * flux_ox)

        # Sync pools
        self.adp = self.atp_adp_pool - self.atp
        self.nad = self.nad_nadh_pool - self.nadh

        # 5. ATP consumption (basal maintenance + spikes)
        atp_cons_rate = self.k_basal * self.atp + self.k_spike * spike_frequency * self.atp
        flux_cons = atp_cons_rate * dt
        self.atp = max(0.0, self.atp - flux_cons)

        # Sync pools
        self.adp = self.atp_adp_pool - self.atp

    @property
    def atp_ratio(self) -> float:
        """Returns the energy charge ratio of the cell (0.0 to 1.0)."""
        return float(self.atp / self.atp_adp_pool)


class MetabolicCell:
    """
    A cognitive-biological cell that translates its genetic sequence to establish
    phenotypic traits, and operates under metabolic limits (Krebs cycle ATP generation).
    """
    def __init__(self, cell_id: int, genome_dna: str):
        self.cell_id = cell_id
        self.genome_dna = genome_dna

        # Transcribe & Translate DNA to establish phenotypic profile
        rna = GeneticTranslator.dna_to_rna(genome_dna)
        self.protein = GeneticTranslator.rna_to_protein(rna)
        traits = GeneticTranslator.protein_to_phenotype(self.protein)

        # Establish baseline SNN cell characteristics
        self.base_energy_capacity = traits["energy_capacity"]
        self.base_anxiety_sensitivity = traits["anxiety_sensitivity"]
        self.base_calm = traits["calm"]
        self.trust_baseline = traits["trust_baseline"]

        # Run-time adaptive parameters
        self.energy_capacity = self.base_energy_capacity
        self.anxiety_sensitivity = self.base_anxiety_sensitivity
        self.calm = self.base_calm

        self.energy = self.energy_capacity
        self.anxiety = 0.0
        self.trust = self.trust_baseline

        # Initialize Metabolic Simulator
        self.metabolism = MetabolicSimulator()

    def process_stimulus(
        self,
        external_stimulus: float,
        spike_frequency: float,
        input_glucose: float = 0.1,
        input_oxygen: float = 0.2,
        dt: float = 0.001
    ) -> tuple[float, float]:
        """
        Processes biological cell tick:
        1. Advances metabolism to determine current ATP capacity.
        2. Scales baseline parameters according to available ATP.
        3. Updates cell state variables (energy, anxiety).
        """
        # Tick metabolic reactions
        self.metabolism.tick(dt, spike_frequency, input_glucose, input_oxygen)
        atp_charge = self.metabolism.atp_ratio

        # Bio-energetic scaling rules:
        # - Low ATP reduces calm capability (fatigue)
        # - Low ATP raises baseline anxiety (stress response)
        # - Low ATP restricts maximum energy capacity
        self.calm = self.base_calm * max(0.2, atp_charge)
        self.anxiety_sensitivity = self.base_anxiety_sensitivity * (2.0 - atp_charge)
        self.energy_capacity = self.base_energy_capacity * max(0.5, atp_charge)

        # Adjust current energy based on metabolic health
        # High ATP replenishes cell energy, low ATP depletes it
        energy_replenishment = (atp_charge - 0.5) * 2.0 * dt
        self.energy = max(0.0, min(self.energy_capacity, self.energy + energy_replenishment))

        # Integrate cognitive stimulus into anxiety
        anxiety_gain = external_stimulus * self.anxiety_sensitivity
        self.anxiety = max(0.0, self.anxiety + (anxiety_gain - self.calm) * dt)

        return self.energy, self.anxiety
