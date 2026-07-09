#!/usr/bin/env python3
"""
Biological Storage Systems
Real DNA storage and retrieval mechanisms with error simulation
"""

import time
import random
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

class StorageStatus(Enum):
    """DNA storage status"""
    STORED = "stored"
    DEGRADED = "degraded"
    CORRUPTED = "corrupted"
    LOST = "lost"
    RETRIEVED = "retrieved"

@dataclass
class StorageEntry:
    """DNA storage entry"""
    entry_id: str
    dna_sequence: str
    original_data: bytes
    storage_time: float
    access_count: int = 0
    last_accessed: Optional[float] = None
    status: StorageStatus = StorageStatus.STORED
    degradation_rate: float = 0.0001  # per day
    error_count: int = 0
    checksum: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.checksum:
            self.checksum = hashlib.sha256(self.original_data).hexdigest()

class BiologicalStorageManager:
    """
    Biological DNA Storage Manager
    Simulates real DNA storage with degradation, errors, and retrieval
    """
    
    def __init__(self):
        """Initialize biological storage manager"""
        self.storage_entries = {}
        self.storage_counter = 0
        
        # Storage environment parameters
        self.storage_conditions = {
            'temperature': 4.0,    # Celsius (optimal for DNA stability)
            'humidity': 50.0,      # Relative humidity %
            'ph': 7.0,            # pH level
            'uv_exposure': 0.1,   # UV exposure level
        }
        
        # Degradation factors
        self.degradation_factors = {
            'thermal': 0.0001,    # Temperature-induced degradation per day
            'hydrolytic': 0.00005, # Water-induced degradation per day
            'oxidative': 0.00002,  # Oxidation degradation per day
            'mechanical': 0.00001, # Physical damage per access
        }
        
        # Error simulation parameters
        self.error_patterns = {
            'point_mutation': 0.00001,  # Single nucleotide changes
            'deletion': 0.000005,       # Missing nucleotides
            'insertion': 0.000003,      # Extra nucleotides
            'inversion': 0.000001,      # Sequence inversions
        }
        
        # Storage capacity (simulated biological constraints)
        self.max_storage_capacity = 1000000  # 1M nucleotides
        self.current_usage = 0
    
    def store_data(self, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store binary data as DNA sequence in biological storage
        
        Args:
            data: Binary data to store
            metadata: Optional metadata
            
        Returns:
            Storage entry ID
        """
        from ..core.encoding import DNAEncoder
        
        if self.current_usage + len(data) * 4 > self.max_storage_capacity:
            raise ValueError("Storage capacity exceeded")
        
        encoder = DNAEncoder()
        dna_sequence = encoder.encode_bytes(data)
        
        # Generate storage ID
        self.storage_counter += 1
        entry_id = f"STORE_{self.storage_counter:08d}_{int(time.time())}"
        
        # Create storage entry
        entry = StorageEntry(
            entry_id=entry_id,
            dna_sequence=dna_sequence,
            original_data=data,
            storage_time=time.time(),
            metadata=metadata or {}
        )
        
        # Add environmental effects
        entry.degradation_rate = self._calculate_degradation_rate()
        
        self.storage_entries[entry_id] = entry
        self.current_usage += len(dna_sequence)
        
        return entry_id
    
    def retrieve_data(self, entry_id: str, error_correction: bool = True) -> Optional[bytes]:
        """
        Retrieve data from biological storage
        
        Args:
            entry_id: Storage entry ID
            error_correction: Whether to apply error correction
            
        Returns:
            Retrieved data or None if failed
        """
        if entry_id not in self.storage_entries:
            return None
        
        entry = self.storage_entries[entry_id]
        
        # Update access tracking
        entry.access_count += 1
        entry.last_accessed = time.time()
        
        # Apply degradation since storage
        degraded_sequence = self._apply_degradation(entry)
        
        # Apply error correction if requested
        if error_correction:
            corrected_sequence = self._apply_error_correction(degraded_sequence, entry)
        else:
            corrected_sequence = degraded_sequence
        
        # Convert back to binary data
        try:
            from ..core.encoding import DNAEncoder
            encoder = DNAEncoder()
            retrieved_data = encoder.decode_dna(corrected_sequence)
            
            # Verify data integrity
            if self._verify_integrity(retrieved_data, entry):
                entry.status = StorageStatus.RETRIEVED
                return retrieved_data
            else:
                entry.status = StorageStatus.CORRUPTED
                entry.error_count += 1
                return None
                
        except Exception as e:
            entry.status = StorageStatus.CORRUPTED
            entry.error_count += 1
            return None
    
    def _calculate_degradation_rate(self) -> float:
        """Calculate degradation rate based on storage conditions"""
        base_rate = 0.0001  # Base degradation per day
        
        # Temperature effect (exponential)
        temp_factor = 1.0 + (self.storage_conditions['temperature'] - 4.0) * 0.1
        
        # Humidity effect
        humidity_factor = 1.0 + abs(self.storage_conditions['humidity'] - 50.0) * 0.01
        
        # pH effect
        ph_factor = 1.0 + abs(self.storage_conditions['ph'] - 7.0) * 0.2
        
        # UV exposure effect
        uv_factor = 1.0 + self.storage_conditions['uv_exposure'] * 5.0
        
        return base_rate * temp_factor * humidity_factor * ph_factor * uv_factor
    
    def _apply_degradation(self, entry: StorageEntry) -> str:
        """Apply time-based degradation to stored DNA sequence"""
        current_time = time.time()
        days_stored = (current_time - entry.storage_time) / (24 * 3600)
        
        # Calculate total degradation
        total_degradation = entry.degradation_rate * days_stored
        
        # Apply mechanical degradation from access
        mechanical_degradation = entry.access_count * self.degradation_factors['mechanical']
        total_degradation += mechanical_degradation
        
        sequence = list(entry.dna_sequence)
        sequence_length = len(sequence)
        
        # Apply various types of errors based on degradation level
        error_probability = min(0.1, total_degradation)  # Cap at 10% error rate
        
        for i in range(sequence_length):
            if random.random() < error_probability:
                error_type = random.choices(
                    list(self.error_patterns.keys()),
                    weights=list(self.error_patterns.values())
                )[0]
                
                if error_type == 'point_mutation':
                    # Random nucleotide substitution
                    nucleotides = ['A', 'U', 'C', 'G']
                    sequence[i] = random.choice([n for n in nucleotides if n != sequence[i]])
                    
                elif error_type == 'deletion' and i < len(sequence):
                    # Remove nucleotide
                    sequence.pop(i)
                    
                elif error_type == 'insertion':
                    # Insert random nucleotide
                    nucleotides = ['A', 'U', 'C', 'G']
                    sequence.insert(i, random.choice(nucleotides))
                    
                elif error_type == 'inversion' and i < len(sequence) - 1:
                    # Swap adjacent nucleotides
                    sequence[i], sequence[i+1] = sequence[i+1], sequence[i]
        
        return ''.join(sequence)
    
    def _apply_error_correction(self, degraded_sequence: str, entry: StorageEntry) -> str:
        """Apply error correction algorithms to degraded sequence"""
        # Simple error correction using redundancy and pattern recognition
        
        original_length = len(entry.dna_sequence)
        current_length = len(degraded_sequence)
        
        # Length correction - pad or truncate to original length
        if current_length < original_length:
            # Pad missing nucleotides with most common nucleotide
            nucleotide_counts = {}
            for nuc in degraded_sequence:
                nucleotide_counts[nuc] = nucleotide_counts.get(nuc, 0) + 1
            
            most_common = max(nucleotide_counts.keys(), key=lambda k: nucleotide_counts[k])
            degraded_sequence += most_common * (original_length - current_length)
            
        elif current_length > original_length:
            # Truncate excess nucleotides
            degraded_sequence = degraded_sequence[:original_length]
        
        # Pattern-based correction
        corrected_sequence = list(degraded_sequence)
        
        # Fix obvious errors (like invalid characters)
        valid_nucleotides = set('AUCG')
        for i, nuc in enumerate(corrected_sequence):
            if nuc not in valid_nucleotides:
                corrected_sequence[i] = 'A'  # Default replacement
        
        # Fix long homopolymer runs (likely errors)
        for i in range(len(corrected_sequence) - 5):
            if len(set(corrected_sequence[i:i+6])) == 1:  # 6+ identical nucleotides
                # Break up homopolymer run
                corrected_sequence[i+3] = {'A': 'U', 'U': 'A', 'C': 'G', 'G': 'C'}[corrected_sequence[i]]
        
        return ''.join(corrected_sequence)
    
    def _verify_integrity(self, retrieved_data: bytes, entry: StorageEntry) -> bool:
        """Verify data integrity using checksum"""
        retrieved_checksum = hashlib.sha256(retrieved_data).hexdigest()
        return retrieved_checksum == entry.checksum
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive storage statistics"""
        total_entries = len(self.storage_entries)
        
        if total_entries == 0:
            return {
                'total_entries': 0,
                'storage_usage': 0,
                'capacity_utilization': 0.0
            }
        
        # Count entries by status
        status_counts = {}
        total_errors = 0
        total_accesses = 0
        oldest_entry = float('inf')
        newest_entry = 0
        
        for entry in self.storage_entries.values():
            status = entry.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            total_errors += entry.error_count
            total_accesses += entry.access_count
            oldest_entry = min(oldest_entry, entry.storage_time)
            newest_entry = max(newest_entry, entry.storage_time)
        
        return {
            'total_entries': total_entries,
            'storage_usage': self.current_usage,
            'max_capacity': self.max_storage_capacity,
            'capacity_utilization': self.current_usage / self.max_storage_capacity,
            'status_distribution': status_counts,
            'total_errors': total_errors,
            'total_accesses': total_accesses,
            'average_accesses': total_accesses / total_entries,
            'error_rate': total_errors / max(1, total_accesses),
            'oldest_entry_age_days': (time.time() - oldest_entry) / (24 * 3600) if oldest_entry != float('inf') else 0,
            'newest_entry_age_days': (time.time() - newest_entry) / (24 * 3600),
            'storage_conditions': self.storage_conditions.copy()
        }
    
    def optimize_storage_conditions(self) -> Dict[str, float]:
        """Optimize storage conditions for minimum degradation"""
        optimal_conditions = {
            'temperature': 4.0,     # Optimal storage temperature
            'humidity': 50.0,       # Optimal humidity
            'ph': 7.0,             # Neutral pH
            'uv_exposure': 0.0,    # No UV exposure
        }
        
        # Calculate improvement potential
        current_degradation = self._calculate_degradation_rate()
        
        old_conditions = self.storage_conditions.copy()
        self.storage_conditions = optimal_conditions.copy()
        optimal_degradation = self._calculate_degradation_rate()
        self.storage_conditions = old_conditions  # Restore
        
        improvement_factor = current_degradation / optimal_degradation if optimal_degradation > 0 else 1.0
        
        return {
            'current_conditions': old_conditions,
            'optimal_conditions': optimal_conditions,
            'current_degradation_rate': current_degradation,
            'optimal_degradation_rate': optimal_degradation,
            'improvement_factor': improvement_factor
        }
    
    def simulate_long_term_storage(self, entry_id: str, days: int) -> Dict[str, Any]:
        """Simulate long-term storage effects"""
        if entry_id not in self.storage_entries:
            return {'error': 'Entry not found'}
        
        entry = self.storage_entries[entry_id]
        
        # Simulate degradation over time
        original_sequence = entry.dna_sequence
        current_sequence = original_sequence
        
        daily_results = []
        
        for day in range(days):
            # Apply one day of degradation
            old_time = entry.storage_time
            entry.storage_time = time.time() - (days - day - 1) * 24 * 3600
            
            degraded_sequence = self._apply_degradation(entry)
            
            # Calculate error rate for this day
            differences = sum(1 for a, b in zip(original_sequence, degraded_sequence) if a != b)
            error_rate = differences / len(original_sequence) if len(original_sequence) > 0 else 0
            
            daily_results.append({
                'day': day + 1,
                'error_rate': error_rate,
                'sequence_length': len(degraded_sequence),
                'differences': differences
            })
            
            current_sequence = degraded_sequence
            entry.storage_time = old_time  # Restore original time
        
        return {
            'entry_id': entry_id,
            'simulation_days': days,
            'daily_results': daily_results,
            'final_error_rate': daily_results[-1]['error_rate'] if daily_results else 0,
            'survival_probability': 1.0 - daily_results[-1]['error_rate'] if daily_results else 1.0
        }
    
    def backup_storage_entry(self, entry_id: str, redundancy_level: int = 3) -> List[str]:
        """Create redundant backup copies of storage entry"""
        if entry_id not in self.storage_entries:
            raise ValueError("Entry not found")
        
        original_entry = self.storage_entries[entry_id]
        backup_ids = []
        
        for i in range(redundancy_level):
            backup_id = f"{entry_id}_BACKUP_{i+1}"
            
            # Create backup with slight variations to simulate different storage locations
            backup_entry = StorageEntry(
                entry_id=backup_id,
                dna_sequence=original_entry.dna_sequence,
                original_data=original_entry.original_data,
                storage_time=time.time(),
                metadata={**original_entry.metadata, 'backup_of': entry_id, 'backup_number': i+1}
            )
            
            # Slightly different degradation rates for each backup
            backup_entry.degradation_rate = original_entry.degradation_rate * (0.9 + i * 0.1)
            
            self.storage_entries[backup_id] = backup_entry
            backup_ids.append(backup_id)
            self.current_usage += len(backup_entry.dna_sequence)
        
        return backup_ids
    
    def recover_from_backups(self, original_entry_id: str) -> Optional[bytes]:
        """Recover data using backup entries"""
        backup_entries = []
        
        # Find all backup entries
        for entry_id, entry in self.storage_entries.items():
            if entry.metadata.get('backup_of') == original_entry_id:
                backup_entries.append(entry)
        
        if not backup_entries:
            return None
        
        # Try to retrieve from each backup
        best_result = None
        best_quality = 0
        
        for backup_entry in backup_entries:
            try:
                data = self.retrieve_data(backup_entry.entry_id, error_correction=True)
                if data:
                    # Calculate quality score based on integrity
                    quality = 1.0 - backup_entry.error_count / max(1, backup_entry.access_count)
                    if quality > best_quality:
                        best_result = data
                        best_quality = quality
            except:
                continue
        
        return best_result