"""
Masscan Adapter - Fast Port Scanner

Masscan is a very fast port scanner capable of scanning the entire
Internet in under 6 minutes at 10 million packets per second.
"""

import json
import re
from pathlib import Path
from typing import Any
from uuid import UUID

from nethical_recon.adapters.base_plugin import ToolPlugin
from nethical_recon.core.models import Confidence, Finding, Severity


class MasscanAdapter(ToolPlugin):
    """Adapter for masscan port scanner."""

    def __init__(self, tool_path: str | None = None):
        super().__init__("masscan", tool_path)

    def validate_target(self, target: str) -> tuple[bool, str]:
        """Validate target is an IP, CIDR, or range."""
        # Simple validation - IP, CIDR, or range
        if re.match(r"^(\d{1,3}\.){3}\d{1,3}(/\d{1,2})?$", target):
            return True, ""
        if re.match(r"^(\d{1,3}\.){3}\d{1,3}-\d{1,3}$", target):
            return True, ""
        return False, "Target must be IP address, CIDR, or IP range"

    def build_command(self, target: str, output_path: Path, options: dict[str, Any] | None = None) -> list[str]:
        """Build masscan command."""
        options = options or {}

        cmd = [
            self.tool_path,
            target,
            "-p",
            options.get("ports", "1-65535"),  # Default: all ports
            "--rate",
            str(options.get("rate", 1000)),  # Default: 1000 packets/sec
            "-oJ",
            str(output_path),  # JSON output
            "--wait",
            "3",  # Wait for responses
        ]

        # Add optional flags
        if options.get("exclude"):
            cmd.extend(["--exclude", options["exclude"]])

        if options.get("exclude_file"):
            cmd.extend(["--excludefile", options["exclude_file"]])

        return cmd

    def parse_output(self, content: str) -> dict[str, Any]:
        """Parse masscan JSON output."""
        if not content or not content.strip():
            return {"hosts": []}

        hosts = []

        # Masscan outputs multiple JSON objects, one per line
        for line in content.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Remove trailing comma if present
            if line.endswith(","):
                line = line[:-1]

            try:
                entry = json.loads(line)

                # Masscan format: {"ip": "x.x.x.x", "timestamp": "...", "ports": [{"port": 80, "proto": "tcp", "status": "open"}]}
                if "ip" in entry and "ports" in entry:
                    for port_info in entry["ports"]:
                        hosts.append(
                            {
                                "ip": entry["ip"],
                                "port": port_info.get("port"),
                                "protocol": port_info.get("proto", "tcp"),
                                "state": port_info.get("status", "open"),
                                "timestamp": entry.get("timestamp", ""),
                            }
                        )
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse masscan line: {e}")
                continue

        return {"hosts": hosts}

    def to_findings(self, parsed_data: dict[str, Any], run_id: UUID, evidence_id: UUID) -> list[Finding]:
        """Convert masscan results to findings."""
        findings = []

        for host in parsed_data.get("hosts", []):
            ip = host.get("ip")
            port = host.get("port")
            protocol = host.get("protocol", "tcp")
            state = host.get("state", "open")

            if not ip or not port:
                continue

            # Determine severity based on port
            severity = self._assess_port_severity(port, protocol)

            finding = Finding(
                run_id=run_id,
                title=f"Open {protocol.upper()} Port {port}",
                description=f"Port {port}/{protocol} is {state} on {ip}",
                severity=severity,
                confidence=Confidence.HIGH,
                category="open_port",
                affected_asset=ip,
                port=port,
                protocol=protocol,
                tags=["masscan", "port-scan", protocol],
                evidence_ids=[evidence_id],
                raw_data=host,
            )

            findings.append(finding)

        return findings

    def _assess_port_severity(self, port: int, protocol: str) -> Severity:
        """Assess severity based on port number."""
        # High-risk ports
        high_risk_ports = {
            22: "SSH",
            23: "Telnet",
            3389: "RDP",
            5900: "VNC",
            1433: "MSSQL",
            3306: "MySQL",
            5432: "PostgreSQL",
            6379: "Redis",
            27017: "MongoDB",
            9200: "Elasticsearch",
        }

        # Critical ports
        critical_ports = {445: "SMB", 139: "NetBIOS", 135: "RPC"}

        if port in critical_ports:
            return Severity.CRITICAL
        elif port in high_risk_ports:
            return Severity.HIGH
        elif port < 1024:  # Privileged ports
            return Severity.MEDIUM
        else:
            return Severity.LOW
