"""
Security Testing API Router

FastAPI router for security testing endpoints.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from nethical_recon.security_testing import (
    APISecurityTester,
    ComplianceReporter,
    WebSecurityTester,
)
from nethical_recon.security_testing.api_security import APIEndpoint
from nethical_recon.security_testing.compliance import ComplianceFramework
from nethical_recon.api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/security-testing", tags=["security-testing"])


class WebSecurityTestRequest(BaseModel):
    """Request to test web security."""

    url: str = Field(..., description="Target URL")


class APISecurityTestRequest(BaseModel):
    """Request to test API security."""

    url: str = Field(..., description="API endpoint URL")
    method: str = Field("GET", description="HTTP method")
    auth_required: bool = Field(True, description="Whether authentication is required")


class ComplianceReportRequest(BaseModel):
    """Request to generate compliance report."""

    framework: str = Field(..., description="Compliance framework (owasp_wstg, pci_dss, etc.)")
    target: str = Field(..., description="Target system")


@router.post("/web-security")
async def test_web_security(
    request: WebSecurityTestRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Test web security based on OWASP WSTG.

    Performs security header checks, information disclosure tests, and other web security tests.
    """
    logger.info(f"Web security test requested for {request.url} by user {current_user['username']}")

    try:
        tester = WebSecurityTester(timeout=10)
        results = tester.test_all(request.url)

        return {
            "target": request.url,
            "total_tests": len(results),
            "summary": tester.get_summary(results),
            "results": [
                {
                    "test_id": r.test_id,
                    "test_name": r.test_name,
                    "status": r.status.value,
                    "severity": r.severity.value,
                    "description": r.description,
                    "details": r.details,
                    "recommendations": r.recommendations,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in results
            ],
        }

    except Exception as e:
        logger.error(f"Web security test failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Security test failed: {str(e)}")


@router.post("/api-security")
async def test_api_security(
    request: APISecurityTestRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Test API security based on OWASP API Security Top 10.

    Performs authentication, authorization, and rate limiting tests.
    """
    logger.info(f"API security test requested for {request.url} by user {current_user['username']}")

    try:
        tester = APISecurityTester(timeout=10)
        endpoint = APIEndpoint(
            url=request.url,
            method=request.method,
            auth_required=request.auth_required,
        )

        results = tester.test_all(endpoint)

        return {
            "target": request.url,
            "method": request.method,
            "total_tests": len(results),
            "results": [
                {
                    "test_id": r.test_id,
                    "test_name": r.test_name,
                    "status": r.status.value,
                    "severity": r.severity.value,
                    "description": r.description,
                    "details": r.details,
                    "recommendations": r.recommendations,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in results
            ],
        }

    except Exception as e:
        logger.error(f"API security test failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"API security test failed: {str(e)}")


@router.post("/compliance-report")
async def generate_compliance_report(
    request: ComplianceReportRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Generate compliance report for specified framework.

    Supports OWASP WSTG, PCI DSS, GDPR, and other frameworks.
    """
    logger.info(
        f"Compliance report requested for {request.target} ({request.framework}) " f"by user {current_user['username']}"
    )

    try:
        reporter = ComplianceReporter()

        # Map framework string to enum
        framework_map = {
            "owasp_wstg": ComplianceFramework.OWASP_WSTG,
            "owasp_asvs": ComplianceFramework.OWASP_ASVS,
            "pci_dss": ComplianceFramework.PCI_DSS,
            "gdpr": ComplianceFramework.GDPR,
            "nist": ComplianceFramework.NIST,
            "cisa_kev": ComplianceFramework.CISA_KEV,
        }

        framework = framework_map.get(request.framework.lower())
        if not framework:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown framework: {request.framework}. " f"Supported: {', '.join(framework_map.keys())}",
            )

        # Generate appropriate report based on framework
        if framework == ComplianceFramework.OWASP_WSTG:
            # Would need actual test results
            report = reporter.generate_owasp_report(request.target, [])
        elif framework == ComplianceFramework.PCI_DSS:
            report = reporter.generate_pci_dss_report(request.target, [])
        else:
            raise HTTPException(
                status_code=501,
                detail=f"Report generation for {framework.value} not yet implemented",
            )

        return reporter.export_to_dict(report)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compliance report generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/compliance-report/{report_id}/html")
async def get_compliance_report_html(
    report_id: str,
    current_user: dict = Depends(get_current_user),
) -> str:
    """
    Get compliance report in HTML format.

    Returns an HTML document suitable for viewing or PDF conversion.
    """
    logger.info(f"HTML report requested for {report_id} by user {current_user['username']}")

    # This would load the report from storage
    raise HTTPException(
        status_code=501,
        detail="HTML report generation requires report storage implementation",
    )
