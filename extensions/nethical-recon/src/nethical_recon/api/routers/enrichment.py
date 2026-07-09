"""
Enrichment API Router

FastAPI router for threat intelligence enrichment endpoints.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from nethical_recon.enrichment import (
    ThreatEnricher,
    AbuseIPDBProvider,
    OTXProvider,
    GreyNoiseProvider,
    VirusTotalProvider,
    RiskScorer,
)
from nethical_recon.api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/enrichment", tags=["enrichment"])


class EnrichRequest(BaseModel):
    """Request to enrich an indicator."""

    indicator: str = Field(..., description="Indicator to enrich (IP, domain, etc.)")
    indicator_type: str = Field(..., description="Type of indicator (ip, domain, url, hash)")
    providers: list[str] | None = Field(None, description="Specific providers to use (optional)")


class BatchEnrichRequest(BaseModel):
    """Request to enrich multiple indicators."""

    indicators: list[dict[str, str]] = Field(..., description="List of {indicator, indicator_type} dicts")


class EnrichmentResponse(BaseModel):
    """Enrichment result response."""

    indicator: str
    indicator_type: str
    enriched: bool
    sources: list[str]
    threat_level: str
    confidence: float
    tags: list[str]
    metadata: dict[str, Any]


class RiskScoreRequest(BaseModel):
    """Request to calculate risk score."""

    asset: dict[str, Any] = Field(..., description="Asset data")
    enrichment_data: dict[str, Any] | None = Field(None, description="Optional enrichment data")


class RiskScoreResponse(BaseModel):
    """Risk score response."""

    asset_id: str
    asset_type: str
    overall_score: float
    risk_level: str
    factors: list[dict[str, Any]]
    recommendations: list[str]


@router.post("/enrich", response_model=EnrichmentResponse)
async def enrich_indicator(
    request: EnrichRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Enrich an indicator with threat intelligence.

    Queries multiple threat intelligence sources and aggregates results.
    """
    logger.info(f"Enriching {request.indicator_type}: {request.indicator} by user {current_user['username']}")

    try:
        enricher = ThreatEnricher()

        # Add providers (would use API keys from config in production)
        if not request.providers or "abuseipdb" in request.providers:
            enricher.add_provider(AbuseIPDBProvider())
        if not request.providers or "otx" in request.providers:
            enricher.add_provider(OTXProvider())
        if not request.providers or "greynoise" in request.providers:
            enricher.add_provider(GreyNoiseProvider())
        if not request.providers or "virustotal" in request.providers:
            enricher.add_provider(VirusTotalProvider())

        result = enricher.enrich(request.indicator, request.indicator_type)

        return {
            "indicator": result.indicator,
            "indicator_type": result.indicator_type,
            "enriched": result.enriched,
            "sources": result.sources,
            "threat_level": result.aggregated_threat_level,
            "confidence": result.aggregated_confidence,
            "tags": result.tags,
            "metadata": result.metadata,
        }
    except Exception as e:
        logger.error(f"Failed to enrich indicator: {e}")
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")


@router.post("/enrich/batch")
async def enrich_batch(
    request: BatchEnrichRequest,
    current_user: dict = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """
    Enrich multiple indicators in batch.

    More efficient than individual requests for large sets of indicators.
    """
    logger.info(f"Batch enriching {len(request.indicators)} indicators")

    try:
        enricher = ThreatEnricher()

        # Add all providers
        enricher.add_provider(AbuseIPDBProvider())
        enricher.add_provider(OTXProvider())
        enricher.add_provider(GreyNoiseProvider())
        enricher.add_provider(VirusTotalProvider())

        indicators = [(i["indicator"], i["indicator_type"]) for i in request.indicators]
        results = enricher.enrich_batch(indicators)

        return [
            {
                "indicator": r.indicator,
                "indicator_type": r.indicator_type,
                "enriched": r.enriched,
                "sources": r.sources,
                "threat_level": r.aggregated_threat_level,
                "confidence": r.aggregated_confidence,
                "tags": r.tags,
            }
            for r in results
        ]
    except Exception as e:
        logger.error(f"Failed to batch enrich: {e}")
        raise HTTPException(status_code=500, detail=f"Batch enrichment failed: {str(e)}")


@router.post("/risk-score", response_model=RiskScoreResponse)
async def calculate_risk_score(
    request: RiskScoreRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Calculate risk score for an asset.

    Considers threat intelligence, exposure, configuration, and other factors.
    """
    logger.info(f"Calculating risk score for asset {request.asset.get('asset_id')}")

    try:
        scorer = RiskScorer()
        risk_score = scorer.score_asset(request.asset, request.enrichment_data)

        return {
            "asset_id": risk_score.asset_id,
            "asset_type": risk_score.asset_type,
            "overall_score": risk_score.overall_score,
            "risk_level": risk_score.risk_level,
            "factors": [
                {
                    "name": f.name,
                    "category": f.category,
                    "score": f.score,
                    "weight": f.weight,
                    "description": f.description,
                    "evidence": f.evidence,
                }
                for f in risk_score.factors
            ],
            "recommendations": risk_score.recommendations,
        }
    except Exception as e:
        logger.error(f"Failed to calculate risk score: {e}")
        raise HTTPException(status_code=500, detail=f"Risk scoring failed: {str(e)}")


@router.get("/providers")
async def list_providers(
    current_user: dict = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """
    List available threat intelligence providers.

    Returns information about configured providers and their capabilities.
    """
    logger.info("Listing threat intelligence providers")

    providers = [
        {
            "name": "AbuseIPDB",
            "supported_indicators": ["ip"],
            "description": "IP reputation and abuse reports",
            "status": "available",
        },
        {
            "name": "AlienVault OTX",
            "supported_indicators": ["ip", "domain", "url", "hash"],
            "description": "Open Threat Exchange",
            "status": "available",
        },
        {
            "name": "GreyNoise",
            "supported_indicators": ["ip"],
            "description": "Internet scanner classification",
            "status": "available",
        },
        {
            "name": "VirusTotal",
            "supported_indicators": ["ip", "domain", "url", "hash"],
            "description": "Multi-scanner threat intelligence",
            "status": "available",
        },
    ]

    return providers
