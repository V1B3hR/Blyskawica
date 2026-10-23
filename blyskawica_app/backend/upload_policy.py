"""Bounded-upload policy for the legacy compatibility API."""

MAX_MEDIA_UPLOAD_BYTES = 25 * 1024 * 1024
MEDIA_UPLOAD_CHUNK_BYTES = 64 * 1024


def exceeds_media_upload_limit(total_bytes: int) -> bool:
    """Reject uploads once their streamed byte count exceeds the hard cap."""
    return total_bytes > MAX_MEDIA_UPLOAD_BYTES
