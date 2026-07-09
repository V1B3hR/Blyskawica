"""
Active Reconnaissance API Router

FastAPI router for active scanning endpoints.
"""

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from nethical_recon.active_recon import ActiveScanner, BannerGrabber, TLSFingerprinter
from nethical_recon.api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/active-recon", tags=["active-reconnaissance"])


class ScanRequest(BaseModel):
    """Request to perform active scan."""

    target: str = Field(..., description="Target host or network")
    profile: str = Field("standard", description="Scan profile (quick, standard, comprehensive, stealth, aggressive)")
    ports: Optional[str] = Field(None, description="Port specification (e.g., '80,443,1-1000')")


class BannerRequest(BaseModel):
    """Request to grab service banners."""

    host: str = Field(..., description="Target host")
    ports: list[int] = Field(..., description="List of ports to probe")


class TLSRequest(BaseModel):
    """Request to fingerprint TLS."""

    host: str = Field(..., description="Target host")
    port: int = Field(443, description="Target port")


@router.post("/scan")
async def active_scan(
    request: ScanRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Perform active port scan using Nmap.

    Requires Nmap to be installed on the system.
    """
    logger.info(f"Active scan requested for {request.target} by user {current_user['username']}")

    try:
        scanner = ActiveScanner()

        if not scanner.is_available():
            raise HTTPException(
                status_code=503,
                detail="Nmap is not installed or not available",
            )

        # Convert profile string to enum
        from nethical_recon.active_recon.scanner import ScanProfile

        profile_map = {
            "quick": ScanProfile.QUICK,
            "standard": ScanProfile.STANDARD,
            "comprehensive": ScanProfile.COMPREHENSIVE,
            "stealth": ScanProfile.STEALTH,
            "aggressive": ScanProfile.AGGRESSIVE,
        }
        profile = profile_map.get(request.profile.lower(), ScanProfile.STANDARD)

        result = scanner.scan(request.target, profile, request.ports)

        if result.error:
            raise HTTPException(status_code=500, detail=result.error)

        return {
            "scan_id": result.scan_id,
            "target": result.target,
            "profile": result.profile.value,
            "started_at": result.started_at.isoformat(),
            "completed_at": result.completed_at.isoformat() if result.completed_at else None,
            "ports": [
                {
                    "port": p.port,
                    "protocol": p.protocol,
                    "state": p.state,
                    "service": p.service,
                    "version": p.version,
                }
                for p in result.ports
            ],
            "findings": len(result.findings),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Active scan failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/banner-grab")
async def grab_banners(
    request: BannerRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Grab service banners from specified ports.
    """
    logger.info(f"Banner grab requested for {request.host} by user {current_user['username']}")

    try:
        grabber = BannerGrabber(timeout=5)
        results = grabber.grab_multiple(request.host, request.ports)

        return {
            "host": request.host,
            "results": [
                {
                    "port": r.port,
                    "banner": r.banner,
                    "service": r.service,
                    "ssl_enabled": r.ssl_enabled,
                    "error": r.error,
                }
                for r in results
            ],
        }

    except Exception as e:
        logger.error(f"Banner grab failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Banner grab failed: {str(e)}")


@router.post("/tls-fingerprint")
async def tls_fingerprint(
    request: TLSRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Fingerprint TLS/SSL connection.
    """
    logger.info(f"TLS fingerprint requested for {request.host}:{request.port} by user {current_user['username']}")

    try:
        fingerprinter = TLSFingerprinter(timeout=5)
        result = fingerprinter.fingerprint(request.host, request.port)

        if result.error:
            raise HTTPException(status_code=500, detail=result.error)

        # Check for vulnerabilities
        vulnerabilities = fingerprinter.check_vulnerabilities(result)

        return {
            "host": result.host,
            "port": result.port,
            "protocol_version": result.protocol_version,
            "cipher_suite": result.cipher_suite,
            "certificate": {
                "subject": result.certificate_subject,
                "issuer": result.certificate_issuer,
                "serial": result.certificate_serial,
                "not_before": result.certificate_not_before,
                "not_after": result.certificate_not_after,
                "san": result.san_list,
            },
            "ja3_hash": result.ja3_hash,
            "vulnerabilities": vulnerabilities,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TLS fingerprint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"TLS fingerprint failed: {str(e)}")
