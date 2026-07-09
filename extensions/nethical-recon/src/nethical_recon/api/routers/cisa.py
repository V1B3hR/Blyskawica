"""
CISA API Router

FastAPI router for CISA integration endpoints including KEV, alerts,
policy modes, compliance reports, and BOD compliance.
"""

import logging
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from nethical_recon.compliance import (
    CISAKEVClient,
    CISAAlertFeedClient,
    CISAShieldsUpMonitor,
    CISAPolicyMode,
)
from nethical_recon.compliance.cisa_policy import CISAPolicyManager
from nethical_recon.compliance.cisa_reporting import CISAComplianceReporter
from nethical_recon.compliance.cisa_mapping import CISACategoryMapper
from nethical_recon.compliance.cisa_attack_surface import CISAAttackSurfaceMonitor
from nethical_recon.plugins import CISABODChecker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/cisa", tags=["cisa"])


# Initialize CISA components
kev_client = CISAKEVClient()
alert_client = CISAAlertFeedClient()
shields_up_monitor = CISAShieldsUpMonitor()
policy_manager = CISAPolicyManager()
compliance_reporter = CISAComplianceReporter()
category_mapper = CISACategoryMapper()
attack_surface_monitor = CISAAttackSurfaceMonitor()
bod_checker = CISABODChecker(kev_client=kev_client)


# Request/Response Models


class KEVCheckRequest(BaseModel):
    """Request to check if CVEs are in KEV catalog."""

    cve_ids: list[str] = Field(..., description="List of CVE IDs to check")


class KEVStatusResponse(BaseModel):
    """KEV status response."""

    cve_id: str
    is_kev: bool
    kev_metadata: Optional[dict[str, Any]] = None


class PolicyModeRequest(BaseModel):
    """Request to apply CISA policy mode."""

    mode: str = Field(
        ..., description="Policy mode: critical_infrastructure, federal_agency, enterprise, small_business"
    )


class ComplianceReportRequest(BaseModel):
    """Request to generate compliance report."""

    organization: str = Field(..., description="Organization name")
    policy_mode: str = Field(..., description="CISA policy mode")
    kev_vulnerabilities: list[dict[str, Any]] = Field(default_factory=list)
    active_alerts: list[dict[str, Any]] = Field(default_factory=list)
    compliance_data: dict[str, Any] = Field(default_factory=dict)


class BODCheckRequest(BaseModel):
    """Request for BOD compliance check."""

    directive: str = Field(..., description="BOD directive: bod_22_01, bod_23_01, bod_18_01, all")
    vulnerabilities: list[dict[str, Any]] = Field(default_factory=list)
    assets: list[dict[str, Any]] = Field(default_factory=list)
    scan_coverage: float = Field(default=0.0, ge=0, le=100)
    email_config: dict[str, Any] = Field(default_factory=dict)
    web_config: dict[str, Any] = Field(default_factory=dict)


# KEV Endpoints


@router.get("/kev/statistics")
async def get_kev_statistics():
    """Get CISA KEV catalog statistics."""
    try:
        stats = kev_client.get_statistics()
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"Failed to get KEV statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kev/check")
async def check_kev_status(request: KEVCheckRequest):
    """Check if CVEs are in CISA KEV catalog."""
    try:
        results = []
        for cve_id in request.cve_ids:
            is_kev = kev_client.is_kev(cve_id)
            kev_metadata = kev_client.get_kev_metadata(cve_id) if is_kev else None

            results.append(KEVStatusResponse(cve_id=cve_id, is_kev=is_kev, kev_metadata=kev_metadata))

        return {"success": True, "data": results}
    except Exception as e:
        logger.error(f"Failed to check KEV status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kev/vulnerabilities")
async def list_kev_vulnerabilities(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
):
    """List all vulnerabilities in CISA KEV catalog."""
    try:
        entries = kev_client.get_all_kev_entries()
        limited_entries = entries[:limit]

        return {
            "success": True,
            "data": {
                "total": len(entries),
                "returned": len(limited_entries),
                "vulnerabilities": [
                    {
                        "cve_id": e.cve_id,
                        "vendor_project": e.vendor_project,
                        "product": e.product,
                        "vulnerability_name": e.vulnerability_name,
                        "date_added": e.date_added,
                        "required_action": e.required_action,
                        "due_date": e.due_date,
                    }
                    for e in limited_entries
                ],
            },
        }
    except Exception as e:
        logger.error(f"Failed to list KEV vulnerabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kev/update")
async def update_kev_catalog(force: bool = Query(False, description="Force update even if cache is fresh")):
    """Update CISA KEV catalog cache."""
    try:
        success = kev_client.update_cache(force=force)
        if success:
            return {"success": True, "message": "KEV catalog updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update KEV catalog")
    except Exception as e:
        logger.error(f"Failed to update KEV catalog: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Shields Up Endpoints


@router.get("/shields-up/status")
async def get_shields_up_status():
    """Get current CISA Shields Up status."""
    try:
        status = shields_up_monitor.get_current_status()
        return {"success": True, "data": status}
    except Exception as e:
        logger.error(f"Failed to get Shields Up status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/recent")
async def get_recent_alerts(days: int = Query(30, ge=1, le=365)):
    """Get recent CISA alerts."""
    try:
        alerts = alert_client.fetch_recent_alerts(days=days)
        return {
            "success": True,
            "data": {
                "days": days,
                "count": len(alerts),
                "alerts": alerts,
            },
        }
    except Exception as e:
        logger.error(f"Failed to fetch recent alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Policy Mode Endpoints


@router.get("/policy/modes")
async def list_policy_modes():
    """List available CISA policy modes."""
    try:
        modes = [
            {
                "mode": mode.value,
                "profile": {
                    "name": policy_manager.get_profile(mode).name,
                    "description": policy_manager.get_profile(mode).description,
                    "scan_frequency_days": policy_manager.get_profile(mode).scan_frequency_days,
                },
            }
            for mode in CISAPolicyMode
        ]

        return {"success": True, "data": modes}
    except Exception as e:
        logger.error(f"Failed to list policy modes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/policy/apply")
async def apply_policy_mode(request: PolicyModeRequest):
    """Apply CISA policy mode."""
    try:
        mode = CISAPolicyMode(request.mode)
        config = policy_manager.apply_profile(mode)
        return {"success": True, "data": config}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid policy mode: {request.mode}")
    except Exception as e:
        logger.error(f"Failed to apply policy mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policy/current")
async def get_current_policy():
    """Get currently active policy mode."""
    try:
        mode = policy_manager.get_current_mode()
        profile = policy_manager.get_profile(mode)

        return {
            "success": True,
            "data": {
                "mode": mode.value,
                "profile": {
                    "name": profile.name,
                    "description": profile.description,
                    "scan_frequency_days": profile.scan_frequency_days,
                    "required_tests": profile.required_tests,
                    "compliance_requirements": profile.compliance_requirements,
                },
            },
        }
    except Exception as e:
        logger.error(f"Failed to get current policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Compliance Report Endpoints


@router.post("/reports/generate")
async def generate_compliance_report(request: ComplianceReportRequest):
    """Generate CISA compliance report."""
    try:
        report = compliance_reporter.generate_report(
            organization=request.organization,
            policy_mode=request.policy_mode,
            kev_vulnerabilities=request.kev_vulnerabilities,
            active_alerts=request.active_alerts,
            compliance_data=request.compliance_data,
        )

        return {
            "success": True,
            "data": {
                "report_id": str(report.report_id),
                "generated_at": report.generated_at.isoformat(),
                "executive_summary": report.executive_summary,
            },
        }
    except Exception as e:
        logger.error(f"Failed to generate compliance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_id}")
async def get_compliance_report(report_id: UUID, format: str = Query("json", regex="^(json|html)$")):
    """Get compliance report by ID."""
    try:
        report = compliance_reporter.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        if format == "html":
            html_content = compliance_reporter.render_html(report)
            return {"success": True, "format": "html", "content": html_content}
        else:
            json_content = compliance_reporter.render_json(report)
            return {"success": True, "format": "json", "data": json_content}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get compliance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Coverage and Mapping Endpoints


@router.get("/coverage")
async def get_cisa_coverage():
    """Get CISA monitoring coverage report."""
    try:
        coverage = category_mapper.get_coverage_report()
        return {"success": True, "data": coverage}
    except Exception as e:
        logger.error(f"Failed to get CISA coverage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attack-surface/coverage")
async def get_attack_surface_coverage():
    """Get CISA attack surface monitoring coverage."""
    try:
        coverage = attack_surface_monitor.get_coverage_report()
        return {"success": True, "data": coverage}
    except Exception as e:
        logger.error(f"Failed to get attack surface coverage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attack-surface/exposed")
async def get_exposed_assets_summary():
    """Get summary of exposed assets across CISA attack surface areas."""
    try:
        summary = attack_surface_monitor.get_exposed_assets_summary()
        return {"success": True, "data": summary}
    except Exception as e:
        logger.error(f"Failed to get exposed assets summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# BOD Compliance Endpoints


@router.post("/bod/check")
async def check_bod_compliance(request: BODCheckRequest):
    """Check CISA BOD compliance."""
    try:
        if request.directive == "all":
            results = bod_checker.check_all(
                vulnerabilities=request.vulnerabilities,
                assets=request.assets,
                scan_coverage=request.scan_coverage,
                email_config=request.email_config,
                web_config=request.web_config,
            )
        elif request.directive == "bod_22_01":
            results = {"bod_22_01": bod_checker.check_bod_22_01(request.vulnerabilities)}
        elif request.directive == "bod_23_01":
            results = {"bod_23_01": bod_checker.check_bod_23_01(request.assets, request.scan_coverage)}
        elif request.directive == "bod_18_01":
            results = {"bod_18_01": bod_checker.check_bod_18_01(request.email_config, request.web_config)}
        else:
            raise HTTPException(status_code=400, detail=f"Invalid BOD directive: {request.directive}")

        # Convert dataclass results to dicts
        results_dict = {}
        for key, result in results.items():
            results_dict[key] = {
                "directive": result.directive.value,
                "compliant": result.compliant,
                "compliance_percentage": result.compliance_percentage,
                "findings": result.findings,
                "recommendations": result.recommendations,
                "details": result.details,
            }

        return {"success": True, "data": results_dict}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check BOD compliance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
