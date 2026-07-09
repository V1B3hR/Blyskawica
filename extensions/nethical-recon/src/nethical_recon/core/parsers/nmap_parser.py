"""Nmap XML output parser."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from uuid import UUID

from ..models import Confidence, Finding, Severity
from . import BaseParser


class NmapParser(BaseParser):
    """Parser for Nmap XML output."""

    def __init__(self):
        """Initialize Nmap parser."""
        super().__init__()
        self.supported_tools = ["nmap"]

    def parse(self, output: str | dict, run_id: UUID) -> list[Finding]:
        """Parse Nmap XML output.

        Args:
            output: Nmap XML output as string.
            run_id: ID of the tool run.

        Returns:
            List of Finding objects.
        """
        if isinstance(output, dict):
            # If already parsed, handle it (future enhancement)
            return []

        findings: list[Finding] = []

        try:
            root = ET.fromstring(output)
        except ET.ParseError:
            # If XML parsing fails, return empty list
            return findings

        # Parse each host
        for host in root.findall(".//host"):
            # Get host address
            address_elem = host.find("address[@addrtype='ipv4']")
            if address_elem is None:
                address_elem = host.find("address[@addrtype='ipv6']")
            if address_elem is None:
                continue

            host_addr = address_elem.get("addr", "unknown")

            # Get hostname if available
            hostname = None
            hostname_elem = host.find(".//hostname")
            if hostname_elem is not None:
                hostname = hostname_elem.get("name")

            # Parse ports
            for port in host.findall(".//port"):
                port_id = port.get("portid")
                protocol = port.get("protocol", "tcp")

                state_elem = port.find("state")
                if state_elem is None:
                    continue

                state = state_elem.get("state")

                # Get service information
                service_elem = port.find("service")
                service_name = service_elem.get("name") if service_elem is not None else "unknown"
                service_version = None
                service_product = None

                if service_elem is not None:
                    service_product = service_elem.get("product")
                    service_version = service_elem.get("version")
                    if service_product and service_version:
                        service_version = f"{service_product} {service_version}"
                    elif service_product:
                        service_version = service_product

                # Create finding for open port
                if state == "open":
                    affected = hostname if hostname else host_addr

                    finding = Finding(
                        run_id=run_id,
                        title=f"Open Port: {port_id}/{protocol}",
                        description=f"Port {port_id}/{protocol} is open on {affected}",
                        severity=self._determine_severity(int(port_id), service_name),
                        confidence=Confidence.HIGH,
                        category="open_port",
                        affected_asset=affected,
                        port=int(port_id),
                        protocol=protocol,
                        service=service_name,
                        service_version=service_version,
                        tags=["network", "port-scan"],
                    )
                    findings.append(finding)

        return findings

    def _determine_severity(self, port: int, service: str) -> Severity:
        """Determine severity based on port and service.

        Args:
            port: Port number.
            service: Service name.

        Returns:
            Severity level.
        """
        # High-risk ports
        high_risk_ports = {21, 23, 445, 3389}  # FTP, Telnet, SMB, RDP
        sensitive_services = {"telnet", "ftp", "smb", "rdp"}

        if port in high_risk_ports or service in sensitive_services:
            return Severity.HIGH

        # Medium-risk ports
        medium_risk_ports = {22, 80, 443, 3306, 5432, 1433, 27017}  # SSH, HTTP, HTTPS, databases
        if port in medium_risk_ports:
            return Severity.MEDIUM

        # Everything else is low
        return Severity.LOW
