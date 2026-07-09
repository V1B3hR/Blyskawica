"""Active port scanner using Nmap integration."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from nethical_recon.adapters.nmap_adapter import NmapAdapter
from nethical_recon.core.parsers.nmap_parser import NmapParser


class ScanProfile(Enum):
    """Predefined scan profiles."""

    QUICK = "quick"  # Fast scan, top 100 ports
    STANDARD = "standard"  # Normal scan, version detection
    COMPREHENSIVE = "comprehensive"  # Deep scan with scripts
    STEALTH = "stealth"  # Slow, evasive scan
    AGGRESSIVE = "aggressive"  # Fast, noisy scan


@dataclass
class PortInfo:
    """Information about a discovered port."""

    port: int
    protocol: str
    state: str
    service: Optional[str] = None
    version: Optional[str] = None
    banner: Optional[str] = None


@dataclass
class ScanResult:
    """Result from an active scan."""

    scan_id: str
    target: str
    profile: ScanProfile
    started_at: datetime
    completed_at: Optional[datetime] = None
    ports: list[PortInfo] = field(default_factory=list)
    hostname: Optional[str] = None
    os_info: Optional[dict[str, Any]] = None
    raw_output: Optional[str] = None
    findings: list[Any] = field(default_factory=list)
    error: Optional[str] = None


class ActiveScanner:
    """Active port scanner using Nmap."""

    def __init__(self):
        """Initialize active scanner."""
        try:
            self.nmap = NmapAdapter()
        except RuntimeError as e:
            # Nmap not installed
            self.nmap = None
            self._error = str(e)

    def is_available(self) -> bool:
        """Check if Nmap is available."""
        return self.nmap is not None

    def get_profile_options(self, profile: ScanProfile) -> dict[str, Any]:
        """Get Nmap options for a scan profile.

        Args:
            profile: Scan profile

        Returns:
            Dictionary of Nmap options
        """
        profiles = {
            ScanProfile.QUICK: {
                "F": True,  # Fast scan (top 100 ports)
                "T": "4",  # Aggressive timing
            },
            ScanProfile.STANDARD: {
                "sV": True,  # Version detection
                "sC": True,  # Default scripts
                "T": "3",  # Normal timing
            },
            ScanProfile.COMPREHENSIVE: {
                "sV": True,  # Version detection
                "sC": True,  # Default scripts
                "O": True,  # OS detection
                "A": True,  # Aggressive scan (OS, version, scripts, traceroute)
                "T": "3",  # Normal timing
            },
            ScanProfile.STEALTH: {
                "sS": True,  # SYN scan
                "sV": True,  # Version detection
                "T": "2",  # Polite timing
            },
            ScanProfile.AGGRESSIVE: {
                "A": True,  # Aggressive scan
                "T": "5",  # Insane timing
            },
        }
        return profiles.get(profile, profiles[ScanProfile.STANDARD])

    def scan(
        self,
        target: str,
        profile: ScanProfile = ScanProfile.STANDARD,
        ports: Optional[str] = None,
        timeout: int = 3600,
    ) -> ScanResult:
        """Perform active port scan.

        Args:
            target: Target host or network
            profile: Scan profile to use
            ports: Port specification (e.g., "80,443,1-1000")
            timeout: Scan timeout in seconds

        Returns:
            ScanResult object
        """
        scan_id = str(uuid.uuid4())
        started_at = datetime.now()

        result = ScanResult(
            scan_id=scan_id,
            target=target,
            profile=profile,
            started_at=started_at,
        )

        if not self.is_available():
            result.error = getattr(self, "_error", "Nmap is not available")
            result.completed_at = datetime.now()
            return result

        try:
            # Build options
            options = self.get_profile_options(profile)
            options["oX"] = "-"  # XML output to stdout

            if ports:
                options["p"] = ports

            # Run Nmap
            job_id = uuid.uuid4()
            run_id = uuid.uuid4()
            tool_run = self.nmap.run(target, job_id, run_id, options, timeout)

            result.completed_at = datetime.now()
            result.raw_output = tool_run.stdout

            if tool_run.status.value == "completed" and tool_run.stdout:
                # Parse results
                parser = NmapParser()
                result.findings = parser.parse(tool_run.stdout, run_id)

                # Extract port information
                result.ports = self._extract_ports(tool_run.stdout)

            elif tool_run.status.value == "failed":
                result.error = tool_run.stderr or "Scan failed"

        except Exception as e:
            result.error = f"Scan error: {str(e)}"
            result.completed_at = datetime.now()

        return result

    def _extract_ports(self, nmap_xml: str) -> list[PortInfo]:
        """Extract port information from Nmap XML output.

        Args:
            nmap_xml: Nmap XML output

        Returns:
            List of PortInfo objects
        """
        import xml.etree.ElementTree as ET

        ports = []

        try:
            root = ET.fromstring(nmap_xml)

            for host in root.findall(".//host"):
                for port in host.findall(".//port"):
                    port_id = port.get("portid")
                    protocol = port.get("protocol", "tcp")

                    state_elem = port.find("state")
                    if state_elem is None:
                        continue

                    state = state_elem.get("state")

                    # Get service information
                    service_elem = port.find("service")
                    service_name = None
                    service_version = None

                    if service_elem is not None:
                        service_name = service_elem.get("name")
                        product = service_elem.get("product")
                        version = service_elem.get("version")

                        if product and version:
                            service_version = f"{product} {version}"
                        elif product:
                            service_version = product

                    ports.append(
                        PortInfo(
                            port=int(port_id),
                            protocol=protocol,
                            state=state,
                            service=service_name,
                            version=service_version,
                        )
                    )

        except ET.ParseError:
            pass

        return ports

    def scan_ports(
        self,
        target: str,
        ports: list[int],
        profile: ScanProfile = ScanProfile.STANDARD,
    ) -> ScanResult:
        """Scan specific ports on a target.

        Args:
            target: Target host
            ports: List of ports to scan
            profile: Scan profile

        Returns:
            ScanResult object
        """
        ports_str = ",".join(map(str, ports))
        return self.scan(target, profile, ports_str)
