"""Bounded-upload policy for the legacy compatibility API."""

import stat
from pathlib import Path

MAX_MEDIA_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_MEDIA_STORAGE_BYTES = 250 * 1024 * 1024
MEDIA_UPLOAD_CHUNK_BYTES = 64 * 1024
MEDIA_STORAGE_ENTRY_LIMIT = 10_000


def exceeds_media_upload_limit(total_bytes: int) -> bool:
    """Reject uploads once their streamed byte count exceeds the hard cap."""
    return total_bytes > MAX_MEDIA_UPLOAD_BYTES


def exceeds_media_storage_limit(current_bytes: int, incoming_bytes: int) -> bool:
    """Reject uploads that would push the complete store over its hard cap."""
    return current_bytes + incoming_bytes > MAX_MEDIA_STORAGE_BYTES


def media_storage_usage_bytes(storage_root: Path) -> tuple[int, bool]:
    """Return a bounded regular-file size scan without following symbolic links."""
    if not storage_root.exists():
        return 0, True

    total_bytes = 0
    inspected_entries = 0
    try:
        paths = storage_root.rglob("*")
        for path in paths:
            inspected_entries += 1
            if inspected_entries > MEDIA_STORAGE_ENTRY_LIMIT:
                return total_bytes, False
            metadata = path.lstat()
            if stat.S_ISLNK(metadata.st_mode):
                return total_bytes, False
            if stat.S_ISREG(metadata.st_mode):
                total_bytes += metadata.st_size
    except OSError:
        return total_bytes, False
    return total_bytes, True
