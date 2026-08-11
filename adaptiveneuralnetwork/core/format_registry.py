import csv
import json
from dataclasses import dataclass
from enum import Enum
from io import StringIO
from typing import Any


class DataFormat(Enum):
    JSON = "json"
    XML = "xml"
    HTML = "html"
    MARKDOWN = "markdown"
    CSV = "csv"
    PLAIN_TEXT = "plain_text"

@dataclass
class FormatInfo:
    detected_format: DataFormat
    confidence: float

@dataclass
class NormalizedPacket:
    content_type: str
    fields: dict[str, Any]
    raw_text: str
    record_count: int
    flat_text: str

    def to_flat_text(self) -> str:
        return self.flat_text

class FormatRegistry:
    def __init__(self):
        pass

    def detect_format(self, data: str, mime_type: str | None = None) -> FormatInfo:
        if mime_type is not None:
            mime_lower = mime_type.lower()
            if "json" in mime_lower:
                return FormatInfo(DataFormat.JSON, 1.0)
            if "xml" in mime_lower:
                return FormatInfo(DataFormat.XML, 1.0)
            if "html" in mime_lower:
                return FormatInfo(DataFormat.HTML, 1.0)
            if "markdown" in mime_lower or "md" in mime_lower:
                return FormatInfo(DataFormat.MARKDOWN, 1.0)
            if "csv" in mime_lower:
                return FormatInfo(DataFormat.CSV, 1.0)
            if "text" in mime_lower:
                return FormatInfo(DataFormat.PLAIN_TEXT, 0.8)

        # Content-based heuristics
        stripped = data.strip()
        if not stripped:
            return FormatInfo(DataFormat.PLAIN_TEXT, 1.0)

        if (stripped.startswith('{') and stripped.endswith('}')) or (stripped.startswith('[') and stripped.endswith(']')):
            return FormatInfo(DataFormat.JSON, 0.9)
        if stripped.startswith('<?xml') or stripped.startswith('<root') or (stripped.startswith('<') and stripped.endswith('>') and '<xml' in stripped):
            return FormatInfo(DataFormat.XML, 0.9)
        if stripped.startswith('<!DOCTYPE html>') or stripped.startswith('<html>') or '<body>' in stripped:
            return FormatInfo(DataFormat.HTML, 0.9)
        if stripped.startswith('# ') or '**' in stripped or '## ' in stripped or '\n\n' in stripped and ('#' in stripped or '*' in stripped):
            return FormatInfo(DataFormat.MARKDOWN, 0.8)
        if ',' in stripped and '\n' in stripped:
            # Let's count if most lines have same number of commas
            lines = [line for line in stripped.split('\n') if line.strip()]
            if len(lines) > 1:
                commas = [line.count(',') for line in lines]
                if len(set(commas)) == 1 and commas[0] > 0:
                    return FormatInfo(DataFormat.CSV, 0.8)
            return FormatInfo(DataFormat.CSV, 0.5)

        return FormatInfo(DataFormat.PLAIN_TEXT, 0.5)

    def normalize(self, data: str, source_format: DataFormat | None = None) -> NormalizedPacket:
        if source_format is None:
            source_format = self.detect_format(data).detected_format

        if source_format == DataFormat.JSON:
            try:
                parsed = json.loads(data)
                if isinstance(parsed, dict):
                    flat_items = []
                    for k, v in parsed.items():
                        flat_items.append(f"{k} is {v}")
                    flat_text = " ".join(flat_items)
                    fields = parsed
                elif isinstance(parsed, list):
                    flat_text = " ".join([str(item) for item in parsed])
                    fields = {"list": parsed}
                else:
                    flat_text = str(parsed)
                    fields = {"value": parsed}
                return NormalizedPacket(
                    content_type="structured",
                    fields=fields,
                    raw_text=data,
                    record_count=1,
                    flat_text=flat_text
                )
            except Exception:
                pass

        if source_format == DataFormat.CSV:
            try:
                reader = csv.DictReader(StringIO(data))
                records = list(reader)
                flat_text = " ".join([" ".join([f"{k} {v}" for k, v in record.items()]) for record in records])
                return NormalizedPacket(
                    content_type="tabular",
                    fields={"records": records},
                    raw_text=data,
                    record_count=len(records),
                    flat_text=flat_text
                )
            except Exception:
                pass

        # Default fallback for PLAIN_TEXT, HTML, XML, MARKDOWN
        content_type = "text"
        if source_format == DataFormat.HTML:
            content_type = "html"
        elif source_format == DataFormat.XML:
            content_type = "xml"
        elif source_format == DataFormat.MARKDOWN:
            content_type = "markdown"

        return NormalizedPacket(
            content_type=content_type,
            fields={},
            raw_text=data,
            record_count=1,
            flat_text=data
        )

    def can_parse(self, format_name: str) -> bool:
        name_lower = format_name.lower()
        for f in DataFormat:
            if f.value == name_lower:
                return True
        return False
