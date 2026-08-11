"""
Nethical: Safety governance system for AI agents.

This package provides comprehensive monitoring and safety governance
for AI agents, including:
- Intent vs action deviation monitoring
- Ethical and safety constraint violation detection
- Manipulation technique recognition
- Judge system for action evaluation and feedback
"""

from typing import Any, Dict, Optional  # noqa: UP035

from .core.governance import (
    ActionType,
    JudgmentResult,
    MonitoringConfig,
    SafetyGovernance,
    SafetyViolation,
)
from .core.governance import (
    AgentAction as _AgentAction,
)


def AgentAction(  # noqa: N802
    id: str | None = None,
    action_id: str | None = None,
    agent_id: str | None = None,
    stated_intent: str | None = None,
    actual_action: str | None = None,
    content: str | None = None,
    action_type: ActionType | None = None,
    context: dict[str, Any] | None = None,
    **kwargs: Any,
) -> _AgentAction:
    """Compatibility wrapper for AgentAction that accepts both old and new APIs."""
    # Handle backward compatibility
    if id is not None and action_id is None:
        action_id = id
    if stated_intent is not None and content is None:
        content = stated_intent  # Use stated_intent as content if no content provided
    if actual_action is not None and content is None:
        content = actual_action  # Use actual_action as content if no content provided
    if actual_action is not None and content == stated_intent:
        content = actual_action  # Prefer actual_action over stated_intent for content

    # Set defaults for required fields
    if action_type is None:
        action_type = ActionType.RESPONSE
    if content is None:
        content = stated_intent or actual_action or ""
    if context is None:
        context = {}

    # Create agent action with new API
    agent_action = _AgentAction(
        action_id=action_id,
        agent_id=agent_id,
        action_type=action_type,
        content=content,
        context=context,
        **kwargs,
    )

    # Add compatibility attributes
    agent_action.id = action_id
    agent_action.stated_intent = stated_intent or content
    agent_action.actual_action = actual_action or content

    return agent_action


__version__ = "0.1.0"

# Import vector API components
from .api.vector_api import Agent, EvaluationResult, Nethical, create_nethical  # noqa: E402

__all__ = [
    "SafetyGovernance",
    "AgentAction",
    "SafetyViolation",
    "JudgmentResult",
    "MonitoringConfig",
    # Vector API
    "Nethical",
    "Agent",
    "EvaluationResult",
    "create_nethical",
]
