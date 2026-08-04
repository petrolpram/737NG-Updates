import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import py7zr
from jsonschema import Draft202012Validator

from tools.generate_resource_release import generate_release_files


class GenerateResourceReleaseTests(unittest.TestCase):
    def test_generates_extraction_manifest_and_checksums_for_valid_7z(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            source = root_path / "Paintkit"
            (source / "Templates").mkdir(parents=True)
            (source / "readme.txt").write_text("paintkit", encoding="utf-8")
            (source / "Templates" / "wing.txt").write_text("wing", encoding="utf-8")
            archive_path = root_path / "LevelUp-737NG-Paintkit-1.1.0.7z"
            with py7zr.SevenZipFile(archive_path, "w") as archive:
                archive.writeall(source, arcname="Paintkit")

            manifest_path, checksums_path = generate_release_files(
                archive_path,
                root_path / "out",
                "levelup.paintkit",
                "1.1.0",
                "resource-paintkit-v1.1.0",
                "stable",
                "Paintkit",
            )

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            schema_path = Path(__file__).parents[1] / "schemas" / "resource-package-manifest.schema.json"
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            Draft202012Validator(schema).validate(manifest)
            expected_archive_hash = hashlib.sha256(archive_path.read_bytes()).hexdigest()
            expected_manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            self.assertEqual("resource", manifest["packageType"])
            self.assertEqual("extract", manifest["deliveryMode"])
            self.assertEqual("Paintkit", manifest["archiveRoot"])
            self.assertEqual("Paintkit", manifest["targetDirectory"])
            self.assertEqual(12, manifest["extractedSize"])
            self.assertEqual(["Templates/wing.txt", "readme.txt"], sorted(file["path"] for file in manifest["files"]))
            self.assertEqual(archive_path.name, manifest["archive"]["fileName"])
            self.assertEqual(archive_path.stat().st_size, manifest["archive"]["size"])
            self.assertEqual(expected_archive_hash, manifest["archive"]["sha256"])
            self.assertEqual(
                f"{expected_archive_hash}  {archive_path.name}\n"
                f"{expected_manifest_hash}  {manifest_path.name}\n",
                checksums_path.read_text(encoding="utf-8"),
            )

    def test_rejects_archive_with_parent_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            archive_path = root_path / "unsafe.7z"
            with py7zr.SevenZipFile(archive_path, "w") as archive:
                archive.writestr("unsafe", "Paintkit/../outside.txt")

            with self.assertRaisesRegex(ValueError, "Unsafe 7z member path"):
                generate_release_files(
                    archive_path,
                    root_path / "out",
                    "levelup.paintkit",
                    "1.1.0",
                    "resource-paintkit-v1.1.0",
                    "stable",
                    "Paintkit",
                )

    def test_rejects_archive_outside_declared_root(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            archive_path = root_path / "wrong-root.7z"
            with py7zr.SevenZipFile(archive_path, "w") as archive:
                archive.writestr("resource", "Other/readme.txt")

            with self.assertRaisesRegex(ValueError, "outside the declared archive root"):
                generate_release_files(
                    archive_path,
                    root_path / "out",
                    "levelup.paintkit",
                    "1.1.0",
                    "resource-paintkit-v1.1.0",
                    "stable",
                    "Paintkit",
                )

    def test_refuses_to_overwrite_generated_metadata_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            source = root_path / "Paintkit"
            source.mkdir()
            (source / "readme.txt").write_text("resource", encoding="utf-8")
            archive_path = root_path / "resource.7z"
            with py7zr.SevenZipFile(archive_path, "w") as archive:
                archive.writeall(source, arcname="Paintkit")
            output_path = root_path / "out"

            def generate_resource() -> tuple[Path, Path]:
                return generate_release_files(
                    archive_path,
                    output_path,
                    "levelup.paintkit",
                    "1.1.0",
                    "resource-paintkit-v1.1.0",
                    "stable",
                    "Paintkit",
                )

            generate_resource()

            with self.assertRaises(FileExistsError):
                generate_resource()


if __name__ == "__main__":
    unittest.main()
