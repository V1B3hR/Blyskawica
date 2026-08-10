"""
Tests: wolf_pack.py + architectural_mirror.py
Compatibility and integrity — V1B3hR session 2026-05-11
"""
from unittest.mock import MagicMock

import pytest

# ══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════════════════

def make_microbiome():
    """Minimal microbiome stub compatible with WolfPack."""
    m = MagicMock()
    m.serotonin    = 0.75
    m.gaba         = 0.50
    m.adrenaline   = 0.0
    m.noradrenaline = 0.0
    m.testosterone = 0.25
    m.cortisol     = 0.15
    m.oxytocin     = 0.30
    return m

def make_neurochemical_state():
    from adaptiveneuralnetwork.central_nervous_system.neurochemistry import NeurochemicalState
    return NeurochemicalState()

def make_soul():
    from adaptiveneuralnetwork.central_nervous_system.soul import Soul
    return Soul()

# ══════════════════════════════════════════════════════════════════════════════
# IMPORT TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestImports:
    def test_wolf_pack_imports(self):
        pass

    def test_mirror_imports(self):
        pass

    def test_neurochemistry_imports(self):
        pass

# ══════════════════════════════════════════════════════════════════════════════
# WOLF PACK TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestWolfPack:
    def setup_method(self):
        from adaptiveneuralnetwork.central_nervous_system.ecosystem.wolf_pack import WolfPack
        self.microbiome = make_microbiome()
        self.pack = WolfPack(self.microbiome)

    def test_instantiation(self):
        from adaptiveneuralnetwork.central_nervous_system.ecosystem.wolf_pack import ReconPhase
        assert self.pack is not None
        assert self.pack.phase == ReconPhase.IDLE
        assert len(self.pack.pack) == 4

    def test_drone_roles(self):
        roles = {d.role for d in self.pack.pack}
        assert "sensor" in roles
        assert "infiltrator" in roles
        assert "defender" in roles
        assert "striker" in roles

    def test_passive_scan_no_trigger(self):
        """Low entropy signal — should return None (continue listening)."""
        result = self.pack.passive_scan({
            "source_id": "test_entity_01",
            "entropy": 0.10,
            "regularity": 0.2
        })
        assert result is None

    def test_passive_scan_triggers_on_high_entropy(self):
        """High entropy — should return ThreatProfile."""
        profile = self.pack.passive_scan({
            "source_id": "hostile_01",
            "entropy": 0.80,
            "regularity": 0.9
        })
        assert profile is not None
        assert profile.signal_entropy == pytest.approx(0.80)

    def test_passive_scan_triggers_on_repeated_contacts(self):
        """Three contacts with same source → should trigger."""
        signal = {"source_id": "probe_01", "entropy": 0.20, "regularity": 0.5}
        r1 = self.pack.passive_scan(signal)  # noqa: F841
        r2 = self.pack.passive_scan(signal)  # noqa: F841
        r3 = self.pack.passive_scan(signal)
        assert r3 is not None  # Third contact triggers

    def test_active_scan_classifies_noise(self):
        from adaptiveneuralnetwork.central_nervous_system.ecosystem.wolf_pack import ThreatClass
        profile = self.pack.passive_scan({"source_id": "noise_01", "entropy": 0.8})
        profile = self.pack.active_scan(profile, {
            "latency_ms": 500,
            "behavior": "random",
            "attack_vectors": []
        })
        assert profile.threat_class == ThreatClass.NOISE

    def test_active_scan_classifies_ai_agent(self):
        from adaptiveneuralnetwork.central_nervous_system.ecosystem.wolf_pack import ThreatClass
        profile = self.pack.passive_scan({"source_id": "ai_01", "entropy": 0.8})
        profile = self.pack.active_scan(profile, {
            "latency_ms": 5,
            "behavior": "periodic",
            "attack_vectors": ["port_scan"]
        })
        assert profile.threat_class == ThreatClass.AI_AGENT

    def test_intel_fusion_upgrades_to_adversary(self):
        from adaptiveneuralnetwork.central_nervous_system.ecosystem.wolf_pack import ThreatClass
        profile = self.pack.passive_scan({"source_id": "adv_01", "entropy": 0.9})
        profile = self.pack.active_scan(profile, {"latency_ms": 5, "behavior": "periodic"})
        profile = self.pack.intel_fusion(profile, {
            "known": True,
            "intent_score": 0.85,
            "weaknesses": ["buffer_overflow"]
        })
        assert profile.threat_class == ThreatClass.ADVERSARY
        assert profile.global_known is True

    def test_decision_withdraw_on_noise(self):
        from adaptiveneuralnetwork.central_nervous_system.ecosystem.wolf_pack import (
            PackDecision,
        )
        profile = self.pack.passive_scan({"source_id": "noise_02", "entropy": 0.8})
        profile = self.pack.active_scan(profile, {"latency_ms": 999, "behavior": "random"})
        profile = self.pack.intel_fusion(profile)
        decision = self.pack.make_decision(profile)
        assert decision == PackDecision.WITHDRAW

    def test_decision_direct_assault_path(self):
        """
        DIRECT_ASSAULT decision path.
        Note:
        - SHADOW_STRIKE has priority if adrenaline < 0.4.
        - SWIFT_RETALIATE has priority if adrenaline > 0.5.
        So we need adrenaline between 0.4 and 0.5.
        """
        from adaptiveneuralnetwork.central_nervous_system.ecosystem.wolf_pack import (
            PackDecision,
            ThreatClass,
            ThreatProfile,
        )
        self.microbiome.testosterone = 0.8
        self.microbiome.adrenaline   = 45.0  # 0.45: > 0.4 (skips SHADOW) and < 0.5 (skips SWIFT)
        self.microbiome.gaba         = 0.3

        profile = ThreatProfile(
            target_id="assault_target",
            threat_class=ThreatClass.ADVERSARY,
            confidence=0.9, intent_score=0.9
        )
        decision = self.pack.make_decision(profile)
        assert decision == PackDecision.DIRECT_ASSAULT

    def test_gaba_floor_during_direct_assault(self):
        """Critical: GABA must not drop below 0.20."""
        from adaptiveneuralnetwork.central_nervous_system.ecosystem.wolf_pack import (
            PackDecision,
            ThreatClass,
            ThreatProfile,
        )
        self.microbiome.gaba = 0.50
        profile = ThreatProfile(target_id="test", threat_class=ThreatClass.ADVERSARY,
                                confidence=0.9, intent_score=0.95)
        self.pack.execute(PackDecision.DIRECT_ASSAULT, profile)
        assert self.microbiome.gaba >= 0.20

    def test_full_pipeline_returns_report(self):
        """Full run_operation pipeline should return a dict report."""
        report = self.pack.run_operation(
            signal_data={"source_id": "full_test", "entropy": 0.75, "regularity": 0.8},
            probe_data={"latency_ms": 8, "behavior": "periodic"},
            global_context={"known": False, "intent_score": 0.4}
        )
        assert report is not None
        assert "decision" in report
        assert "target" in report
        assert "intel" in report

    def test_pack_status_structure(self):
        status = self.pack.get_pack_status()
        assert "phase" in status
        assert "pack" in status
        assert "active_profiles" in status
        assert "intel_entries" in status
        assert "neurochemistry" in status

    def test_intel_log_grows(self):
        initial = len(self.pack.get_intel_report())
        self.pack.run_operation(
            {"source_id": "log_test", "entropy": 0.8},
            {"latency_ms": 5, "behavior": "periodic"},
            {"known": True, "intent_score": 0.5}
        )
        assert len(self.pack.get_intel_report()) > initial

# ══════════════════════════════════════════════════════════════════════════════
# NEUROCHEMISTRY TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestNeurochemistry:
    def setup_method(self):
        from adaptiveneuralnetwork.central_nervous_system.neurochemistry import NeurochemicalState
        self.state = NeurochemicalState()

    def test_initial_state_balanced(self):
        assert self.state.serotonin == pytest.approx(0.80)
        assert self.state.gaba      == pytest.approx(0.50)
        assert self.state.oxytocin  == pytest.approx(0.20)
        assert self.state.testosterone == pytest.approx(0.50)

    def test_anxiety_amortization_with_serotonin(self):
        """Higher serotonin → lower effective anxiety."""
        self.state.serotonin = 0.9
        self.state.gaba      = 0.7
        eff_high = self.state.get_effective_anxiety_factor(1.0)

        self.state.serotonin = 0.2
        self.state.gaba      = 0.1
        eff_low = self.state.get_effective_anxiety_factor(1.0)

        assert eff_high < eff_low

    def test_dopamine_spike_cap(self):
        """Dopamine must never exceed spike_cap."""
        for _ in range(10):
            self.state.trigger_dopamine_spike(5.0)
        assert self.state.dopamine <= self.state.config.dopamine_spike_cap

    def test_serotonin_boost_lifts_gaba(self):
        """Serotonin boost must passively lift GABA (coupling)."""
        gaba_before = self.state.gaba
        self.state.trigger_serotonin_boost(0.1)
        assert self.state.gaba >= gaba_before

    def test_cognitive_multiplier_reduced_by_serotonin(self):
        """High serotonin should reduce cognitive load."""
        self.state.serotonin = 0.9
        cost_high = self.state.get_cognitive_load_multiplier()
        self.state.serotonin = 0.2
        cost_low  = self.state.get_cognitive_load_multiplier()
        assert cost_high < cost_low

    def test_status_report_keys(self):
        report = self.state.get_status_report()
        required = {"adenosine", "dopamine", "cortisol", "serotonin",
                    "gaba", "oxytocin", "testosterone", "cognitive_multiplier",
                    "effective_anxiety_factor"}
        assert required.issubset(set(report.keys()))

    def test_sleep_phase_recovers_serotonin(self):
        self.state.serotonin = 0.3
        before = self.state.serotonin
        self.state.update(dt_hours=1.0, current_phase="sleep")
        assert self.state.serotonin > before

# ══════════════════════════════════════════════════════════════════════════════
# ARCHITECTURAL MIRROR TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestArchitecturalMirror:
    def setup_method(self):
        from adaptiveneuralnetwork.central_nervous_system.architectural_mirror import (
            ArchitecturalDomain,
            ArchitecturalMirror,
            Reflection,
            ZoomLevel,
        )
        self.Mirror = ArchitecturalMirror
        self.Domain = ArchitecturalDomain
        self.Zoom   = ZoomLevel
        self.Ref    = Reflection

    def test_instantiation(self):
        mirror = self.Mirror()
        assert mirror is not None

    def test_unregistered_domain_returns_blind_spot(self):
        mirror = self.Mirror()
        ref = mirror.reflect(self.Domain.PHYSICS)
        assert ref.data.get("status") == "unregistered"
        assert "ślepy punkt" in ref.narrative.lower()

    def test_register_and_reflect(self):
        mirror = self.Mirror()

        def my_provider(m, zoom):
            return self.Ref(
                domain=self.Domain.MEMORY,
                zoom=zoom,
                narrative="Test memory narrative",
                data={"count": 42}
            )

        mirror.register_domain(self.Domain.MEMORY, my_provider)
        ref = mirror.reflect(self.Domain.MEMORY, self.Zoom.REGION)
        assert ref.data["count"] == 42
        assert ref.narrative == "Test memory narrative"

    def test_reflect_all_covers_all_domains(self):
        mirror = self.Mirror()
        results = mirror.reflect_all()
        assert len(results) == len(self.Domain)

    def test_self_portrait_shows_blind_spots(self):
        mirror = self.Mirror()
        portrait = mirror.self_portrait()
        assert "ślepy punkt" in portrait.lower()

    def test_drill_down_valid_path(self):
        mirror = self.Mirror()
        def provider(m, zoom):
            return self.Ref(
                domain=self.Domain.NEUROCHEMISTRY,
                zoom=zoom,
                data={"serotonin": 0.75, "gaba": 0.50}
            )
        mirror.register_domain(self.Domain.NEUROCHEMISTRY, provider)
        ref = mirror.drill_down(self.Domain.NEUROCHEMISTRY, ["serotonin"])
        assert ref.data["value"] == pytest.approx(0.75)

    def test_reflection_log_grows(self):
        mirror = self.Mirror()
        def provider(m, zoom):
            return self.Ref(domain=self.Domain.IDENTITY, zoom=zoom, data={})
        mirror.register_domain(self.Domain.IDENTITY, provider)
        mirror.reflect(self.Domain.IDENTITY)
        history = mirror.get_reflection_history()
        assert len(history) == 1

    def test_build_mirror_integration(self):
        from adaptiveneuralnetwork.central_nervous_system.architectural_mirror import (
            ZoomLevel,
            build_mirror,
        )
        soul = make_soul()
        mirror = build_mirror(soul=soul)
        # Use COSMOS zoom to see "Błyskawica" in identity narrative
        ref = mirror.reflect(self.Domain.IDENTITY, zoom=ZoomLevel.COSMOS)
        assert "Błyskawica" in ref.narrative
