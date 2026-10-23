from blyskawica_app.backend.upload_policy import (
    MAX_MEDIA_UPLOAD_BYTES,
    MEDIA_UPLOAD_CHUNK_BYTES,
    exceeds_media_upload_limit,
)


def test_media_upload_limit_accepts_exact_cap_and_rejects_next_byte() -> None:
    assert not exceeds_media_upload_limit(MAX_MEDIA_UPLOAD_BYTES)
    assert exceeds_media_upload_limit(MAX_MEDIA_UPLOAD_BYTES + 1)


def test_media_upload_chunks_are_bounded() -> None:
    assert 0 < MEDIA_UPLOAD_CHUNK_BYTES < MAX_MEDIA_UPLOAD_BYTES
