"""
Plugins Module

Extensible plugins for additional security checks and compliance.
"""

from .cisa_bod_checker import BODCheckResult, CISABODChecker

__all__ = ["CISABODChecker", "BODCheckResult"]
