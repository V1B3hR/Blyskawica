"""
Plugin Verifier
Security verification and validation for marketplace plugins
"""

import ast
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class VerificationStatus(Enum):
    """Plugin verification status"""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


@dataclass
class SecurityCheck:
    """Security check result"""

    check_name: str
    passed: bool
    severity: str  # info, warning, error, critical
    message: str
    details: dict[str, Any]


@dataclass
class VerificationResult:
    """Plugin verification result"""

    plugin_id: UUID
    status: VerificationStatus
    checks: list[SecurityCheck]
    verified_at: datetime
    verifier: str
    notes: str


class PluginVerifier:
    """
    Plugin security verifier

    Features:
    - Static code analysis
    - Dependency scanning
    - Security checks
    - Best practices validation
    """

    def __init__(self):
        """Initialize plugin verifier"""
        self._verification_results: dict[UUID, VerificationResult] = {}

    def verify_plugin(self, plugin_id: UUID, plugin_code: str, dependencies: list[str]) -> VerificationResult:
        """
        Verify a plugin for security and best practices

        Args:
            plugin_id: Plugin ID
            plugin_code: Plugin source code
            dependencies: List of dependencies

        Returns:
            Verification result
        """
        checks: list[SecurityCheck] = []

        # Run all security checks
        checks.extend(self._check_dangerous_imports(plugin_code))
        checks.extend(self._check_code_injection(plugin_code))
        checks.extend(self._check_file_operations(plugin_code))
        checks.extend(self._check_network_operations(plugin_code))
        checks.extend(self._check_dependencies(dependencies))
        checks.extend(self._check_best_practices(plugin_code))

        # Determine overall status
        critical_failures = [c for c in checks if not c.passed and c.severity == "critical"]
        errors = [c for c in checks if not c.passed and c.severity == "error"]
        warnings = [c for c in checks if not c.passed and c.severity == "warning"]

        if critical_failures:
            status = VerificationStatus.FAILED
        elif errors:
            status = VerificationStatus.NEEDS_REVIEW
        elif warnings:
            status = VerificationStatus.NEEDS_REVIEW
        else:
            status = VerificationStatus.PASSED

        result = VerificationResult(
            plugin_id=plugin_id,
            status=status,
            checks=checks,
            verified_at=datetime.now(),
            verifier="automated",
            notes=self._generate_notes(checks),
        )

        self._verification_results[plugin_id] = result
        return result

    def _check_dangerous_imports(self, code: str) -> list[SecurityCheck]:
        """Check for dangerous imports using AST analysis."""
        checks = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [
                SecurityCheck(
                    check_name="syntax_error",
                    passed=False,
                    severity="critical",
                    message=f"Syntax error in plugin code: {e}",
                    details={"error": str(e)},
                )
            ]

        dangerous_found = set()
        dangerous_imports = {"os", "subprocess", "sys", "shutil"}
        dangerous_builtins = {"eval", "exec", "__import__", "compile"}

        # Walk the AST to find dangerous patterns
        for node in ast.walk(tree):
            # Check for dangerous imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in dangerous_imports:
                        dangerous_found.add(f"import {alias.name}")

            elif isinstance(node, ast.ImportFrom):
                if node.module in dangerous_imports:
                    dangerous_found.add(f"from {node.module} import ...")

            # Check for dangerous function calls
            elif isinstance(node, ast.Call):
                # Direct calls to eval, exec, etc.
                if isinstance(node.func, ast.Name):
                    if node.func.id in dangerous_builtins:
                        dangerous_found.add(f"{node.func.id}()")

                # Attribute calls like os.system, subprocess.call
                elif isinstance(node.func, ast.Attribute):
                    attr = node.func.attr
                    if attr in {"system", "popen", "call", "run", "Popen"}:
                        dangerous_found.add(f"*.{attr}()")

        # Generate security checks based on findings
        if dangerous_found:
            for pattern in dangerous_found:
                checks.append(
                    SecurityCheck(
                        check_name="dangerous_code",
                        passed=False,
                        severity="critical",
                        message=f"Dangerous pattern detected: {pattern}",
                        details={"pattern": pattern},
                    )
                )
        else:
            checks.append(
                SecurityCheck(
                    check_name="dangerous_imports",
                    passed=True,
                    severity="info",
                    message="No dangerous imports or patterns found",
                    details={},
                )
            )

        return checks

    def _check_code_injection(self, code: str) -> list[SecurityCheck]:
        """Check for code injection vulnerabilities using AST analysis."""
        checks = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            # Already handled in _check_dangerous_imports
            return []

        injection_found = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for eval/exec/compile calls
                if isinstance(node.func, ast.Name):
                    if node.func.id in {"eval", "exec", "compile"}:
                        injection_found.add(node.func.id)

                # Check for dynamic attribute access that might be used for injection
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in {"__import__", "getattr", "setattr"}:
                        injection_found.add(node.func.attr)

        # Generate security checks
        if injection_found:
            for func_name in injection_found:
                checks.append(
                    SecurityCheck(
                        check_name="code_injection",
                        passed=False,
                        severity="critical",
                        message=f"Potential code injection: {func_name}() function",
                        details={"function": func_name},
                    )
                )
        else:
            checks.append(
                SecurityCheck(
                    check_name="code_injection",
                    passed=True,
                    severity="info",
                    message="No code injection patterns found",
                    details={},
                )
            )

        return checks

    def _check_file_operations(self, code: str) -> list[SecurityCheck]:
        """Check for unsafe file operations"""
        file_patterns = [
            ("open(", "File operations"),
            ("os.remove", "File deletion"),
            ("os.unlink", "File deletion"),
            ("shutil.rmtree", "Directory deletion"),
        ]

        checks = []
        for pattern, description in file_patterns:
            if pattern in code:
                checks.append(
                    SecurityCheck(
                        check_name="file_operations",
                        passed=False,
                        severity="warning",
                        message=f"File operation detected: {description}",
                        details={"pattern": pattern},
                    )
                )

        return checks

    def _check_network_operations(self, code: str) -> list[SecurityCheck]:
        """Check for network operations"""
        network_patterns = [
            ("socket.", "Raw socket operations"),
            ("urllib.request", "URL requests"),
            ("requests.", "HTTP requests"),
        ]

        checks = []
        for pattern, description in network_patterns:
            if pattern in code:
                checks.append(
                    SecurityCheck(
                        check_name="network_operations",
                        passed=True,
                        severity="info",
                        message=f"Network operation: {description}",
                        details={"pattern": pattern},
                    )
                )

        return checks

    def _check_dependencies(self, dependencies: list[str]) -> list[SecurityCheck]:
        """Check plugin dependencies"""
        checks = []

        # Check for known vulnerable packages (simplified)
        known_vulnerable = ["pickle", "yaml.load"]

        for dep in dependencies:
            if any(vuln in dep.lower() for vuln in known_vulnerable):
                checks.append(
                    SecurityCheck(
                        check_name="dependencies",
                        passed=False,
                        severity="error",
                        message=f"Potentially vulnerable dependency: {dep}",
                        details={"dependency": dep},
                    )
                )

        # Check dependency count
        if len(dependencies) > 20:
            checks.append(
                SecurityCheck(
                    check_name="dependencies",
                    passed=False,
                    severity="warning",
                    message=f"High number of dependencies ({len(dependencies)})",
                    details={"count": len(dependencies)},
                )
            )

        if not checks:
            checks.append(
                SecurityCheck(
                    check_name="dependencies",
                    passed=True,
                    severity="info",
                    message=f"{len(dependencies)} dependencies checked",
                    details={"count": len(dependencies)},
                )
            )

        return checks

    def _check_best_practices(self, code: str) -> list[SecurityCheck]:
        """Check for best practices"""
        checks = []

        # Check for documentation
        if '"""' not in code and "'''" not in code:
            checks.append(
                SecurityCheck(
                    check_name="best_practices",
                    passed=False,
                    severity="warning",
                    message="Missing documentation strings",
                    details={},
                )
            )

        # Check for type hints
        if "def " in code and "->" not in code:
            checks.append(
                SecurityCheck(
                    check_name="best_practices",
                    passed=False,
                    severity="info",
                    message="Consider adding type hints",
                    details={},
                )
            )

        # Check for error handling
        if "try:" not in code and "except" not in code:
            checks.append(
                SecurityCheck(
                    check_name="best_practices",
                    passed=False,
                    severity="warning",
                    message="Consider adding error handling",
                    details={},
                )
            )

        return checks

    def _generate_notes(self, checks: list[SecurityCheck]) -> str:
        """Generate verification notes"""
        critical = [c for c in checks if not c.passed and c.severity == "critical"]
        errors = [c for c in checks if not c.passed and c.severity == "error"]
        warnings = [c for c in checks if not c.passed and c.severity == "warning"]

        notes = []

        if critical:
            notes.append(f"CRITICAL: {len(critical)} critical issues found")

        if errors:
            notes.append(f"ERROR: {len(errors)} errors found")

        if warnings:
            notes.append(f"WARNING: {len(warnings)} warnings found")

        if not (critical or errors or warnings):
            notes.append("All checks passed")

        return "; ".join(notes)

    def get_verification_result(self, plugin_id: UUID) -> VerificationResult | None:
        """Get verification result for a plugin"""
        return self._verification_results.get(plugin_id)

    def is_verified(self, plugin_id: UUID) -> bool:
        """Check if plugin is verified"""
        result = self._verification_results.get(plugin_id)
        return result.status == VerificationStatus.PASSED if result else False
