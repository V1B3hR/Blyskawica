"""
DuetMindAgent.py - 3NGIN3 Architecture Dual Agent System

Implements the DuetMind system with:
- Style Vectors for agent personality configuration
- "Dusty Mirror" noise injection for resilience testing
- Dual agent interaction and collaboration
"""

import logging
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import random
import copy


@dataclass
class StyleVector:
    """Style vector defining agent personality and behavior characteristics"""
    logic: float = 0.5      # 0.0 = intuitive, 1.0 = highly logical
    creativity: float = 0.5  # 0.0 = conservative, 1.0 = highly creative
    risk_tolerance: float = 0.5  # 0.0 = risk-averse, 1.0 = risk-seeking
    verbosity: float = 0.5   # 0.0 = concise, 1.0 = verbose
    empathy: float = 0.5     # 0.0 = analytical, 1.0 = empathetic
    
    def __post_init__(self):
        """Ensure all values are in valid range [0.0, 1.0]"""
        for field in ['logic', 'creativity', 'risk_tolerance', 'verbosity', 'empathy']:
            value = getattr(self, field)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field} must be between 0.0 and 1.0, got {value}")
                
    def distance(self, other: 'StyleVector') -> float:
        """Calculate Euclidean distance between style vectors"""
        return np.sqrt(
            (self.logic - other.logic) ** 2 +
            (self.creativity - other.creativity) ** 2 +
            (self.risk_tolerance - other.risk_tolerance) ** 2 +
            (self.verbosity - other.verbosity) ** 2 +
            (self.empathy - other.empathy) ** 2
        )
        
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary representation"""
        return {
            'logic': self.logic,
            'creativity': self.creativity,
            'risk_tolerance': self.risk_tolerance,
            'verbosity': self.verbosity,
            'empathy': self.empathy
        }


class DuetMindAgent:
    """
    Individual agent with configurable style vector and behavior patterns
    """
    
    def __init__(self, agent_id: str, style_vector: StyleVector, config: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.style_vector = style_vector
        self.config = config or {}
        self.interaction_history = []
        self.mirror_agent = None
        self.dusty_mirror_active = False
        self.noise_level = 0.1  # Default noise level for dusty mirror
        
        logging.info(f"DuetMindAgent {agent_id} initialized with style: {style_vector.to_dict()}")
        
    def process_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a prompt according to the agent's style vector"""
        context = context or {}
        
        # Apply style vector to shape response
        response = self._generate_styled_response(prompt, context)
        
        # Apply dusty mirror if active
        if self.dusty_mirror_active and self.mirror_agent:
            response = self._apply_dusty_mirror(response)
            
        result = {
            "agent_id": self.agent_id,
            "prompt": prompt,
            "response": response,
            "style_influence": self._get_style_influence(),
            "mirror_applied": self.dusty_mirror_active,
            "context": context
        }
        
        self.interaction_history.append(result)
        return result
        
    def _generate_styled_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate a response influenced by the agent's style vector"""
        base_response = self._generate_base_response(prompt, context)
        
        # Modify response based on style vector
        styled_response = base_response
        
        # Logic influence
        if self.style_vector.logic > 0.7:
            styled_response = f"[LOGICAL ANALYSIS] {styled_response}"
        elif self.style_vector.logic < 0.3:
            styled_response = f"[INTUITIVE RESPONSE] {styled_response}"
            
        # Creativity influence
        if self.style_vector.creativity > 0.7:
            styled_response = f"{styled_response} [CREATIVE EXTENSION: This opens up new possibilities...]"
        elif self.style_vector.creativity < 0.3:
            styled_response = f"{styled_response} [CONSERVATIVE APPROACH: Following established patterns...]"
            
        # Risk tolerance influence
        if self.style_vector.risk_tolerance > 0.7:
            styled_response = f"{styled_response} [BOLD RECOMMENDATION: Let's explore uncharted territory!]"
        elif self.style_vector.risk_tolerance < 0.3:
            styled_response = f"{styled_response} [CAUTIOUS NOTE: We should proceed carefully...]"
            
        # Verbosity influence
        if self.style_vector.verbosity > 0.7:
            styled_response = f"{styled_response} [DETAILED ELABORATION: Let me explain further with additional context and considerations...]"
        elif self.style_vector.verbosity < 0.3:
            styled_response = styled_response  # Keep concise
            
        # Empathy influence
        if self.style_vector.empathy > 0.7:
            styled_response = f"[EMPATHETIC CONSIDERATION] {styled_response} [How are you feeling about this?]"
        elif self.style_vector.empathy < 0.3:
            styled_response = f"[ANALYTICAL FOCUS] {styled_response}"
            
        return styled_response
        
    def _generate_base_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate base response to prompt"""
        # Simple response generation for testing
        if "question" in prompt.lower():
            return f"Analyzing the question: '{prompt}' - Based on available information, here's my assessment."
        elif "problem" in prompt.lower():
            return f"Problem identified: '{prompt}' - Proposing solution approach."
        elif "help" in prompt.lower():
            return f"I'm here to assist with: '{prompt}' - Let me provide guidance."
        else:
            return f"Processing input: '{prompt}' - Generating appropriate response."
            
    def _get_style_influence(self) -> Dict[str, str]:
        """Get description of how style vector influenced the response"""
        influences = {}
        
        if self.style_vector.logic > 0.6:
            influences["logic"] = "high_logical_reasoning"
        elif self.style_vector.logic < 0.4:
            influences["logic"] = "intuitive_processing"
            
        if self.style_vector.creativity > 0.6:
            influences["creativity"] = "creative_expansion"
        elif self.style_vector.creativity < 0.4:
            influences["creativity"] = "conservative_approach"
            
        return influences
        
    def create_mirror_agent(self, noise_level: float = 0.1) -> 'DuetMindAgent':
        """Create a mirror agent with dusty mirror noise injection"""
        self.noise_level = noise_level
        
        # Create noisy style vector
        noisy_style = self._inject_noise_to_style(self.style_vector, noise_level)
        
        # Create mirror agent
        mirror_id = f"{self.agent_id}_mirror"
        mirror_agent = DuetMindAgent(mirror_id, noisy_style, self.config.copy())
        mirror_agent.dusty_mirror_active = True
        
        # Link agents
        self.mirror_agent = mirror_agent
        mirror_agent.mirror_agent = self
        
        logging.info(f"Mirror agent {mirror_id} created with noise level {noise_level}")
        return mirror_agent
        
    def _inject_noise_to_style(self, style: StyleVector, noise_level: float) -> StyleVector:
        """Inject noise into style vector for dusty mirror effect"""
        noisy_values = {}
        
        for field in ['logic', 'creativity', 'risk_tolerance', 'verbosity', 'empathy']:
            original_value = getattr(style, field)
            # Add Gaussian noise
            noise = np.random.normal(0, noise_level)
            noisy_value = np.clip(original_value + noise, 0.0, 1.0)
            noisy_values[field] = noisy_value
            
        return StyleVector(**noisy_values)
        
    def _apply_dusty_mirror(self, response: str) -> str:
        """Apply dusty mirror noise injection to response"""
        # Add subtle variations to simulate noise injection
        variations = [
            lambda x: x.replace("analysis", "evaluation"),
            lambda x: x.replace("approach", "methodology"), 
            lambda x: x.replace("solution", "resolution"),
            lambda x: x + " [MIRROR_VARIANCE]",
            lambda x: f"[NOISY_PROCESSING] {x}"
        ]
        
        # Apply random variation based on noise level
        if random.random() < self.noise_level * 5:  # Scale noise probability
            variation = random.choice(variations)
            response = variation(response)
            
        return response
        
    def activate_dusty_mirror(self, noise_level: float = 0.1):
        """Activate dusty mirror mode"""
        self.dusty_mirror_active = True
        self.noise_level = noise_level
        logging.info(f"Dusty mirror activated for agent {self.agent_id} with noise level {noise_level}")
        
    def deactivate_dusty_mirror(self):
        """Deactivate dusty mirror mode"""
        self.dusty_mirror_active = False
        logging.info(f"Dusty mirror deactivated for agent {self.agent_id}")
        
    def get_interaction_history(self) -> List[Dict[str, Any]]:
        """Get the interaction history"""
        return self.interaction_history.copy()


class DuetMindSystem:
    """
    System managing multiple DuetMind agents and their interactions
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.agents = {}
        self.collaboration_history = []
        
    def create_agent(self, agent_id: str, style_vector: StyleVector) -> DuetMindAgent:
        """Create a new agent in the system"""
        agent = DuetMindAgent(agent_id, style_vector, self.config)
        self.agents[agent_id] = agent
        logging.info(f"Agent {agent_id} added to DuetMind system")
        return agent
        
    def create_opposing_agents(self, base_agent_id: str) -> Tuple[DuetMindAgent, DuetMindAgent]:
        """Create two agents with opposing style vectors"""
        # High logic, low creativity agent
        logical_style = StyleVector(
            logic=0.9,
            creativity=0.1,
            risk_tolerance=0.2,
            verbosity=0.7,
            empathy=0.3
        )
        
        # Low logic, high creativity agent  
        creative_style = StyleVector(
            logic=0.1,
            creativity=0.9,
            risk_tolerance=0.8,
            verbosity=0.6,
            empathy=0.7
        )
        
        logical_agent = self.create_agent(f"{base_agent_id}_logical", logical_style)
        creative_agent = self.create_agent(f"{base_agent_id}_creative", creative_style)
        
        return logical_agent, creative_agent
        
    def collaborate(self, agent_ids: List[str], prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Facilitate collaboration between multiple agents"""
        if not all(agent_id in self.agents for agent_id in agent_ids):
            missing = [aid for aid in agent_ids if aid not in self.agents]
            raise ValueError(f"Agents not found: {missing}")
            
        responses = {}
        for agent_id in agent_ids:
            agent = self.agents[agent_id]
            response = agent.process_prompt(prompt, context)
            responses[agent_id] = response
            
        # Analyze collaboration
        collaboration_result = {
            "prompt": prompt,
            "context": context,
            "agent_responses": responses,
            "style_diversity": self._calculate_style_diversity(agent_ids),
            "consensus_level": self._calculate_consensus(responses),
            "collaboration_quality": self._assess_collaboration_quality(responses)
        }
        
        self.collaboration_history.append(collaboration_result)
        return collaboration_result
        
    def _calculate_style_diversity(self, agent_ids: List[str]) -> float:
        """Calculate diversity of style vectors among agents"""
        if len(agent_ids) < 2:
            return 0.0
            
        styles = [self.agents[aid].style_vector for aid in agent_ids]
        total_distance = 0.0
        comparisons = 0
        
        for i, style1 in enumerate(styles):
            for j, style2 in enumerate(styles[i+1:], i+1):
                total_distance += style1.distance(style2)
                comparisons += 1
                
        return total_distance / comparisons if comparisons > 0 else 0.0
        
    def _calculate_consensus(self, responses: Dict[str, Dict[str, Any]]) -> float:
        """Calculate consensus level among agent responses"""
        # Simple heuristic: measure similarity in response lengths and key words
        response_texts = [resp["response"] for resp in responses.values()]
        
        if len(response_texts) < 2:
            return 1.0
            
        # Basic consensus metric based on response length similarity
        lengths = [len(text) for text in response_texts]
        length_variance = np.var(lengths)
        max_length = max(lengths) if lengths else 1
        
        # Lower variance relative to max length indicates higher consensus
        consensus = 1.0 - min(1.0, length_variance / (max_length ** 2))
        return consensus
        
    def _assess_collaboration_quality(self, responses: Dict[str, Dict[str, Any]]) -> str:
        """Assess the quality of collaboration"""
        num_agents = len(responses)
        
        if num_agents == 1:
            return "single_agent"
        elif num_agents == 2:
            return "duet_collaboration"
        elif num_agents <= 4:
            return "small_group_collaboration"
        else:
            return "large_group_collaboration"
            
    def test_dusty_mirror_resilience(self, agent_id: str, test_prompts: List[str], noise_level: float = 0.1) -> Dict[str, Any]:
        """Test system resilience using dusty mirror noise injection"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
            
        original_agent = self.agents[agent_id]
        mirror_agent = original_agent.create_mirror_agent(noise_level)
        
        original_responses = []
        mirror_responses = []
        
        for prompt in test_prompts:
            original_resp = original_agent.process_prompt(prompt)
            mirror_resp = mirror_agent.process_prompt(prompt)
            
            original_responses.append(original_resp)
            mirror_responses.append(mirror_resp)
            
        # Calculate resilience metrics
        resilience_score = self._calculate_resilience_score(original_responses, mirror_responses)
        
        return {
            "agent_id": agent_id,
            "mirror_agent_id": mirror_agent.agent_id,
            "noise_level": noise_level,
            "test_prompts": test_prompts,
            "original_responses": original_responses,
            "mirror_responses": mirror_responses,
            "resilience_score": resilience_score,
            "differences_detected": resilience_score < 1.0
        }
        
    def _calculate_resilience_score(self, original_responses: List[Dict], mirror_responses: List[Dict]) -> float:
        """Calculate resilience score based on response similarity"""
        if len(original_responses) != len(mirror_responses):
            return 0.0
            
        similarity_scores = []
        
        for orig, mirror in zip(original_responses, mirror_responses):
            orig_text = orig["response"]
            mirror_text = mirror["response"]
            
            # Simple similarity based on shared words (excluding mirror tags)
            orig_words = set(orig_text.lower().split())
            mirror_words = set(mirror_text.lower().split())
            
            # Remove mirror-specific tags for fair comparison
            mirror_words.discard("[mirror_variance]")
            mirror_words.discard("[noisy_processing]")
            
            if len(orig_words) == 0 and len(mirror_words) == 0:
                similarity = 1.0
            elif len(orig_words) == 0 or len(mirror_words) == 0:
                similarity = 0.0
            else:
                overlap = len(orig_words.intersection(mirror_words))
                total = len(orig_words.union(mirror_words))
                similarity = overlap / total if total > 0 else 0.0
                
            similarity_scores.append(similarity)
            
        return np.mean(similarity_scores) if similarity_scores else 0.0
        
    def get_agents(self) -> Dict[str, DuetMindAgent]:
        """Get all agents in the system"""
        return self.agents.copy()
        
    def get_collaboration_history(self) -> List[Dict[str, Any]]:
        """Get collaboration history"""
        return self.collaboration_history.copy()