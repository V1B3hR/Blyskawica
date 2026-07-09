"""
Integration API - Common API for Nethical tool ecosystem

Provides standardized endpoints for integrating with other Nethical tools.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


class ToolType(str, Enum):
    """Types of Nethical tools"""

    RECON = "recon"
    SCANNER = "scanner"
    EXPLOIT = "exploit"
    REPORTING = "reporting"
    THREAT_INTEL = "threat_intel"
    FORENSICS = "forensics"


class IntegrationStatus(str, Enum):
    """Status of tool integration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"


@dataclass
class ToolIntegration:
    """Integration with another Nethical tool"""

    tool_id: str
    tool_name: str
    tool_type: ToolType
    api_url: str
    api_key: Optional[str] = None
    status: IntegrationStatus = IntegrationStatus.PENDING
    version: str = "1.0"
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AssetRequest(BaseModel):
    """Request for asset information"""

    asset_id: Optional[str] = None
    asset_value: Optional[str] = None
    asset_type: Optional[str] = None


class AssetResponse(BaseModel):
    """Response with asset information"""

    asset_id: str
    asset_value: str
    asset_type: str
    risk_score: float = Field(..., ge=0, le=100)
    findings_count: int = 0
    last_scan: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ScanRequest(BaseModel):
    """Request to initiate scan"""

    target: str
    scan_type: str = "comprehensive"
    priority: str = "normal"
    callback_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ScanResponse(BaseModel):
    """Response with scan status"""

    scan_id: str
    status: str
    message: str
    estimated_completion: Optional[datetime] = None


class IntegrationAPI:
    """
    Common API for Nethical tool integrations.

    Provides standardized endpoints for cross-tool communication.
    """

    def __init__(self):
        self.router = APIRouter(prefix="/api/integration", tags=["integration"])
        self.integrations: Dict[str, ToolIntegration] = {}
        self._register_routes()

    def register_tool(self, integration: ToolIntegration):
        """Register new tool integration"""
        self.integrations[integration.tool_id] = integration

    def unregister_tool(self, tool_id: str):
        """Unregister tool integration"""
        self.integrations.pop(tool_id, None)

    def get_integration(self, tool_id: str) -> Optional[ToolIntegration]:
        """Get tool integration by ID"""
        return self.integrations.get(tool_id)

    def _register_routes(self):
        """Register API routes"""

        @self.router.get("/tools", response_model=List[Dict[str, Any]])
        async def list_integrated_tools():
            """List all integrated Nethical tools"""
            return [
                {
                    "tool_id": t.tool_id,
                    "tool_name": t.tool_name,
                    "tool_type": t.tool_type.value,
                    "status": t.status.value,
                    "version": t.version,
                    "capabilities": t.capabilities,
                }
                for t in self.integrations.values()
            ]

        @self.router.post("/tools/register")
        async def register_tool(
            tool_id: str,
            tool_name: str,
            tool_type: ToolType,
            api_url: str,
            api_key: Optional[str] = None,
            capabilities: List[str] = [],
        ):
            """Register new Nethical tool"""
            integration = ToolIntegration(
                tool_id=tool_id,
                tool_name=tool_name,
                tool_type=tool_type,
                api_url=api_url,
                api_key=api_key,
                capabilities=capabilities,
                status=IntegrationStatus.ACTIVE,
            )
            self.register_tool(integration)
            return {"status": "registered", "tool_id": tool_id}

        @self.router.get("/assets/{asset_id}", response_model=AssetResponse)
        async def get_asset_info(asset_id: str):
            """Get asset information for cross-tool sharing"""
            # Placeholder - would query asset database
            return AssetResponse(
                asset_id=asset_id,
                asset_value="example.com",
                asset_type="domain",
                risk_score=65.0,
                findings_count=5,
                last_scan=datetime.now(timezone.utc),
                metadata={"source": "nethical-recon"},
            )

        @self.router.post("/scans/request", response_model=ScanResponse)
        async def request_scan(request: ScanRequest):
            """Request scan from another tool"""
            # Placeholder - would initiate scan and return ID
            scan_id = "scan-" + str(UUID.__new__(UUID).hex[:8])
            return ScanResponse(
                scan_id=scan_id,
                status="queued",
                message="Scan request received",
                estimated_completion=datetime.now(timezone.utc),
            )

        @self.router.get("/health")
        async def health_check():
            """Health check for integration API"""
            return {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "integrations_count": len(self.integrations),
            }

    def get_router(self) -> APIRouter:
        """Get configured router"""
        return self.router
