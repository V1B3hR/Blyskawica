"""Banner grabbing module for service identification."""

from __future__ import annotations

import socket
import ssl
from dataclasses import dataclass
from typing import Optional


@dataclass
class BannerResult:
    """Result from banner grabbing."""

    host: str
    port: int
    banner: Optional[str] = None
    service: Optional[str] = None
    error: Optional[str] = None
    ssl_enabled: bool = False


class BannerGrabber:
    """Banner grabber for service identification."""

    def __init__(self, timeout: int = 5):
        """Initialize banner grabber.

        Args:
            timeout: Socket timeout in seconds
        """
        self.timeout = timeout

    def grab_banner(self, host: str, port: int, use_ssl: bool = False) -> BannerResult:
        """Grab banner from a service.

        Args:
            host: Target host
            port: Target port
            use_ssl: Use SSL/TLS connection

        Returns:
            BannerResult object
        """
        result = BannerResult(host=host, port=port, ssl_enabled=use_ssl)

        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)

            # Wrap with SSL if requested
            if use_ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=host)

            # Connect
            sock.connect((host, port))

            # Try to receive banner
            try:
                banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
                if banner:
                    result.banner = banner
                    result.service = self._identify_service(banner, port)
            except socket.timeout:
                # Some services don't send banner immediately, try sending a probe
                probe = self._get_probe(port)
                if probe:
                    sock.send(probe.encode("utf-8"))
                    try:
                        banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
                        if banner:
                            result.banner = banner
                            result.service = self._identify_service(banner, port)
                    except:
                        pass

            sock.close()

        except socket.timeout:
            result.error = "Connection timeout"
        except ConnectionRefusedError:
            result.error = "Connection refused"
        except Exception as e:
            result.error = f"Error: {str(e)}"

        return result

    def grab_multiple(self, host: str, ports: list[int], auto_detect_ssl: bool = True) -> list[BannerResult]:
        """Grab banners from multiple ports.

        Args:
            host: Target host
            ports: List of ports
            auto_detect_ssl: Automatically try SSL for common SSL ports

        Returns:
            List of BannerResult objects
        """
        results = []
        ssl_ports = {443, 8443, 465, 993, 995, 636, 989, 990, 992, 5061}

        for port in ports:
            use_ssl = auto_detect_ssl and port in ssl_ports
            result = self.grab_banner(host, port, use_ssl)
            results.append(result)

        return results

    def _get_probe(self, port: int) -> Optional[str]:
        """Get service-specific probe string.

        Args:
            port: Port number

        Returns:
            Probe string or None
        """
        probes = {
            80: "GET / HTTP/1.0\r\n\r\n",
            443: "GET / HTTP/1.0\r\n\r\n",
            8080: "GET / HTTP/1.0\r\n\r\n",
            21: "USER anonymous\r\n",
            25: "EHLO test\r\n",
            110: "USER test\r\n",
            143: "A001 CAPABILITY\r\n",
        }
        return probes.get(port)

    def _identify_service(self, banner: str, port: int) -> Optional[str]:
        """Identify service from banner.

        Args:
            banner: Banner string
            port: Port number

        Returns:
            Service name or None
        """
        banner_lower = banner.lower()

        # HTTP servers
        if "http" in banner_lower or port in [80, 443, 8080, 8443]:
            if "apache" in banner_lower:
                return "Apache HTTP Server"
            elif "nginx" in banner_lower:
                return "Nginx"
            elif "microsoft-iis" in banner_lower or "iis" in banner_lower:
                return "Microsoft IIS"
            elif "http" in banner_lower:
                return "HTTP Server"

        # SSH
        if "ssh" in banner_lower or port == 22:
            if "openssh" in banner_lower:
                return "OpenSSH"
            return "SSH Server"

        # FTP
        if "ftp" in banner_lower or port == 21:
            if "vsftpd" in banner_lower:
                return "vsftpd"
            elif "filezilla" in banner_lower:
                return "FileZilla FTP Server"
            return "FTP Server"

        # SMTP
        if "smtp" in banner_lower or port in [25, 465, 587]:
            if "postfix" in banner_lower:
                return "Postfix"
            elif "exim" in banner_lower:
                return "Exim"
            return "SMTP Server"

        # Database services
        if "mysql" in banner_lower or port == 3306:
            return "MySQL"
        if "postgresql" in banner_lower or port == 5432:
            return "PostgreSQL"
        if "mongodb" in banner_lower or port == 27017:
            return "MongoDB"

        # SMB
        if port == 445:
            return "SMB/CIFS"

        # RDP
        if port == 3389:
            return "Remote Desktop Protocol"

        return None
