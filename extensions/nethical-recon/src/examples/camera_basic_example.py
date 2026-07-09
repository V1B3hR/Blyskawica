#!/usr/bin/env python3
"""
Nethical Recon - Camera Basic Example
Demonstrates usage of Fala 2: Kamery na Podczerwień (IR Cameras)

This example shows how to use the camera system for deep/dark discovery.
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cameras import CameraManager, DNSEnumerator, ShodanEye, SSLScanner, WAFDetector


def print_banner():
    """Print example banner"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              🌙 NETHICAL CAMERAS - FALA 2 🌙              ║
║              IR Night Vision Reconnaissance              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)


def example_dns_enumeration():
    """Example: DNS Ghost Vision"""
    print("\n" + "=" * 60)
    print("👻 DNS ENUMERATOR - Ghost Vision Example")
    print("=" * 60)

    # Create DNS camera
    dns_cam = DNSEnumerator(config={"check_zone_transfer": True, "timeout": 3})

    # Scan a domain (use a safe test domain)
    target = "example.com"
    print(f"\n[*] Scanning DNS for: {target}")
    print("[*] This will enumerate subdomains and DNS records...")

    dns_cam.start(target)
    results = dns_cam.scan(target)
    dns_cam.stop()

    # Display results
    print(f"\n[+] Found {len(results['subdomains'])} subdomains:")
    for subdomain in results["subdomains"][:5]:  # Show first 5
        print(f"    - {subdomain}")

    print("\n[+] Nameservers:")
    for ns in results["nameservers"]:
        print(f"    - {ns}")

    print(f"\n[+] DNS Records for {target}:")
    for record_type, values in results["dns_records"].get(target, {}).items():
        print(f"    {record_type}: {', '.join(values[:3])}")  # Show first 3

    if results.get("zone_transfer", {}).get("successful"):
        print("\n[!] WARNING: Zone transfer successful! (Security issue)")

    # Display discoveries
    discoveries = dns_cam.get_discoveries()
    print(f"\n[+] Total discoveries: {len(discoveries)}")
    print(f"[+] Statistics: {dns_cam.get_statistics()}")


def example_ssl_scanner():
    """Example: SSL X-ray Vision"""
    print("\n" + "=" * 60)
    print("🕳️ SSL SCANNER - X-ray Vision Example")
    print("=" * 60)

    # Create SSL scanner
    ssl_cam = SSLScanner(config={"ports": [443], "check_vulnerabilities": True})

    # Scan a well-known site
    target = "example.com"
    print(f"\n[*] Analyzing SSL/TLS on: {target}")
    print("[*] Checking certificates and vulnerabilities...")

    ssl_cam.start(target)
    results = ssl_cam.scan(target)
    ssl_cam.stop()

    # Display results
    if results["certificates"]:
        for port, cert_info in results["certificates"].items():
            print(f"\n[+] Certificate on port {port}:")
            print(f"    Subject: {cert_info['subject']}")
            print(f"    Issuer: {cert_info['issuer']}")
            print(f"    Valid: {cert_info['not_before']} to {cert_info['not_after']}")
            print(f"    Protocol: {cert_info['protocol_version']}")
            print(f"    Cipher: {cert_info['cipher']['name']}")

    # Display vulnerabilities
    if results["vulnerabilities"]:
        print(f"\n[!] Found {len(results['vulnerabilities'])} vulnerabilities:")
        for vuln in results["vulnerabilities"]:
            print(f"    [{vuln['severity']}] {vuln['type']}: {vuln['description']}")
    else:
        print("\n[+] No vulnerabilities detected!")

    print(f"\n[+] Summary: {results['summary']}")


def example_waf_detector():
    """Example: WAF Mask Detection"""
    print("\n" + "=" * 60)
    print("🎭 WAF DETECTOR - Mask Detection Example")
    print("=" * 60)

    # Create WAF detector
    waf_cam = WAFDetector(config={"test_payloads": True})

    # Test popular sites (many use WAFs)
    targets = [
        "https://example.com",
    ]

    for target in targets:
        print(f"\n[*] Detecting WAF on: {target}")

        waf_cam.start(target)
        results = waf_cam.scan(target)
        waf_cam.stop()

        if results.get("waf_detected"):
            print(f"[!] WAF DETECTED: {results['waf_name']}")
            print(f"    Confidence: {results['confidence']:.0%}")
            print(f"    Evidence: {', '.join(results['evidence'][:3])}")
        else:
            print("[+] No WAF detected")


def example_camera_manager():
    """Example: Using Camera Manager"""
    print("\n" + "=" * 60)
    print("📷 CAMERA MANAGER - Orchestration Example")
    print("=" * 60)

    # Create manager
    manager = CameraManager()

    # Create and register cameras
    dns_cam = DNSEnumerator()
    ssl_cam = SSLScanner()
    waf_cam = WAFDetector()

    manager.register_camera(dns_cam)
    manager.register_camera(ssl_cam)
    manager.register_camera(waf_cam)

    print(f"\n[*] Registered {len(manager.cameras)} cameras")

    # Get status
    status = manager.get_status_all()
    print("\n[*] Camera Status:")
    for name, stat in status.items():
        print(f"    {name}: {stat['status']} (mode: {stat['mode']})")

    # Scan with specific camera
    target = "example.com"
    print(f"\n[*] Scanning {target} with DNSEnumerator...")

    result = manager.scan_with_camera("DNSEnumerator", target)
    if result:
        print(f"[+] Found {len(result['subdomains'])} subdomains")

    # Get all discoveries
    all_discoveries = manager.get_all_discoveries()
    print(f"\n[+] Total discoveries across all cameras: {len(all_discoveries)}")

    # Get statistics
    stats = manager.get_statistics()
    print("\n[+] Statistics:")
    print(f"    Total cameras: {stats['total_cameras']}")
    print(f"    Total discoveries: {stats['total_discoveries']}")
    print(f"    By severity: {stats['by_severity']}")


def example_shodan_eye():
    """Example: Shodan Night Vision (requires API key)"""
    print("\n" + "=" * 60)
    print("🌙 SHODAN EYE - Night Vision Example")
    print("=" * 60)

    # Check if API key is available
    api_key = os.getenv("SHODAN_API_KEY")
    if not api_key:
        print("\n[!] SHODAN_API_KEY not set. Skipping Shodan example.")
        print("[i] To use Shodan Eye, set your API key:")
        print("    export SHODAN_API_KEY='your_key'")
        return

    # Create Shodan camera
    shodan_cam = ShodanEye(config={"api_key": api_key})

    # Search for Apache servers (example query)
    query = "apache"
    print(f"\n[*] Searching Shodan for: {query}")
    print("[*] This will show publicly exposed Apache servers...")

    shodan_cam.start(query)
    results = shodan_cam.scan(query)
    shodan_cam.stop()

    if "error" in results:
        print(f"[!] Error: {results['error']}")
        return

    # Display results
    print(f"\n[+] Found {results['total_results']} results")

    if results["search_results"]:
        print("\n[+] Sample results:")
        for i, result in enumerate(results["search_results"][:3], 1):
            print(f"\n    Result {i}:")
            print(f"    IP: {result['ip']}")
            print(f"    Port: {result['port']}")
            print(f"    Organization: {result['organization']}")
            print(f"    Country: {result['country']}")


def main():
    """Main example runner"""
    print_banner()

    print("This example demonstrates the Cameras module (Fala 2)")
    print("Cameras provide 'IR Night Vision' for deep/dark discovery")
    print("\nNote: Some cameras require API keys or system tools")
    print("      All scans use safe, public test domains\n")

    try:
        # Run examples
        example_dns_enumeration()
        time.sleep(1)

        example_ssl_scanner()
        time.sleep(1)

        example_waf_detector()
        time.sleep(1)

        example_camera_manager()
        time.sleep(1)

        # Optional: Shodan example (requires API key)
        example_shodan_eye()

    except KeyboardInterrupt:
        print("\n\n[*] Interrupted by user")
    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)
    print("\nFor more information, see cameras/README.md")


if __name__ == "__main__":
    main()
