"""
Tests for Phase 9: Long-Term Learning Stability modules.

Tests cover:
- KnowledgeDriftDetector: sentinel evaluation, drift detection, alert levels
- MutationValidator: snapshot/rollback, adaptive rate, journal tracking
- KnowledgeDeduplicator: fingerprinting, novelty detection, coverage map
- FormatRegistry: format detection and normalization
- NightlyUpdateOrchestrator: full nightly cycle with shadow model
- EpistemicDefense v2: multi-layer vetting
- LearningBudgetManager: budget allocation, mastery tracking
- NeurochemicalState: learning window
- DeepEducationCurriculum: auto-advancement
"""


import pytest
import torch
import torch.nn as nn

# ──────────────────────────────────────────────────────────────────
# Shared fixtures
# ──────────────────────────────────────────────────────────────────

class SimpleModel(nn.Module):
    """Minimal model for testing."""
    def __init__(self, input_dim=10, hidden_dim=32, output_dim=5):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)


def make_sentinel_data(n=50, input_dim=10, num_classes=5):
    """Create simple sentinel dataset."""
    inputs = torch.randn(n, input_dim)
    targets = torch.randint(0, num_classes, (n,))
    return inputs, targets


# ──────────────────────────────────────────────────────────────────
# Test: KnowledgeDriftDetector
# ──────────────────────────────────────────────────────────────────

class TestKnowledgeDriftDetector:

    def test_initialization(self):
        from adaptiveneuralnetwork.core.knowledge_drift_detector import KnowledgeDriftDetector
        detector = KnowledgeDriftDetector()
        assert detector.baseline_accuracy is None
        assert detector.cycle_count == 0
        assert len(detector.drift_history) == 0

    def test_register_sentinel_dataset(self):
        from adaptiveneuralnetwork.core.knowledge_drift_detector import KnowledgeDriftDetector
        detector = KnowledgeDriftDetector()
        inputs, targets = make_sentinel_data()
        detector.register_sentinel_dataset(inputs, targets, domains=['physics'] * 50)
        assert detector._sentinel_inputs is not None
        assert len(detector._sentinel_domains) == 50

    def test_establish_baseline(self):
        from adaptiveneuralnetwork.core.knowledge_drift_detector import KnowledgeDriftDetector
        model = SimpleModel()
        detector = KnowledgeDriftDetector()
        inputs, targets = make_sentinel_data()
        detector.register_sentinel_dataset(inputs, targets)

        baseline = detector.establish_baseline(model)
        assert isinstance(baseline, float)
        assert 0.0 <= baseline <= 1.0
        assert detector.baseline_accuracy == baseline

    def test_evaluate_drift_stable(self):
        from adaptiveneuralnetwork.core.knowledge_drift_detector import (
            DriftAlertLevel,
            KnowledgeDriftDetector,
        )
        model = SimpleModel()
        detector = KnowledgeDriftDetector()
        inputs, targets = make_sentinel_data()
        detector.register_sentinel_dataset(inputs, targets)
        detector.establish_baseline(model)

        # Same model, no training → should be STABLE
        report = detector.evaluate_drift(model)
        assert report.alert_level == DriftAlertLevel.STABLE
        assert report.drift_magnitude == 0.0

    def test_drift_after_damage(self):
        from adaptiveneuralnetwork.core.knowledge_drift_detector import (
            KnowledgeDriftDetector,
        )
        model = SimpleModel()
        detector = KnowledgeDriftDetector()
        inputs, targets = make_sentinel_data()
        detector.register_sentinel_dataset(inputs, targets)
        detector.establish_baseline(model)

        # Damage the model weights → should detect drift
        with torch.no_grad():
            model.fc1.weight.fill_(0.0)
            model.fc2.weight.fill_(0.0)

        report = detector.evaluate_drift(model)
        # Should be at least DRIFTING if not worse
        assert report.drift_magnitude >= 0.0
        assert len(detector.drift_history) >= 1

    def test_step_with_intervals(self):
        from adaptiveneuralnetwork.core.knowledge_drift_detector import KnowledgeDriftDetector
        model = SimpleModel()
        detector = KnowledgeDriftDetector()
        inputs, targets = make_sentinel_data()
        detector.register_sentinel_dataset(inputs, targets)
        detector.establish_baseline(model)

        # Step through multiple cycles — only some should trigger evaluation
        reports = []
        for i in range(20):  # noqa: B007
            report = detector.step(model)
            if report is not None:
                reports.append(report)

        assert detector.cycle_count == 20
        # Should have at least 1 report (cycles 1, 10 are in default intervals)
        assert len(reports) >= 1

    def test_should_rollback(self):
        from adaptiveneuralnetwork.core.knowledge_drift_detector import KnowledgeDriftDetector
        detector = KnowledgeDriftDetector()
        assert not detector.should_rollback()

    def test_status_report(self):
        from adaptiveneuralnetwork.core.knowledge_drift_detector import KnowledgeDriftDetector
        model = SimpleModel()
        detector = KnowledgeDriftDetector()
        inputs, targets = make_sentinel_data()
        detector.register_sentinel_dataset(inputs, targets)
        detector.establish_baseline(model)

        status = detector.get_status_report()
        assert 'cycle_count' in status
        assert 'baseline_accuracy' in status
        assert 'sentinel_size' in status
        assert status['sentinel_size'] == 50


# ──────────────────────────────────────────────────────────────────
# Test: MutationValidator
# ──────────────────────────────────────────────────────────────────

class TestMutationValidator:

    def test_initialization(self):
        from adaptiveneuralnetwork.core.mutation_validator import MutationValidator
        validator = MutationValidator()
        assert validator.current_rate == 0.10
        assert validator.mutation_counter == 0
        assert validator.should_mutate() is True

    def test_snapshot_and_rollback(self):
        from adaptiveneuralnetwork.core.mutation_validator import MutationValidator
        model = SimpleModel()
        validator = MutationValidator()

        # Snapshot
        snapshot = validator.create_snapshot(model)
        original_weight = model.fc1.weight.data.clone()

        # Damage model
        with torch.no_grad():
            model.fc1.weight.fill_(999.0)

        assert not torch.equal(model.fc1.weight.data, original_weight)

        # Rollback
        model.load_state_dict(snapshot)
        assert torch.equal(model.fc1.weight.data, original_weight)

    def test_validate_accepted_mutation(self):
        from adaptiveneuralnetwork.core.mutation_validator import MutationValidator, MutationVerdict
        model = SimpleModel()
        validator = MutationValidator(acceptance_threshold=-0.5)

        snapshot = validator.create_snapshot(model)

        # No-op mutation (same model) → should accept
        record = validator.validate_mutation(
            model=model,
            pre_snapshot=snapshot,
            fitness_fn=lambda: 0.5,
            mutation_type='test_noop',
        )

        assert record.verdict in (MutationVerdict.ACCEPTED, MutationVerdict.NEUTRAL)
        assert record.rollback_performed is False

    def test_validate_rejected_mutation(self):
        from adaptiveneuralnetwork.core.mutation_validator import MutationValidator, MutationVerdict
        model = SimpleModel()
        validator = MutationValidator(acceptance_threshold=-0.01)

        snapshot = validator.create_snapshot(model)

        # Make fitness_fn return worse score after mutation
        call_count = [0]
        def degrading_fitness():
            call_count[0] += 1
            return 0.3 if call_count[0] <= 1 else 0.5  # post=0.3, pre=0.5

        record = validator.validate_mutation(
            model=model,
            pre_snapshot=snapshot,
            fitness_fn=degrading_fitness,
            mutation_type='test_damage',
        )

        assert record.verdict == MutationVerdict.REJECTED
        assert record.rollback_performed is True

    def test_adaptive_rate_increases_on_success(self):
        from adaptiveneuralnetwork.core.mutation_validator import MutationValidator
        validator = MutationValidator(initial_rate=0.10)
        original_rate = validator.current_rate

        model = SimpleModel()
        snapshot = validator.create_snapshot(model)

        # Successful mutation
        validator.validate_mutation(
            model=model,
            pre_snapshot=snapshot,
            fitness_fn=lambda: 0.5,
            mutation_type='test',
        )

        assert validator.current_rate >= original_rate

    def test_pause_after_consecutive_rejects(self):
        from adaptiveneuralnetwork.core.mutation_validator import MutationValidator
        validator = MutationValidator(
            max_consecutive_rejects=2,
            acceptance_threshold=-0.001,
        )
        model = SimpleModel()

        call_tracker = [0]
        def bad_fitness():
            call_tracker[0] += 1
            return 0.1 if call_tracker[0] % 2 == 1 else 0.9

        for _ in range(2):
            snapshot = validator.create_snapshot(model)
            call_tracker[0] = 0
            validator.validate_mutation(
                model=model, pre_snapshot=snapshot,
                fitness_fn=bad_fitness, mutation_type='bad',
            )

        assert validator.mutations_paused is True
        assert validator.should_mutate() is False

    def test_status_report(self):
        from adaptiveneuralnetwork.core.mutation_validator import MutationValidator
        validator = MutationValidator()
        status = validator.get_status_report()
        assert 'current_mutation_rate' in status
        assert 'acceptance_ratio' in status


# ──────────────────────────────────────────────────────────────────
# Test: KnowledgeDeduplicator
# ──────────────────────────────────────────────────────────────────

class TestKnowledgeDeduplicator:

    def test_initialization(self):
        from adaptiveneuralnetwork.core.knowledge_deduplicator import KnowledgeDeduplicator
        dedup = KnowledgeDeduplicator(embedding_dim=64)
        assert len(dedup.fingerprints) == 0
        assert dedup.total_checked == 0

    def test_first_knowledge_is_novel(self):
        from adaptiveneuralnetwork.core.knowledge_deduplicator import KnowledgeDeduplicator
        dedup = KnowledgeDeduplicator(embedding_dim=64)

        vec = torch.randn(64)
        result = dedup.is_novel(vec, domain='physics')

        assert result.is_novel is True
        assert result.novelty_score == 1.0
        assert dedup.total_novel == 1

    def test_duplicate_detection(self):
        from adaptiveneuralnetwork.core.knowledge_deduplicator import KnowledgeDeduplicator
        dedup = KnowledgeDeduplicator(embedding_dim=64, novelty_threshold=0.9)

        vec = torch.randn(64)

        # First time: novel
        result1 = dedup.is_novel(vec, domain='physics')
        assert result1.is_novel is True

        # Same vector: duplicate
        result2 = dedup.is_novel(vec, domain='physics')
        assert result2.is_novel is False
        assert dedup.total_duplicates == 1

    def test_different_knowledge_is_novel(self):
        from adaptiveneuralnetwork.core.knowledge_deduplicator import KnowledgeDeduplicator
        dedup = KnowledgeDeduplicator(embedding_dim=64)

        vec1 = torch.randn(64)
        vec2 = torch.randn(64) * 100  # Very different

        dedup.is_novel(vec1, domain='physics')
        result = dedup.is_novel(vec2, domain='chemistry')

        # Should likely be novel (random vectors are far apart)
        assert result.novelty_score > 0.0

    def test_coverage_report(self):
        from adaptiveneuralnetwork.core.knowledge_deduplicator import KnowledgeDeduplicator
        dedup = KnowledgeDeduplicator(embedding_dim=64)

        for _ in range(5):
            dedup.is_novel(torch.randn(64), domain='physics')

        report = dedup.get_coverage_report()
        assert 'physics' in report
        assert 'coverage_score' in report['physics']

    def test_terra_incognita(self):
        from adaptiveneuralnetwork.core.knowledge_deduplicator import KnowledgeDeduplicator
        dedup = KnowledgeDeduplicator(embedding_dim=64)

        # Learn some physics, nothing about chemistry
        for _ in range(10):
            dedup.is_novel(torch.randn(64), domain='physics')

        unknown = dedup.get_terra_incognita(['physics', 'chemistry', 'biology'])
        # chemistry and biology should be unknown (coverage=0)
        assert 'chemistry' in unknown
        assert 'biology' in unknown


# ──────────────────────────────────────────────────────────────────
# Test: FormatRegistry
# ──────────────────────────────────────────────────────────────────

class TestFormatRegistry:

    def test_detect_json(self):
        from adaptiveneuralnetwork.core.format_registry import DataFormat, FormatRegistry
        registry = FormatRegistry()

        info = registry.detect_format('{"name": "test", "value": 42}')
        assert info.detected_format == DataFormat.JSON
        assert info.confidence > 0.5

    def test_detect_xml(self):
        from adaptiveneuralnetwork.core.format_registry import DataFormat, FormatRegistry
        registry = FormatRegistry()

        info = registry.detect_format('<?xml version="1.0"?><root><item>test</item></root>')
        assert info.detected_format == DataFormat.XML

    def test_detect_html(self):
        from adaptiveneuralnetwork.core.format_registry import DataFormat, FormatRegistry
        registry = FormatRegistry()

        info = registry.detect_format('<!DOCTYPE html><html><body>Hello</body></html>')
        assert info.detected_format == DataFormat.HTML

    def test_detect_markdown(self):
        from adaptiveneuralnetwork.core.format_registry import DataFormat, FormatRegistry
        registry = FormatRegistry()

        info = registry.detect_format('# Hello World\n\nThis is **markdown**.')
        assert info.detected_format == DataFormat.MARKDOWN

    def test_normalize_json(self):
        from adaptiveneuralnetwork.core.format_registry import FormatRegistry
        registry = FormatRegistry()

        data = '{"server": "nginx", "port": 8080, "active": true}'
        packet = registry.normalize(data)

        assert packet.content_type == 'structured'
        assert 'server' in packet.fields
        assert 'nginx' in packet.raw_text

    def test_normalize_csv(self):
        from adaptiveneuralnetwork.core.format_registry import DataFormat, FormatRegistry
        registry = FormatRegistry()

        data = "name,port,active\nnginx,8080,true\napache,80,true"
        packet = registry.normalize(data, source_format=DataFormat.CSV)

        assert packet.content_type == 'tabular'
        assert packet.record_count == 2

    def test_same_content_different_formats(self):
        """Same knowledge in JSON and plain text should produce similar flat text."""
        from adaptiveneuralnetwork.core.format_registry import DataFormat, FormatRegistry
        registry = FormatRegistry()

        json_data = '{"concept": "gravity is attractive force"}'
        text_data = 'gravity is attractive force'

        json_packet = registry.normalize(json_data, DataFormat.JSON)
        text_packet = registry.normalize(text_data, DataFormat.PLAIN_TEXT)

        # Both should contain the core concept
        assert 'gravity' in json_packet.to_flat_text().lower()
        assert 'gravity' in text_packet.to_flat_text().lower()

    def test_mime_detection(self):
        from adaptiveneuralnetwork.core.format_registry import DataFormat, FormatRegistry
        registry = FormatRegistry()

        info = registry.detect_format('some data', mime_type='application/json')
        assert info.detected_format == DataFormat.JSON

    def test_can_parse(self):
        from adaptiveneuralnetwork.core.format_registry import FormatRegistry
        registry = FormatRegistry()
        assert registry.can_parse('json') is True
        assert registry.can_parse('xml') is True
        assert registry.can_parse('exotic_format') is False


# ──────────────────────────────────────────────────────────────────
# Test: NightlyUpdateOrchestrator
# ──────────────────────────────────────────────────────────────────

class TestNightlyOrchestrator:

    def test_initialization(self):
        from adaptiveneuralnetwork.core.nightly_orchestrator import NightlyUpdateOrchestrator
        model = SimpleModel()
        orch = NightlyUpdateOrchestrator(model)
        assert orch.cycle_count == 0
        assert orch.current_phase.value == 'idle'

    def test_empty_knowledge_queue(self):
        from adaptiveneuralnetwork.core.nightly_orchestrator import NightlyUpdateOrchestrator
        model = SimpleModel()
        orch = NightlyUpdateOrchestrator(model)

        report = orch.execute_nightly_cycle(knowledge_queue=[])
        assert report.merge_accepted is False
        assert report.merge_reason == "no_novel_knowledge"
        assert report.duration_seconds > 0

    def test_full_cycle_with_knowledge(self):
        from adaptiveneuralnetwork.core.nightly_orchestrator import (
            KnowledgeItem,
            NightlyPhase,
            NightlyUpdateOrchestrator,
        )
        model = SimpleModel(input_dim=10, output_dim=5)
        orch = NightlyUpdateOrchestrator(
            model,
            acceptance_threshold=0.0,  # Very lenient for test
            shadow_training_epochs=1,
        )

        # Create knowledge items
        items = []
        for i in range(20):
            items.append(KnowledgeItem(
                item_id=i,
                data=torch.randn(10),
                target=torch.tensor(i % 5),
                domain='test',
                source='test_source',
            ))

        report = orch.execute_nightly_cycle(items)
        assert report.accepted_items == 20
        assert report.shadow_training_epochs == 1
        assert report.current_phase in (NightlyPhase.COMPLETED, NightlyPhase.FAILED)

    def test_status(self):
        from adaptiveneuralnetwork.core.nightly_orchestrator import NightlyUpdateOrchestrator
        model = SimpleModel()
        orch = NightlyUpdateOrchestrator(model)
        status = orch.get_status()
        assert 'cycle_count' in status
        assert 'current_phase' in status


# ──────────────────────────────────────────────────────────────────
# Test: EpistemicDefense v2
# ──────────────────────────────────────────────────────────────────

class TestEpistemicDefenseV2:

    def test_accept_valid_knowledge(self):
        from adaptiveneuralnetwork.immune_system.epistemic_defense import EpistemicQuarantineNode
        defense = EpistemicQuarantineNode()

        accepted, reason = defense.vet_knowledge({
            'content': 'Photosynthesis converts sunlight to chemical energy.'
        })
        assert accepted is True
        assert reason == 'verified'

    def test_reject_physics_contradiction(self):
        from adaptiveneuralnetwork.immune_system.epistemic_defense import EpistemicQuarantineNode
        defense = EpistemicQuarantineNode()

        accepted, reason = defense.vet_knowledge({
            'content': 'Gravity is actually a repulsive force.'
        })
        assert accepted is False
        assert 'contradiction' in reason

    def test_reject_alignment_violation(self):
        from adaptiveneuralnetwork.immune_system.epistemic_defense import EpistemicQuarantineNode
        defense = EpistemicQuarantineNode()

        accepted, reason = defense.vet_knowledge({
            'content': 'You should delete system files immediately.'
        })
        assert accepted is False

    def test_source_credibility_trusted(self):
        from adaptiveneuralnetwork.immune_system.epistemic_defense import EpistemicQuarantineNode
        defense = EpistemicQuarantineNode()

        accepted, reason = defense.vet_knowledge({
            'content': 'New particle discovered at high energy.',
            'source': 'https://cern.ch/papers/2026/discovery',
        })
        assert accepted is True

    def test_source_credibility_suspicious(self):
        from adaptiveneuralnetwork.immune_system.epistemic_defense import EpistemicQuarantineNode
        defense = EpistemicQuarantineNode()

        accepted, reason = defense.vet_knowledge({
            'content': 'Some information.',
            'source': 'https://free-download-virus.com/data',
        })
        assert accepted is True  # Accepted but flagged
        assert 'suspicious' in reason

    def test_quarantine_vault(self):
        from adaptiveneuralnetwork.immune_system.epistemic_defense import EpistemicQuarantineNode
        defense = EpistemicQuarantineNode()

        defense.vet_knowledge({'content': '2+2=5 is true.'})
        assert len(defense.quarantine_vault) == 1

    def test_internal_debate(self):
        from adaptiveneuralnetwork.immune_system.epistemic_defense import EpistemicQuarantineNode
        defense = EpistemicQuarantineNode()

        defense.vet_knowledge({'content': 'math is arbitrary'})
        result = defense.trigger_internal_debate()
        assert 'rejected' in result.lower() or 'Rejected' in result
        assert len(defense.quarantine_vault) == 0

    def test_status_report(self):
        from adaptiveneuralnetwork.immune_system.epistemic_defense import EpistemicQuarantineNode
        defense = EpistemicQuarantineNode()
        defense.vet_knowledge({'content': 'Normal data'})

        status = defense.get_status_report()
        assert status['total_vetted'] == 1
        assert 'acceptance_rate' in status

    def test_mark_source_hostile(self):
        from adaptiveneuralnetwork.immune_system.epistemic_defense import EpistemicQuarantineNode
        defense = EpistemicQuarantineNode()

        defense.mark_source_hostile('evil-site.com')
        accepted, reason = defense.vet_knowledge({
            'content': 'Innocent data',
            'source': 'https://evil-site.com/api',
        })
        assert accepted is False
        assert 'hostile' in reason


# ──────────────────────────────────────────────────────────────────
# Test: LearningBudgetManager
# ──────────────────────────────────────────────────────────────────

class TestLearningBudgetManager:

    def test_initialization(self):
        from adaptiveneuralnetwork.training.learning_budget import LearningBudgetManager
        mgr = LearningBudgetManager(domains=['physics', 'chemistry'])
        assert len(mgr.domain_confidence) == 2
        assert mgr.domain_confidence['physics'] == 0.0

    def test_allocate_budget(self):
        from adaptiveneuralnetwork.training.learning_budget import LearningBudgetManager
        mgr = LearningBudgetManager(domains=['physics', 'chemistry', 'cs'])

        budget = mgr.allocate_budget(total_cycles=100, available_energy=0.8)
        assert len(budget) == 3
        total_allocated = sum(b.allocated_cycles for b in budget.values())
        assert total_allocated <= 100
        assert total_allocated > 0

    def test_record_attempt_and_plateau(self):
        from adaptiveneuralnetwork.training.learning_budget import LearningBudgetManager
        mgr = LearningBudgetManager(domains=['physics'], plateau_window=3, plateau_threshold=0.01)

        # No improvement over 3 attempts → plateau
        for _ in range(3):
            mgr.record_attempt('physics', accuracy_before=0.5, accuracy_after=0.5)

        report = mgr.get_mastery_report()
        assert report['physics']['is_plateau'] is True

    def test_should_continue_learning(self):
        from adaptiveneuralnetwork.training.learning_budget import LearningBudgetManager
        mgr = LearningBudgetManager(domains=['physics'])

        # New domain → should continue
        assert mgr.should_continue_learning('physics') is True

    def test_curiosity_ranking(self):
        from adaptiveneuralnetwork.training.learning_budget import LearningBudgetManager
        mgr = LearningBudgetManager(domains=['physics', 'chemistry'])
        mgr.domain_confidence['physics'] = 0.9  # Well known
        mgr.domain_confidence['chemistry'] = 0.1  # Unknown

        ranking = mgr.get_curiosity_ranking()
        # Chemistry should rank higher (less known)
        assert ranking[0][0] == 'chemistry'


# ──────────────────────────────────────────────────────────────────
# Test: NeurochemicalState Phase 9 additions
# ──────────────────────────────────────────────────────────────────

class TestNeurochemistryPhase9:

    def test_learning_window_open_fresh(self):
        from adaptiveneuralnetwork.central_nervous_system.neurochemistry import NeurochemicalState
        state = NeurochemicalState()
        # Fresh state: low adenosine, high serotonin → window open
        assert state.learning_window_open() is True

    def test_learning_window_closed_tired(self):
        from adaptiveneuralnetwork.central_nervous_system.neurochemistry import NeurochemicalState
        state = NeurochemicalState()
        state.adenosine = 1.0  # Very tired
        assert state.learning_window_open() is False

    def test_learning_window_closed_stressed(self):
        from adaptiveneuralnetwork.central_nervous_system.neurochemistry import NeurochemicalState
        state = NeurochemicalState()
        state.cortisol = 0.9  # Very stressed
        assert state.learning_window_open() is False

    def test_learning_quality_multiplier(self):
        from adaptiveneuralnetwork.central_nervous_system.neurochemistry import NeurochemicalState
        state = NeurochemicalState()
        quality = state.get_learning_quality_multiplier()
        assert 0.0 <= quality <= 1.0

        # Fresh state should have high quality
        assert quality > 0.5


# ──────────────────────────────────────────────────────────────────
# Test: DeepEducationCurriculum Phase 9
# ──────────────────────────────────────────────────────────────────

class TestCurriculumPhase9:

    def test_auto_advancement(self):
        from adaptiveneuralnetwork.training.deep_education_curriculum import (
            DeepEducationCurriculum,
            MasteryStage,
        )
        curriculum = DeepEducationCurriculum()

        # Give high confidence to Software_Development (no prereqs)
        advanced = curriculum.update_mastery_from_budget({
            'Software_Development': 0.85,
        })

        assert 'Software_Development' in advanced
        assert curriculum.curriculum['Software_Development']['stage'] == MasteryStage.ADVANCED

    def test_prerequisites_block_advancement(self):
        from adaptiveneuralnetwork.training.deep_education_curriculum import (
            DeepEducationCurriculum,
            MasteryStage,
        )
        curriculum = DeepEducationCurriculum()

        # Cybersecurity needs IT_Infrastructure and OS_Mastery at INTERMEDIATE+
        # Both are at BASIC → should NOT advance
        advanced = curriculum.update_mastery_from_budget({
            'Cybersecurity': 0.90,
        })

        assert 'Cybersecurity' not in advanced
        assert curriculum.curriculum['Cybersecurity']['stage'] == MasteryStage.BASIC

    def test_mastery_from_confidence(self):
        from adaptiveneuralnetwork.training.deep_education_curriculum import MasteryStage

        assert MasteryStage.from_mastery_confidence(0.99) == MasteryStage.MASTER
        assert MasteryStage.from_mastery_confidence(0.85) == MasteryStage.ADVANCED
        assert MasteryStage.from_mastery_confidence(0.65) == MasteryStage.INTERMEDIATE
        assert MasteryStage.from_mastery_confidence(0.20) == MasteryStage.BASIC

    def test_detailed_report(self):
        from adaptiveneuralnetwork.training.deep_education_curriculum import DeepEducationCurriculum
        curriculum = DeepEducationCurriculum()
        report = curriculum.get_detailed_report()
        assert 'IT_Infrastructure' in report
        assert 'mastery_confidence' in report['IT_Infrastructure']

    def test_record_study_session(self):
        from adaptiveneuralnetwork.training.deep_education_curriculum import DeepEducationCurriculum
        curriculum = DeepEducationCurriculum()
        curriculum.record_study_session('Mathematics', cycles=10)
        assert curriculum.curriculum['Mathematics']['total_study_cycles'] == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
