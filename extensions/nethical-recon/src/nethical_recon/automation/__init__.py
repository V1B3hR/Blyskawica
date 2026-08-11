"""
Automation Module

Provides automation capabilities including playbooks, orchestration, and SOAR integration.
"""

from .cisa_playbooks import (
    EmergencyDirectivePlaybook,
    KEVRemediationPlaybook,
    ShieldsUpResponsePlaybook,
)

__all__ = [
    "KEVRemediationPlaybook",
    "ShieldsUpResponsePlaybook",
    "EmergencyDirectivePlaybook",
]
