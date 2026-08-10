"""Observability Module

Comprehensive observability for Nethical governance system including:
- Metrics (Prometheus-compatible)
- Tracing (OpenTelemetry)
- Logging with PII sanitization
- Alert rules
"""

from .alerts import Alert, AlertRuleManager, AlertSeverity
from .metrics import MetricsCollector, get_metrics_collector, record_action, record_violation
from .sanitization import LogSanitizer, get_sanitizer, sanitize_dict, sanitize_log
from .tracing import TracingManager, get_tracer, trace_span

__all__ = [
    'MetricsCollector',
    'get_metrics_collector',
    'record_action',
    'record_violation',
    'TracingManager',
    'get_tracer',
    'trace_span',
    'LogSanitizer',
    'get_sanitizer',
    'sanitize_log',
    'sanitize_dict',
    'AlertRuleManager',
    'AlertSeverity',
    'Alert',
]
