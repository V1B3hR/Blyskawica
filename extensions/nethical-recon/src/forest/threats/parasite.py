"""
forest/threats/parasite.py
Parasite threat - represents cryptominers and resource abusers.

The parasite:
- Drains resources from the host (CPU/GPU)
- Slowly weakens the host
- Difficult to detect without resource monitoring
"""

from typing import Any

from .base import BaseThreat, ThreatSeverity, ThreatType


class Parasite(BaseThreat):
    """
    Parasite threat - Cryptominer/Resource abuse.

    Analogia: 🐛 Pasożyt - Wysysa soki z drzewa
    """

    def __init__(
        self,
        threat_id: str,
        name: str,
        severity: ThreatSeverity = ThreatSeverity.MEDIUM,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Initialize a Parasite threat.

        Args:
            threat_id: Unique identifier
            name: Parasite name/type
            severity: Severity level (default: MEDIUM)
            metadata: Additional metadata
        """
        super().__init__(threat_id, name, ThreatType.PARASITE, severity, metadata)

        # Parasite-specific attributes
        self.parasite_type = metadata.get("parasite_type", "cryptominer") if metadata else "cryptominer"
        self.cryptocurrency = metadata.get("cryptocurrency") if metadata else None
        self.mining_pool = metadata.get("mining_pool") if metadata else None

        # Resource drain
        self.cpu_usage_percent = 0.0
        self.gpu_usage_percent = 0.0
        self.network_usage_mbps = 0.0

        # Impact tracking
        self.estimated_cost_per_day = 0.0  # USD
        self.duration_days = 0.0

    def get_description(self) -> str:
        """Get description of the Parasite threat"""
        desc = f"Resource abuse detected: {self.name} ({self.parasite_type}). "

        if self.parasite_type == "cryptominer":
            desc += "This parasite is mining "
            if self.cryptocurrency:
                desc += f"{self.cryptocurrency} "
            desc += "and draining system resources. "
            if self.mining_pool:
                desc += f"Mining pool: {self.mining_pool}."
        else:
            desc += "This parasite is consuming excessive system resources."

        return desc

    def get_behavior_pattern(self) -> str:
        """Get characteristic behavior pattern"""
        behaviors = [f"Type: {self.parasite_type}"]

        if self.cpu_usage_percent > 0:
            behaviors.append(f"CPU: {self.cpu_usage_percent:.1f}%")
        if self.gpu_usage_percent > 0:
            behaviors.append(f"GPU: {self.gpu_usage_percent:.1f}%")
        if self.network_usage_mbps > 0:
            behaviors.append(f"Network: {self.network_usage_mbps:.1f} Mbps")
        if self.estimated_cost_per_day > 0:
            behaviors.append(f"Cost: ${self.estimated_cost_per_day:.2f}/day")

        return " | ".join(behaviors)

    def update_resource_usage(self, cpu: float = None, gpu: float = None, network_mbps: float = None):
        """
        Update resource usage metrics.

        Args:
            cpu: CPU usage percentage
            gpu: GPU usage percentage
            network_mbps: Network usage in Mbps
        """
        if cpu is not None:
            self.cpu_usage_percent = cpu
        if gpu is not None:
            self.gpu_usage_percent = gpu
        if network_mbps is not None:
            self.network_usage_mbps = network_mbps

        # Auto-escalate severity based on resource drain
        total_drain = self.cpu_usage_percent + self.gpu_usage_percent
        if total_drain > 150 and self.severity == ThreatSeverity.MEDIUM:
            self.severity = ThreatSeverity.HIGH

    def estimate_cost(self, electricity_cost_per_kwh: float = 0.12, system_power_watts: float = 300):
        """
        Estimate financial cost of the parasite.

        Args:
            electricity_cost_per_kwh: Cost per kilowatt-hour
            system_power_watts: System power consumption in watts
        """
        # Rough calculation based on CPU/GPU usage
        usage_multiplier = (self.cpu_usage_percent + self.gpu_usage_percent) / 200.0
        daily_kwh = (system_power_watts * usage_multiplier * 24) / 1000.0
        self.estimated_cost_per_day = daily_kwh * electricity_cost_per_kwh

    def set_mining_details(self, cryptocurrency: str, pool: str):
        """
        Set cryptocurrency mining details.

        Args:
            cryptocurrency: Name of cryptocurrency being mined
            pool: Mining pool address
        """
        self.cryptocurrency = cryptocurrency
        self.mining_pool = pool
        if pool:
            self.add_indicator(pool, "mining_pool")

    def __str__(self):
        base_str = super().__str__()
        if self.cpu_usage_percent > 0 or self.gpu_usage_percent > 0:
            base_str += f" [CPU: {self.cpu_usage_percent:.0f}%, GPU: {self.gpu_usage_percent:.0f}%]"
        return base_str
