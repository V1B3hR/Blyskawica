import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock

from download_extensions import safe_extract_zip


class TestSafeExtractZip(unittest.TestCase):
    def test_extracts_once(self):
        archive = Mock()
        archive.infolist.return_value = []
        destination = Path("extensions")

        safe_extract_zip(archive, destination)

        archive.extractall.assert_called_once_with(destination)

    def test_extracts_valid_archive(self):
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w") as archive:
            archive.writestr("extension/file.txt", "contents")
        data.seek(0)

        with tempfile.TemporaryDirectory() as directory, zipfile.ZipFile(data) as archive:
            safe_extract_zip(archive, Path(directory))
            self.assertEqual((Path(directory) / "extension/file.txt").read_text(), "contents")

    def test_rejects_path_traversal_before_extracting(self):
        archive = Mock()
        archive.infolist.return_value = [zipfile.ZipInfo("../outside")]

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RuntimeError):
                safe_extract_zip(archive, Path(directory))

        archive.extractall.assert_not_called()

    def test_rejects_existing_symlink_outside_destination(self):
        archive = Mock()
        archive.infolist.return_value = [zipfile.ZipInfo("link/file.txt")]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            destination = root / "destination"
            destination.mkdir()
            try:
                (destination / "link").symlink_to(root, target_is_directory=True)
            except OSError:
                self.skipTest("Creating symlinks is unavailable")
            with self.assertRaises(RuntimeError):
                safe_extract_zip(archive, destination)
        archive.extractall.assert_not_called()
