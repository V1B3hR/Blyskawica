"""
confirmation_automation.py - Automated Confirmation System for Human-AI Collaboration

Implements confirmation procedure automation:
- Risk-based confirmation level determination
- Automated confirmation workflow management
- User preference learning and adaptation
- Multi-modal confirmation interfaces
- Timeout and escalation handling
"""

import logging
import time
import threading
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from .types import Action, ActionType, SafetyLevel, ConfirmationLevel, CollaborationContext


class ConfirmationStatus(Enum):
    """Status of confirmation requests"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    TIMEOUT = "timeout"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class ConfirmationInterface(Enum):
    """Types of confirmation interfaces"""
    TEXT = "text"               # Text-based confirmation
    VOICE = "voice"             # Voice confirmation
    NEURAL = "neural"           # Neural signal confirmation
    GESTURE = "gesture"         # Gesture-based confirmation
    BIOMETRIC = "biometric"     # Biometric confirmation
    MULTI_MODAL = "multi_modal" # Multiple confirmation methods


@dataclass
class ConfirmationPreferences:
    """User preferences for confirmation procedures"""
    user_id: str
    preferred_interface: ConfirmationInterface = ConfirmationInterface.TEXT
    confirmation_timeout: int = 30  # seconds
    auto_confirm_trusted_actions: bool = False
    require_enhanced_confirmation: List[ActionType] = field(default_factory=list)
    trusted_action_types: List[ActionType] = field(default_factory=list)
    notification_preferences: Dict[str, bool] = field(default_factory=dict)
    accessibility_requirements: List[str] = field(default_factory=list)


@dataclass
class ConfirmationRequest:
    """Represents a confirmation request"""
    request_id: str
    action: Action
    context: CollaborationContext
    confirmation_level: ConfirmationLevel
    proposed_interface: ConfirmationInterface
    requested_at: float
    timeout_seconds: int
    status: ConfirmationStatus = ConfirmationStatus.PENDING
    user_response: Optional[str] = None
    response_time: Optional[float] = None
    alternatives_shown: List[str] = field(default_factory=list)
    rationale: Optional[str] = None
    consequences_explained: bool = False
    reversibility_info: Optional[str] = None


@dataclass
class ConfirmationHistory:
    """Historical confirmation data for learning"""
    user_id: str
    confirmation_responses: List[Dict[str, Any]] = field(default_factory=list)
    response_times: List[float] = field(default_factory=list)
    preferred_confirmation_levels: Dict[ActionType, ConfirmationLevel] = field(default_factory=dict)
    interface_effectiveness: Dict[ConfirmationInterface, float] = field(default_factory=dict)
    common_rejections: List[str] = field(default_factory=list)


class ConfirmationAutomationSystem:
    """
    Automated confirmation system for human-AI collaboration.
    
    Handles confirmation workflow automation, user preference learning,
    and adaptive confirmation procedures.
    """
    
    def __init__(self):
        """Initialize the confirmation automation system"""
        self.logger = logging.getLogger(__name__)
        
        # User data
        self.user_preferences: Dict[str, ConfirmationPreferences] = {}
        self.user_histories: Dict[str, ConfirmationHistory] = {}
        
        # Active requests
        self.active_requests: Dict[str, ConfirmationRequest] = {}
        self.completed_requests: List[ConfirmationRequest] = []
        
        # Configuration
        self.default_timeout = 30  # seconds
        self.max_retries = 3
        self.escalation_threshold = 2  # number of timeouts before escalation
        
        # Callbacks for different interfaces
        self.interface_handlers: Dict[ConfirmationInterface, Callable] = {}
        self.notification_callbacks: List[Callable] = []
        
        # Background processing
        self.monitor_thread = None
        self.shutdown_flag = threading.Event()
        
        self.logger.info("Confirmation Automation System initialized")

    def start_monitoring(self):
        """Start background monitoring for timeouts and escalations"""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.shutdown_flag.clear()
            self.monitor_thread = threading.Thread(target=self._monitoring_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            self.logger.info("Confirmation monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.shutdown_flag.set()
            self.monitor_thread.join(timeout=5.0)
            self.logger.info("Confirmation monitoring stopped")

    def request_confirmation(self, action: Action, context: CollaborationContext,
                           rationale: Optional[str] = None) -> str:
        """
        Request confirmation for an action
        
        Args:
            action: Action requiring confirmation
            context: Collaboration context
            rationale: Optional explanation for the action
            
        Returns:
            Request ID for tracking
        """
        request_id = f"confirm_{int(time.time() * 1000)}"
        
        # Determine appropriate confirmation level and interface
        confirmation_level = self._determine_confirmation_level(action, context)
        interface = self._select_confirmation_interface(context.user_id, confirmation_level)
        timeout = self._calculate_timeout(context.user_id, confirmation_level)
        
        # Create confirmation request
        request = ConfirmationRequest(
            request_id=request_id,
            action=action,
            context=context,
            confirmation_level=confirmation_level,
            proposed_interface=interface,
            requested_at=time.time(),
            timeout_seconds=timeout,
            rationale=rationale
        )
        
        # Store active request
        self.active_requests[request_id] = request
        
        # Trigger confirmation interface
        self._trigger_confirmation_interface(request)
        
        # Update user history
        self._record_confirmation_request(context.user_id, request)
        
        self.logger.info(f"Confirmation requested: {request_id} for action {action.description}")
        return request_id

    def provide_confirmation_response(self, request_id: str, response: str,
                                    response_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Provide response to confirmation request
        
        Args:
            request_id: ID of the confirmation request
            response: User's response ("confirm", "reject", "alternative")
            response_data: Additional response data
            
        Returns:
            Whether response was successfully processed
        """
        if request_id not in self.active_requests:
            self.logger.warning(f"Confirmation request {request_id} not found")
            return False
            
        request = self.active_requests[request_id]
        request.user_response = response
        request.response_time = time.time() - request.requested_at
        
        # Process response
        if response.lower() in ["confirm", "yes", "proceed", "accept"]:
            request.status = ConfirmationStatus.CONFIRMED
        elif response.lower() in ["reject", "no", "cancel", "deny"]:
            request.status = ConfirmationStatus.REJECTED
        else:
            # Handle alternative or unclear responses
            request.status = ConfirmationStatus.PENDING
            return self._handle_alternative_response(request, response, response_data)
        
        # Move to completed requests
        self.completed_requests.append(request)
        del self.active_requests[request_id]
        
        # Update user learning data
        self._update_user_learning(request)
        
        # Trigger callbacks
        self._notify_confirmation_response(request)
        
        self.logger.info(f"Confirmation response processed: {request_id} -> {request.status}")
        return True

    def learn_user_preferences(self, user_id: str) -> ConfirmationPreferences:
        """
        Learn and update user confirmation preferences
        
        Args:
            user_id: User identifier
            
        Returns:
            Updated user preferences
        """
        if user_id not in self.user_histories:
            # Create default preferences for new user
            preferences = ConfirmationPreferences(user_id=user_id)
            self.user_preferences[user_id] = preferences
            return preferences
            
        history = self.user_histories[user_id]
        
        # Analyze response patterns
        preferences = self.user_preferences.get(user_id, ConfirmationPreferences(user_id=user_id))
        
        # Learn preferred interface
        if history.interface_effectiveness:
            best_interface = max(history.interface_effectiveness.items(), key=lambda x: x[1])
            preferences.preferred_interface = best_interface[0]
        
        # Learn timeout preferences from response times
        if history.response_times:
            avg_response_time = sum(history.response_times) / len(history.response_times)
            preferences.confirmation_timeout = max(15, int(avg_response_time * 2))  # 2x average with minimum
        
        # Learn trusted action types
        confirmed_actions = [
            resp for resp in history.confirmation_responses 
            if resp.get("status") == ConfirmationStatus.CONFIRMED
        ]
        
        if len(confirmed_actions) > 10:  # Enough data for learning
            action_type_confirmations = defaultdict(list)
            for resp in confirmed_actions:
                if "action_type" in resp:
                    action_type_confirmations[resp["action_type"]].append(resp)
            
            # Actions confirmed >90% of the time can be trusted
            for action_type, confirmations in action_type_confirmations.items():
                confirmation_rate = len(confirmations) / len([
                    r for r in history.confirmation_responses 
                    if r.get("action_type") == action_type
                ])
                
                if confirmation_rate > 0.9:
                    if action_type not in preferences.trusted_action_types:
                        preferences.trusted_action_types.append(action_type)
        
        self.user_preferences[user_id] = preferences
        self.logger.info(f"Updated preferences for user {user_id}")
        return preferences

    def predict_confirmation_needs(self, action: Action, context: CollaborationContext) -> Dict[str, Any]:
        """
        Predict confirmation needs for an action
        
        Args:
            action: Proposed action
            context: Collaboration context
            
        Returns:
            Prediction results including recommended level and confidence
        """
        user_id = context.user_id
        
        # Get user preferences and history
        preferences = self.user_preferences.get(user_id, ConfirmationPreferences(user_id=user_id))
        history = self.user_histories.get(user_id, ConfirmationHistory(user_id=user_id))
        
        # Predict based on action type patterns
        predicted_level = self._determine_confirmation_level(action, context)
        
        # Adjust based on user trust and history
        if action.action_type in preferences.trusted_action_types:
            predicted_level = ConfirmationLevel(max(0, predicted_level.value - 1))
            confidence = 0.9
        elif action.action_type in preferences.require_enhanced_confirmation:
            predicted_level = ConfirmationLevel(min(4, predicted_level.value + 1))
            confidence = 0.8
        else:
            confidence = 0.7
        
        # Consider recent rejection patterns
        if history.common_rejections:
            similar_rejections = [
                rejection for rejection in history.common_rejections
                if any(keyword in action.description.lower() for keyword in rejection.lower().split())
            ]
            if similar_rejections:
                confidence *= 0.8  # Lower confidence due to potential rejection
        
        return {
            "recommended_level": predicted_level,
            "confidence": confidence,
            "predicted_interface": preferences.preferred_interface,
            "estimated_response_time": preferences.confirmation_timeout * 0.7,
            "auto_confirm_eligible": (
                action.action_type in preferences.trusted_action_types and
                preferences.auto_confirm_trusted_actions
            )
        }

    def get_confirmation_statistics(self) -> Dict[str, Any]:
        """Get statistics about confirmation system performance"""
        total_requests = len(self.completed_requests)
        
        if total_requests == 0:
            return {"message": "No confirmation requests processed yet"}
        
        # Calculate statistics
        confirmed_count = len([r for r in self.completed_requests if r.status == ConfirmationStatus.CONFIRMED])
        rejected_count = len([r for r in self.completed_requests if r.status == ConfirmationStatus.REJECTED])
        timeout_count = len([r for r in self.completed_requests if r.status == ConfirmationStatus.TIMEOUT])
        
        response_times = [r.response_time for r in self.completed_requests if r.response_time]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Interface effectiveness
        interface_stats = defaultdict(lambda: {"total": 0, "confirmed": 0})
        for request in self.completed_requests:
            interface = request.proposed_interface
            interface_stats[interface]["total"] += 1
            if request.status == ConfirmationStatus.CONFIRMED:
                interface_stats[interface]["confirmed"] += 1
        
        interface_effectiveness = {
            interface.value: stats["confirmed"] / stats["total"] if stats["total"] > 0 else 0
            for interface, stats in interface_stats.items()
        }
        
        return {
            "total_requests": total_requests,
            "confirmation_rate": confirmed_count / total_requests,
            "rejection_rate": rejected_count / total_requests,
            "timeout_rate": timeout_count / total_requests,
            "average_response_time": avg_response_time,
            "interface_effectiveness": interface_effectiveness,
            "active_requests": len(self.active_requests),
            "learned_user_preferences": len(self.user_preferences)
        }

    # Private helper methods
    
    def _determine_confirmation_level(self, action: Action, context: CollaborationContext) -> ConfirmationLevel:
        """Determine appropriate confirmation level for action"""
        # Base level on action type and risk
        risk_levels = {
            ActionType.COMPUTATION: ConfirmationLevel.NONE,
            ActionType.COMMUNICATION: ConfirmationLevel.IMPLICIT,
            ActionType.DATA_ACCESS: ConfirmationLevel.EXPLICIT,
            ActionType.SYSTEM_MODIFICATION: ConfirmationLevel.ENHANCED,
            ActionType.EXTERNAL_INTERACTION: ConfirmationLevel.EXPLICIT
        }
        
        base_level = risk_levels.get(action.action_type, ConfirmationLevel.EXPLICIT)
        
        # Adjust based on context urgency
        if context.urgency_level >= 4:
            # High urgency - reduce confirmation level
            base_level = ConfirmationLevel(max(0, base_level.value - 1))
        elif context.urgency_level <= 2:
            # Low urgency - can afford higher confirmation
            base_level = ConfirmationLevel(min(4, base_level.value + 1))
        
        # Adjust based on trust level
        if context.trust_level > 0.8:
            base_level = ConfirmationLevel(max(0, base_level.value - 1))
        elif context.trust_level < 0.3:
            base_level = ConfirmationLevel(min(4, base_level.value + 1))
        
        return base_level

    def _select_confirmation_interface(self, user_id: str, confirmation_level: ConfirmationLevel) -> ConfirmationInterface:
        """Select appropriate confirmation interface for user"""
        preferences = self.user_preferences.get(user_id, ConfirmationPreferences(user_id=user_id))
        
        # For critical confirmations, use multi-modal if available
        if confirmation_level == ConfirmationLevel.CRITICAL:
            return ConfirmationInterface.MULTI_MODAL
        
        # Otherwise use user preference or default to text
        return preferences.preferred_interface

    def _calculate_timeout(self, user_id: str, confirmation_level: ConfirmationLevel) -> int:
        """Calculate timeout for confirmation request"""
        preferences = self.user_preferences.get(user_id, ConfirmationPreferences(user_id=user_id))
        base_timeout = preferences.confirmation_timeout
        
        # Adjust timeout based on confirmation level
        level_multipliers = {
            ConfirmationLevel.NONE: 0,
            ConfirmationLevel.IMPLICIT: 0.5,
            ConfirmationLevel.EXPLICIT: 1.0,
            ConfirmationLevel.ENHANCED: 1.5,
            ConfirmationLevel.CRITICAL: 2.0
        }
        
        return int(base_timeout * level_multipliers.get(confirmation_level, 1.0))

    def _trigger_confirmation_interface(self, request: ConfirmationRequest):
        """Trigger the appropriate confirmation interface"""
        interface = request.proposed_interface
        
        if interface in self.interface_handlers:
            try:
                self.interface_handlers[interface](request)
            except Exception as e:
                self.logger.error(f"Error triggering {interface} interface: {e}")
        else:
            # Default text-based confirmation
            self._default_confirmation_handler(request)

    def _default_confirmation_handler(self, request: ConfirmationRequest):
        """Default confirmation handler (logs confirmation request)"""
        self.logger.info(f"CONFIRMATION REQUIRED: {request.action.description}")
        if request.rationale:
            self.logger.info(f"Rationale: {request.rationale}")
        self.logger.info(f"Timeout: {request.timeout_seconds}s")

    def _record_confirmation_request(self, user_id: str, request: ConfirmationRequest):
        """Record confirmation request for learning"""
        if user_id not in self.user_histories:
            self.user_histories[user_id] = ConfirmationHistory(user_id=user_id)

    def _handle_alternative_response(self, request: ConfirmationRequest, response: str,
                                   response_data: Optional[Dict[str, Any]]) -> bool:
        """Handle alternative or unclear responses"""
        # For now, treat unclear responses as needing clarification
        self.logger.info(f"Unclear response '{response}' for request {request.request_id}")
        
        # Could trigger follow-up confirmation with clarification
        return False

    def _update_user_learning(self, request: ConfirmationRequest):
        """Update user learning data from completed request"""
        user_id = request.context.user_id
        
        if user_id not in self.user_histories:
            self.user_histories[user_id] = ConfirmationHistory(user_id=user_id)
        
        history = self.user_histories[user_id]
        
        # Record response
        history.confirmation_responses.append({
            "status": request.status,
            "action_type": request.action.action_type,
            "confirmation_level": request.confirmation_level,
            "interface": request.proposed_interface,
            "response_time": request.response_time
        })
        
        # Record response time
        if request.response_time:
            history.response_times.append(request.response_time)
            
        # Record interface effectiveness
        if request.proposed_interface not in history.interface_effectiveness:
            history.interface_effectiveness[request.proposed_interface] = 0.0
            
        # Update effectiveness based on response
        effectiveness_adjustment = 0.1 if request.status == ConfirmationStatus.CONFIRMED else -0.05
        history.interface_effectiveness[request.proposed_interface] = max(0.0, min(1.0,
            history.interface_effectiveness[request.proposed_interface] + effectiveness_adjustment
        ))
        
        # Record rejections for pattern analysis
        if request.status == ConfirmationStatus.REJECTED and request.user_response:
            history.common_rejections.append(request.user_response)
            # Keep only recent rejections
            if len(history.common_rejections) > 20:
                history.common_rejections.pop(0)

    def _notify_confirmation_response(self, request: ConfirmationRequest):
        """Notify registered callbacks of confirmation response"""
        for callback in self.notification_callbacks:
            try:
                callback(request)
            except Exception as e:
                self.logger.error(f"Error in confirmation callback: {e}")

    def _monitoring_loop(self):
        """Background monitoring loop for timeouts and escalations"""
        while not self.shutdown_flag.is_set():
            try:
                current_time = time.time()
                
                # Check for timeouts
                for request_id, request in list(self.active_requests.items()):
                    if current_time - request.requested_at > request.timeout_seconds:
                        self.logger.warning(f"Confirmation request {request_id} timed out")
                        
                        request.status = ConfirmationStatus.TIMEOUT
                        self.completed_requests.append(request)
                        del self.active_requests[request_id]
                        
                        # Could trigger escalation here
                        self._handle_confirmation_timeout(request)
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in confirmation monitoring loop: {e}")
                time.sleep(30)

    def _handle_confirmation_timeout(self, request: ConfirmationRequest):
        """Handle confirmation timeout"""
        # Could implement escalation logic here
        self.logger.warning(f"Handling timeout for confirmation {request.request_id}")

    # Public interface registration methods
    
    def register_interface_handler(self, interface: ConfirmationInterface, handler: Callable):
        """Register handler for confirmation interface"""
        self.interface_handlers[interface] = handler
        self.logger.info(f"Registered handler for {interface} interface")
        
    def register_notification_callback(self, callback: Callable):
        """Register callback for confirmation notifications"""
        self.notification_callbacks.append(callback)

    def shutdown(self):
        """Shutdown the confirmation automation system"""
        self.stop_monitoring()
        self.logger.info("Confirmation Automation System shutdown complete")