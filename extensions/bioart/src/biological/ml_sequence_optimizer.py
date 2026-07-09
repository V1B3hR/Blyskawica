#!/usr/bin/env python3
"""
Machine Learning-Based Sequence Optimization
Advanced ML algorithms for optimizing DNA sequences for biological storage and computation
"""

import math
import random
import json
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib

class OptimizationObjective(Enum):
    """Optimization objectives for DNA sequences"""
    GC_CONTENT = "gc_content"
    CODON_OPTIMIZATION = "codon_optimization"
    SECONDARY_STRUCTURE = "secondary_structure"
    SYNTHESIS_EFFICIENCY = "synthesis_efficiency"
    STORAGE_STABILITY = "storage_stability"
    ERROR_RESILIENCE = "error_resilience"
    EXPRESSION_LEVEL = "expression_level"

@dataclass
class SequenceFeatures:
    """Feature extraction for DNA sequences"""
    gc_content: float = 0.0
    length: int = 0
    homopolymer_runs: int = 0
    repeat_content: float = 0.0
    secondary_structure_energy: float = 0.0
    codon_adaptation_index: float = 0.0
    synthesis_complexity: float = 0.0
    melting_temperature: float = 0.0
    
    def to_vector(self) -> List[float]:
        """Convert features to numerical vector for ML"""
        return [
            self.gc_content,
            self.length / 1000.0,  # Normalize length
            self.homopolymer_runs / 10.0,  # Normalize runs
            self.repeat_content,
            self.secondary_structure_energy / 100.0,  # Normalize energy
            self.codon_adaptation_index,
            self.synthesis_complexity,
            self.melting_temperature / 100.0  # Normalize temperature
        ]

@dataclass
class OptimizationResult:
    """Result of sequence optimization"""
    original_sequence: str
    optimized_sequence: str
    score_improvement: float
    optimization_steps: int
    features_before: SequenceFeatures
    features_after: SequenceFeatures
    optimization_log: List[str] = field(default_factory=list)

class GeneticAlgorithmOptimizer:
    """Genetic algorithm for sequence optimization"""
    
    def __init__(self, population_size: int = 100, mutation_rate: float = 0.01):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.nucleotides = ['A', 'U', 'C', 'G']
        
    def mutate_sequence(self, sequence: str) -> str:
        """Apply random mutations to sequence"""
        sequence_list = list(sequence)
        for i in range(len(sequence_list)):
            if random.random() < self.mutation_rate:
                sequence_list[i] = random.choice(self.nucleotides)
        return ''.join(sequence_list)
    
    def crossover(self, parent1: str, parent2: str) -> Tuple[str, str]:
        """Perform crossover between two sequences"""
        if len(parent1) != len(parent2):
            return parent1, parent2
            
        crossover_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2

class NeuralNetworkPredictor:
    """Simple neural network for sequence quality prediction"""
    
    def __init__(self, input_size: int = 8, hidden_size: int = 16):
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        # Initialize weights randomly
        self.weights_input_hidden = [
            [random.gauss(0, 0.1) for _ in range(hidden_size)]
            for _ in range(input_size)
        ]
        self.weights_hidden_output = [random.gauss(0, 0.1) for _ in range(hidden_size)]
        self.bias_hidden = [random.gauss(0, 0.1) for _ in range(hidden_size)]
        self.bias_output = random.gauss(0, 0.1)
    
    def sigmoid(self, x: float) -> float:
        """Sigmoid activation function"""
        return 1.0 / (1.0 + math.exp(-max(-500, min(500, x))))
    
    def predict(self, features: List[float]) -> float:
        """Predict sequence quality score"""
        # Forward pass through hidden layer
        hidden = []
        for j in range(self.hidden_size):
            activation = self.bias_hidden[j]
            for i in range(self.input_size):
                if i < len(features):
                    activation += features[i] * self.weights_input_hidden[i][j]
            hidden.append(self.sigmoid(activation))
        
        # Forward pass to output
        output = self.bias_output
        for j in range(self.hidden_size):
            output += hidden[j] * self.weights_hidden_output[j]
        
        return self.sigmoid(output)

class MLSequenceOptimizer:
    """
    Machine Learning-Based DNA Sequence Optimizer
    Uses genetic algorithms and neural networks for sequence optimization
    """
    
    def __init__(self):
        self.nucleotides = ['A', 'U', 'C', 'G']
        self.genetic_optimizer = GeneticAlgorithmOptimizer()
        self.neural_predictor = NeuralNetworkPredictor()
        self.optimization_history = []
        
        # Codon optimization tables (simplified)
        self.codon_table = {
            'UUU': 'F', 'UUC': 'F', 'UUA': 'L', 'UUG': 'L',
            'UCU': 'S', 'UCC': 'S', 'UCA': 'S', 'UCG': 'S',
            'UAU': 'Y', 'UAC': 'Y', 'UAA': '*', 'UAG': '*',
            'UGU': 'C', 'UGC': 'C', 'UGA': '*', 'UGG': 'W',
            'CUU': 'L', 'CUC': 'L', 'CUA': 'L', 'CUG': 'L',
            'CCU': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
            'CAU': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
            'CGU': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
            'AUU': 'I', 'AUC': 'I', 'AUA': 'I', 'AUG': 'M',
            'ACU': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
            'AAU': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
            'AGU': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
            'GUU': 'V', 'GUC': 'V', 'GUA': 'V', 'GUG': 'V',
            'GCU': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
            'GAU': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
            'GGU': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
        }
        
        # Preferred codons (higher CAI scores)
        self.preferred_codons = {
            'F': 'UUC', 'L': 'CUG', 'S': 'UCG', 'Y': 'UAC',
            'C': 'UGC', 'W': 'UGG', 'P': 'CCG', 'H': 'CAC',
            'Q': 'CAG', 'R': 'CGC', 'I': 'AUC', 'M': 'AUG',
            'T': 'ACG', 'N': 'AAC', 'K': 'AAG', 'V': 'GUG',
            'A': 'GCG', 'D': 'GAC', 'E': 'GAG', 'G': 'GGC'
        }
    
    def extract_features(self, sequence: str) -> SequenceFeatures:
        """Extract features from DNA sequence"""
        features = SequenceFeatures()
        
        if not sequence:
            return features
        
        features.length = len(sequence)
        
        # Calculate GC content
        gc_count = sequence.count('G') + sequence.count('C')
        features.gc_content = gc_count / len(sequence) if len(sequence) > 0 else 0.0
        
        # Count homopolymer runs
        features.homopolymer_runs = self._count_homopolymer_runs(sequence)
        
        # Calculate repeat content
        features.repeat_content = self._calculate_repeat_content(sequence)
        
        # Estimate secondary structure energy (simplified)
        features.secondary_structure_energy = self._estimate_secondary_structure(sequence)
        
        # Calculate codon adaptation index
        features.codon_adaptation_index = self._calculate_cai(sequence)
        
        # Estimate synthesis complexity
        features.synthesis_complexity = self._estimate_synthesis_complexity(sequence)
        
        # Calculate melting temperature
        features.melting_temperature = self._calculate_melting_temperature(sequence)
        
        return features
    
    def _count_homopolymer_runs(self, sequence: str) -> int:
        """Count homopolymer runs (consecutive identical nucleotides)"""
        if len(sequence) < 2:
            return 0
        
        runs = 0
        current_run = 1
        
        for i in range(1, len(sequence)):
            if sequence[i] == sequence[i-1]:
                current_run += 1
            else:
                if current_run >= 4:  # Consider runs of 4+ as problematic
                    runs += 1
                current_run = 1
        
        if current_run >= 4:
            runs += 1
        
        return runs
    
    def _calculate_repeat_content(self, sequence: str) -> float:
        """Calculate percentage of sequence in repeats"""
        if len(sequence) < 6:
            return 0.0
        
        repeat_bases = 0
        window_size = 3
        
        for i in range(len(sequence) - window_size * 2 + 1):
            window = sequence[i:i + window_size]
            remaining = sequence[i + window_size:]
            
            if window in remaining:
                repeat_bases += window_size
        
        return repeat_bases / len(sequence)
    
    def _estimate_secondary_structure(self, sequence: str) -> float:
        """Estimate secondary structure formation energy"""
        if len(sequence) < 4:
            return 0.0
        
        # Simplified base pairing energy calculation
        energy = 0.0
        pairing_energy = {'AU': -2.0, 'UA': -2.0, 'GC': -3.0, 'CG': -3.0}
        
        for i in range(len(sequence) - 3):
            for j in range(i + 4, len(sequence)):
                pair = sequence[i] + sequence[j]
                if pair in pairing_energy:
                    # Distance penalty
                    distance_factor = 1.0 / (j - i)
                    energy += pairing_energy[pair] * distance_factor
        
        return abs(energy)
    
    def _calculate_cai(self, sequence: str) -> float:
        """Calculate Codon Adaptation Index"""
        if len(sequence) % 3 != 0:
            return 0.0
        
        cai_sum = 0.0
        codon_count = 0
        
        for i in range(0, len(sequence) - 2, 3):
            codon = sequence[i:i+3]
            if codon in self.codon_table:
                amino_acid = self.codon_table[codon]
                if amino_acid != '*':  # Skip stop codons
                    # Higher score for preferred codons
                    if amino_acid in self.preferred_codons:
                        if codon == self.preferred_codons[amino_acid]:
                            cai_sum += 1.0
                        else:
                            cai_sum += 0.5
                    else:
                        cai_sum += 0.7
                    codon_count += 1
        
        return cai_sum / codon_count if codon_count > 0 else 0.0
    
    def _estimate_synthesis_complexity(self, sequence: str) -> float:
        """Estimate synthesis difficulty"""
        complexity = 0.0
        
        # Penalize extreme GC content
        gc_content = (sequence.count('G') + sequence.count('C')) / len(sequence) if sequence else 0
        if gc_content < 0.3 or gc_content > 0.7:
            complexity += abs(gc_content - 0.5) * 2
        
        # Penalize homopolymer runs
        complexity += self._count_homopolymer_runs(sequence) * 0.1
        
        # Penalize repeats
        complexity += self._calculate_repeat_content(sequence)
        
        return min(complexity, 1.0)
    
    def _calculate_melting_temperature(self, sequence: str) -> float:
        """Calculate melting temperature (simplified)"""
        if not sequence:
            return 0.0
        
        # Simple Tm calculation
        gc_count = sequence.count('G') + sequence.count('C')
        at_count = sequence.count('A') + sequence.count('U')
        
        if len(sequence) < 14:
            return (at_count * 2) + (gc_count * 4)
        else:
            return 64.9 + 41 * (gc_count - 16.4) / len(sequence)
    
    def calculate_fitness_score(self, sequence: str, objectives: List[OptimizationObjective]) -> float:
        """Calculate fitness score for sequence optimization"""
        features = self.extract_features(sequence)
        score = 0.0
        
        for objective in objectives:
            if objective == OptimizationObjective.GC_CONTENT:
                # Optimal GC content around 50%
                gc_score = 1.0 - abs(features.gc_content - 0.5) * 2
                score += max(0, gc_score)
                
            elif objective == OptimizationObjective.CODON_OPTIMIZATION:
                score += features.codon_adaptation_index
                
            elif objective == OptimizationObjective.SECONDARY_STRUCTURE:
                # Lower secondary structure energy is better
                structure_score = 1.0 - min(features.secondary_structure_energy / 100.0, 1.0)
                score += structure_score
                
            elif objective == OptimizationObjective.SYNTHESIS_EFFICIENCY:
                # Lower synthesis complexity is better
                synthesis_score = 1.0 - features.synthesis_complexity
                score += synthesis_score
                
            elif objective == OptimizationObjective.STORAGE_STABILITY:
                # Balanced features for stability
                stability_score = (
                    (1.0 - abs(features.gc_content - 0.5) * 2) * 0.4 +
                    (1.0 - min(features.homopolymer_runs / 10.0, 1.0)) * 0.3 +
                    (1.0 - features.repeat_content) * 0.3
                )
                score += stability_score
                
            elif objective == OptimizationObjective.ERROR_RESILIENCE:
                # Features that improve error resilience
                resilience_score = (
                    features.codon_adaptation_index * 0.5 +
                    (1.0 - features.repeat_content) * 0.5
                )
                score += resilience_score
        
        # Use neural network prediction as additional factor
        nn_score = self.neural_predictor.predict(features.to_vector())
        score = (score / len(objectives)) * 0.8 + nn_score * 0.2
        
        return min(max(score, 0.0), 1.0)
    
    def optimize_sequence(self, 
                         sequence: str, 
                         objectives: List[OptimizationObjective],
                         max_iterations: int = 100,
                         target_score: float = 0.95) -> OptimizationResult:
        """
        Optimize DNA sequence using machine learning approaches
        """
        original_features = self.extract_features(sequence)
        original_score = self.calculate_fitness_score(sequence, objectives)
        
        best_sequence = sequence
        best_score = original_score
        optimization_log = [f"Initial score: {original_score:.3f}"]
        
        # Genetic Algorithm Optimization
        population = [sequence]
        
        # Create initial population with mutations
        for _ in range(self.genetic_optimizer.population_size - 1):
            mutated = self.genetic_optimizer.mutate_sequence(sequence)
            population.append(mutated)
        
        for iteration in range(max_iterations):
            # Evaluate population
            population_scores = [
                (seq, self.calculate_fitness_score(seq, objectives))
                for seq in population
            ]
            
            # Sort by score (best first)
            population_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Update best if improved
            if population_scores[0][1] > best_score:
                best_sequence = population_scores[0][0]
                best_score = population_scores[0][1]
                optimization_log.append(f"Iteration {iteration}: New best score {best_score:.3f}")
                
                # Check if target reached
                if best_score >= target_score:
                    optimization_log.append(f"Target score {target_score} reached!")
                    break
            
            # Create next generation
            next_population = []
            
            # Keep top 20% (elitism)
            elite_count = max(1, self.genetic_optimizer.population_size // 5)
            for i in range(elite_count):
                next_population.append(population_scores[i][0])
            
            # Generate offspring through crossover and mutation
            while len(next_population) < self.genetic_optimizer.population_size:
                # Tournament selection
                parent1 = self._tournament_selection(population_scores[:50])  # Top 50%
                parent2 = self._tournament_selection(population_scores[:50])
                
                # Crossover
                if len(parent1) == len(parent2):
                    child1, child2 = self.genetic_optimizer.crossover(parent1, parent2)
                else:
                    child1, child2 = parent1, parent2
                
                # Mutation
                child1 = self.genetic_optimizer.mutate_sequence(child1)
                child2 = self.genetic_optimizer.mutate_sequence(child2)
                
                next_population.extend([child1, child2])
            
            # Trim to population size
            population = next_population[:self.genetic_optimizer.population_size]
        
        # Local optimization using hill climbing
        current_sequence = best_sequence
        current_score = best_score
        
        for local_iter in range(20):  # Limited local search
            improved = False
            
            # Try single nucleotide changes
            for pos in range(len(current_sequence)):
                original_nucleotide = current_sequence[pos]
                
                for nucleotide in self.nucleotides:
                    if nucleotide != original_nucleotide:
                        test_sequence = current_sequence[:pos] + nucleotide + current_sequence[pos+1:]
                        test_score = self.calculate_fitness_score(test_sequence, objectives)
                        
                        if test_score > current_score:
                            current_sequence = test_sequence
                            current_score = test_score
                            improved = True
                            optimization_log.append(f"Local optimization: Score improved to {current_score:.3f}")
                            break
                
                if improved:
                    break
            
            if not improved:
                break
        
        final_features = self.extract_features(current_sequence)
        score_improvement = current_score - original_score
        
        result = OptimizationResult(
            original_sequence=sequence,
            optimized_sequence=current_sequence,
            score_improvement=score_improvement,
            optimization_steps=max_iterations,
            features_before=original_features,
            features_after=final_features,
            optimization_log=optimization_log
        )
        
        self.optimization_history.append(result)
        return result
    
    def _tournament_selection(self, population_scores: List[Tuple[str, float]], 
                             tournament_size: int = 3) -> str:
        """Tournament selection for genetic algorithm"""
        tournament = random.sample(population_scores, 
                                 min(tournament_size, len(population_scores)))
        return max(tournament, key=lambda x: x[1])[0]
    
    def batch_optimize(self, 
                      sequences: List[str], 
                      objectives: List[OptimizationObjective],
                      max_iterations: int = 50) -> List[OptimizationResult]:
        """Optimize multiple sequences in batch"""
        results = []
        
        for i, sequence in enumerate(sequences):
            print(f"Optimizing sequence {i+1}/{len(sequences)}...")
            result = self.optimize_sequence(sequence, objectives, max_iterations)
            results.append(result)
        
        return results
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        if not self.optimization_history:
            return {"message": "No optimizations performed yet"}
        
        total_optimizations = len(self.optimization_history)
        total_improvement = sum(r.score_improvement for r in self.optimization_history)
        avg_improvement = total_improvement / total_optimizations
        
        successful_optimizations = sum(1 for r in self.optimization_history 
                                     if r.score_improvement > 0)
        success_rate = successful_optimizations / total_optimizations
        
        report = {
            "total_optimizations": total_optimizations,
            "average_improvement": avg_improvement,
            "success_rate": success_rate,
            "best_improvement": max(r.score_improvement for r in self.optimization_history),
            "recent_optimizations": [
                {
                    "original_length": len(r.original_sequence),
                    "optimized_length": len(r.optimized_sequence),
                    "improvement": r.score_improvement,
                    "steps": r.optimization_steps
                }
                for r in self.optimization_history[-5:]  # Last 5
            ]
        }
        
        return report