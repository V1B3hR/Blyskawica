"""
DNS Watcher Sensor
🌐 Monitors DNS queries for suspicious patterns
Analogia: "Szepty w lesie" (Whispers in the forest)
"""

import re
import subprocess
import threading
import time
from collections import Counter
from typing import Any

from ..base import BaseSensor, SensorStatus


class DNSWatcher(BaseSensor):
    """
    Monitors DNS queries for suspicious patterns like:
    - DGA (Domain Generation Algorithm) patterns
    - DNS tunneling
    - Connections to known malicious domains
    - Unusual query volumes
    """

    def __init__(self, name: str = "dns_watcher", config: dict[str, Any] = None):
        """
        Initialize DNS Watcher

        Config options:
            - interface: Network interface to monitor (default: any)
            - query_threshold: Queries per minute to trigger alert (default: 100)
            - suspicious_tlds: List of suspicious TLDs (default: ['tk', 'ml', 'ga'])
            - check_interval: Seconds between checks (default: 60)
        """
        super().__init__(name, config)
        self.interface = self.config.get("interface", "any")
        self.query_threshold = self.config.get("query_threshold", 100)
        self.suspicious_tlds = self.config.get("suspicious_tlds", ["tk", "ml", "ga", "cf", "gq"])
        self.check_interval = self.config.get("check_interval", 60)

        self._monitor_thread = None
        self._stop_flag = False
        self._query_counts = Counter()  # Track query counts
        self._suspicious_domains = set()  # Track suspicious domains

    def start(self) -> bool:
        """Start DNS monitoring"""
        if self.status == SensorStatus.RUNNING:
            self.logger.warning("DNS watcher already running")
            return False

        try:
            self._stop_flag = False
            self._monitor_thread = threading.Thread(target=self._monitor_dns, daemon=True)
            self._monitor_thread.start()

            self.status = SensorStatus.RUNNING
            self.logger.info(f"Started DNS monitoring on interface {self.interface}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start DNS watcher: {e}")
            self.status = SensorStatus.ERROR
            return False

    def stop(self) -> bool:
        """Stop DNS monitoring"""
        if self.status != SensorStatus.RUNNING:
            return False

        try:
            self._stop_flag = True

            # Wait for monitor thread
            if self._monitor_thread:
                self._monitor_thread.join(timeout=5)

            self.status = SensorStatus.STOPPED
            self.logger.info("Stopped DNS monitoring")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping DNS watcher: {e}")
            return False

    def check(self) -> dict[str, Any]:
        """Perform a single DNS check"""
        try:
            queries = self._capture_dns_queries(duration=10)
            analysis = self._analyze_queries(queries)

            return {"status": "success", "queries_captured": len(queries), "analysis": analysis}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _monitor_dns(self):
        """Internal monitoring loop"""
        while not self._stop_flag:
            try:
                # Capture DNS queries
                queries = self._capture_dns_queries(duration=self.check_interval)

                # Analyze queries
                analysis = self._analyze_queries(queries)

                # Handle findings
                if analysis["suspicious_queries"]:
                    self._handle_suspicious_queries(analysis["suspicious_queries"])

                if analysis["high_volume"]:
                    self._handle_high_volume(analysis["total_queries"])

            except Exception as e:
                self.logger.error(f"Error in DNS monitoring: {e}")
                time.sleep(self.check_interval)

    def _capture_dns_queries(self, duration: int = 60) -> list:
        """
        Capture DNS queries for specified duration.

        Tries tcpdump first, falls back to scapy if tcpdump is not available.

        Args:
            duration: Capture duration in seconds

        Returns:
            List of DNS queries
        """
        try:
            return self._capture_with_tcpdump(duration)
        except FileNotFoundError:
            self.logger.warning("tcpdump not available, using scapy fallback")
            return self._capture_with_scapy(duration)
        except Exception as e:
            self.logger.error(f"Error capturing DNS queries: {e}")
            return []

    def _capture_with_tcpdump(self, duration: int) -> list:
        """
        Capture DNS queries using tcpdump.

        Args:
            duration: Capture duration in seconds

        Returns:
            List of DNS queries
        """
        queries = []

        # Use tcpdump to capture DNS traffic
        result = subprocess.run(
            ["timeout", str(duration), "tcpdump", "-i", self.interface, "-n", "udp", "port", "53", "-l"],
            capture_output=True,
            text=True,
            timeout=duration + 5,
        )

        # Parse output
        for line in result.stdout.split("\n"):
            query = self._parse_dns_query(line)
            if query:
                queries.append(query)

        return queries

    def _capture_with_scapy(self, duration: int) -> list:
        """
        Capture DNS queries using scapy as fallback.

        Args:
            duration: Capture duration in seconds

        Returns:
            List of DNS queries
        """
        try:
            from scapy.all import DNS, DNSQR, IP, sniff
        except ImportError:
            self.logger.error("Neither tcpdump nor scapy available. Install scapy with: pip install scapy")
            return []

        queries = []

        def packet_handler(pkt):
            """Handle captured DNS packet."""
            try:
                if pkt.haslayer(DNS) and pkt.haslayer(DNSQR):
                    query_name = pkt[DNSQR].qname.decode("utf-8", errors="ignore").rstrip(".")
                    source_ip = pkt[IP].src if pkt.haslayer(IP) else "unknown"

                    queries.append(
                        {"source": source_ip, "domain": query_name, "raw": f"DNS query: {query_name} from {source_ip}"}
                    )
            except Exception as e:
                self.logger.debug(f"Error parsing DNS packet: {e}")

        try:
            # Capture packets with timeout
            sniff(
                iface=self.interface if self.interface != "any" else None,
                filter="udp port 53",
                prn=packet_handler,
                timeout=duration,
                store=False,
            )
        except Exception as e:
            self.logger.error(f"Error in scapy capture: {e}")

        return queries

    def _parse_dns_query(self, line: str) -> dict[str, Any]:
        """
        Parse DNS query from tcpdump output

        Args:
            line: tcpdump output line

        Returns:
            Parsed query dict or None
        """
        # Basic DNS query pattern
        # Example: 10:30:00.123456 IP 192.168.1.100.12345 > 8.8.8.8.53: 12345+ A? example.com. (28)

        match = re.search(r"(\S+)\s+>\s+\S+\.53.*\?\s+(\S+)\.", line)
        if match:
            source_ip = match.group(1).split(".")[0]  # Extract IP
            domain = match.group(2)

            return {"source": source_ip, "domain": domain, "raw": line.strip()}

        return None

    def _analyze_queries(self, queries: list) -> dict[str, Any]:
        """
        Analyze DNS queries for suspicious patterns

        Args:
            queries: List of DNS queries

        Returns:
            Analysis results
        """
        analysis = {
            "total_queries": len(queries),
            "unique_domains": set(),
            "suspicious_queries": [],
            "high_volume": False,
        }

        for query in queries:
            domain = query.get("domain", "")
            analysis["unique_domains"].add(domain)

            # Check for suspicious patterns
            if self._is_suspicious_domain(domain):
                analysis["suspicious_queries"].append(query)

        # Check for high volume
        if len(queries) > self.query_threshold:
            analysis["high_volume"] = True

        return analysis

    def _is_suspicious_domain(self, domain: str) -> bool:
        """
        Check if domain is suspicious

        Args:
            domain: Domain name

        Returns:
            bool: True if suspicious
        """
        # Check for suspicious TLDs
        for tld in self.suspicious_tlds:
            if domain.endswith("." + tld):
                return True

        # Check for DGA-like patterns (long random-looking subdomains)
        parts = domain.split(".")
        if len(parts) > 1:
            subdomain = parts[0]
            # Long subdomain with high entropy (simplified check)
            if len(subdomain) > 20 and not self._has_dictionary_words(subdomain):
                return True

        # Check for excessive length (possible DNS tunneling)
        if len(domain) > 100:
            return True

        return False

    def _has_dictionary_words(self, text: str) -> bool:
        """
        Check if text contains dictionary words (simplified)

        Args:
            text: Text to check

        Returns:
            bool: True if contains recognizable words
        """
        # Simplified check - look for vowel patterns
        vowel_count = sum(1 for c in text.lower() if c in "aeiou")
        return vowel_count > len(text) * 0.3  # At least 30% vowels

    def _handle_suspicious_queries(self, queries: list):
        """
        Handle suspicious DNS queries

        Args:
            queries: List of suspicious queries
        """
        for query in queries[:5]:  # Limit alerts
            domain = query.get("domain", "unknown")
            source = query.get("source", "unknown")

            self.raise_alert("WARNING", f"Suspicious DNS query: {domain} from {source}", query)

    def _handle_high_volume(self, query_count: int):
        """
        Handle high volume of DNS queries

        Args:
            query_count: Number of queries
        """
        self.raise_alert(
            "WARNING",
            f"High DNS query volume: {query_count} queries in {self.check_interval}s",
            {"query_count": query_count, "threshold": self.query_threshold, "interval": self.check_interval},
        )

    def get_statistics(self) -> dict[str, Any]:
        """Get DNS monitoring statistics"""
        return {
            "status": self.status.value,
            "interface": self.interface,
            "query_threshold": self.query_threshold,
            "suspicious_tlds": self.suspicious_tlds,
            "check_interval": self.check_interval,
            "alerts": len(self.alerts),
        }
