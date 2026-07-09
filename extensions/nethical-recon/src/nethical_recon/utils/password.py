"""Password validation utilities for user authentication."""

import re
from dataclasses import dataclass


@dataclass
class PasswordValidationResult:
    """Result of password validation."""

    is_valid: bool
    errors: list[str]
    strength_score: int  # 0-100


def validate_password_strength(password: str, min_length: int = 12) -> PasswordValidationResult:
    """
    Validate password strength according to security requirements.

    Requirements:
    - Minimum length (default: 12 characters)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - No common patterns

    Args:
        password: Password to validate
        min_length: Minimum password length (default: 12)

    Returns:
        PasswordValidationResult with validation details
    """
    errors = []
    strength_score = 0

    # Check minimum length
    if len(password) < min_length:
        errors.append(f"Password must be at least {min_length} characters long")
    else:
        strength_score += 25

    # Check for uppercase letters
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    else:
        strength_score += 20

    # Check for lowercase letters
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    else:
        strength_score += 20

    # Check for digits
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")
    else:
        strength_score += 20

    # Check for special characters
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        errors.append("Password must contain at least one special character (!@#$%^&*()_+-=[]{}; etc.)")
    else:
        strength_score += 15

    # Check for common patterns (simple check)
    common_patterns = [
        "password",
        "12345",
        "qwerty",
        "admin",
        "letmein",
        "welcome",
        "monkey",
        "dragon",
    ]

    password_lower = password.lower()
    for pattern in common_patterns:
        if pattern in password_lower:
            errors.append(f"Password contains common pattern: {pattern}")
            strength_score = max(0, strength_score - 30)
            break

    # Bonus for extra length
    if len(password) >= 16:
        strength_score = min(100, strength_score + 10)

    is_valid = len(errors) == 0

    return PasswordValidationResult(is_valid=is_valid, errors=errors, strength_score=strength_score)


def generate_password_requirements_message() -> str:
    """
    Generate a user-friendly message describing password requirements.

    Returns:
        Human-readable password requirements
    """
    return (
        "Password requirements:\n"
        "- Minimum 12 characters\n"
        "- At least one uppercase letter (A-Z)\n"
        "- At least one lowercase letter (a-z)\n"
        "- At least one digit (0-9)\n"
        "- At least one special character (!@#$%^&*()_+-=[]{}; etc.)\n"
        "- Must not contain common patterns (e.g., 'password', '12345', 'admin')\n"
        "- Recommended: 16+ characters for enhanced security"
    )
