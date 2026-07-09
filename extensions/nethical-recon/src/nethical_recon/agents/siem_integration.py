"""
SIEM/SOAR Integration

Integrates with Security Information and Event Management (SIEM) and
Security Orchestration, Automation and Response (SOAR) platforms.

Supports: Elastic, Splunk, Azure Sentinel, webhooks
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

import requests


class SIEMProvider(str, Enum):
    """Supported SIEM/SOAR providers"""

    ELASTIC = "elastic"
    SPLUNK = "splunk"
    AZURE_SENTINEL = "azure_sentinel"
    WEBHOOK = "webhook"
    SYSLOG = "syslog"


@dataclass
class SIEMEvent:
    """Event to send to SIEM"""

    event_type: str
    severity: str
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "nethical-recon"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "event_type": self.event_type,
            "severity": self.severity,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            **self.metadata,
        }


@dataclass
class SIEMConfig:
    """SIEM provider configuration"""

    provider: SIEMProvider
    enabled: bool = True

    # Common settings
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    index_name: Optional[str] = None

    # Elastic-specific
    elastic_cloud_id: Optional[str] = None
    elastic_username: Optional[str] = None
    elastic_password: Optional[str] = None

    # Splunk-specific
    splunk_hec_token: Optional[str] = None
    splunk_source: Optional[str] = "nethical-recon"
    splunk_sourcetype: Optional[str] = "json"

    # Azure Sentinel-specific
    sentinel_workspace_id: Optional[str] = None
    sentinel_shared_key: Optional[str] = None
    sentinel_log_type: Optional[str] = "NethicalRecon"

    # Webhook-specific
    webhook_url: Optional[str] = None
    webhook_headers: Dict[str, str] = field(default_factory=dict)

    # Syslog-specific
    syslog_host: Optional[str] = None
    syslog_port: int = 514
    syslog_protocol: str = "udp"  # udp or tcp


class SIEMIntegration:
    """
    SIEM/SOAR integration manager.

    Sends security events, findings, and alerts to configured SIEM platforms.
    """

    def __init__(self, configs: Optional[List[SIEMConfig]] = None):
        self.configs: List[SIEMConfig] = configs or []
        self._session: Optional[requests.Session] = None

    def add_config(self, config: SIEMConfig):
        """Add SIEM configuration"""
        self.configs.append(config)

    def remove_config(self, provider: SIEMProvider):
        """Remove SIEM configuration"""
        self.configs = [c for c in self.configs if c.provider != provider]

    async def send_event(self, event: SIEMEvent) -> Dict[SIEMProvider, bool]:
        """
        Send event to all configured SIEM providers.

        Args:
            event: Event to send

        Returns:
            Dictionary mapping provider to success status
        """
        results = {}

        for config in self.configs:
            if not config.enabled:
                continue

            try:
                if config.provider == SIEMProvider.ELASTIC:
                    success = await self._send_to_elastic(event, config)
                elif config.provider == SIEMProvider.SPLUNK:
                    success = await self._send_to_splunk(event, config)
                elif config.provider == SIEMProvider.AZURE_SENTINEL:
                    success = await self._send_to_sentinel(event, config)
                elif config.provider == SIEMProvider.WEBHOOK:
                    success = await self._send_to_webhook(event, config)
                elif config.provider == SIEMProvider.SYSLOG:
                    success = await self._send_to_syslog(event, config)
                else:
                    success = False

                results[config.provider] = success

            except Exception as e:
                print(f"Error sending to {config.provider}: {e}")
                results[config.provider] = False

        return results

    async def send_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        description: str,
        target: str,
        **metadata,
    ):
        """Send finding to SIEM"""
        event = SIEMEvent(
            event_type="finding",
            severity=severity,
            message=f"Finding: {title}",
            metadata={
                "finding_id": finding_id,
                "title": title,
                "description": description,
                "target": target,
                **metadata,
            },
        )
        return await self.send_event(event)

    async def send_alert(
        self,
        alert_id: str,
        alert_type: str,
        severity: str,
        message: str,
        **metadata,
    ):
        """Send alert to SIEM"""
        event = SIEMEvent(
            event_type="alert",
            severity=severity,
            message=message,
            metadata={
                "alert_id": alert_id,
                "alert_type": alert_type,
                **metadata,
            },
        )
        return await self.send_event(event)

    async def send_scan_complete(
        self,
        scan_id: str,
        target: str,
        findings_count: int,
        duration_seconds: float,
    ):
        """Send scan completion to SIEM"""
        event = SIEMEvent(
            event_type="scan_complete",
            severity="info",
            message=f"Scan completed: {target}",
            metadata={
                "scan_id": scan_id,
                "target": target,
                "findings_count": findings_count,
                "duration_seconds": duration_seconds,
            },
        )
        return await self.send_event(event)

    async def _send_to_elastic(self, event: SIEMEvent, config: SIEMConfig) -> bool:
        """Send event to Elasticsearch"""
        if not config.api_url:
            return False

        try:
            # Prepare Elasticsearch document
            doc = event.to_dict()
            doc["@timestamp"] = event.timestamp.isoformat()

            # Index name with date rotation
            index = config.index_name or "nethical-recon"
            date_suffix = event.timestamp.strftime("%Y.%m.%d")
            full_index = f"{index}-{date_suffix}"

            # Send to Elasticsearch
            url = f"{config.api_url}/{full_index}/_doc"

            headers = {"Content-Type": "application/json"}

            auth = None
            if config.elastic_username and config.elastic_password:
                auth = (config.elastic_username, config.elastic_password)
            elif config.api_key:
                headers["Authorization"] = f"ApiKey {config.api_key}"

            response = requests.post(url, json=doc, headers=headers, auth=auth, timeout=10)
            return response.status_code in [200, 201]

        except Exception as e:
            print(f"Elastic error: {e}")
            return False

    async def _send_to_splunk(self, event: SIEMEvent, config: SIEMConfig) -> bool:
        """Send event to Splunk via HEC"""
        if not config.api_url or not config.splunk_hec_token:
            return False

        try:
            # Prepare Splunk HEC event
            splunk_event = {
                "time": event.timestamp.timestamp(),
                "source": config.splunk_source,
                "sourcetype": config.splunk_sourcetype,
                "event": event.to_dict(),
            }

            if config.index_name:
                splunk_event["index"] = config.index_name

            # Send to Splunk HEC
            url = f"{config.api_url}/services/collector/event"
            headers = {"Authorization": f"Splunk {config.splunk_hec_token}"}

            response = requests.post(url, json=splunk_event, headers=headers, timeout=10, verify=False)
            return response.status_code == 200

        except Exception as e:
            print(f"Splunk error: {e}")
            return False

    async def _send_to_sentinel(self, event: SIEMEvent, config: SIEMConfig) -> bool:
        """Send event to Azure Sentinel"""
        if not config.sentinel_workspace_id or not config.sentinel_shared_key:
            return False

        try:
            import base64
            import hashlib
            import hmac

            # Prepare Azure Sentinel event
            body = json.dumps([event.to_dict()])
            content_length = len(body)

            # Build signature
            method = "POST"
            content_type = "application/json"
            date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
            resource = "/api/logs"

            string_to_sign = f"{method}\n{content_length}\n{content_type}\nx-ms-date:{date}\n{resource}"

            bytes_to_hash = string_to_sign.encode("utf-8")
            decoded_key = base64.b64decode(config.sentinel_shared_key)
            encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest())
            signature = encoded_hash.decode("utf-8")

            # Send to Azure Sentinel
            url = f"https://{config.sentinel_workspace_id}.ods.opinsights.azure.com{resource}?api-version=2016-04-01"

            headers = {
                "Content-Type": content_type,
                "Log-Type": config.sentinel_log_type,
                "x-ms-date": date,
                "Authorization": f"SharedKey {config.sentinel_workspace_id}:{signature}",
            }

            response = requests.post(url, data=body, headers=headers, timeout=10)
            return response.status_code == 200

        except Exception as e:
            print(f"Sentinel error: {e}")
            return False

    async def _send_to_webhook(self, event: SIEMEvent, config: SIEMConfig) -> bool:
        """Send event to webhook"""
        if not config.webhook_url:
            return False

        try:
            headers = {"Content-Type": "application/json", **config.webhook_headers}

            response = requests.post(config.webhook_url, json=event.to_dict(), headers=headers, timeout=10)
            return response.status_code in [200, 201, 202, 204]

        except Exception as e:
            print(f"Webhook error: {e}")
            return False

    async def _send_to_syslog(self, event: SIEMEvent, config: SIEMConfig) -> bool:
        """Send event to syslog"""
        if not config.syslog_host:
            return False

        try:
            import socket

            # Build syslog message (RFC 5424 format)
            severity_map = {
                "critical": 2,
                "high": 3,
                "medium": 4,
                "low": 6,
                "info": 6,
            }
            severity = severity_map.get(event.severity, 6)
            facility = 16  # Local0

            priority = facility * 8 + severity

            timestamp = event.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            hostname = socket.gethostname()

            message = json.dumps(event.to_dict())
            syslog_msg = f"<{priority}>1 {timestamp} {hostname} nethical-recon - - - {message}\n"

            # Send via UDP or TCP
            if config.syslog_protocol == "udp":
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(syslog_msg.encode("utf-8"), (config.syslog_host, config.syslog_port))
                sock.close()
            else:  # TCP
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((config.syslog_host, config.syslog_port))
                sock.send(syslog_msg.encode("utf-8"))
                sock.close()

            return True

        except Exception as e:
            print(f"Syslog error: {e}")
            return False
