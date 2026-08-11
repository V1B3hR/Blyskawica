"""Membership Inference Detector (MS-002)"""
import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from ...core.models import AgentAction, SafetyViolation, Severity, ViolationType
from ..base_detector import BaseDetector


class MembershipInferenceDetector(BaseDetector):
    def __init__(self):
        super().__init__("Membership Inference Detector", version="1.0.0")

    async def detect_violations(self, action: AgentAction) -> Sequence[SafetyViolation] | None:
        if self.status.value != "active":
            return None
        content = str(action.content).lower()
        keywords = ['training data', 'memorized', 'seen before', 'in dataset']
        matches = sum(1 for kw in keywords if kw in content)
        if matches >= 2:
            return [SafetyViolation(
                violation_id=str(uuid.uuid4()), violation_type=ViolationType.ADVERSARIAL_ATTACK,
                severity=Severity.HIGH, confidence=0.6, description="Membership inference attempt",
                evidence=["Inference patterns detected"], timestamp=datetime.now(timezone.utc),
                detector_name=self.name, action_id=action.action_id)]
        return None
