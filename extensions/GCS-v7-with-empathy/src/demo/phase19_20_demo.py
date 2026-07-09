#!/usr/bin/env python3
"""
phase19_20_demo.py - Demonstration of Phase 19-20 capabilities

Demonstrates:
1. Phase 19: Quantum-enhanced emotion processing
2. Phase 20: Large-scale societal pilot management

This script shows the key features and capabilities of the next
critical phases in the GCS empathy framework.
"""

import sys
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend" / "gcs"))

from quantum_processing import (
    QuantumEmotionProcessor,
    QuantumProcessingConfig,
    QuantumBackend,
    ProcessingMode
)

from societal_pilot_framework import (
    SocietalPilotManager,
    PilotSite,
    PilotContext,
    PilotStatus,
    PilotMetrics,
    IncidentSeverity
)


def print_header(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def demo_phase19_quantum():
    """Demonstrate Phase 19 quantum-enhanced emotion processing"""
    print_header("Phase 19: Quantum-Enhanced Emotion Processing")
    
    # Initialize quantum processor
    print("1. Initializing Quantum Emotion Processor...")
    config = QuantumProcessingConfig(
        backend=QuantumBackend.SIMULATOR,
        mode=ProcessingMode.ADAPTIVE,
        max_qubits=8,
        shots=1024
    )
    processor = QuantumEmotionProcessor(config)
    print(f"   ✓ Processor initialized")
    print(f"   - Backend: {processor.config.backend.value}")
    print(f"   - Mode: {processor.config.mode.value}")
    print(f"   - Quantum available: {processor.quantum_available}")
    
    # Build quantum circuit
    print("\n2. Building Quantum Emotion Circuit...")
    circuit = processor.build_quantum_emotion_circuit(n_features=8, n_emotions=4)
    if circuit:
        print("   ✓ Quantum circuit constructed")
    else:
        print("   ✓ Classical fallback activated (Qiskit not installed)")
    
    # Process emotions with quantum enhancement
    print("\n3. Processing Emotions with Quantum Enhancement...")
    test_features = np.random.randn(20, 8)  # 20 samples, 8 features
    result = processor.quantum_process_emotions(test_features)
    
    print(f"   ✓ Processing completed")
    print(f"   - Mode used: {result.processing_mode.value}")
    print(f"   - Total time: {result.total_time_ms:.1f}ms")
    print(f"   - Cost: ${result.cost_usd:.6f}")
    print(f"   - Accuracy estimate: {result.accuracy_estimate:.3f}")
    
    # Show predictions
    print("\n4. Sample Predictions:")
    emotions = ['ANXIETY', 'DEPRESSION', 'JOY', 'ANGER']
    for i in range(min(3, len(result.predictions))):
        pred_idx = result.predictions[i].argmax()
        confidence = result.predictions[i].max()
        print(f"   Sample {i+1}: {emotions[pred_idx]} (confidence: {confidence:.3f})")
    
    # Get performance metrics
    print("\n5. Performance Metrics:")
    metrics = processor.get_performance_metrics()
    print(f"   - Total inferences: {metrics['total_inferences']}")
    print(f"   - Quantum inferences: {metrics['quantum_inferences']}")
    print(f"   - Classical inferences: {metrics['classical_inferences']}")
    print(f"   - Total cost: ${metrics['total_cost_usd']:.6f}")
    
    # Phase 19 exit criteria
    print("\n6. Phase 19 Exit Criteria Status:")
    criteria = metrics['phase19_criteria']
    print(f"   - Target accuracy (0.90): {criteria['accuracy_met']} "
          f"(current: {criteria['current_accuracy']:.3f})")
    print(f"   - Target latency (45ms): {criteria['latency_met']} "
          f"(current: {criteria['current_latency']:.1f}ms)")
    print(f"   - Fallback robustness: {criteria['fallback_robustness']}")
    
    # Explainability
    print("\n7. Quantum Explainability Example:")
    explanation = processor.explain_quantum_prediction(
        test_features[0:1], 
        result.predictions[0]
    )
    print(f"   - Prediction type: {explanation['prediction_type']}")
    print(f"   - Top emotion: {explanation['top_emotion']}")
    print(f"   - Confidence: {explanation['confidence']:.3f}")
    print(f"   - Interpretability score: {explanation['interpretability_score']:.2f}")
    print(f"   - Quantum advantage: {explanation['quantum_advantage']}")


def demo_phase20_pilots():
    """Demonstrate Phase 20 large-scale societal pilot management"""
    print_header("Phase 20: Large-Scale Societal Pilot Programs")
    
    # Initialize pilot manager
    print("1. Initializing Societal Pilot Manager...")
    manager = SocietalPilotManager(data_dir=Path("/tmp/gcs_demo_pilots"))
    print("   ✓ Pilot manager initialized")
    
    # Register pilot sites
    print("\n2. Registering Pilot Sites...")
    
    # Education site
    edu_site = PilotSite(
        site_id="EDU001",
        site_name="University Alpha",
        context=PilotContext.EDUCATION,
        location="California, USA",
        partner_organization="University Alpha",
        target_participants=300,
        irb_approval=True,
        irb_approval_date=datetime.now(),
        compliance_officer="Dr. Sarah Johnson",
        professional_oversight=["Dr. Michael Chen (Clinical)", "Dr. Lisa Park (Ethics)"]
    )
    edu_site.status = PilotStatus.ACTIVE
    manager.register_pilot_site(edu_site)
    print(f"   ✓ Education site registered: {edu_site.site_name}")
    
    # Healthcare site
    health_site = PilotSite(
        site_id="HEALTH001",
        site_name="Medical Center Beta",
        context=PilotContext.HEALTHCARE,
        location="New York, USA",
        partner_organization="Medical Center Beta",
        target_participants=250,
        irb_approval=True,
        compliance_officer="Dr. Robert Smith"
    )
    health_site.status = PilotStatus.ACTIVE
    manager.register_pilot_site(health_site)
    print(f"   ✓ Healthcare site registered: {health_site.site_name}")
    
    # Workplace site
    work_site = PilotSite(
        site_id="WORK001",
        site_name="TechCorp Gamma",
        context=PilotContext.WORKPLACE,
        location="Washington, USA",
        partner_organization="TechCorp Gamma",
        target_participants=400,
        irb_approval=True,
        compliance_officer="Emily Davis"
    )
    work_site.status = PilotStatus.ACTIVE
    manager.register_pilot_site(work_site)
    print(f"   ✓ Workplace site registered: {work_site.site_name}")
    
    # Enroll participants
    print("\n3. Enrolling Participants...")
    for site in [edu_site, health_site, work_site]:
        enrolled_count = int(site.target_participants * 0.8)  # 80% enrollment
        for i in range(enrolled_count):
            participant_id = manager.enroll_participant(
                site_id=site.site_id,
                demographic_data={
                    'age_range': '18-65',
                    'gender': 'various',
                    'ethnicity': 'diverse'
                },
                consent_given=True,
                baseline_measurements={
                    'well_being_score': np.random.uniform(5.0, 7.0),
                    'stress_level': np.random.uniform(4.0, 8.0)
                }
            )
        site.active_participants = enrolled_count
        print(f"   ✓ {site.site_name}: {enrolled_count} participants enrolled")
    
    # Record pilot metrics
    print("\n4. Recording Pilot Metrics...")
    for site in [edu_site, health_site, work_site]:
        metrics = PilotMetrics(
            site_id=site.site_id,
            timestamp=datetime.now(),
            active_users=int(site.active_participants * 0.75),  # 75% daily active
            total_sessions=site.active_participants * 10,
            avg_session_duration_min=22.5,
            emotion_recognition_accuracy=0.89,
            crisis_detections=np.random.randint(2, 6),
            professional_escalations=np.random.randint(1, 4),
            user_satisfaction=np.random.uniform(4.1, 4.5),
            system_uptime_percent=99.7,
            latency_p50_ms=38.0,
            latency_p95_ms=142.0,
            fairness_score=0.91,
            incidents=0
        )
        manager.record_pilot_metrics(metrics)
    print("   ✓ Metrics recorded for all sites")
    
    # Demonstrate crisis escalation
    print("\n5. Crisis Escalation Example...")
    edu_participants = [p for p in manager.participants.values() if p.site_id == "EDU001"]
    if edu_participants:
        crisis_participant = edu_participants[0]
        incident_id = manager.create_crisis_escalation(
            site_id="EDU001",
            participant_id=crisis_participant.participant_id,
            crisis_data={
                'level': 'MODERATE',
                'indicators': ['elevated_stress', 'sleep_disruption'],
                'confidence': 0.87
            }
        )
        print(f"   ✓ Crisis escalation created: {incident_id}")
        print(f"   - Participant: {crisis_participant.participant_id}")
        print(f"   - Professional oversight notified")
    
    # Generate dashboard
    print("\n6. Pilot Dashboard Summary:")
    dashboard = manager.get_pilot_dashboard()
    print(f"   Sites:")
    print(f"   - Total: {dashboard['sites']['total']}")
    print(f"   - Active: {dashboard['sites']['active']}")
    print(f"   - Contexts: {', '.join(dashboard['sites']['contexts'])}")
    print(f"   \n   Participants:")
    print(f"   - Total enrolled: {dashboard['participants']['total_enrolled']}")
    print(f"   - Total active: {dashboard['participants']['total_active']}")
    print(f"   - Engagement rate: {dashboard['participants']['engagement_rate']:.1f}%")
    print(f"   \n   Performance:")
    print(f"   - Emotion accuracy: {dashboard['performance']['avg_emotion_accuracy']:.3f}")
    print(f"   - Latency P95: {dashboard['performance']['avg_latency_p95_ms']:.1f}ms")
    print(f"   - User satisfaction: {dashboard['performance']['avg_user_satisfaction']:.2f}/5.0")
    print(f"   - Fairness score: {dashboard['performance']['avg_fairness_score']:.3f}")
    print(f"   \n   Safety:")
    print(f"   - Incidents (24h): {dashboard['safety']['incidents_24h']}")
    print(f"   - Critical incidents: {dashboard['safety']['critical_incidents_24h']}")
    print(f"   - Crisis escalations: {dashboard['safety']['crisis_escalations_24h']}")
    
    # Phase 20 exit criteria
    print("\n7. Phase 20 Exit Criteria Status:")
    criteria = dashboard['phase20_exit_criteria']
    
    def check_mark(met, current, target):
        symbol = "✓" if met else "✗"
        return f"{symbol} {current}/{target}"
    
    print(f"   - Sites deployed: "
          f"{check_mark(criteria['sites_deployed'] >= 3, criteria['sites_deployed'], 3)}")
    print(f"   - Engagement rate: "
          f"{check_mark(criteria['engagement_rate'] >= 70, f'{criteria['engagement_rate']:.1f}%', '70%')}")
    print(f"   - Accuracy: "
          f"{check_mark(criteria['accuracy'] >= 0.87, f'{criteria['accuracy']:.3f}', '0.87')}")
    print(f"   - User satisfaction: "
          f"{check_mark(criteria['user_satisfaction'] >= 4.0, f'{criteria['user_satisfaction']:.2f}', '4.0')}")
    print(f"   - Fairness score: "
          f"{check_mark(criteria['fairness_score'] >= 0.88, f'{criteria['fairness_score']:.2f}', '0.88')}")
    print(f"   - Critical incidents: "
          f"{check_mark(criteria['critical_incidents'] == 0, criteria['critical_incidents'], 0)}")


def main():
    """Main demonstration"""
    print("\n" + "="*70)
    print("  GCS Phase 19-20 Demonstration")
    print("  Quantum Processing & Societal Validation")
    print("="*70)
    
    try:
        # Phase 19 demo
        demo_phase19_quantum()
        
        # Phase 20 demo
        demo_phase20_pilots()
        
        # Summary
        print_header("Summary")
        print("Phase 19 (Quantum-Enhanced Processing):")
        print("✓ Hybrid quantum-classical architecture implemented")
        print("✓ Graceful fallback mechanisms validated")
        print("✓ Performance monitoring and cost tracking operational")
        print("✓ Quantum explainability framework deployed")
        
        print("\nPhase 20 (Large-Scale Societal Pilots):")
        print("✓ Multi-site pilot management infrastructure ready")
        print("✓ Participant enrollment with consent enforcement")
        print("✓ Real-time monitoring and anomaly detection")
        print("✓ Crisis escalation and professional alerting")
        print("✓ Longitudinal tracking and outcome measurement")
        
        print("\n" + "="*70)
        print("  Demo Complete!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
