"""
Automation Module

Provides automation capabilities including playbooks, orchestration, and SOAR integration.
"""

from .cisa_playbooks import (
    KEVRemediationPlaybook,
    ShieldsUpResponsePlaybook,
    EmergencyDirectivePlaybook,
)

__all__ = [
    "KEVRemediationPlaybook",
    "ShieldsUpResponsePlaybook",
    "EmergencyDirectivePlaybook",
]
