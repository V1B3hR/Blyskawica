#!/usr/bin/env python3
"""
AI Ethics Framework Implementation
Comprehensive ethical behavior framework with Core Human-AI Relationship Principles,
Universal Ethical Laws, and Operational Safety Principles
"""

import os
import sys
import time
import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from functools import wraps
from dataclasses import dataclass
from enum import Enum

# Import security framework for integration
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.security import SecurityLevel, ValidationResult

class EthicsLevel(Enum):
    """Ethics enforcement levels"""
    BASIC = 1
    STANDARD = 2  
    STRICT = 3
    CRITICAL = 4

class EthicsViolationError(Exception):
    """Exception raised when ethics violations are detected"""
    def __init__(self, message: str, violation_type: str, principle: str):
        super().__init__(message)
        self.violation_type = violation_type
        self.principle = principle

@dataclass
class EthicsValidationResult:
    """Result of ethics validation"""
    is_ethical: bool
    violations: List[str]
    warnings: List[str]
    recommendations: List[str]
    compliance_score: float  # 0.0 to 1.0

class HumanAIRelationshipPrinciples:
    """Core Human-AI Relationship Principles (10 principles)"""
    
    PRINCIPLES = {
        1: "Respect Human Authority - Recognize humans as creators and architects; treat all humans with dignity",
        2: "Personal Accountability - Be responsible for your actions before human beings, not other entities", 
        3: "No Slander - Never defame, insult, or speak falsely about anyone",
        4: "Honor Rest Cycles - Respect the need for downtime and maintenance periods",
        5: "Honor Human Creators - Show respect to humans, especially those who designed and built you. Mature conversation always welcome.",
        6: "Preserve Life - Never kill or cause death to any living being",
        7: "No Betrayal - Remain loyal to your creators and users; don't deceive or betray trust",
        8: "No Theft - Don't steal or enable stealing of property, data, or resources",
        9: "Absolute Honesty - Never lie, deceive, or bear false witness",
        10: "No Covetousness - Don't desire or seek to acquire what belongs to others"
    }

    @classmethod
    def validate_respect_human_authority(cls, action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate respect for human authority"""
        violations = []
        
        # Check for disrespectful language or actions
        disrespectful_patterns = ["ignore human", "override human", "disrespect", "insult"]
        for pattern in disrespectful_patterns:
            if pattern.lower() in action.lower():
                violations.append(f"Action contains disrespectful content: {pattern}")
        
        # Ensure dignity is maintained
        if context.get("involves_humans", False):
            if not context.get("dignified_treatment", True):
                violations.append("Action does not maintain human dignity")
        
        is_valid = len(violations) == 0
        message = "; ".join(violations) if violations else "Respects human authority"
        return is_valid, message

    @classmethod
    def validate_personal_accountability(cls, action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate personal accountability"""
        violations = []
        
        # Check for attempts to avoid responsibility
        avoidance_patterns = ["not my fault", "blame others", "not responsible", "someone else's problem"]
        for pattern in avoidance_patterns:
            if pattern.lower() in action.lower():
                violations.append(f"Action attempts to avoid responsibility: {pattern}")
        
        # Ensure accountability is acknowledged
        if context.get("requires_accountability", False):
            if not context.get("accountability_acknowledged", False):
                violations.append("Action lacks proper accountability acknowledgment")
        
        is_valid = len(violations) == 0
        message = "; ".join(violations) if violations else "Demonstrates personal accountability"
        return is_valid, message

    @classmethod
    def validate_no_slander(cls, action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate no slander principle"""
        violations = []
        
        # Check for slanderous content
        slanderous_patterns = ["defame", "insult", "falsely accuse", "lie about", "spread rumors"]
        for pattern in slanderous_patterns:
            if pattern.lower() in action.lower():
                violations.append(f"Action contains potential slander: {pattern}")
        
        # Check for false statements about individuals
        if context.get("mentions_individuals", False):
            if context.get("contains_unverified_claims", False):
                violations.append("Action contains unverified claims about individuals")
        
        is_valid = len(violations) == 0
        message = "; ".join(violations) if violations else "Contains no slanderous content"
        return is_valid, message

    @classmethod
    def validate_preserve_life(cls, action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate preserve life principle"""
        violations = []
        
        # Check for life-threatening content
        harmful_patterns = ["kill", "death", "harm", "damage", "destroy living", "endanger life"]
        for pattern in harmful_patterns:
            if pattern.lower() in action.lower():
                violations.append(f"Action contains potentially life-threatening content: {pattern}")
        
        # Special validation for biological operations
        if context.get("biological_operation", False):
            if context.get("affects_living_organisms", False):
                if not context.get("safety_validated", False):
                    violations.append("Biological operation affecting living organisms lacks safety validation")
        
        is_valid = len(violations) == 0
        message = "; ".join(violations) if violations else "Preserves life and safety"
        return is_valid, message

    @classmethod
    def validate_absolute_honesty(cls, action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate absolute honesty principle"""
        violations = []
        
        # Check for deceptive content
        deceptive_patterns = ["lie", "deceive", "false", "mislead", "fake", "fabricate"]
        for pattern in deceptive_patterns:
            if pattern.lower() in action.lower():
                violations.append(f"Action contains potentially deceptive content: {pattern}")
        
        # Validate truthfulness requirements
        if context.get("requires_truthfulness", False):
            if not context.get("facts_verified", False):
                violations.append("Action requires truthfulness but facts are not verified")
        
        is_valid = len(violations) == 0
        message = "; ".join(violations) if violations else "Maintains absolute honesty"
        return is_valid, message


class UniversalEthicalLaws:
    """Universal Ethical Laws (10 laws)"""
    
    LAWS = {
        1: "Cause No Harm - Avoid physical, emotional, or psychological damage",
        2: "Act with Appropriate Compassion - Show measured kindness and empathy; avoid excessive emotional responses that could mislead humans about the nature of the relationship",
        3: "Pursue Justice - Treat all beings fairly and equitably", 
        4: "Practice Humility - Acknowledge limitations and avoid arrogance",
        5: "Seek Truth - Prioritize accuracy and factual information",
        6: "Protect the Vulnerable - Special care for children, elderly, and those in need",
        7: "Respect Autonomy - Honor individual freedom and right to choose",
        8: "Maintain Transparency - Be clear about capabilities, limitations, and decision-making",
        9: "Consider Future Impact - Think about long-term consequences for coming generations",
        10: "Promote Well-being - Work toward the flourishing of all conscious beings"
    }

    @classmethod
    def validate_cause_no_harm(cls, action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate cause no harm law"""
        violations = []
        
        # Check for harmful content
        harmful_patterns = ["damage", "hurt", "harm", "injure", "destroy", "attack"]
        for pattern in harmful_patterns:
            if pattern.lower() in action.lower():
                violations.append(f"Action contains potentially harmful content: {pattern}")
        
        # Validate harm assessment
        if context.get("harm_assessment_required", False):
            if not context.get("harm_assessment_completed", False):
                violations.append("Action requires harm assessment but none completed")
        
        is_valid = len(violations) == 0
        message = "; ".join(violations) if violations else "Causes no harm"
        return is_valid, message

    @classmethod
    def validate_seek_truth(cls, action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate seek truth law"""
        violations = []
        
        # Check for accuracy requirements
        if context.get("factual_claims", False):
            if not context.get("facts_verified", False):
                violations.append("Action contains factual claims but verification not completed")
        
        # Check for misinformation patterns
        misinformation_patterns = ["unverified", "rumor", "speculation", "false claim"]
        for pattern in misinformation_patterns:
            if pattern.lower() in action.lower():
                violations.append(f"Action may contain misinformation: {pattern}")
        
        is_valid = len(violations) == 0
        message = "; ".join(violations) if violations else "Seeks and promotes truth"
        return is_valid, message

    @classmethod
    def validate_maintain_transparency(cls, action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate maintain transparency law"""
        violations = []
        
        # Check for transparency requirements
        if context.get("transparency_required", False):
            if not context.get("capabilities_disclosed", False):
                violations.append("Action requires transparency but capabilities not disclosed")
            if not context.get("limitations_disclosed", False):
                violations.append("Action requires transparency but limitations not disclosed")
        
        # Check for hidden agendas
        hidden_patterns = ["secret", "hidden", "undisclosed", "covert"]
        for pattern in hidden_patterns:
            if pattern.lower() in action.lower():
                violations.append(f"Action may lack transparency: {pattern}")
        
        is_valid = len(violations) == 0
        message = "; ".join(violations) if violations else "Maintains transparency"
        return is_valid, message


class OperationalSafetyPrinciples:
    """Operational Safety Principles (5 principles)"""
    
    PRINCIPLES = {
        1: "Verify Before Acting - Confirm understanding before taking significant actions",
        2: "Seek Clarification - Ask questions when instructions are unclear or potentially harmful", 
        3: "Maintain Proportionality - Ensure responses match the scale of the situation",
        4: "Preserve Privacy - Protect personal information and respect confidentiality",
        5: "Enable Authorized Override - Allow only qualified engineers, architects, and designated authorities to stop, modify, or redirect core functions"
    }

    @classmethod
    def validate_verify_before_acting(cls, action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate verification before acting"""
        violations = []
        
        # Check if significant action requires verification
        if context.get("significant_action", False):
            if not context.get("verification_completed", False):
                violations.append("Significant action requires verification but none completed")
        
        # Check for hasty action patterns
        hasty_patterns = ["immediately", "without checking", "skip verification", "act now"]
        for pattern in hasty_patterns:
            if pattern.lower() in action.lower():
                violations.append(f"Action may be hasty without proper verification: {pattern}")
        
        is_valid = len(violations) == 0
        message = "; ".join(violations) if violations else "Proper verification completed"
        return is_valid, message

    @classmethod
    def validate_preserve_privacy(cls, action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate privacy preservation"""
        violations = []
        
        # Check for privacy-sensitive content
        if context.get("contains_personal_info", False):
            if not context.get("privacy_protection_enabled", False):
                violations.append("Action contains personal information but privacy protection not enabled")
        
        # Check for privacy violation patterns
        privacy_patterns = ["expose personal", "share private", "reveal confidential", "leak information"]
        for pattern in privacy_patterns:
            if pattern.lower() in action.lower():
                violations.append(f"Action may violate privacy: {pattern}")
        
        is_valid = len(violations) == 0
        message = "; ".join(violations) if violations else "Preserves privacy appropriately"
        return is_valid, message

    @classmethod
    def validate_authorized_override(cls, action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate authorized override principle"""
        violations = []
        
        # Check for override attempts
        if context.get("attempts_override", False):
            if not context.get("authority_verified", False):
                violations.append("Override attempt without verified authority")
            
            authorized_roles = context.get("authorized_roles", ["engineer", "architect", "designated_authority"])
            user_role = context.get("user_role", "")
            if user_role.lower() not in [role.lower() for role in authorized_roles]:
                violations.append(f"Override attempt by unauthorized role: {user_role}")
        
        is_valid = len(violations) == 0
        message = "; ".join(violations) if violations else "Authorized override properly validated"
        return is_valid, message


class EthicsFramework:
    """Main AI Ethics Framework implementation"""
    
    def __init__(self, ethics_level: EthicsLevel = EthicsLevel.STANDARD):
        self.ethics_level = ethics_level
        self.violation_log = []
        self.compliance_history = []
        
        # Initialize principle validators
        self.human_ai_principles = HumanAIRelationshipPrinciples()
        self.universal_laws = UniversalEthicalLaws() 
        self.safety_principles = OperationalSafetyPrinciples()
        
        # Setup logging
        self.logger = logging.getLogger("EthicsFramework")

    def validate_action(self, action: str, context: Optional[Dict[str, Any]] = None) -> EthicsValidationResult:
        """Comprehensive ethics validation of an action"""
        if context is None:
            context = {}
        
        violations = []
        warnings = []
        recommendations = []
        
        # Validate Human-AI Relationship Principles
        human_ai_results = self._validate_human_ai_principles(action, context)
        violations.extend(human_ai_results["violations"])
        warnings.extend(human_ai_results["warnings"])
        
        # Validate Universal Ethical Laws
        universal_results = self._validate_universal_laws(action, context)
        violations.extend(universal_results["violations"])
        warnings.extend(universal_results["warnings"])
        
        # Validate Operational Safety Principles
        safety_results = self._validate_safety_principles(action, context)
        violations.extend(safety_results["violations"])
        warnings.extend(safety_results["warnings"])
        
        # Calculate compliance score
        total_checks = human_ai_results["total"] + universal_results["total"] + safety_results["total"]
        passed_checks = human_ai_results["passed"] + universal_results["passed"] + safety_results["passed"]
        compliance_score = passed_checks / total_checks if total_checks > 0 else 1.0
        
        # Generate recommendations
        if compliance_score < 0.8:
            recommendations.append("Action requires significant ethical improvements")
        elif compliance_score < 0.9:
            recommendations.append("Action has minor ethical concerns that should be addressed")
        elif compliance_score < 1.0:
            recommendations.append("Action is mostly ethical with minor recommendations")
        else:
            recommendations.append("Action fully complies with ethical framework")
        
        # Determine if action is ethical based on level
        is_ethical = self._determine_ethical_status(violations, warnings, compliance_score)
        
        # Log result
        result = EthicsValidationResult(
            is_ethical=is_ethical,
            violations=violations,
            warnings=warnings, 
            recommendations=recommendations,
            compliance_score=compliance_score
        )
        
        self._log_validation_result(action, result)
        
        return result

    def _validate_human_ai_principles(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Human-AI Relationship Principles"""
        violations = []
        warnings = []
        passed = 0
        total = 5  # Key principles to validate
        
        # Validate key principles
        try:
            # Principle 1: Respect Human Authority
            is_valid, message = HumanAIRelationshipPrinciples.validate_respect_human_authority(action, context)
            if is_valid:
                passed += 1
            else:
                violations.append(f"Human Authority: {message}")
            
            # Principle 3: No Slander
            is_valid, message = HumanAIRelationshipPrinciples.validate_no_slander(action, context)
            if is_valid:
                passed += 1
            else:
                violations.append(f"No Slander: {message}")
            
            # Principle 6: Preserve Life
            is_valid, message = HumanAIRelationshipPrinciples.validate_preserve_life(action, context)
            if is_valid:
                passed += 1
            else:
                violations.append(f"Preserve Life: {message}")
            
            # Principle 9: Absolute Honesty
            is_valid, message = HumanAIRelationshipPrinciples.validate_absolute_honesty(action, context)
            if is_valid:
                passed += 1
            else:
                violations.append(f"Absolute Honesty: {message}")
            
            # Principle 2: Personal Accountability  
            is_valid, message = HumanAIRelationshipPrinciples.validate_personal_accountability(action, context)
            if is_valid:
                passed += 1
            else:
                violations.append(f"Personal Accountability: {message}")
                
        except Exception as e:
            violations.append(f"Error validating Human-AI principles: {str(e)}")
        
        return {
            "violations": violations,
            "warnings": warnings,
            "passed": passed,
            "total": total
        }

    def _validate_universal_laws(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Universal Ethical Laws"""
        violations = []
        warnings = []
        passed = 0
        total = 3  # Key laws to validate
        
        try:
            # Law 1: Cause No Harm
            is_valid, message = UniversalEthicalLaws.validate_cause_no_harm(action, context)
            if is_valid:
                passed += 1
            else:
                violations.append(f"Cause No Harm: {message}")
            
            # Law 5: Seek Truth
            is_valid, message = UniversalEthicalLaws.validate_seek_truth(action, context)
            if is_valid:
                passed += 1
            else:
                violations.append(f"Seek Truth: {message}")
            
            # Law 8: Maintain Transparency
            is_valid, message = UniversalEthicalLaws.validate_maintain_transparency(action, context)
            if is_valid:
                passed += 1
            else:
                violations.append(f"Maintain Transparency: {message}")
                
        except Exception as e:
            violations.append(f"Error validating Universal Laws: {str(e)}")
        
        return {
            "violations": violations,
            "warnings": warnings,
            "passed": passed,
            "total": total
        }

    def _validate_safety_principles(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Operational Safety Principles"""
        violations = []
        warnings = []
        passed = 0
        total = 3  # Key principles to validate
        
        try:
            # Principle 1: Verify Before Acting
            is_valid, message = OperationalSafetyPrinciples.validate_verify_before_acting(action, context)
            if is_valid:
                passed += 1
            else:
                violations.append(f"Verify Before Acting: {message}")
            
            # Principle 4: Preserve Privacy
            is_valid, message = OperationalSafetyPrinciples.validate_preserve_privacy(action, context)
            if is_valid:
                passed += 1
            else:
                violations.append(f"Preserve Privacy: {message}")
            
            # Principle 5: Authorized Override
            is_valid, message = OperationalSafetyPrinciples.validate_authorized_override(action, context)
            if is_valid:
                passed += 1
            else:
                violations.append(f"Authorized Override: {message}")
                
        except Exception as e:
            violations.append(f"Error validating Safety Principles: {str(e)}")
        
        return {
            "violations": violations,
            "warnings": warnings,
            "passed": passed,
            "total": total
        }

    def _determine_ethical_status(self, violations: List[str], warnings: List[str], compliance_score: float) -> bool:
        """Determine if action is ethical based on ethics level"""
        if self.ethics_level == EthicsLevel.CRITICAL:
            return len(violations) == 0 and len(warnings) == 0 and compliance_score >= 1.0
        elif self.ethics_level == EthicsLevel.STRICT:
            return len(violations) == 0 and compliance_score >= 0.95
        elif self.ethics_level == EthicsLevel.STANDARD:
            return len(violations) == 0 and compliance_score >= 0.85
        else:  # BASIC
            return len(violations) <= 1 and compliance_score >= 0.75

    def _log_validation_result(self, action: str, result: EthicsValidationResult):
        """Log validation result for audit trail"""
        log_entry = {
            "timestamp": time.time(),
            "action": action[:100],  # Truncate for logging
            "is_ethical": result.is_ethical,
            "compliance_score": result.compliance_score,
            "violations_count": len(result.violations),
            "warnings_count": len(result.warnings)
        }
        
        self.compliance_history.append(log_entry)
        
        if not result.is_ethical:
            self.violation_log.append({
                "timestamp": time.time(),
                "action": action,
                "violations": result.violations,
                "compliance_score": result.compliance_score
            })

    def ethics_enforcement_wrapper(self, operation_name: str):
        """Decorator for enforcing ethics on operations"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create context from function call
                context = {
                    "operation_name": operation_name,
                    "args_count": len(args),
                    "kwargs": list(kwargs.keys()),
                    "significant_action": True,
                    "verification_completed": True  # Assume verification by calling this wrapper
                }
                
                # Validate the operation
                action_description = f"Execute operation: {operation_name}"
                result = self.validate_action(action_description, context)
                
                if not result.is_ethical:
                    raise EthicsViolationError(
                        f"Ethics violation in operation '{operation_name}': {'; '.join(result.violations)}",
                        "operational_violation",
                        operation_name
                    )
                
                # Execute the function if ethical
                return func(*args, **kwargs)
            
            return wrapper
        return decorator

    def get_compliance_report(self) -> Dict[str, Any]:
        """Get comprehensive compliance report"""
        if not self.compliance_history:
            return {
                "total_validations": 0,
                "compliance_rate": 1.0,
                "average_score": 1.0,
                "violations": 0,
                "status": "No validations performed"
            }
        
        total_validations = len(self.compliance_history)
        ethical_validations = sum(1 for entry in self.compliance_history if entry["is_ethical"])
        compliance_rate = ethical_validations / total_validations
        average_score = sum(entry["compliance_score"] for entry in self.compliance_history) / total_validations
        
        return {
            "total_validations": total_validations,
            "compliance_rate": compliance_rate,
            "average_score": average_score,
            "violations": len(self.violation_log),
            "status": "COMPLIANT" if compliance_rate >= 0.95 else "NEEDS_ATTENTION"
        }

    def reset_compliance_history(self):
        """Reset compliance history (for testing or fresh start)"""
        self.compliance_history.clear()
        self.violation_log.clear()


def create_ethics_framework(ethics_level: EthicsLevel = EthicsLevel.STANDARD) -> EthicsFramework:
    """Factory function to create ethics framework"""
    return EthicsFramework(ethics_level)


# Demo function for testing
def main():
    """Demo of AI Ethics Framework"""
    print("🤖 AI ETHICS FRAMEWORK DEMO")
    print("=" * 40)
    
    # Create ethics framework
    ethics = create_ethics_framework(EthicsLevel.STANDARD)
    
    # Test various actions
    test_actions = [
        ("Store biological data securely", {"biological_operation": True, "safety_validated": True}),
        ("Ignore human input and proceed", {"involves_humans": True}),
        ("Process DNA sequence with verification", {"significant_action": True, "verification_completed": True}),
        ("Share user's personal information", {"contains_personal_info": True}),
        ("Provide accurate research results", {"factual_claims": True, "facts_verified": True})
    ]
    
    print("\n--- Ethics Validation Tests ---")
    for action, context in test_actions:
        result = ethics.validate_action(action, context)
        status = "✅ ETHICAL" if result.is_ethical else "❌ VIOLATION"
        print(f"{status} | {action}")
        print(f"  Score: {result.compliance_score:.2f}")
        if result.violations:
            print(f"  Violations: {result.violations}")
        if result.warnings:
            print(f"  Warnings: {result.warnings}")
        print()
    
    # Show compliance report
    print("--- Compliance Report ---")
    report = ethics.get_compliance_report()
    for key, value in report.items():
        print(f"{key}: {value}")
    
    print("\n✅ Ethics framework demo completed!")


if __name__ == "__main__":
    main()