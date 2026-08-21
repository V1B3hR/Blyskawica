"""
[Module: Deep Sleep LogHub Parser & Hard Anomaly Detector for Win 11]
Implements a strict, standardized LogHub-style log parsing architecture
for Windows 11 system events, DirectX/WGSL shader errors, and Tauri IPC latency spikes.
Enforces the Zero-Sycophancy Hard Anomaly Policy (Never sugarcoating system defects).
"""

import hashlib
import json
import logging
import re
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(name)s: %(message)s")
logger = logging.getLogger("loghub_parser")


class LogCategory(str, Enum):
    SHADER_ERROR = "SHADER_COMPILATION_ERROR"
    TAURI_IPC_ANOMALY = "TAURI_IPC_ANOMALY"
    WINDOWS_EVENT_CRASH = "WINDOWS_EVENT_CRASH"
    MEMORY_PRESSURE_LEAK = "MEMORY_PRESSURE_LEAK"
    THREAD_DEADLOCK = "THREAD_DEADLOCK"
    SYSTEM_INFO = "SYSTEM_INFO"


@dataclass
class LogHubParsedEvent:
    timestamp: float
    source: str  # TAURI_CORE, GPU_WEBVIEW2, DIRECTX, WIN_EVENT_LOG, RUST_IPC
    level: str   # CRITICAL, ERROR, WARNING, INFO
    category: LogCategory
    template_id: str
    raw_message: str
    structured_params: Dict[str, Any] = field(default_factory=dict)
    is_hard_anomaly: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value
        return d


@dataclass
class HardAnomalyReport:
    total_logs_scanned: int
    hard_anomalies_detected: int
    critical_shader_errors: int
    ipc_failures: int
    memory_leaks: int
    integrity_status: str  # "STABLE_CLEAN" or "HARD_ANOMALIES_DETECTED"
    detailed_anomalies: List[Dict[str, Any]] = field(default_factory=list)
    remediation_suggestions: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DeepSleepLogHubParser:
    """
    Rigorously parses raw runtime logs and diagnostics during DEEP_SLEEP,
    extracting hard anomalies without masking defects or latency degradations.
    """
    def __init__(self):
        # LogHub-style regex signatures for Windows 11, DirectX, WebGL, and Tauri IPC
        self.signatures = [
            (
                re.compile(r"(DXGI_ERROR_\w+|D3D12_ERROR_\w+|Shader compilation failed|VK_ERROR_\w+|GL_OUT_OF_MEMORY|WGPU_ERROR)", re.IGNORECASE),
                LogCategory.SHADER_ERROR,
                "CRITICAL",
                True
            ),
            (
                re.compile(r"(IPC timeout|IPC channel closed|Broken pipe|Payload serialization error|IPC latency >\s*(\d+)ms)", re.IGNORECASE),
                LogCategory.TAURI_IPC_ANOMALY,
                "CRITICAL",
                True
            ),
            (
                re.compile(r"(EventID:\s*(1000|1001|1002)|Application Hang|WerFault\.exe|Process terminated unexpectedly)", re.IGNORECASE),
                LogCategory.WINDOWS_EVENT_CRASH,
                "CRITICAL",
                True
            ),
            (
                re.compile(r"(Memory allocation failed|High working set growth|VRAM allocation exceeded|OOM killer)", re.IGNORECASE),
                LogCategory.MEMORY_PRESSURE_LEAK,
                "CRITICAL",
                True
            ),
            (
                re.compile(r"(Deadlock detected in tokio worker|Thread hung waiting on lock)", re.IGNORECASE),
                LogCategory.THREAD_DEADLOCK,
                "CRITICAL",
                True
            ),
        ]

    def extract_template_id(self, message: str) -> str:
        """Generates a Drain-style template hash by masking numbers and UUIDs."""
        normalized = re.sub(r"\b0x[0-9a-fA-F]+\b", "<HEX>", message)
        normalized = re.sub(r"\b\d+\b", "<NUM>", normalized)
        normalized = re.sub(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", "<UUID>", normalized)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:8]

    def parse_line(self, line: str, default_source: str = "TAURI_CORE") -> LogHubParsedEvent:
        """Parses a single log line into a standardized LogHub event."""
        line_clean = line.strip()
        matched_cat = LogCategory.SYSTEM_INFO
        matched_level = "INFO"
        is_hard = False
        params = {}

        for pattern, cat, level, hard_flag in self.signatures:
            m = pattern.search(line_clean)
            if m:
                matched_cat = cat
                matched_level = level
                is_hard = hard_flag
                params["matched_token"] = m.group(0)
                break

        template_id = self.extract_template_id(line_clean)

        return LogHubParsedEvent(
            timestamp=time.time(),
            source=default_source,
            level=matched_level,
            category=matched_cat,
            template_id=template_id,
            raw_message=line_clean,
            structured_params=params,
            is_hard_anomaly=is_hard
        )

    def process_log_batch(self, log_lines: List[str], source: str = "TAURI_CORE") -> HardAnomalyReport:
        """
        Processes a batch of logs and compiles an unvarnished Hard Anomaly Report.
        """
        parsed_events = [self.parse_line(l, default_source=source) for l in log_lines if l.strip()]

        hard_anomalies = [e for e in parsed_events if e.is_hard_anomaly]

        shader_errors = sum(1 for e in hard_anomalies if e.category == LogCategory.SHADER_ERROR)
        ipc_failures = sum(1 for e in hard_anomalies if e.category == LogCategory.TAURI_IPC_ANOMALY)
        memory_leaks = sum(1 for e in hard_anomalies if e.category == LogCategory.MEMORY_PRESSURE_LEAK)

        detailed = []
        remediations = []

        for e in hard_anomalies:
            detailed.append({
                "source": e.source,
                "category": e.category.value,
                "level": e.level,
                "template_id": e.template_id,
                "message": e.raw_message,
                "details": e.structured_params
            })

        if shader_errors > 0:
            remediations.append("Zalecenie: Przełączenie akceleracji WebView2 z DirectX na tryb bezpieczny WARP lub optymalizacja shaderów WGSL.")
        if ipc_failures > 0:
            remediations.append("Zalecenie: Zwiększenie rozmiaru kolejki kanału tokio mpsc w blyskawica_core i redukcja częstotliwości payloadu IPC.")
        if memory_leaks > 0:
            remediations.append("Zalecenie: Wywołanie natywnego GC na buforach HNSW i zresetowanie alokatora mimalloc.")

        status = "STABLE_CLEAN" if len(hard_anomalies) == 0 else "HARD_ANOMALIES_DETECTED"

        return HardAnomalyReport(
            total_logs_scanned=len(parsed_events),
            hard_anomalies_detected=len(hard_anomalies),
            critical_shader_errors=shader_errors,
            ipc_failures=ipc_failures,
            memory_leaks=memory_leaks,
            integrity_status=status,
            detailed_anomalies=detailed,
            remediation_suggestions=remediations
        )

    def export_audit_report(self, report: HardAnomalyReport, out_path: Optional[Path] = None) -> bool:
        """Persists the Hard Anomaly Report into integrity_audit_latest.json."""
        if out_path is None:
            out_path = Path(__file__).resolve().parent.parent.parent / "integrity_audit_latest.json"

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info("⚡ Zapisano Raport Audytu Twardych Anomalii do: %s (Status: %s)", out_path, report.integrity_status)
            return True
        except Exception as e:
            logger.error("Błąd zapisu raportu audytu: %s", e)
            return False
