"""
test_phase22_sustainability.py - Test suite for Phase 22 sustainability framework

Tests sustainability and global equity capabilities including:
- Energy monitoring and optimization
- Carbon footprint tracking
- Model compression
- Global equity measurement
- Phase 22 exit criteria validation
"""

import unittest
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sustainability_framework import (
    SustainabilityFramework,
    SustainabilityMonitor,
    ModelOptimizer,
    GlobalEquityManager,
    EnergyMetrics,
    CarbonMetrics,
    EquityMetrics,
    ModelEfficiencyMetrics,
    ComputeEnvironment,
    DeploymentRegion,
    EnergySource
)


class TestPhase22Sustainability(unittest.TestCase):
    """Test suite for Phase 22 sustainability capabilities"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.framework = SustainabilityFramework(data_dir="/tmp/test_sustainability")
        
    def test_framework_initialization(self):
        """Test sustainability framework initialization"""
        self.assertIsNotNone(self.framework)
        self.assertIsNotNone(self.framework.sustainability_monitor)
        self.assertIsNotNone(self.framework.model_optimizer)
        self.assertIsNotNone(self.framework.equity_manager)
        
        self.assertEqual(self.framework.energy_reduction_target, 0.35)
        self.assertEqual(self.framework.global_equity_target, 0.88)
        
        print("✓ Sustainability framework initialization successful")
    
    def test_energy_monitoring(self):
        """Test energy consumption monitoring"""
        monitor = self.framework.sustainability_monitor
        
        # Record some energy metrics
        for i in range(10):
            energy = 5.0 - (i * 0.3)  # Decreasing energy
            self.framework.record_inference(
                environment=ComputeEnvironment.CLOUD_GPU,
                energy_joules=energy,
                duration_ms=50.0
            )
        
        self.assertEqual(len(monitor.energy_records), 10)
        self.assertIsNotNone(monitor.baseline_energy_per_inference)
        
        reduction = monitor.get_energy_reduction()
        self.assertGreaterEqual(reduction, 0.0)
        
        print(f"✓ Energy monitoring validated")
        print(f"  Records: {len(monitor.energy_records)}")
        print(f"  Energy reduction: {reduction:.1%}")
    
    def test_carbon_footprint_calculation(self):
        """Test carbon footprint calculation"""
        monitor = self.framework.sustainability_monitor
        
        # Record energy consumption
        for _ in range(50):
            self.framework.record_inference(
                environment=ComputeEnvironment.CLOUD_GPU,
                energy_joules=4.5,
                duration_ms=45.0
            )
        
        # Calculate carbon for a region
        carbon = monitor.calculate_carbon_footprint(DeploymentRegion.NORTH_AMERICA)
        
        self.assertIsNotNone(carbon)
        self.assertGreater(carbon.energy_kwh, 0.0)
        self.assertGreater(carbon.carbon_emissions_kg, 0.0)
        
        print(f"✓ Carbon footprint calculated")
        print(f"  Energy: {carbon.energy_kwh:.6f} kWh")
        print(f"  Emissions: {carbon.carbon_emissions_kg:.6f} kg CO2")
    
    def test_model_optimization(self):
        """Test model compression and optimization"""
        optimizer = self.framework.model_optimizer
        
        original = ModelEfficiencyMetrics(
            model_name="test_model",
            model_size_mb=500.0,
            inference_latency_ms=150.0,
            accuracy=0.90,
            energy_per_inference_j=6.0
        )
        
        # Apply multiple optimization techniques
        techniques = ['quantization', 'pruning']
        optimized = optimizer.compress_model(original, techniques, accuracy_budget=0.03)
        
        self.assertTrue(optimized.is_compressed)
        self.assertLess(optimized.model_size_mb, original.model_size_mb)
        self.assertLess(optimized.energy_per_inference_j, original.energy_per_inference_j)
        self.assertGreater(optimized.compression_ratio, 1.0)
        
        # Verify accuracy is within budget
        accuracy_loss = original.accuracy - optimized.accuracy
        self.assertLessEqual(accuracy_loss, 0.03)
        
        print(f"✓ Model optimization successful")
        print(f"  Size: {original.model_size_mb:.1f}MB → {optimized.model_size_mb:.1f}MB")
        print(f"  Energy: {original.energy_per_inference_j:.2f}J → {optimized.energy_per_inference_j:.2f}J")
        print(f"  Compression: {optimized.compression_ratio:.1f}x")
        print(f"  Accuracy: {original.accuracy:.3f} → {optimized.accuracy:.3f}")
    
    def test_optimization_recommendations(self):
        """Test optimization technique recommendations"""
        optimizer = self.framework.model_optimizer
        
        model = ModelEfficiencyMetrics(
            model_name="test_model",
            model_size_mb=400.0,
            inference_latency_ms=120.0,
            accuracy=0.88,
            energy_per_inference_j=5.5
        )
        
        # Test different reduction targets
        recommendations_15 = optimizer.recommend_optimizations(model, 0.15)
        recommendations_35 = optimizer.recommend_optimizations(model, 0.35)
        recommendations_50 = optimizer.recommend_optimizations(model, 0.50)
        
        self.assertGreater(len(recommendations_15), 0)
        self.assertGreater(len(recommendations_35), len(recommendations_15))
        self.assertGreaterEqual(len(recommendations_50), len(recommendations_35))
        
        print(f"✓ Optimization recommendations validated")
        print(f"  15% target: {recommendations_15}")
        print(f"  35% target: {recommendations_35}")
        print(f"  50% target: {recommendations_50}")
    
    def test_regional_equity_tracking(self):
        """Test global equity tracking across regions"""
        manager = self.framework.equity_manager
        
        # Register multiple regions
        regions = [
            (DeploymentRegion.NORTH_AMERICA, 50000, 0.95, 0.90, 0.92, 0.88, 0.94),
            (DeploymentRegion.EUROPE, 45000, 0.93, 0.88, 0.90, 0.90, 0.92),
            (DeploymentRegion.ASIA_PACIFIC, 100000, 0.85, 0.75, 0.82, 0.70, 0.78)
        ]
        
        for region, pop, acc, lang, cult, cost, infra in regions:
            metrics = EquityMetrics(
                region=region,
                population_served=pop,
                accessibility_score=acc,
                language_coverage=lang,
                cultural_adaptation_score=cult,
                cost_accessibility=cost,
                infrastructure_adequacy=infra
            )
            manager.register_region(metrics)
        
        self.assertEqual(len(manager.regional_metrics), 3)
        
        # Calculate global equity score
        global_score = manager.calculate_global_equity_score()
        self.assertGreater(global_score, 0.0)
        self.assertLessEqual(global_score, 1.0)
        
        print(f"✓ Regional equity tracking validated")
        print(f"  Regions: {len(manager.regional_metrics)}")
        print(f"  Global equity score: {global_score:.2f}")
    
    def test_equity_gap_identification(self):
        """Test identification of equity gaps"""
        manager = self.framework.equity_manager
        
        # Register regions with varying equity scores
        regions = [
            (DeploymentRegion.NORTH_AMERICA, 50000, 0.95, 0.90, 0.92, 0.88, 0.94),  # High
            (DeploymentRegion.AFRICA, 20000, 0.80, 0.70, 0.78, 0.60, 0.68),  # Low
            (DeploymentRegion.LATIN_AMERICA, 30000, 0.85, 0.75, 0.82, 0.65, 0.72)  # Medium
        ]
        
        for region, pop, acc, lang, cult, cost, infra in regions:
            metrics = EquityMetrics(
                region=region,
                population_served=pop,
                accessibility_score=acc,
                language_coverage=lang,
                cultural_adaptation_score=cult,
                cost_accessibility=cost,
                infrastructure_adequacy=infra
            )
            manager.register_region(metrics)
        
        # Identify gaps (threshold = 0.88)
        gaps = manager.identify_equity_gaps(threshold=0.88)
        
        self.assertGreater(len(gaps), 0)
        # Verify gaps are sorted by score (ascending)
        scores = [score for _, score in gaps]
        self.assertEqual(scores, sorted(scores))
        
        print(f"✓ Equity gap identification successful")
        print(f"  Regions below threshold: {len(gaps)}")
        for region, score in gaps:
            print(f"    - {region.value}: {score:.2f}")
    
    def test_sustainability_report_generation(self):
        """Test sustainability report generation"""
        # Set up test data
        for i in range(100):
            energy = 5.0 * (0.7 + 0.3 * (100 - i) / 100)  # Decreasing
            self.framework.record_inference(
                environment=ComputeEnvironment.CLOUD_GPU,
                energy_joules=energy,
                duration_ms=50.0
            )
        
        # Register regions
        self.framework.equity_manager.register_region(EquityMetrics(
            region=DeploymentRegion.NORTH_AMERICA,
            population_served=50000,
            accessibility_score=0.95,
            language_coverage=0.90,
            cultural_adaptation_score=0.92,
            cost_accessibility=0.88,
            infrastructure_adequacy=0.94
        ))
        
        report = self.framework.generate_sustainability_report()
        
        self.assertIn('energy', report)
        self.assertIn('carbon', report)
        self.assertIn('equity', report)
        
        self.assertIn('reduction_vs_baseline', report['energy'])
        self.assertIn('total_emissions_kg', report['carbon'])
        self.assertIn('global_score', report['equity'])
        
        print(f"✓ Sustainability report generated")
        print(f"  Energy reduction: {report['energy']['reduction_vs_baseline']:.1%}")
        print(f"  Carbon emissions: {report['carbon']['total_emissions_kg']:.2f} kg")
        print(f"  Global equity: {report['equity']['global_score']:.2f}")
    
    def test_phase22_exit_criteria(self):
        """Test Phase 22 exit criteria validation"""
        # Set up comprehensive test scenario
        
        # 1. Energy optimization (need >35% reduction)
        for i in range(200):
            # Simulate energy reduction over time
            base = 6.0
            reduction = 0.4  # 40% reduction
            energy = base * (1 - reduction + 0.1 * (200 - i) / 200)
            self.framework.record_inference(
                environment=ComputeEnvironment.CLOUD_GPU,
                energy_joules=energy,
                duration_ms=45.0
            )
        
        # 2. Register all major regions with good equity scores
        regions_data = [
            (DeploymentRegion.NORTH_AMERICA, 50000, 0.95, 0.90, 0.92, 0.88, 0.94),
            (DeploymentRegion.EUROPE, 45000, 0.93, 0.88, 0.90, 0.90, 0.92),
            (DeploymentRegion.ASIA_PACIFIC, 100000, 0.88, 0.80, 0.85, 0.78, 0.82),
            (DeploymentRegion.LATIN_AMERICA, 30000, 0.90, 0.82, 0.88, 0.75, 0.80),
            (DeploymentRegion.AFRICA, 20000, 0.88, 0.78, 0.85, 0.70, 0.75)
        ]
        
        for region, pop, acc, lang, cult, cost, infra in regions_data:
            metrics = EquityMetrics(
                region=region,
                population_served=pop,
                accessibility_score=acc,
                language_coverage=lang,
                cultural_adaptation_score=cult,
                cost_accessibility=cost,
                infrastructure_adequacy=infra
            )
            self.framework.equity_manager.register_region(metrics)
        
        # Check exit criteria
        exit_check = self.framework.check_phase22_exit_criteria()
        
        self.assertIn('criteria', exit_check)
        self.assertIn('all_criteria_met', exit_check)
        
        print("\n" + "=" * 60)
        print("Phase 22 Exit Criteria Validation")
        print("=" * 60)
        
        for criterion, values in exit_check['criteria'].items():
            status = "✓" if values['met'] else "✗"
            actual_str = f"{values['actual']:.2f}" if isinstance(values['actual'], float) else str(values['actual'])
            target_str = f"{values['target']:.2f}" if isinstance(values['target'], float) else str(values['target'])
            print(f"{status} {criterion}: {actual_str} / {target_str}")
        
        print(f"\nAll criteria met: {'✓ YES' if exit_check['all_criteria_met'] else '✗ NO'}")
    
    def test_energy_efficiency_score(self):
        """Test energy efficiency scoring"""
        model = ModelEfficiencyMetrics(
            model_name="efficient_model",
            model_size_mb=200.0,
            inference_latency_ms=50.0,
            accuracy=0.92,
            energy_per_inference_j=2.5
        )
        
        score = model.efficiency_score
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # High accuracy, low latency, low energy should give high score
        self.assertGreater(score, 0.7)
        
        print(f"✓ Efficiency score calculated: {score:.2f}")
    
    def test_carbon_intensity_by_region(self):
        """Test region-specific carbon intensity"""
        monitor = self.framework.sustainability_monitor
        
        # Verify carbon intensity is defined for all regions
        for region in DeploymentRegion:
            self.assertIn(region, monitor.carbon_intensity)
            intensity = monitor.carbon_intensity[region]
            self.assertGreater(intensity, 0)
            
        # Verify renewable-heavy regions have lower intensity
        latin_america = monitor.carbon_intensity[DeploymentRegion.LATIN_AMERICA]
        middle_east = monitor.carbon_intensity[DeploymentRegion.MIDDLE_EAST]
        self.assertLess(latin_america, middle_east)
        
        print(f"✓ Carbon intensity validated for all regions")


if __name__ == '__main__':
    unittest.main(verbosity=2)
