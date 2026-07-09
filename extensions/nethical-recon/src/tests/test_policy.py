"""Tests for worker policy engine."""

from __future__ import annotations

import pytest

from nethical_recon.worker.policy import (
    NetworkPolicy,
    PolicyEngine,
    RateLimitPolicy,
    RiskLevel,
    ToolPolicy,
    get_policy_engine,
    reset_policy_engine,
)


class TestNetworkPolicy:
    """Tests for NetworkPolicy."""

    def test_allow_ip_in_allowed_network(self):
        """Test that IP in allowed network is permitted."""
        policy = NetworkPolicy(allowed_networks=["192.168.1.0/24"])
        is_allowed, msg = policy.is_target_allowed("192.168.1.100")
        assert is_allowed
        assert "allowed network" in msg

    def test_deny_ip_in_denied_network(self):
        """Test that IP in denied network is blocked."""
        policy = NetworkPolicy(denied_networks=["10.0.0.0/8"])
        is_allowed, msg = policy.is_target_allowed("10.1.2.3")
        assert not is_allowed
        assert "denied network" in msg

    def test_denied_takes_precedence(self):
        """Test that denied networks take precedence over allowed."""
        policy = NetworkPolicy(
            allowed_networks=["192.168.0.0/16"],
            denied_networks=["192.168.1.0/24"],
        )
        is_allowed, msg = policy.is_target_allowed("192.168.1.50")
        assert not is_allowed

    def test_allow_by_default_when_no_restrictions(self):
        """Test that targets are allowed by default when no restrictions set."""
        policy = NetworkPolicy()
        is_allowed, msg = policy.is_target_allowed("1.2.3.4")
        assert is_allowed
        assert "No network restrictions" in msg

    def test_deny_ip_not_in_allowed_networks(self):
        """Test that IP not in any allowed network is denied."""
        policy = NetworkPolicy(allowed_networks=["192.168.1.0/24"])
        is_allowed, msg = policy.is_target_allowed("10.0.0.1")
        assert not is_allowed
        assert "not in any allowed network" in msg

    def test_allow_domain_in_allowed_list(self):
        """Test that domain in allowed list is permitted."""
        policy = NetworkPolicy(allowed_domains=["example.com"])
        is_allowed, msg = policy.is_target_allowed("example.com")
        assert is_allowed

    def test_allow_subdomain_of_allowed_domain(self):
        """Test that subdomain of allowed domain is permitted."""
        policy = NetworkPolicy(allowed_domains=["example.com"])
        is_allowed, msg = policy.is_target_allowed("api.example.com")
        assert is_allowed

    def test_deny_domain_not_in_allowed_list(self):
        """Test that domain not in allowed list is denied."""
        policy = NetworkPolicy(allowed_domains=["example.com"])
        is_allowed, msg = policy.is_target_allowed("evil.com")
        assert not is_allowed

    def test_deny_domain_in_denied_list(self):
        """Test that domain in denied list is blocked."""
        policy = NetworkPolicy(denied_domains=["evil.com"])
        is_allowed, msg = policy.is_target_allowed("evil.com")
        assert not is_allowed
        assert "denied domain" in msg

    def test_cidr_target(self):
        """Test CIDR target validation."""
        policy = NetworkPolicy(allowed_networks=["192.168.0.0/16"])
        is_allowed, msg = policy.is_target_allowed("192.168.1.0/24")
        assert is_allowed


class TestToolPolicy:
    """Tests for ToolPolicy."""

    def test_default_tool_risk_levels(self):
        """Test that default tool risk levels are set."""
        policy = ToolPolicy()
        assert policy.get_tool_risk("nmap") == RiskLevel.LOW
        assert policy.get_tool_risk("nikto") == RiskLevel.MEDIUM
        assert policy.get_tool_risk("sqlmap") == RiskLevel.HIGH

    def test_unknown_tool_gets_default_risk(self):
        """Test that unknown tools get default risk level."""
        policy = ToolPolicy()
        assert policy.get_tool_risk("unknown_tool") == RiskLevel.MEDIUM

    def test_disabled_tool_not_allowed(self):
        """Test that disabled tools are blocked."""
        policy = ToolPolicy(disabled_tools=["sqlmap"])
        is_allowed, msg = policy.is_tool_allowed("sqlmap")
        assert not is_allowed
        assert "disabled" in msg

    def test_restricted_tool_requires_approval(self):
        """Test that restricted tools require explicit approval."""
        policy = ToolPolicy(restricted_tools=["nikto"])
        is_allowed, msg = policy.is_tool_allowed("nikto", explicit_approval=False)
        assert not is_allowed
        assert "requires explicit approval" in msg

    def test_restricted_tool_allowed_with_approval(self):
        """Test that restricted tools are allowed with approval."""
        policy = ToolPolicy(restricted_tools=["nikto"])
        is_allowed, msg = policy.is_tool_allowed("nikto", explicit_approval=True)
        assert is_allowed

    def test_high_risk_tool_requires_approval(self):
        """Test that high-risk tools require explicit approval."""
        policy = ToolPolicy()
        is_allowed, msg = policy.is_tool_allowed("sqlmap", explicit_approval=False)
        assert not is_allowed
        assert "High-risk" in msg

    def test_high_risk_tool_allowed_with_approval(self):
        """Test that high-risk tools are allowed with approval."""
        policy = ToolPolicy()
        is_allowed, msg = policy.is_tool_allowed("sqlmap", explicit_approval=True)
        assert is_allowed

    def test_low_risk_tool_allowed(self):
        """Test that low-risk tools are allowed without approval."""
        policy = ToolPolicy()
        is_allowed, msg = policy.is_tool_allowed("nmap")
        assert is_allowed


class TestRateLimitPolicy:
    """Tests for RateLimitPolicy."""

    def test_default_rate_limits(self):
        """Test default rate limit values."""
        policy = RateLimitPolicy()
        assert policy.max_requests_per_second == 10.0
        assert policy.max_concurrent_tools == 3
        assert policy.max_concurrent_scans_per_target == 1
        assert policy.inter_request_delay == 0.1

    def test_custom_rate_limits(self):
        """Test custom rate limit values."""
        policy = RateLimitPolicy(
            max_requests_per_second=5.0,
            max_concurrent_tools=2,
        )
        assert policy.max_requests_per_second == 5.0
        assert policy.max_concurrent_tools == 2


class TestPolicyEngine:
    """Tests for PolicyEngine."""

    def test_validate_scan_with_valid_target_and_tools(self):
        """Test scan validation with valid target and tools."""
        policy = PolicyEngine(
            network=NetworkPolicy(allowed_networks=["192.168.1.0/24"]),
            tool=ToolPolicy(),
        )
        is_valid, messages = policy.validate_scan(
            "192.168.1.100",
            ["nmap"],
        )
        assert is_valid
        assert len(messages) > 0

    def test_validate_scan_with_invalid_target(self):
        """Test scan validation rejects invalid target."""
        policy = PolicyEngine(
            network=NetworkPolicy(denied_networks=["10.0.0.0/8"]),
        )
        is_valid, messages = policy.validate_scan(
            "10.1.2.3",
            ["nmap"],
        )
        assert not is_valid
        assert any("denied" in msg.lower() for msg in messages)

    def test_validate_scan_with_disabled_tool(self):
        """Test scan validation rejects disabled tool."""
        policy = PolicyEngine(
            tool=ToolPolicy(disabled_tools=["sqlmap"]),
        )
        is_valid, messages = policy.validate_scan(
            "example.com",
            ["sqlmap"],
        )
        assert not is_valid
        assert any("disabled" in msg.lower() for msg in messages)

    def test_validate_scan_with_high_risk_tool(self):
        """Test scan validation rejects high-risk tool without approval."""
        policy = PolicyEngine(tool=ToolPolicy())
        is_valid, messages = policy.validate_scan(
            "example.com",
            ["sqlmap"],
            explicit_approval=False,
        )
        assert not is_valid
        assert any("high-risk" in msg.lower() for msg in messages)

    def test_validate_scan_with_approval(self):
        """Test scan validation allows high-risk tool with approval."""
        policy = PolicyEngine(tool=ToolPolicy())
        is_valid, messages = policy.validate_scan(
            "example.com",
            ["sqlmap"],
            explicit_approval=True,
        )
        assert is_valid

    def test_audit_mode_logs_but_allows(self):
        """Test that audit mode logs violations but doesn't block."""
        policy = PolicyEngine(
            network=NetworkPolicy(denied_networks=["10.0.0.0/8"]),
            audit_mode=True,
        )
        is_valid, messages = policy.validate_scan(
            "10.1.2.3",
            ["nmap"],
        )
        assert is_valid  # Audit mode allows despite violation
        assert any("AUDIT" in msg for msg in messages)

    def test_disabled_enforcement(self):
        """Test that disabled enforcement allows everything."""
        policy = PolicyEngine(
            network=NetworkPolicy(denied_networks=["0.0.0.0/0"]),
            enforce_policies=False,
        )
        is_valid, messages = policy.validate_scan(
            "1.2.3.4",
            ["sqlmap"],
        )
        assert is_valid
        assert any("disabled" in msg.lower() for msg in messages)

    def test_get_global_policy_engine(self):
        """Test getting global policy engine instance."""
        reset_policy_engine()  # Reset first
        engine1 = get_policy_engine()
        engine2 = get_policy_engine()
        assert engine1 is engine2  # Should be same instance

    def test_reset_policy_engine(self):
        """Test resetting global policy engine."""
        engine1 = get_policy_engine()
        reset_policy_engine()
        engine2 = get_policy_engine()
        assert engine1 is not engine2  # Should be different instances
