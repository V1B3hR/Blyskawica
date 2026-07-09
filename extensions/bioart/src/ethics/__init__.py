#!/usr/bin/env python3
"""
AI Ethics Framework for Bioart DNA Programming Language
Comprehensive ethical behavior and safety implementation
"""

__version__ = "1.0.0"
__author__ = "Bioart AI Ethics Implementation"

# Import main ethics components
from .ai_ethics_framework import (
    EthicsFramework,
    EthicsViolationError,
    EthicsLevel,
    EthicsValidationResult,
    HumanAIRelationshipPrinciples,
    UniversalEthicalLaws,
    OperationalSafetyPrinciples
)

__all__ = [
    'EthicsFramework',
    'EthicsViolationError', 
    'EthicsLevel',
    'EthicsValidationResult',
    'HumanAIRelationshipPrinciples',
    'UniversalEthicalLaws',
    'OperationalSafetyPrinciples'
]