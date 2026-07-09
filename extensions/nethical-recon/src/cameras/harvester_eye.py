"""
Harvester Eye - Bad Weather Vision Camera
🌧️ Zła pogoda Mode - OSINT through the fog

Uses theHarvester to gather:
- Email addresses
- Subdomains
- Hosts
- Employee names
- Open ports
- Banners
"""

import json
import os
import subprocess
import tempfile
from typing import Any

from .base import BaseCamera, CameraMode


class HarvesterEye(BaseCamera):
    """
    theHarvester-powered camera for OSINT reconnaissance

    Configuration:
        sources: List of sources to use (default: ['google', 'bing', 'duckduckgo'])
        limit: Limit of results per source (default: 500)
        timeout: Timeout in seconds (default: 120)
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__("HarvesterEye", CameraMode.BAD_WEATHER, config)
        self.sources = self.config.get("sources", ["google", "bing", "duckduckgo", "baidu"])
        self.limit = self.config.get("limit", 500)
        self.timeout = self.config.get("timeout", 120)

    def validate_config(self) -> bool:
        """Validate configuration"""
        # Check if theHarvester is installed
        try:
            result = subprocess.run(["which", "theHarvester"], capture_output=True, timeout=5)
            if result.returncode != 0:
                self.logger.error("theHarvester not found. Install it first.")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Failed to check for theHarvester: {e}")
            return False

    def scan(self, target: str) -> dict[str, Any]:
        """
        Scan target using theHarvester

        Args:
            target: Domain to scan

        Returns:
            Dict with scan results
        """
        if not self.validate_config():
            return {"error": "theHarvester not installed"}

        self.logger.info(f"🌧️ Bad Weather Vision: Scanning {target} with theHarvester...")

        results = {
            "target": target,
            "emails": [],
            "hosts": [],
            "subdomains": [],
            "ips": [],
            "asns": [],
            "by_source": {},
        }

        # Run theHarvester for each source
        for source in self.sources:
            try:
                self.logger.info(f"Gathering data from {source}...")
                source_results = self._run_harvester(target, source)

                if source_results:
                    # Aggregate results
                    results["emails"].extend(source_results.get("emails", []))
                    results["hosts"].extend(source_results.get("hosts", []))
                    results["ips"].extend(source_results.get("ips", []))
                    results["asns"].extend(source_results.get("asns", []))

                    # Store by source
                    results["by_source"][source] = source_results

            except Exception as e:
                self.logger.error(f"Failed to gather from {source}: {e}")
                continue

        # Remove duplicates
        results["emails"] = list(set(results["emails"]))
        results["hosts"] = list(set(results["hosts"]))
        results["ips"] = list(set(results["ips"]))
        results["asns"] = list(set(results["asns"]))

        # Extract subdomains from hosts
        for host in results["hosts"]:
            if host.endswith(target):
                results["subdomains"].append(host)

        # Record discoveries
        for email in results["emails"]:
            self.record_discovery("email", email, {"source": "theHarvester"}, confidence=0.8, severity="INFO")

        for subdomain in results["subdomains"]:
            self.record_discovery("subdomain", subdomain, {"parent_domain": target}, confidence=0.9, severity="INFO")

        self.logger.info(
            f"Found {len(results['emails'])} emails, "
            f"{len(results['subdomains'])} subdomains, "
            f"{len(results['hosts'])} hosts"
        )

        return results

    def _run_harvester(self, domain: str, source: str) -> dict[str, Any]:
        """
        Run theHarvester for a specific source

        Args:
            domain: Target domain
            source: Data source

        Returns:
            Dict with results
        """
        # Create temporary file for output
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            output_file = tmp.name

        try:
            # Build command
            command = [
                "theHarvester",
                "-d",
                domain,
                "-b",
                source,
                "-l",
                str(self.limit),
                "-f",
                output_file.replace(".json", ""),  # theHarvester adds .json
            ]

            # Run theHarvester
            result = subprocess.run(command, capture_output=True, text=True, timeout=self.timeout)

            # Read JSON output
            json_file = output_file
            if os.path.exists(json_file):
                with open(json_file) as f:
                    data = json.load(f)
                return data
            else:
                # Try to parse stdout if JSON file doesn't exist
                return self._parse_stdout(result.stdout)

        except subprocess.TimeoutExpired:
            self.logger.warning(f"theHarvester timed out for {source}")
            return {}

        except json.JSONDecodeError:
            self.logger.warning(f"Failed to parse JSON output for {source}")
            return {}

        except Exception as e:
            self.logger.error(f"Error running theHarvester: {e}")
            return {}

        finally:
            # Clean up temporary file
            try:
                if os.path.exists(output_file):
                    os.unlink(output_file)
            except Exception:
                pass

    def _parse_stdout(self, stdout: str) -> dict[str, Any]:
        """
        Parse theHarvester stdout output (fallback)

        Args:
            stdout: Standard output from theHarvester

        Returns:
            Dict with parsed results
        """
        results = {"emails": [], "hosts": [], "ips": []}

        # Simple parsing of common patterns
        import re

        # Extract emails
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        results["emails"] = list(set(re.findall(email_pattern, stdout)))

        # Extract IPs
        ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        results["ips"] = list(set(re.findall(ip_pattern, stdout)))

        # Extract hostnames (basic)
        host_pattern = (
            r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*"
        )
        potential_hosts = re.findall(host_pattern, stdout)
        results["hosts"] = [h for h in potential_hosts if "." in h and len(h) > 3]

        return results

    def quick_scan(self, target: str, source: str = "google") -> dict[str, Any]:
        """
        Quick scan with a single source

        Args:
            target: Domain to scan
            source: Single source to use

        Returns:
            Dict with results
        """
        self.logger.info(f"Quick scan of {target} using {source}")
        return self._run_harvester(target, source)
