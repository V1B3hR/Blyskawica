#!/usr/bin/env python3
"""
DNA Synthesis Systems Integration
Provides interfaces for biological DNA synthesis platforms and validation
Enhanced with real-world testing capabilities and cost optimization
"""

import time
import random
import json
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import threading
from collections import defaultdict

class SynthesisStatus(Enum):
    """DNA synthesis job status"""
    QUEUED = "queued"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATED = "validated"
    CANCELLED = "cancelled"
    QUALITY_CHECK = "quality_check"
    READY_FOR_TESTING = "ready_for_testing"

class SynthesisPlatform(Enum):
    """Available synthesis platforms"""
    TWIST_BIOSCIENCE = "twist_bioscience"
    IDT = "integrated_dna_technologies"
    GENSCRIPT = "genscript"
    EUROFINS = "eurofins"
    THERMOFISHER = "thermofisher"
    CUSTOM_LAB = "custom_lab"

@dataclass
class QualityMetrics:
    """Quality metrics for synthesized DNA"""
    purity: float = 0.0
    length_accuracy: float = 0.0
    sequence_fidelity: float = 0.0
    structural_integrity: float = 0.0
    contamination_level: float = 0.0
    overall_score: float = 0.0
    
    def __post_init__(self):
        if self.overall_score == 0.0:
            self.overall_score = (
                self.purity * 0.3 +
                self.length_accuracy * 0.2 +
                self.sequence_fidelity * 0.3 +
                self.structural_integrity * 0.15 +
                (1.0 - self.contamination_level) * 0.05
            )

@dataclass
class SynthesisJob:
    """Enhanced DNA synthesis job specification"""
    job_id: str
    dna_sequence: str
    length: int
    priority: int = 5
    quality_threshold: float = 0.95
    platform: SynthesisPlatform = SynthesisPlatform.TWIST_BIOSCIENCE
    created_time: float = 0.0
    status: SynthesisStatus = SynthesisStatus.QUEUED
    estimated_completion: float = 0.0
    actual_completion: Optional[float] = None
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    quality_metrics: Optional[QualityMetrics] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Real-world testing fields
    testing_protocols: List[str] = field(default_factory=list)
    testing_results: Dict[str, Any] = field(default_factory=dict)
    validation_status: str = "pending"
    
    def __post_init__(self):
        if self.created_time == 0.0:
            self.created_time = time.time()

class DNASynthesisManager:
    """
    Enhanced DNA Synthesis Systems Manager
    Interfaces with biological synthesis platforms for real DNA production
    Includes cost optimization, quality control, and testing integration
    """
    
    def __init__(self):
        """Initialize enhanced synthesis manager"""
        self.synthesis_queue = []
        self.completed_jobs = []
        self.failed_jobs = []
        self.cancelled_jobs = []
        
        # Enhanced platform specifications with real-world parameters
        self.synthesis_platforms = {
            SynthesisPlatform.TWIST_BIOSCIENCE: {
                'capacity': 100000,  # nucleotides per batch
                'error_rate': 0.0001,
                'speed': 200,  # nucleotides per minute
                'cost_per_nucleotide': 0.08,
                'min_order': 200,
                'max_length': 300000,
                'turnaround_days': 3,
                'quality_guarantee': 0.99,
                'specialties': ['gene_synthesis', 'large_constructs', 'complex_sequences']
            },
            SynthesisPlatform.IDT: {
                'capacity': 50000,
                'error_rate': 0.0002,
                'speed': 150,
                'cost_per_nucleotide': 0.10,
                'min_order': 100,
                'max_length': 20000,
                'turnaround_days': 2,
                'quality_guarantee': 0.98,
                'specialties': ['oligos', 'primers', 'short_sequences']
            },
            SynthesisPlatform.GENSCRIPT: {
                'capacity': 75000,
                'error_rate': 0.0003,
                'speed': 120,
                'cost_per_nucleotide': 0.06,
                'min_order': 300,
                'max_length': 50000,
                'turnaround_days': 5,
                'quality_guarantee': 0.97,
                'specialties': ['cloning', 'mutagenesis', 'optimization']
            },
            SynthesisPlatform.EUROFINS: {
                'capacity': 40000,
                'error_rate': 0.0004,
                'speed': 100,
                'cost_per_nucleotide': 0.12,
                'min_order': 50,
                'max_length': 15000,
                'turnaround_days': 1,
                'quality_guarantee': 0.96,
                'specialties': ['fast_turnaround', 'sequencing', 'validation']
            },
            SynthesisPlatform.THERMOFISHER: {
                'capacity': 60000,
                'error_rate': 0.0002,
                'speed': 180,
                'cost_per_nucleotide': 0.09,
                'min_order': 200,
                'max_length': 100000,
                'turnaround_days': 4,
                'quality_guarantee': 0.98,
                'specialties': ['vectors', 'expression_systems', 'therapeutics']
            },
            SynthesisPlatform.CUSTOM_LAB: {
                'capacity': 10000,
                'error_rate': 0.001,
                'speed': 50,
                'cost_per_nucleotide': 0.20,
                'min_order': 1,
                'max_length': 5000,
                'turnaround_days': 7,
                'quality_guarantee': 0.95,
                'specialties': ['research', 'custom_protocols', 'experimental']
            }
        }
        
        self.job_counter = 0
        
        # Enhanced biological constraints
        self.forbidden_sequences = [
            'AAAAAAAAAA',  # Poly-A sequences
            'TTTTTTTTTT',  # Poly-T sequences  
            'GGGGGGGGGG',  # Poly-G sequences
            'CCCCCCCCCC',  # Poly-C sequences
            'CGTCTC',      # BsaI recognition site
            'GGATCC',      # BamHI recognition site
            'GAATTC',      # EcoRI recognition site
        ]
        
        # Quality control parameters
        self.min_gc_content = 0.2
        self.max_gc_content = 0.8
        self.min_complexity = 0.3
        
        # Cost optimization settings
        self.bulk_discount_threshold = 10000  # nucleotides
        self.bulk_discount_rate = 0.1
        self.priority_cost_multiplier = {1: 3.0, 2: 2.5, 3: 2.0, 4: 1.5, 5: 1.0, 
                                       6: 0.9, 7: 0.8, 8: 0.7, 9: 0.6, 10: 0.5}
        
        # Real-world testing protocols
        self.testing_protocols = {
            'sequence_verification': {
                'description': 'Sanger sequencing verification',
                'cost': 50.0,
                'time_hours': 24,
                'accuracy': 0.999
            },
            'functional_assay': {
                'description': 'Functional expression testing',
                'cost': 200.0,
                'time_hours': 72,
                'accuracy': 0.95
            },
            'structural_analysis': {
                'description': 'Secondary structure validation',
                'cost': 150.0,
                'time_hours': 48,
                'accuracy': 0.92
            },
            'enzymatic_activity': {
                'description': 'Enzymatic activity measurement',
                'cost': 300.0,
                'time_hours': 96,
                'accuracy': 0.90
            },
            'stability_test': {
                'description': 'Thermal and chemical stability',
                'cost': 250.0,
                'time_hours': 120,
                'accuracy': 0.88
            }
        }
        
        # Threading for asynchronous operations
        self._processing_thread = None
        self._stop_processing = False
        
    
    def submit_synthesis_job(self, dna_sequence: str, priority: int = 5, 
                           platform: Optional[SynthesisPlatform] = None,
                           testing_protocols: Optional[List[str]] = None) -> str:
        """
        Submit DNA sequence for biological synthesis with enhanced options
        
        Args:
            dna_sequence: DNA sequence to synthesize
            priority: Job priority (1-10, higher is more urgent)
            platform: Target synthesis platform (auto-select if None)
            testing_protocols: List of testing protocols to apply
            
        Returns:
            Job ID for tracking
        """
        # Validate sequence
        validation_result = self._validate_sequence(dna_sequence)
        if not validation_result['valid']:
            raise ValueError(f"Invalid sequence: {validation_result['errors']}")
        
        # Generate job ID
        self.job_counter += 1
        job_id = f"SYN_{self.job_counter:06d}_{int(time.time())}"
        
        # Select optimal platform
        if platform is None:
            platform = self._select_optimal_platform(
                len(dna_sequence), 
                priority, 
                testing_protocols or []
            )
        
        # Calculate costs
        cost_estimate = self._calculate_synthesis_cost(dna_sequence, platform, priority)
        
        # Create enhanced synthesis job
        job = SynthesisJob(
            job_id=job_id,
            dna_sequence=dna_sequence,
            length=len(dna_sequence),
            priority=priority,
            platform=platform,
            estimated_cost=cost_estimate['total_cost'],
            testing_protocols=testing_protocols or [],
            metadata={
                'gc_content': validation_result['gc_content'],
                'complexity': validation_result['complexity'],
                'platform_specs': self.synthesis_platforms[platform],
                'cost_breakdown': cost_estimate
            }
        )
        
        # Calculate estimated completion
        platform_info = self.synthesis_platforms[platform]
        synthesis_time = (len(dna_sequence) / platform_info['speed']) * 60  # seconds
        testing_time = sum(self.testing_protocols[protocol]['time_hours'] * 3600 
                          for protocol in job.testing_protocols)
        job.estimated_completion = time.time() + synthesis_time + testing_time
        
        # Add to queue (sorted by priority)
        self.synthesis_queue.append(job)
        self.synthesis_queue.sort(key=lambda x: (-x.priority, x.created_time))
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get enhanced synthesis job status and details"""
        # Check all job lists
        all_jobs = self.synthesis_queue + self.completed_jobs + self.failed_jobs + self.cancelled_jobs
        
        for job in all_jobs:
            if job.job_id == job_id:
                return {
                    'job_id': job.job_id,
                    'status': job.status.value,
                    'platform': job.platform.value,
                    'length': job.length,
                    'priority': job.priority,
                    'created_time': job.created_time,
                    'estimated_completion': job.estimated_completion,
                    'actual_completion': job.actual_completion,
                    'estimated_cost': job.estimated_cost,
                    'actual_cost': job.actual_cost,
                    'quality_metrics': job.quality_metrics.__dict__ if job.quality_metrics else None,
                    'testing_protocols': job.testing_protocols,
                    'testing_results': job.testing_results,
                    'validation_status': job.validation_status,
                    'metadata': job.metadata
                }
        
        return None
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a synthesis job if it hasn't started"""
        for job in self.synthesis_queue:
            if job.job_id == job_id and job.status == SynthesisStatus.QUEUED:
                job.status = SynthesisStatus.CANCELLED
                self.synthesis_queue.remove(job)
                self.cancelled_jobs.append(job)
                return True
        return False
    
    def process_synthesis_queue(self) -> List[Dict[str, Any]]:
        """
        Enhanced synthesis queue processing with quality control and testing
        """
        completed_jobs = []
        current_time = time.time()
        
        for job in self.synthesis_queue[:]:
            if job.status == SynthesisStatus.QUEUED:
                job.status = SynthesisStatus.SYNTHESIZING
                
            elif job.status == SynthesisStatus.SYNTHESIZING:
                if current_time >= job.estimated_completion:
                    success = self._simulate_enhanced_synthesis(job)
                    
                    if success:
                        job.status = SynthesisStatus.QUALITY_CHECK
                        job.actual_completion = current_time
                        
                        # Generate quality metrics
                        job.quality_metrics = self._generate_quality_metrics(job)
                        
                        if job.quality_metrics.overall_score >= job.quality_threshold:
                            job.status = SynthesisStatus.COMPLETED
                            
                            # Start testing protocols if any
                            if job.testing_protocols:
                                job.status = SynthesisStatus.READY_FOR_TESTING
                                self._initiate_testing(job)
                            
                            self.completed_jobs.append(job)
                            completed_jobs.append({
                                'job_id': job.job_id,
                                'status': job.status.value,
                                'dna_sequence': job.dna_sequence,
                                'quality_score': job.quality_metrics.overall_score,
                                'actual_cost': job.actual_cost
                            })
                        else:
                            job.status = SynthesisStatus.FAILED
                            self.failed_jobs.append(job)
                    else:
                        job.status = SynthesisStatus.FAILED
                        job.actual_completion = current_time
                        self.failed_jobs.append(job)
                    
                    self.synthesis_queue.remove(job)
        
        return completed_jobs
    
    def run_testing_protocols(self, job_id: str) -> Dict[str, Any]:
        """
        Execute testing protocols for synthesized DNA
        """
        job = None
        for j in self.completed_jobs:
            if j.job_id == job_id:
                job = j
                break
        
        if not job or not job.testing_protocols:
            return {'status': 'error', 'message': 'Job not found or no testing protocols'}
        
        results = {}
        total_cost = 0
        
        for protocol in job.testing_protocols:
            if protocol in self.testing_protocols:
                # Simulate testing
                protocol_spec = self.testing_protocols[protocol]
                success_rate = protocol_spec['accuracy']
                
                # Simulate test execution
                test_passed = random.random() < success_rate
                measurement = random.uniform(0.8, 1.0) if test_passed else random.uniform(0.3, 0.7)
                
                results[protocol] = {
                    'passed': test_passed,
                    'measurement': measurement,
                    'cost': protocol_spec['cost'],
                    'description': protocol_spec['description']
                }
                
                total_cost += protocol_spec['cost']
        
        job.testing_results = results
        job.actual_cost += total_cost
        job.validation_status = 'completed'
        
        # Update job status based on test results
        if all(result['passed'] for result in results.values()):
            job.status = SynthesisStatus.VALIDATED
        else:
            job.status = SynthesisStatus.FAILED
        
        return {
            'status': 'completed',
            'results': results,
            'total_cost': total_cost,
            'overall_validation': job.validation_status
        }
    
    def _calculate_synthesis_cost(self, dna_sequence: str, platform: SynthesisPlatform, priority: int) -> Dict[str, float]:
        """Calculate detailed synthesis cost breakdown"""
        platform_specs = self.synthesis_platforms[platform]
        
        base_cost = len(dna_sequence) * platform_specs['cost_per_nucleotide']
        
        # Apply bulk discount
        bulk_discount = 0.0
        if len(dna_sequence) >= self.bulk_discount_threshold:
            bulk_discount = base_cost * self.bulk_discount_rate
        
        # Apply priority multiplier
        priority_multiplier = self.priority_cost_multiplier.get(priority, 1.0)
        priority_cost = base_cost * (priority_multiplier - 1.0)
        
        # Minimum order cost
        min_order_cost = max(0, platform_specs['min_order'] * platform_specs['cost_per_nucleotide'] - base_cost)
        
        total_cost = base_cost + priority_cost + min_order_cost - bulk_discount
        
        return {
            'base_cost': base_cost,
            'bulk_discount': -bulk_discount,
            'priority_adjustment': priority_cost,
            'minimum_order_fee': min_order_cost,
            'total_cost': total_cost
        }
    
    def _select_optimal_platform(self, sequence_length: int, priority: int, testing_protocols: List[str]) -> SynthesisPlatform:
        """Enhanced platform selection with cost optimization"""
        suitable_platforms = []
        
        for platform, specs in self.synthesis_platforms.items():
            if sequence_length <= specs['max_length'] and sequence_length >= specs['min_order']:
                # Calculate score based on multiple factors
                cost_score = 1.0 / specs['cost_per_nucleotide']
                speed_score = specs['speed'] / 200.0  # Normalize to typical speed
                quality_score = specs['quality_guarantee']
                turnaround_score = 1.0 / specs['turnaround_days']
                
                # Adjust for priority
                if priority <= 3:  # High priority
                    turnaround_score *= 2.0
                
                # Adjust for testing requirements
                specialty_bonus = 0.0
                for protocol in testing_protocols:
                    if any(specialty in protocol for specialty in specs['specialties']):
                        specialty_bonus += 0.1
                
                overall_score = (cost_score * 0.3 + speed_score * 0.2 + 
                               quality_score * 0.3 + turnaround_score * 0.2 + specialty_bonus)
                
                suitable_platforms.append((platform, overall_score))
        
        if not suitable_platforms:
            # Fallback to platform with highest capacity
            return max(self.synthesis_platforms.keys(), 
                      key=lambda p: self.synthesis_platforms[p]['capacity'])
        
        # Select platform with highest score
        best_platform = max(suitable_platforms, key=lambda x: x[1])
        return best_platform[0]
    
    def _simulate_enhanced_synthesis(self, job: SynthesisJob) -> bool:
        """Enhanced synthesis simulation with realistic factors"""
        platform_specs = self.synthesis_platforms[job.platform]
        
        # Base success rate from platform quality guarantee
        base_success_rate = platform_specs['quality_guarantee']
        
        # Adjust for sequence complexity
        complexity_factor = job.metadata['complexity']
        complexity_bonus = (complexity_factor - 0.5) * 0.2  # Bonus/penalty based on complexity
        
        # GC content adjustment
        gc_content = job.metadata['gc_content']
        optimal_gc = 0.5
        gc_penalty = abs(gc_content - optimal_gc) * 0.3
        
        # Length penalty for very long sequences
        length_factor = min(1.0, job.length / platform_specs['max_length'])
        length_penalty = length_factor * 0.1
        
        # Priority bonus (rush jobs might have slightly lower success rate)
        priority_penalty = max(0, (3 - job.priority) * 0.02)
        
        final_success_rate = (base_success_rate + complexity_bonus - 
                            gc_penalty - length_penalty - priority_penalty)
        final_success_rate = max(0.5, min(0.99, final_success_rate))
        
        success = random.random() < final_success_rate
        
        # Calculate actual cost with potential overruns
        if success:
            cost_variation = random.uniform(0.95, 1.05)  # ±5% variation
        else:
            cost_variation = random.uniform(1.2, 1.8)  # Higher cost for failed attempts
        
        job.actual_cost = job.estimated_cost * cost_variation
        
        return success
    
    def _generate_quality_metrics(self, job: SynthesisJob) -> QualityMetrics:
        """Generate realistic quality metrics for synthesized DNA"""
        platform_specs = self.synthesis_platforms[job.platform]
        base_quality = platform_specs['quality_guarantee']
        
        # Add some randomness around the base quality
        purity = max(0.8, min(1.0, base_quality + random.uniform(-0.05, 0.02)))
        length_accuracy = max(0.85, min(1.0, base_quality + random.uniform(-0.03, 0.02)))
        sequence_fidelity = max(0.9, min(1.0, base_quality + random.uniform(-0.02, 0.01)))
        structural_integrity = max(0.85, min(1.0, base_quality + random.uniform(-0.04, 0.02)))
        contamination_level = max(0.0, min(0.1, (1.0 - base_quality) + random.uniform(-0.01, 0.02)))
        
        return QualityMetrics(
            purity=purity,
            length_accuracy=length_accuracy,
            sequence_fidelity=sequence_fidelity,
            structural_integrity=structural_integrity,
            contamination_level=contamination_level
        )
    
    def _initiate_testing(self, job: SynthesisJob) -> None:
        """Initiate testing protocols for synthesized DNA"""
        # This would interface with real laboratory equipment in production
        # For now, we just mark that testing has been initiated
        job.metadata['testing_initiated'] = time.time()
        job.metadata['testing_status'] = 'initiated'
    
    def _validate_sequence(self, dna_sequence: str) -> Dict[str, Any]:
        """Enhanced sequence validation with biological constraints"""
        sequence = dna_sequence.upper().replace('T', 'U')  # Convert T to U for RNA
        errors = []
        warnings = []
        
        # Check length constraints for different platforms
        max_length = max(specs['max_length'] for specs in self.synthesis_platforms.values())
        if len(sequence) > max_length:
            errors.append(f"Sequence too long: {len(sequence)} > {max_length}")
        
        # Check for forbidden sequences (restriction sites, toxic sequences)
        for forbidden in self.forbidden_sequences:
            if forbidden in sequence:
                errors.append(f"Contains forbidden sequence: {forbidden}")
        
        # Check nucleotide composition
        valid_nucleotides = set('AUCG')
        invalid_chars = set(sequence) - valid_nucleotides
        if invalid_chars:
            errors.append(f"Invalid nucleotides: {invalid_chars}")
        
        # Calculate GC content
        gc_count = sequence.count('G') + sequence.count('C')
        gc_content = gc_count / len(sequence) if len(sequence) > 0 else 0
        
        if gc_content < self.min_gc_content or gc_content > self.max_gc_content:
            errors.append(f"GC content out of range: {gc_content:.2f} not in [{self.min_gc_content}, {self.max_gc_content}]")
        elif gc_content < 0.3 or gc_content > 0.7:
            warnings.append(f"GC content may cause synthesis difficulties: {gc_content:.2f}")
        
        # Calculate sequence complexity
        complexity = self._calculate_complexity(sequence)
        if complexity < self.min_complexity:
            errors.append(f"Sequence complexity too low: {complexity:.2f} < {self.min_complexity}")
        
        # Check for problematic motifs
        problematic_motifs = ['AAAAAAA', 'CCCCCCC', 'GGGGGGG', 'UUUUUUU']
        for motif in problematic_motifs:
            if motif in sequence:
                warnings.append(f"Contains potentially problematic motif: {motif}")
        
        # Check for secondary structures (simplified)
        if self._has_strong_secondary_structure(sequence):
            warnings.append("Sequence may form strong secondary structures")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'gc_content': gc_content,
            'complexity': complexity,
            'length': len(sequence)
        }
    
    def _calculate_complexity(self, sequence: str) -> float:
        """Calculate sequence complexity using Shannon entropy"""
        if not sequence:
            return 0.0
        
        # Count nucleotide frequencies
        nucleotide_counts = defaultdict(int)
        for nucleotide in sequence:
            nucleotide_counts[nucleotide] += 1
        
        # Calculate Shannon entropy
        length = len(sequence)
        entropy = 0.0
        for count in nucleotide_counts.values():
            probability = count / length
            if probability > 0:
                import math
                entropy -= probability * math.log2(probability)
        
        # Normalize to 0-1 range (max entropy for 4 nucleotides is 2)
        return entropy / 2.0
    
    def _has_strong_secondary_structure(self, sequence: str) -> bool:
        """Check for potential strong secondary structures (simplified)"""
        # Look for inverted repeats that could form hairpins
        min_stem_length = 6
        max_loop_size = 10
        
        for i in range(len(sequence) - min_stem_length * 2):
            for j in range(i + min_stem_length, min(i + min_stem_length + max_loop_size, len(sequence) - min_stem_length)):
                stem1 = sequence[i:i + min_stem_length]
                stem2_start = j + min_stem_length
                if stem2_start + min_stem_length <= len(sequence):
                    stem2 = sequence[stem2_start:stem2_start + min_stem_length]
                    # Check if stems are complementary (simplified)
                    if self._are_complementary(stem1, stem2[::-1]):  # Reverse stem2
                        return True
        return False
    
    def _are_complementary(self, seq1: str, seq2: str) -> bool:
        """Check if two sequences are complementary"""
        complements = {'A': 'U', 'U': 'A', 'C': 'G', 'G': 'C'}
        if len(seq1) != len(seq2):
            return False
        
        matches = 0
        for n1, n2 in zip(seq1, seq2):
            if complements.get(n1) == n2:
                matches += 1
        
        # Consider >70% complementarity as strong
        return matches / len(seq1) > 0.7
    
    def get_platform_comparison(self, dna_sequence: str) -> Dict[str, Any]:
        """Compare all platforms for a specific sequence"""
        validation = self._validate_sequence(dna_sequence)
        if not validation['valid']:
            return {'error': 'Invalid sequence', 'details': validation['errors']}
        
        comparisons = {}
        
        for platform in SynthesisPlatform:
            specs = self.synthesis_platforms[platform]
            
            # Check if platform can handle this sequence
            if len(dna_sequence) <= specs['max_length'] and len(dna_sequence) >= specs['min_order']:
                cost_estimate = self._calculate_synthesis_cost(dna_sequence, platform, 5)
                
                comparisons[platform.value] = {
                    'can_synthesize': True,
                    'estimated_cost': cost_estimate['total_cost'],
                    'turnaround_days': specs['turnaround_days'],
                    'quality_guarantee': specs['quality_guarantee'],
                    'specialties': specs['specialties'],
                    'error_rate': specs['error_rate'],
                    'cost_breakdown': cost_estimate
                }
            else:
                comparisons[platform.value] = {
                    'can_synthesize': False,
                    'reason': f"Length constraints: {specs['min_order']}-{specs['max_length']} nucleotides"
                }
        
        return {
            'sequence_length': len(dna_sequence),
            'sequence_analysis': validation,
            'platform_comparison': comparisons,
            'recommended_platform': self._select_optimal_platform(len(dna_sequence), 5, []).value
        }
    
    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Get comprehensive synthesis system statistics"""
        all_jobs = self.synthesis_queue + self.completed_jobs + self.failed_jobs + self.cancelled_jobs
        total_jobs = len(all_jobs)
        
        if total_jobs == 0:
            return {'status': 'no_jobs_processed'}
        
        # Calculate platform usage
        platform_usage = defaultdict(int)
        platform_success = defaultdict(int)
        platform_costs = defaultdict(float)
        
        for job in all_jobs:
            platform_usage[job.platform.value] += 1
            if job.status in [SynthesisStatus.COMPLETED, SynthesisStatus.VALIDATED]:
                platform_success[job.platform.value] += 1
            if job.actual_cost > 0:
                platform_costs[job.platform.value] += job.actual_cost
        
        # Quality metrics
        quality_scores = [job.quality_metrics.overall_score for job in self.completed_jobs + self.failed_jobs 
                         if job.quality_metrics]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Cost analysis
        total_costs = sum(job.actual_cost for job in all_jobs if job.actual_cost > 0)
        avg_cost_per_nucleotide = total_costs / sum(job.length for job in all_jobs if job.actual_cost > 0) if total_costs > 0 else 0
        
        return {
            'total_jobs': total_jobs,
            'queued_jobs': len(self.synthesis_queue),
            'completed_jobs': len(self.completed_jobs),
            'failed_jobs': len(self.failed_jobs),
            'cancelled_jobs': len(self.cancelled_jobs),
            'overall_success_rate': len(self.completed_jobs) / max(1, total_jobs - len(self.cancelled_jobs)),
            'platform_usage': dict(platform_usage),
            'platform_success_rates': {
                platform: platform_success[platform] / max(1, platform_usage[platform])
                for platform in platform_usage
            },
            'average_quality_score': avg_quality,
            'total_synthesis_cost': total_costs,
            'average_cost_per_nucleotide': avg_cost_per_nucleotide,
            'platform_costs': dict(platform_costs),
            'available_platforms': [platform.value for platform in SynthesisPlatform],
            'testing_protocols_available': list(self.testing_protocols.keys())
        }