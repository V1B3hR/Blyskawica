#!/usr/bin/env python3
"""
Genetic Engineering Tools Interface
Interface with CRISPR, genetic modification, and synthetic biology tools
"""

import time
import random
import json
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum

class ModificationType(Enum):
    """Types of genetic modifications"""
    INSERTION = "insertion"
    DELETION = "deletion"
    SUBSTITUTION = "substitution"
    INVERSION = "inversion"
    TRANSLOCATION = "translocation"
    DUPLICATION = "duplication"

class ToolType(Enum):
    """Types of genetic engineering tools"""
    CRISPR_CAS9 = "crispr_cas9"
    CRISPR_CAS12 = "crispr_cas12"
    ZINC_FINGER = "zinc_finger"
    TALEN = "talen"
    BASE_EDITOR = "base_editor"
    PRIME_EDITOR = "prime_editor"

@dataclass
class GuideRNA:
    """Guide RNA specification for CRISPR systems"""
    sequence: str
    target_site: str
    pam_sequence: str
    gc_content: float
    off_target_score: float
    efficiency_score: float
    
@dataclass
class GeneticModification:
    """Genetic modification specification"""
    modification_id: str
    tool_type: ToolType
    modification_type: ModificationType
    target_sequence: str
    target_position: int
    modification_sequence: Optional[str]
    guide_rnas: List[GuideRNA]
    success_probability: float
    off_target_sites: List[str]
    created_time: float
    metadata: Dict[str, Any]

class GeneticEngineeringInterface:
    """
    Interface for genetic engineering tools and operations
    Provides CRISPR design, modification tracking, and synthetic biology integration
    """
    
    def __init__(self):
        """Initialize genetic engineering interface"""
        self.modifications = {}
        self.guide_rna_database = {}
        self.modification_counter = 0
        
        # Tool specifications
        self.tool_specifications = {
            ToolType.CRISPR_CAS9: {
                'pam_sequence': 'NGG',
                'cut_position': -3,
                'efficiency': 0.8,
                'off_target_rate': 0.1,
                'guide_length': 20
            },
            ToolType.CRISPR_CAS12: {
                'pam_sequence': 'TTTV',
                'cut_position': 18,
                'efficiency': 0.7,
                'off_target_rate': 0.05,
                'guide_length': 23
            },
            ToolType.ZINC_FINGER: {
                'recognition_length': 9,
                'efficiency': 0.6,
                'off_target_rate': 0.2,
                'design_difficulty': 'high'
            },
            ToolType.TALEN: {
                'recognition_length': 16,
                'efficiency': 0.7,
                'off_target_rate': 0.15,
                'design_difficulty': 'medium'
            },
            ToolType.BASE_EDITOR: {
                'editing_window': 5,
                'efficiency': 0.9,
                'off_target_rate': 0.02,
                'base_types': ['C>T', 'A>G']
            },
            ToolType.PRIME_EDITOR: {
                'max_insertion': 80,
                'max_deletion': 20,
                'efficiency': 0.6,
                'off_target_rate': 0.01,
                'design_difficulty': 'high'
            }
        }
        
        # PAM sequences for different organisms
        self.organism_pam_preferences = {
            'human': ['NGG', 'NAG'],
            'mouse': ['NGG', 'NGA'],
            'plant': ['NGG', 'NRG'],
            'bacteria': ['NGG', 'NNGRRT'],
            'yeast': ['NGG', 'NAG']
        }
        
        # Off-target prediction parameters
        self.off_target_thresholds = {
            'strict': 0.1,
            'moderate': 0.3,
            'permissive': 0.5
        }
    
    def design_crispr_guides(self, target_sequence: str, tool_type: ToolType = ToolType.CRISPR_CAS9,
                           organism: str = 'human', num_guides: int = 3) -> List[GuideRNA]:
        """
        Design CRISPR guide RNAs for target sequence
        
        Args:
            target_sequence: DNA sequence to target
            tool_type: CRISPR tool type
            organism: Target organism
            num_guides: Number of guide RNAs to generate
            
        Returns:
            List of designed guide RNAs
        """
        tool_spec = self.tool_specifications[tool_type]
        guide_length = tool_spec['guide_length']
        pam_sequences = self.organism_pam_preferences.get(organism, ['NGG'])
        
        candidate_guides = []
        
        # Scan for potential guide sites
        for i in range(len(target_sequence) - guide_length):
            for pam in pam_sequences:
                pam_pattern = self._convert_pam_pattern(pam)
                
                # Check for PAM downstream of guide
                pam_start = i + guide_length
                if pam_start + len(pam_pattern) <= len(target_sequence):
                    potential_pam = target_sequence[pam_start:pam_start + len(pam_pattern)]
                    
                    if self._matches_pam_pattern(potential_pam, pam_pattern):
                        guide_seq = target_sequence[i:i + guide_length]
                        
                        # Calculate guide RNA properties
                        gc_content = self._calculate_gc_content(guide_seq)
                        efficiency_score = self._calculate_efficiency_score(guide_seq, tool_type)
                        off_target_score = self._predict_off_target_score(guide_seq, target_sequence)
                        
                        guide_rna = GuideRNA(
                            sequence=guide_seq,
                            target_site=target_sequence[i:pam_start + len(pam_pattern)],
                            pam_sequence=potential_pam,
                            gc_content=gc_content,
                            off_target_score=off_target_score,
                            efficiency_score=efficiency_score
                        )
                        
                        candidate_guides.append(guide_rna)
        
        # Rank and select best guides
        candidate_guides.sort(key=lambda g: (g.efficiency_score * (1 - g.off_target_score)), reverse=True)
        
        return candidate_guides[:num_guides]
    
    def design_genetic_modification(self, target_sequence: str, modification_type: ModificationType,
                                  modification_sequence: Optional[str] = None, 
                                  tool_type: ToolType = ToolType.CRISPR_CAS9,
                                  target_position: Optional[int] = None) -> str:
        """
        Design genetic modification
        
        Args:
            target_sequence: Target DNA sequence
            modification_type: Type of modification
            modification_sequence: Sequence for insertion/substitution
            tool_type: Genetic engineering tool to use
            target_position: Specific position for modification
            
        Returns:
            Modification ID
        """
        self.modification_counter += 1
        modification_id = f"MOD_{self.modification_counter:06d}_{int(time.time())}"
        
        # Design guide RNAs
        guide_rnas = self.design_crispr_guides(target_sequence, tool_type)
        
        # Calculate success probability
        success_prob = self._calculate_modification_success_probability(
            modification_type, tool_type, len(modification_sequence or "")
        )
        
        # Predict off-target sites
        off_target_sites = self._predict_off_target_sites(guide_rnas, target_sequence)
        
        # Determine target position
        if target_position is None:
            target_position = len(target_sequence) // 2  # Default to middle
        
        modification = GeneticModification(
            modification_id=modification_id,
            tool_type=tool_type,
            modification_type=modification_type,
            target_sequence=target_sequence,
            target_position=target_position,
            modification_sequence=modification_sequence,
            guide_rnas=guide_rnas,
            success_probability=success_prob,
            off_target_sites=off_target_sites,
            created_time=time.time(),
            metadata={
                'organism': 'human',  # Default
                'cell_type': 'unknown',
                'delivery_method': 'lipofection'
            }
        )
        
        self.modifications[modification_id] = modification
        
        return modification_id
    
    def simulate_modification(self, modification_id: str, target_genome: str) -> Dict[str, Any]:
        """
        Simulate genetic modification on target genome
        
        Args:
            modification_id: Modification to simulate
            target_genome: Target genome sequence
            
        Returns:
            Simulation results
        """
        if modification_id not in self.modifications:
            raise ValueError(f"Modification {modification_id} not found")
        
        modification = self.modifications[modification_id]
        
        # Find target site in genome
        target_sites = self._find_target_sites(modification.target_sequence, target_genome)
        
        if not target_sites:
            return {
                'success': False,
                'error': 'Target sequence not found in genome',
                'modified_genome': target_genome
            }
        
        # Simulate modification success
        success = random.random() < modification.success_probability
        
        if not success:
            return {
                'success': False,
                'error': 'Modification failed due to low efficiency',
                'modified_genome': target_genome,
                'attempted_sites': target_sites
            }
        
        # Apply modification
        modified_genome = target_genome
        modifications_applied = []
        
        for site_pos in target_sites[:1]:  # Apply to first site only for safety
            if modification.modification_type == ModificationType.INSERTION:
                if modification.modification_sequence:
                    insert_pos = site_pos + modification.target_position
                    modified_genome = (modified_genome[:insert_pos] + 
                                     modification.modification_sequence + 
                                     modified_genome[insert_pos:])
                    modifications_applied.append({
                        'type': 'insertion',
                        'position': insert_pos,
                        'sequence': modification.modification_sequence
                    })
            
            elif modification.modification_type == ModificationType.DELETION:
                delete_start = site_pos + modification.target_position
                delete_end = delete_start + len(modification.modification_sequence or "1")
                modified_genome = modified_genome[:delete_start] + modified_genome[delete_end:]
                modifications_applied.append({
                    'type': 'deletion',
                    'start': delete_start,
                    'end': delete_end
                })
            
            elif modification.modification_type == ModificationType.SUBSTITUTION:
                if modification.modification_sequence:
                    subst_start = site_pos + modification.target_position
                    subst_end = subst_start + len(modification.modification_sequence)
                    modified_genome = (modified_genome[:subst_start] + 
                                     modification.modification_sequence + 
                                     modified_genome[subst_end:])
                    modifications_applied.append({
                        'type': 'substitution',
                        'position': subst_start,
                        'original': target_genome[subst_start:subst_end],
                        'modified': modification.modification_sequence
                    })
        
        # Check for off-target effects
        off_target_effects = self._simulate_off_target_effects(modification, modified_genome)
        
        return {
            'success': True,
            'modified_genome': modified_genome,
            'target_sites': target_sites,
            'modifications_applied': modifications_applied,
            'off_target_effects': off_target_effects,
            'efficiency': modification.success_probability
        }
    
    def optimize_guide_rna(self, guide_rna: GuideRNA, target_sequence: str) -> GuideRNA:
        """Optimize guide RNA design"""
        optimized_sequence = guide_rna.sequence
        
        # Optimize GC content (target 40-60%)
        current_gc = self._calculate_gc_content(optimized_sequence)
        if current_gc < 0.4 or current_gc > 0.6:
            optimized_sequence = self._adjust_gc_content(optimized_sequence, target_range=(0.4, 0.6))
        
        # Avoid homopolymer runs
        optimized_sequence = self._break_homopolymers(optimized_sequence)
        
        # Recalculate scores
        new_gc_content = self._calculate_gc_content(optimized_sequence)
        new_efficiency = self._calculate_efficiency_score(optimized_sequence, ToolType.CRISPR_CAS9)
        new_off_target = self._predict_off_target_score(optimized_sequence, target_sequence)
        
        return GuideRNA(
            sequence=optimized_sequence,
            target_site=guide_rna.target_site,
            pam_sequence=guide_rna.pam_sequence,
            gc_content=new_gc_content,
            off_target_score=new_off_target,
            efficiency_score=new_efficiency
        )
    
    def predict_off_target_effects(self, guide_rna: GuideRNA, genome_sequence: str,
                                 threshold: str = 'moderate') -> List[Dict[str, Any]]:
        """Predict off-target effects genome-wide"""
        threshold_value = self.off_target_thresholds[threshold]
        off_targets = []
        
        guide_seq = guide_rna.sequence
        
        # Scan genome for potential off-target sites
        for i in range(len(genome_sequence) - len(guide_seq)):
            potential_site = genome_sequence[i:i + len(guide_seq)]
            similarity = self._calculate_sequence_similarity(guide_seq, potential_site)
            
            if similarity >= threshold_value:
                # Check for PAM sequence nearby
                pam_start = i + len(guide_seq)
                if pam_start + 3 <= len(genome_sequence):
                    potential_pam = genome_sequence[pam_start:pam_start + 3]
                    if self._matches_pam_pattern(potential_pam, 'NGG'):
                        off_targets.append({
                            'position': i,
                            'sequence': potential_site,
                            'pam': potential_pam,
                            'similarity': similarity,
                            'mismatch_count': self._count_mismatches(guide_seq, potential_site)
                        })
        
        # Sort by similarity (highest first)
        off_targets.sort(key=lambda x: x['similarity'], reverse=True)
        
        return off_targets[:20]  # Return top 20 potential off-targets
    
    def design_base_editing_strategy(self, target_sequence: str, target_base: str,
                                   desired_base: str, position: int) -> Dict[str, Any]:
        """Design base editing strategy"""
        if f"{target_base}>{desired_base}" not in self.tool_specifications[ToolType.BASE_EDITOR]['base_types']:
            raise ValueError(f"Base editing {target_base}>{desired_base} not supported")
        
        # Design base editor guide
        editing_window = self.tool_specifications[ToolType.BASE_EDITOR]['editing_window']
        
        # Find optimal guide position to place target base in editing window
        optimal_guide_start = position - editing_window // 2 - 10  # Account for guide length
        
        if optimal_guide_start < 0:
            optimal_guide_start = 0
        
        guide_sequence = target_sequence[optimal_guide_start:optimal_guide_start + 20]
        
        # Calculate editing efficiency
        context_score = self._calculate_base_editing_context_score(
            target_sequence, position, target_base, desired_base
        )
        
        return {
            'guide_rna': guide_sequence,
            'target_position_in_guide': position - optimal_guide_start,
            'editing_window': editing_window,
            'context_score': context_score,
            'predicted_efficiency': context_score * 0.6,  # Base editing is typically 60% max
            'target_base': target_base,
            'desired_base': desired_base
        }
    
    def track_modification_history(self, modification_id: str) -> Dict[str, Any]:
        """Track modification history and outcomes"""
        if modification_id not in self.modifications:
            return {'error': 'Modification not found'}
        
        modification = self.modifications[modification_id]
        
        return {
            'modification_id': modification_id,
            'created': modification.created_time,
            'tool_type': modification.tool_type.value,
            'modification_type': modification.modification_type.value,
            'target_sequence': modification.target_sequence,
            'guide_rnas': [
                {
                    'sequence': guide.sequence,
                    'efficiency_score': guide.efficiency_score,
                    'off_target_score': guide.off_target_score,
                    'gc_content': guide.gc_content
                }
                for guide in modification.guide_rnas
            ],
            'success_probability': modification.success_probability,
            'off_target_sites_count': len(modification.off_target_sites),
            'metadata': modification.metadata
        }
    
    # Helper methods
    def _convert_pam_pattern(self, pam: str) -> str:
        """Convert PAM pattern to regex-like pattern"""
        # N = any nucleotide, R = A or G, Y = C or T, etc.
        conversions = {
            'N': '[AUCG]',
            'R': '[AG]',
            'Y': '[CU]',
            'V': '[ACG]'
        }
        
        pattern = pam
        for char, replacement in conversions.items():
            pattern = pattern.replace(char, replacement)
        
        return pattern
    
    def _matches_pam_pattern(self, sequence: str, pattern: str) -> bool:
        """Check if sequence matches PAM pattern"""
        # Simplified pattern matching
        if len(sequence) != len(pattern):
            return False
        
        for i in range(len(sequence)):
            if pattern[i] not in ['N', '[AUCG]'] and pattern[i] != sequence[i]:
                if pattern[i] == '[AG]' and sequence[i] not in 'AG':
                    return False
                elif pattern[i] == '[CU]' and sequence[i] not in 'CU':
                    return False
                elif pattern[i] == '[ACG]' and sequence[i] not in 'ACG':
                    return False
        
        return True
    
    def _calculate_gc_content(self, sequence: str) -> float:
        """Calculate GC content of sequence"""
        gc_count = sequence.count('G') + sequence.count('C')
        return gc_count / len(sequence) if len(sequence) > 0 else 0.0
    
    def _calculate_efficiency_score(self, guide_sequence: str, tool_type: ToolType) -> float:
        """Calculate predicted efficiency score for guide RNA"""
        base_efficiency = self.tool_specifications[tool_type]['efficiency']
        
        # Adjust based on sequence features
        gc_content = self._calculate_gc_content(guide_sequence)
        gc_penalty = abs(gc_content - 0.5) * 0.2  # Penalty for extreme GC content
        
        # Penalty for homopolymer runs
        homopolymer_penalty = 0
        for i in range(len(guide_sequence) - 3):
            if len(set(guide_sequence[i:i+4])) == 1:
                homopolymer_penalty += 0.1
        
        final_score = base_efficiency - gc_penalty - homopolymer_penalty
        return max(0.1, min(1.0, final_score))
    
    def _predict_off_target_score(self, guide_sequence: str, target_sequence: str) -> float:
        """Predict off-target score (higher = more off-targets)"""
        # Simple heuristic: sequences with common motifs have higher off-target potential
        common_motifs = ['AAAA', 'GGGG', 'CCCC', 'UUUU']
        
        motif_count = 0
        for motif in common_motifs:
            motif_count += guide_sequence.count(motif)
        
        # GC content effect
        gc_content = self._calculate_gc_content(guide_sequence)
        gc_effect = abs(gc_content - 0.5) * 0.5
        
        base_off_target = 0.1 + (motif_count * 0.1) + gc_effect
        return min(1.0, base_off_target)
    
    def _calculate_modification_success_probability(self, modification_type: ModificationType,
                                                  tool_type: ToolType, modification_length: int) -> float:
        """Calculate success probability for modification"""
        base_efficiency = self.tool_specifications[tool_type]['efficiency']
        
        # Adjust based on modification type
        type_modifiers = {
            ModificationType.DELETION: 1.0,
            ModificationType.INSERTION: 0.8 if modification_length < 50 else 0.5,
            ModificationType.SUBSTITUTION: 0.9,
            ModificationType.INVERSION: 0.6,
            ModificationType.TRANSLOCATION: 0.3,
            ModificationType.DUPLICATION: 0.7
        }
        
        type_modifier = type_modifiers.get(modification_type, 0.5)
        
        # Length penalty for large modifications
        length_penalty = 1.0
        if modification_length > 100:
            length_penalty = 0.8
        elif modification_length > 1000:
            length_penalty = 0.5
        
        return base_efficiency * type_modifier * length_penalty
    
    def _predict_off_target_sites(self, guide_rnas: List[GuideRNA], target_sequence: str) -> List[str]:
        """Predict potential off-target sites"""
        off_targets = []
        
        for guide in guide_rnas:
            # Simple prediction based on sequence similarity
            guide_seq = guide.sequence
            
            # Generate potential off-target sequences
            for i in range(min(5, len(target_sequence) - len(guide_seq))):
                potential_site = target_sequence[i:i + len(guide_seq)]
                similarity = self._calculate_sequence_similarity(guide_seq, potential_site)
                
                if similarity > 0.7:  # High similarity threshold
                    off_targets.append(potential_site)
        
        return off_targets
    
    def _find_target_sites(self, target_sequence: str, genome: str) -> List[int]:
        """Find all occurrences of target sequence in genome"""
        sites = []
        start = 0
        
        while True:
            pos = genome.find(target_sequence, start)
            if pos == -1:
                break
            sites.append(pos)
            start = pos + 1
        
        return sites
    
    def _simulate_off_target_effects(self, modification: GeneticModification, 
                                   genome: str) -> List[Dict[str, Any]]:
        """Simulate off-target effects"""
        effects = []
        
        for off_target_site in modification.off_target_sites[:3]:  # Check first 3
            sites = self._find_target_sites(off_target_site, genome)
            
            for site_pos in sites:
                if random.random() < 0.1:  # 10% chance of off-target effect
                    effects.append({
                        'position': site_pos,
                        'sequence': off_target_site,
                        'effect_type': 'unintended_cut',
                        'severity': random.choice(['low', 'medium', 'high'])
                    })
        
        return effects
    
    def _calculate_sequence_similarity(self, seq1: str, seq2: str) -> float:
        """Calculate sequence similarity (0-1)"""
        if len(seq1) != len(seq2):
            return 0.0
        
        matches = sum(1 for a, b in zip(seq1, seq2) if a == b)
        return matches / len(seq1)
    
    def _count_mismatches(self, seq1: str, seq2: str) -> int:
        """Count mismatches between sequences"""
        return sum(1 for a, b in zip(seq1, seq2) if a != b)
    
    def _adjust_gc_content(self, sequence: str, target_range: Tuple[float, float]) -> str:
        """Adjust GC content to target range"""
        # Simplified implementation
        current_gc = self._calculate_gc_content(sequence)
        target_gc = (target_range[0] + target_range[1]) / 2
        
        if abs(current_gc - target_gc) < 0.05:
            return sequence
        
        # Simple adjustment by substitution
        sequence_list = list(sequence)
        
        if current_gc < target_gc:  # Need more GC
            for i, nucleotide in enumerate(sequence_list):
                if nucleotide in 'AU' and random.random() < 0.3:
                    sequence_list[i] = random.choice(['G', 'C'])
        else:  # Need less GC
            for i, nucleotide in enumerate(sequence_list):
                if nucleotide in 'GC' and random.random() < 0.3:
                    sequence_list[i] = random.choice(['A', 'U'])
        
        return ''.join(sequence_list)
    
    def _break_homopolymers(self, sequence: str) -> str:
        """Break up homopolymer runs"""
        sequence_list = list(sequence)
        
        for i in range(len(sequence_list) - 3):
            if len(set(sequence_list[i:i+4])) == 1:  # 4+ identical nucleotides
                # Replace middle nucleotide
                current = sequence_list[i]
                alternatives = [n for n in 'AUCG' if n != current]
                sequence_list[i+2] = random.choice(alternatives)
        
        return ''.join(sequence_list)
    
    def _calculate_base_editing_context_score(self, sequence: str, position: int,
                                            target_base: str, desired_base: str) -> float:
        """Calculate context score for base editing"""
        # Check surrounding nucleotides (context matters for base editing)
        context_start = max(0, position - 2)
        context_end = min(len(sequence), position + 3)
        context = sequence[context_start:context_end]
        
        # Favorable contexts for base editing
        favorable_contexts = {
            'C>T': ['AC', 'GC', 'CC'],  # Cytosine base editing
            'A>G': ['AA', 'GA', 'CA']   # Adenine base editing
        }
        
        edit_type = f"{target_base}>{desired_base}"
        if edit_type in favorable_contexts:
            for favorable in favorable_contexts[edit_type]:
                if favorable in context:
                    return 0.8
        
        return 0.5  # Neutral context
    
    def get_genetic_engineering_statistics(self) -> Dict[str, Any]:
        """Get genetic engineering system statistics"""
        total_modifications = len(self.modifications)
        
        if total_modifications == 0:
            return {'total_modifications': 0}
        
        # Analyze modifications by type
        tool_counts = {}
        modification_type_counts = {}
        
        for mod in self.modifications.values():
            tool_type = mod.tool_type.value
            mod_type = mod.modification_type.value
            
            tool_counts[tool_type] = tool_counts.get(tool_type, 0) + 1
            modification_type_counts[mod_type] = modification_type_counts.get(mod_type, 0) + 1
        
        return {
            'total_modifications': total_modifications,
            'tool_usage': tool_counts,
            'modification_types': modification_type_counts,
            'average_success_probability': sum(mod.success_probability for mod in self.modifications.values()) / total_modifications,
            'total_guide_rnas': sum(len(mod.guide_rnas) for mod in self.modifications.values()),
            'available_tools': [tool.value for tool in ToolType],
            'supported_modifications': [mod_type.value for mod_type in ModificationType]
        }