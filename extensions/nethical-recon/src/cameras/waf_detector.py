"""
WAF Detector - Mask Detection Camera
🎭 Maska Mode - Detects hidden defenses

Identifies Web Application Firewalls and security layers:
- WAF signatures
- HTTP headers
- Response patterns
- Security products
"""

import re
from typing import Any

from .base import BaseCamera, CameraMode


class WAFDetector(BaseCamera):
    """
    WAF detection camera with mask vision

    Configuration:
        timeout: HTTP request timeout (default: 10)
        user_agent: Custom user agent (default: Nethical/2.0)
        test_payloads: Use test payloads for detection (default: True)
        verify_ssl: Verify SSL certificates (default: False for recon)
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__("WAFDetector", CameraMode.MASK, config)
        self.timeout = self.config.get("timeout", 10)
        self.user_agent = self.config.get("user_agent", "Nethical/2.0")
        self.test_payloads = self.config.get("test_payloads", True)
        # SSL verification disabled by default for reconnaissance
        # Can be enabled via config if needed
        self.verify_ssl = self.config.get("verify_ssl", False)

        # WAF signatures
        self.waf_signatures = self._load_waf_signatures()

    def _load_waf_signatures(self) -> dict[str, dict[str, list[str]]]:
        """Load WAF detection signatures"""
        return {
            "Cloudflare": {
                "headers": ["cf-ray", "cf-cache-status", "__cfduid"],
                "cookies": ["__cfduid", "__cflb"],
                "content": ["Attention Required", "Cloudflare", "Ray ID"],
            },
            "AWS WAF": {"headers": ["x-amzn-requestid", "x-amz-cf-id"], "content": ["Request blocked", "AWS"]},
            "Akamai": {"headers": ["akamai-origin-hop", "x-akamai"], "content": ["Access Denied", "Akamai"]},
            "Imperva (Incapsula)": {
                "headers": ["x-cdn", "x-iinfo"],
                "cookies": ["incap_ses", "visid_incap"],
                "content": ["Incapsula", "_Incapsula_Resource"],
            },
            "ModSecurity": {"headers": ["server"], "content": ["ModSecurity", "mod_security", "NOYB"]},
            "Sucuri": {"headers": ["x-sucuri-id", "x-sucuri-cache"], "content": ["Sucuri", "Access Denied - Sucuri"]},
            "F5 BIG-IP": {"headers": ["x-cnection"], "cookies": ["BIGipServer", "F5_"], "content": ["BigIP", "F5"]},
            "Barracuda": {
                "headers": ["barra_counter_session"],
                "cookies": ["barra_counter_session"],
                "content": ["Barracuda"],
            },
            "FortiWeb": {"headers": ["fortiwafsid"], "cookies": ["FORTIWAFSID"], "content": ["FortiWeb"]},
            "Citrix NetScaler": {
                "headers": ["ns_af", "citrix_ns_id"],
                "cookies": ["ns_af", "citrix_ns_id", "NSC_"],
                "content": ["NetScaler"],
            },
        }

    def validate_config(self) -> bool:
        """Validate configuration"""
        try:
            import requests

            return True
        except ImportError:
            self.logger.error("requests library not installed. Install with: pip install requests")
            return False

    def scan(self, target: str) -> dict[str, Any]:
        """
        Detect WAF on target

        Args:
            target: URL or domain to scan

        Returns:
            Dict with WAF detection results
        """
        if not self.validate_config():
            return {"error": "requests library not installed"}

        # Ensure target has protocol
        if not target.startswith(("http://", "https://")):
            target = f"http://{target}"

        self.logger.info(f"🎭 Mask Detection: Scanning for WAF on {target}...")

        results = {
            "target": target,
            "waf_detected": False,
            "waf_name": None,
            "confidence": 0.0,
            "evidence": [],
            "all_detections": [],
        }

        try:
            # Perform detection
            detections = self._detect_waf(target)

            if detections:
                results["waf_detected"] = True
                results["all_detections"] = detections

                # Get highest confidence detection
                best = max(detections, key=lambda x: x["confidence"])
                results["waf_name"] = best["name"]
                results["confidence"] = best["confidence"]
                results["evidence"] = best["evidence"]

                self.logger.warning(f"WAF detected: {results['waf_name']} (confidence: {results['confidence']:.0%})")

                # Record discovery
                self.record_discovery(
                    "waf",
                    target,
                    {"waf": results["waf_name"], "confidence": results["confidence"], "evidence": results["evidence"]},
                    confidence=results["confidence"],
                    severity="WARNING",
                )
            else:
                self.logger.info("No WAF detected")

        except Exception as e:
            self.logger.error(f"WAF detection failed: {e}")
            results["error"] = str(e)

        return results

    def _detect_waf(self, url: str) -> list[dict[str, Any]]:
        """
        Detect WAF using multiple techniques

        Args:
            url: Target URL

        Returns:
            List of detected WAFs with confidence scores
        """
        import warnings

        import requests

        detections = []

        # Suppress SSL warnings only if SSL verification is disabled
        # This is intentional for reconnaissance but configurable
        if not self.verify_ssl:
            import urllib3

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)

        try:
            # Normal request
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers, timeout=self.timeout, verify=self.verify_ssl)

            # Check each WAF signature
            for waf_name, signatures in self.waf_signatures.items():
                evidence = []
                matches = 0
                total_checks = 0

                # Check headers
                if "headers" in signatures:
                    for header in signatures["headers"]:
                        total_checks += 1
                        if header.lower() in [h.lower() for h in response.headers.keys()]:
                            matches += 1
                            evidence.append(f"Header: {header}")

                # Check cookies
                if "cookies" in signatures:
                    for cookie in signatures["cookies"]:
                        total_checks += 1
                        if cookie.lower() in [c.lower() for c in response.cookies.keys()]:
                            matches += 1
                            evidence.append(f"Cookie: {cookie}")

                # Check content
                if "content" in signatures:
                    content = response.text
                    for pattern in signatures["content"]:
                        total_checks += 1
                        if re.search(pattern, content, re.IGNORECASE):
                            matches += 1
                            evidence.append(f"Content: {pattern}")

                # Calculate confidence
                if matches > 0 and total_checks > 0:
                    confidence = matches / total_checks
                    detections.append(
                        {"name": waf_name, "confidence": confidence, "evidence": evidence, "matches": matches}
                    )

            # Test with malicious payload if enabled
            if self.test_payloads:
                payload_detections = self._test_with_payloads(url)

                # Merge with existing detections
                for pd in payload_detections:
                    # Check if WAF already detected
                    existing = next((d for d in detections if d["name"] == pd["name"]), None)
                    if existing:
                        # Boost confidence
                        existing["confidence"] = min(1.0, existing["confidence"] + 0.2)
                        existing["evidence"].extend(pd["evidence"])
                    else:
                        detections.append(pd)

        except Exception as e:
            self.logger.error(f"Detection failed: {e}")

        # Sort by confidence
        detections.sort(key=lambda x: x["confidence"], reverse=True)

        return detections

    def _test_with_payloads(self, url: str) -> list[dict[str, Any]]:
        """
        Test WAF with malicious payloads

        Args:
            url: Target URL

        Returns:
            List of detections based on payload responses
        """
        import requests

        detections = []

        # Test payloads
        payloads = ["<script>alert('XSS')</script>", "' OR '1'='1", "../../../etc/passwd", "{{7*7}}", "${7*7}"]

        try:
            normal_response = requests.get(url, timeout=self.timeout, verify=self.verify_ssl)
            normal_status = normal_response.status_code

            for payload in payloads:
                try:
                    # Send malicious request
                    test_url = f"{url}?test={payload}"
                    response = requests.get(test_url, timeout=self.timeout, verify=self.verify_ssl)

                    # Check if response is different
                    if response.status_code != normal_status:
                        # Blocked by WAF
                        status_code = response.status_code

                        # Check which WAF based on block page
                        for waf_name, signatures in self.waf_signatures.items():
                            if "content" in signatures:
                                for pattern in signatures["content"]:
                                    if re.search(pattern, response.text, re.IGNORECASE):
                                        detections.append(
                                            {
                                                "name": waf_name,
                                                "confidence": 0.7,
                                                "evidence": [
                                                    f"Blocked payload: {payload[:20]}...",
                                                    f"Status: {status_code}",
                                                ],
                                                "matches": 1,
                                            }
                                        )
                                        break

                except Exception:
                    continue

        except Exception as e:
            self.logger.error(f"Payload testing failed: {e}")

        return detections

    def quick_scan(self, url: str) -> str | None:
        """
        Quick WAF detection (basic check only)

        Args:
            url: Target URL

        Returns:
            WAF name if detected, None otherwise
        """
        result = self.scan(url)
        return result.get("waf_name")
