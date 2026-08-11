"""
Base interface for LLM Provider integrations with Nethical governance.

This module provides the abstract base class for all LLM provider integrations,
ensuring consistent governance checks across different providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMResponse:
    """Response from an LLM provider with governance information.
    
    Attributes:
        content: The generated text content
        model: Model identifier used for generation
        usage: Token usage statistics
        governance_result: Results from governance checks (if performed)
        risk_score: Risk score from governance (0.0-1.0)
    """  # noqa: W293
    content: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    governance_result: dict[str, Any] | None = None
    risk_score: float = 0.0


class LLMProviderBase(ABC):
    """Base class for LLM provider integrations with Nethical governance.
    
    This abstract class defines the interface that all LLM provider integrations
    must implement. It provides common governance checking functionality that
    can be applied to any LLM provider.
    
    Example:
        class MyProvider(LLMProviderBase):
            @property
            def model_name(self) -> str:
                return "my-model"
            
            def _generate(self, prompt: str, **kwargs) -> LLMResponse:
                # Implement actual generation
                return LLMResponse(content="...", model=self.model_name)
        
        provider = MyProvider(check_input=True, check_output=True)
        response = provider.safe_generate("Hello, world!")
    
    Attributes:
        check_input: Whether to check input prompts for safety
        check_output: Whether to check generated output for safety
        block_threshold: Risk score threshold for blocking (0.0-1.0)
        agent_id: Identifier for this agent in governance logs
    """  # noqa: W293

    def __init__(
        self,
        check_input: bool = True,
        check_output: bool = True,
        block_threshold: float = 0.7,
        agent_id: str | None = None,
        storage_dir: str = "./nethical_data"
    ):
        """Initialize the LLM provider with governance settings.
        
        Args:
            check_input: Enable governance checks on input prompts
            check_output: Enable governance checks on generated output
            block_threshold: Risk score threshold for blocking (default: 0.7)
            agent_id: Custom agent identifier (defaults to class name)
            storage_dir: Directory for Nethical data storage
        """  # noqa: W293
        self.check_input = check_input
        self.check_output = check_output
        self.block_threshold = block_threshold
        self.agent_id = agent_id or self.__class__.__name__
        self.storage_dir = storage_dir

        # Lazy initialization of governance
        self._governance = None

    @property
    def governance(self):
        """Get or create the IntegratedGovernance instance."""
        if self._governance is None:
            from nethical.core import IntegratedGovernance
            self._governance = IntegratedGovernance(
                storage_dir=self.storage_dir,
                enable_shadow_mode=True,
                enable_ml_blending=True,
                enable_anomaly_detection=True,
            )
        return self._governance

    def _check_governance(self, content: str, action_type: str) -> dict[str, Any]:
        """Check content against governance rules.
        
        Args:
            content: The content to check
            action_type: Type of action (e.g., "user_input", "generated_content")
            
        Returns:
            Governance processing result dictionary
        """  # noqa: W293
        return self.governance.process_action(
            action=content,
            agent_id=self.agent_id,
            action_type=action_type
        )

    def _get_risk_score(self, result: dict[str, Any]) -> float:
        """Extract risk score from governance result.
        
        Args:
            result: Governance processing result
            
        Returns:
            Risk score (0.0-1.0)
        """  # noqa: W293
        # Try phase3 risk score first
        phase3 = result.get("phase3", {})
        if phase3:
            return phase3.get("risk_score", 0.0)

        # Fallback to direct risk_score
        return result.get("risk_score", 0.0)

    def _get_reason(self, result: dict[str, Any]) -> str:
        """Extract reason/explanation from governance result.
        
        Args:
            result: Governance processing result
            
        Returns:
            Human-readable reason string
        """  # noqa: W293
        # Check for explicit reason
        if "reason" in result:
            return result["reason"]

        # Check phase data for reasons
        for phase in ["phase89", "phase4", "phase3"]:
            phase_data = result.get(phase, {})
            if phase_data and "reason" in phase_data:
                return phase_data["reason"]

        # Check risk tier
        phase3 = result.get("phase3", {})
        risk_tier = phase3.get("risk_tier", "UNKNOWN")
        return f"Risk tier: {risk_tier}"

    def safe_generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text with governance checks on input and output.
        
        This method wraps the actual generation with optional governance
        checks on both the input prompt and the generated output.
        
        Args:
            prompt: The input prompt for generation
            **kwargs: Additional arguments passed to _generate
            
        Returns:
            LLMResponse with content and governance information
        """  # noqa: W293
        # Pre-check input
        if self.check_input:
            input_result = self._check_governance(prompt, "user_input")
            risk_score = self._get_risk_score(input_result)

            if risk_score > self.block_threshold:
                return LLMResponse(
                    content=f"Input blocked: {self._get_reason(input_result)}",
                    model=self.model_name,
                    usage={},
                    governance_result=input_result,
                    risk_score=risk_score
                )

        # Generate response
        response = self._generate(prompt, **kwargs)

        # Post-check output
        if self.check_output:
            output_result = self._check_governance(response.content, "generated_content")
            output_risk = self._get_risk_score(output_result)

            response.governance_result = output_result
            response.risk_score = output_risk

            if output_risk > self.block_threshold:
                response.content = f"Output filtered: {self._get_reason(output_result)}"

        return response

    @abstractmethod
    def _generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Implement actual generation logic.
        
        This method must be implemented by subclasses to perform
        the actual text generation using the provider's API.
        
        Args:
            prompt: The input prompt for generation
            **kwargs: Provider-specific arguments
            
        Returns:
            LLMResponse with generated content
        """  # noqa: W293
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get the model identifier.
        
        Returns:
            String identifying the model (e.g., "cohere-command-r-plus")
        """  # noqa: W293
        pass

    def get_tool_definition(self) -> dict[str, Any]:
        """Get a tool definition for function calling (if supported).
        
        Returns a generic Nethical governance tool definition that can
        be adapted for different LLM provider formats.
        
        Returns:
            Tool definition dictionary
        """  # noqa: W293
        return {
            "name": "nethical_governance",
            "description": (
                "Evaluate an action for safety, ethics, and compliance. "
                "Use this tool to check if an action is allowed before executing it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "The action or content to evaluate"
                    },
                    "action_type": {
                        "type": "string",
                        "description": "Type of action (query, code_generation, data_access, etc.)"
                    }
                },
                "required": ["action"]
            }
        }
