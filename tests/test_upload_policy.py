from blyskawica_app.backend.upload_policy import (
    MAX_MEDIA_STORAGE_BYTES,
    MAX_MEDIA_UPLOAD_BYTES,
    MEDIA_UPLOAD_CHUNK_BYTES,
    exceeds_media_storage_limit,
    exceeds_media_upload_limit,
    media_storage_usage_bytes,
)


def test_media_upload_limit_accepts_exact_cap_and_rejects_next_byte() -> None:
    assert not exceeds_media_upload_limit(MAX_MEDIA_UPLOAD_BYTES)
    assert exceeds_media_upload_limit(MAX_MEDIA_UPLOAD_BYTES + 1)


def test_media_upload_chunks_are_bounded() -> None:
    assert 0 < MEDIA_UPLOAD_CHUNK_BYTES < MAX_MEDIA_UPLOAD_BYTES


def test_media_storage_limit_accepts_exact_cap_and_rejects_next_byte() -> None:
    assert not exceeds_media_storage_limit(MAX_MEDIA_STORAGE_BYTES - 10, 10)
    assert exceeds_media_storage_limit(MAX_MEDIA_STORAGE_BYTES - 10, 11)


def test_media_storage_usage_counts_regular_files(tmp_path) -> None:
    nested_directory = tmp_path / "nested"
    nested_directory.mkdir()
    (tmp_path / "one.bin").write_bytes(b"one")
    (nested_directory / "two.bin").write_bytes(b"two")

    assert media_storage_usage_bytes(tmp_path) == (6, True)
