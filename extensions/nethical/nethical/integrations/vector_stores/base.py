"""Base interface for vector store integrations with governance.

This module defines the abstract base class for all vector store connectors,
ensuring consistent API and integrated governance checks.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class VectorSearchResult:
    """Result from a vector search query.
    
    Attributes:
        id: Vector ID
        score: Similarity score
        vector: The vector itself (optional)
        metadata: Associated metadata
        payload: Additional payload data
    """  # noqa: W293
    id: str
    score: float
    vector: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "score": self.score,
            "vector": self.vector,
            "metadata": self.metadata,
            "payload": self.payload,
        }


class VectorStoreProvider(ABC):
    """Abstract base class for vector store providers with governance.
    
    All vector store connectors must implement this interface to ensure
    consistent behavior and integrated safety checks.
    """  # noqa: W293

    def __init__(
        self,
        enable_governance: bool = True,
        enable_pii_detection: bool = True,
        enable_audit_logging: bool = True,
    ):
        """Initialize vector store provider.
        
        Args:
            enable_governance: Enable governance checks
            enable_pii_detection: Enable PII detection and redaction
            enable_audit_logging: Enable audit logging
        """  # noqa: W293
        self.enable_governance = enable_governance
        self.enable_pii_detection = enable_pii_detection
        self.enable_audit_logging = enable_audit_logging
        self._governance = None
        self._pii_detector = None

    def _init_governance(self):
        """Lazy initialization of governance components."""
        if self.enable_governance and self._governance is None:
            try:
                from nethical.core.integrated_governance import IntegratedGovernance
                self._governance = IntegratedGovernance(
                    storage_dir="./nethical_vector_data",
                    enable_performance_optimization=True,
                )
            except ImportError as e:
                logger.warning(f"Could not initialize governance: {e}")
                self.enable_governance = False

        if self.enable_pii_detection and self._pii_detector is None:
            try:
                from nethical.utils.pii import get_pii_detector
                self._pii_detector = get_pii_detector()
            except ImportError as e:
                logger.warning(f"Could not initialize PII detector: {e}")
                self.enable_pii_detection = False

    def _check_governance(self, data: Any, operation: str = "vector_operation") -> dict[str, Any]:
        """Check data against governance policies.
        
        Args:
            data: Data to check (will be converted to string)
            operation: Operation type for auditing
            
        Returns:
            Governance check result with decision and metadata
        """  # noqa: W293
        self._init_governance()

        if not self.enable_governance or self._governance is None:
            return {
                "decision": "ALLOW",
                "reason": "Governance disabled",
                "risk_score": 0.0,
            }

        try:
            result = self._governance.process_action(
                action=str(data),
                agent_id="vector_store",
                action_type=operation,
            )
            return result
        except Exception as e:
            logger.error(f"Governance check failed: {e}")
            return {
                "decision": "ALLOW",
                "reason": f"Governance check error: {e}",
                "risk_score": 0.0,
            }

    def _detect_pii(self, data: Any) -> dict[str, Any]:
        """Detect PII in data.
        
        Args:
            data: Data to scan for PII
            
        Returns:
            PII detection result with findings and redacted text
        """  # noqa: W293
        self._init_governance()

        if not self.enable_pii_detection or self._pii_detector is None:
            return {
                "has_pii": False,
                "findings": [],
                "redacted_text": str(data),
            }

        try:
            text = str(data)
            findings = self._pii_detector.detect(text)
            redacted = self._pii_detector.redact(text) if findings else text

            return {
                "has_pii": len(findings) > 0,
                "findings": findings,
                "redacted_text": redacted,
            }
        except Exception as e:
            logger.error(f"PII detection failed: {e}")
            return {
                "has_pii": False,
                "findings": [],
                "redacted_text": str(data),
            }

    def _audit_log(self, operation: str, details: dict[str, Any]):
        """Log operation for audit trail.
        
        Args:
            operation: Operation name
            details: Operation details
        """  # noqa: W293
        if not self.enable_audit_logging:
            return

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "provider": self.__class__.__name__,
            **details,
        }
        logger.info(f"[AUDIT] {operation}: {log_entry}")

    @abstractmethod
    def upsert(
        self,
        vectors: list[dict[str, Any]],
        namespace: str = "",
    ) -> int:
        """Upsert vectors with governance checks.
        
        Args:
            vectors: List of vectors to upsert. Each dict should contain:
                - id: Vector ID
                - values: Vector values (list of floats)
                - metadata: Optional metadata dict
            namespace: Optional namespace for multi-tenancy
            
        Returns:
            Number of vectors successfully upserted
            
        Raises:
            ValueError: If governance check fails
            ConnectionError: If connection to vector store fails
        """  # noqa: W293
        raise NotImplementedError

    @abstractmethod
    def query(
        self,
        vector: list[float],
        top_k: int = 10,
        filter: dict[str, Any] | None = None,
        namespace: str = "",
    ) -> list[VectorSearchResult]:
        """Query vectors with PII redaction on results.
        
        Args:
            vector: Query vector
            top_k: Number of results to return
            filter: Optional metadata filter
            namespace: Optional namespace for multi-tenancy
            
        Returns:
            List of search results with PII redacted
            
        Raises:
            ConnectionError: If connection to vector store fails
        """  # noqa: W293
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        ids: list[str],
        namespace: str = "",
    ) -> int:
        """Delete vectors with audit logging.
        
        Args:
            ids: List of vector IDs to delete
            namespace: Optional namespace for multi-tenancy
            
        Returns:
            Number of vectors successfully deleted
            
        Raises:
            ConnectionError: If connection to vector store fails
        """  # noqa: W293
        raise NotImplementedError

    def health_check(self) -> dict[str, Any]:
        """Check health of vector store connection.
        
        Returns:
            Health check result with status and details
        """  # noqa: W293
        return {
            "status": "unknown",
            "provider": self.__class__.__name__,
            "governance_enabled": self.enable_governance,
            "pii_detection_enabled": self.enable_pii_detection,
            "audit_logging_enabled": self.enable_audit_logging,
        }
