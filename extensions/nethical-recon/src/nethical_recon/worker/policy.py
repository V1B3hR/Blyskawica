"""Policy engine for Rules of Engagement (RoE)."""

from __future__ import annotations

import ipaddress
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RiskLevel(str, Enum):
    """Risk level for tools and operations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class RateLimitPolicy:
    """Rate limiting policy."""

    # Maximum requests per second
    max_requests_per_second: float = 10.0

    # Maximum concurrent tools
    max_concurrent_tools: int = 3

    # Maximum concurrent scans per target
    max_concurrent_scans_per_target: int = 1

    # Delay between requests (seconds)
    inter_request_delay: float = 0.1


@dataclass
class NetworkPolicy:
    """Network access policy."""

    # Allowed networks (CIDR notation)
    allowed_networks: list[str] = field(default_factory=list)

    # Denied networks (CIDR notation)
    denied_networks: list[str] = field(default_factory=list)

    # Allowed domains/hostnames
    allowed_domains: list[str] = field(default_factory=list)

    # Denied domains/hostnames
    denied_domains: list[str] = field(default_factory=list)

    def is_target_allowed(self, target: str) -> tuple[bool, str]:
        """
        Check if a target is allowed based on network policy.

        Args:
            target: IP address, CIDR, or domain name

        Returns:
            Tuple of (is_allowed, reason)
        """
        # Check if target is an IP or CIDR
        try:
            ip_network = ipaddress.ip_network(target, strict=False)

            # Check denied networks first
            for denied_cidr in self.denied_networks:
                denied_net = ipaddress.ip_network(denied_cidr, strict=False)
                if ip_network.overlaps(denied_net):
                    return False, f"Target {target} overlaps with denied network {denied_cidr}"

            # If allowed_networks is empty, allow by default (unless explicitly denied)
            if not self.allowed_networks:
                return True, "No network restrictions configured"

            # Check allowed networks
            for allowed_cidr in self.allowed_networks:
                allowed_net = ipaddress.ip_network(allowed_cidr, strict=False)
                if ip_network.overlaps(allowed_net):
                    return True, f"Target {target} is in allowed network {allowed_cidr}"

            return False, f"Target {target} is not in any allowed network"

        except ValueError:
            # Not an IP, treat as domain
            target_lower = target.lower()

            # Check denied domains
            for denied_domain in self.denied_domains:
                if target_lower == denied_domain.lower() or target_lower.endswith(f".{denied_domain.lower()}"):
                    return False, f"Domain {target} matches denied domain {denied_domain}"

            # If allowed_domains is empty, allow by default (unless explicitly denied)
            if not self.allowed_domains:
                return True, "No domain restrictions configured"

            # Check allowed domains
            for allowed_domain in self.allowed_domains:
                if target_lower == allowed_domain.lower() or target_lower.endswith(f".{allowed_domain.lower()}"):
                    return True, f"Domain {target} matches allowed domain {allowed_domain}"

            return False, f"Domain {target} is not in allowed domains list"


@dataclass
class ToolPolicy:
    """Tool execution policy."""

    # Map of tool names to their risk levels
    tool_risk_levels: dict[str, RiskLevel] = field(default_factory=dict)

    # Tools that require explicit approval
    restricted_tools: list[str] = field(default_factory=list)

    # Tools that are completely disabled
    disabled_tools: list[str] = field(default_factory=list)

    # Default risk level for unknown tools
    default_risk_level: RiskLevel = RiskLevel.MEDIUM

    def __post_init__(self):
        """Initialize default tool risk levels."""
        if not self.tool_risk_levels:
            self.tool_risk_levels = {
                # Low risk - passive reconnaissance
                "nmap": RiskLevel.LOW,
                "dig": RiskLevel.LOW,
                "whois": RiskLevel.LOW,
                "shodan": RiskLevel.LOW,
                "censys": RiskLevel.LOW,
                # Medium risk - active scanning
                "nikto": RiskLevel.MEDIUM,
                "dirb": RiskLevel.MEDIUM,
                "gobuster": RiskLevel.MEDIUM,
                "sublist3r": RiskLevel.MEDIUM,
                # High risk - exploitation/aggressive
                "sqlmap": RiskLevel.HIGH,
                "metasploit": RiskLevel.HIGH,
                "hydra": RiskLevel.HIGH,
                "masscan": RiskLevel.HIGH,
            }

    def get_tool_risk(self, tool_name: str) -> RiskLevel:
        """Get risk level for a tool."""
        return self.tool_risk_levels.get(tool_name.lower(), self.default_risk_level)

    def is_tool_allowed(self, tool_name: str, explicit_approval: bool = False) -> tuple[bool, str]:
        """
        Check if a tool is allowed to run.

        Args:
            tool_name: Name of the tool
            explicit_approval: Whether explicit approval was given

        Returns:
            Tuple of (is_allowed, reason)
        """
        tool_lower = tool_name.lower()

        # Check if tool is disabled
        if tool_lower in [t.lower() for t in self.disabled_tools]:
            return False, f"Tool {tool_name} is disabled by policy"

        # Check if tool requires approval
        if tool_lower in [t.lower() for t in self.restricted_tools]:
            if not explicit_approval:
                return False, f"Tool {tool_name} requires explicit approval"

        # Check risk level and warn for high-risk tools
        risk = self.get_tool_risk(tool_name)
        if risk == RiskLevel.HIGH and not explicit_approval:
            return False, f"High-risk tool {tool_name} requires explicit approval"

        return True, f"Tool {tool_name} is allowed (risk: {risk.value})"


@dataclass
class PolicyEngine:
    """Main policy engine for Rules of Engagement."""

    rate_limit: RateLimitPolicy = field(default_factory=RateLimitPolicy)
    network: NetworkPolicy = field(default_factory=NetworkPolicy)
    tool: ToolPolicy = field(default_factory=ToolPolicy)

    # Enable/disable policy enforcement
    enforce_policies: bool = True

    # Audit mode - log violations but don't block
    audit_mode: bool = False

    @classmethod
    def from_env(cls) -> PolicyEngine:
        """Create policy engine from environment variables."""
        return cls(
            rate_limit=RateLimitPolicy(
                max_requests_per_second=float(os.getenv("ROE_MAX_REQUESTS_PER_SEC", "10.0")),
                max_concurrent_tools=int(os.getenv("ROE_MAX_CONCURRENT_TOOLS", "3")),
                max_concurrent_scans_per_target=int(os.getenv("ROE_MAX_SCANS_PER_TARGET", "1")),
                inter_request_delay=float(os.getenv("ROE_INTER_REQUEST_DELAY", "0.1")),
            ),
            network=NetworkPolicy(
                allowed_networks=(
                    os.getenv("ROE_ALLOWED_NETWORKS", "").split(",") if os.getenv("ROE_ALLOWED_NETWORKS") else []
                ),
                denied_networks=(
                    os.getenv("ROE_DENIED_NETWORKS", "").split(",") if os.getenv("ROE_DENIED_NETWORKS") else []
                ),
                allowed_domains=(
                    os.getenv("ROE_ALLOWED_DOMAINS", "").split(",") if os.getenv("ROE_ALLOWED_DOMAINS") else []
                ),
                denied_domains=(
                    os.getenv("ROE_DENIED_DOMAINS", "").split(",") if os.getenv("ROE_DENIED_DOMAINS") else []
                ),
            ),
            tool=ToolPolicy(
                restricted_tools=(
                    os.getenv("ROE_RESTRICTED_TOOLS", "").split(",") if os.getenv("ROE_RESTRICTED_TOOLS") else []
                ),
                disabled_tools=(
                    os.getenv("ROE_DISABLED_TOOLS", "").split(",") if os.getenv("ROE_DISABLED_TOOLS") else []
                ),
            ),
            enforce_policies=os.getenv("ROE_ENFORCE", "true").lower() == "true",
            audit_mode=os.getenv("ROE_AUDIT_MODE", "false").lower() == "true",
        )

    def validate_scan(self, target: str, tools: list[str], explicit_approval: bool = False) -> tuple[bool, list[str]]:
        """
        Validate if a scan is allowed based on all policies.

        Args:
            target: Target to scan
            tools: List of tools to use
            explicit_approval: Whether explicit approval was given

        Returns:
            Tuple of (is_valid, list of validation messages)
        """
        if not self.enforce_policies:
            return True, ["Policy enforcement is disabled"]

        messages: list[str] = []
        is_valid = True

        # Check network policy
        target_allowed, target_msg = self.network.is_target_allowed(target)
        messages.append(target_msg)
        if not target_allowed:
            if not self.audit_mode:
                is_valid = False
            messages.append(
                "⚠️ AUDIT: Target denied by network policy" if self.audit_mode else "❌ Target denied by network policy"
            )

        # Check tool policies
        for tool in tools:
            tool_allowed, tool_msg = self.tool.is_tool_allowed(tool, explicit_approval)
            messages.append(tool_msg)
            if not tool_allowed:
                if not self.audit_mode:
                    is_valid = False
                messages.append(
                    f"⚠️ AUDIT: Tool {tool} denied by policy" if self.audit_mode else f"❌ Tool {tool} denied by policy"
                )

        return is_valid, messages


# Global policy engine instance
_policy_engine: PolicyEngine | None = None


def get_policy_engine() -> PolicyEngine:
    """Get the global policy engine instance."""
    global _policy_engine
    if _policy_engine is None:
        _policy_engine = PolicyEngine.from_env()
    return _policy_engine


def reset_policy_engine() -> None:
    """Reset the global policy engine (mainly for testing)."""
    global _policy_engine
    _policy_engine = None
