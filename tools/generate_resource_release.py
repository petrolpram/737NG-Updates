#!/usr/bin/env python3
"""Generate extraction metadata for an existing 7z resource archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath

import py7zr
from py7zr.exceptions import ArchiveError


REPOSITORY_URL = "https://github.com/petrolpram/737NG-Updates"
SUPPORTED_PRODUCT = "levelup-737ng"
MAXIMUM_ARCHIVE_SIZE = 2 * 1024 * 1024 * 1024 - 1
MAXIMUM_EXTRACTED_SIZE = 64 * 1024 * 1024 * 1024
SAFE_SEGMENT = re.compile(r"^[A-Za-z0-9._-]+$")
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_direct_directory_name(value: str, label: str) -> None:
    if (
        not value
        or len(value) > 255
        or value in {".", ".."}
        or value != Path(value).name
        or any(character in value for character in '/\\:\0<>"|?*')
        or value.endswith((" ", "."))
        or value.split(".", 1)[0].upper() in WINDOWS_RESERVED_NAMES
    ):
        raise ValueError(f"Resource {label} is not a safe cross-platform directory name: {value}")


def validate_relative_path(value: str, label: str) -> PurePosixPath:
    if (
        not value
        or len(value) > 1024
        or value.startswith("/")
        or "\\" in value
        or re.match(r"^[A-Za-z]:", value)
        or "\0" in value
    ):
        raise ValueError(f"Unsafe {label}: {value}")
    path = PurePosixPath(value)
    parts = value.split("/")
    if any(
        not part
        or part in {".", ".."}
        or any(character in part for character in ':<>"|?*')
        or part.endswith((" ", "."))
        or part.split(".", 1)[0].upper() in WINDOWS_RESERVED_NAMES
        for part in parts
    ):
        raise ValueError(f"Unsafe {label}: {value}")
    return path


def validate_archive(archive_path: Path, archive_root: str) -> list[dict[str, object]]:
    if not archive_path.is_file():
        raise ValueError(f"Resource archive does not exist: {archive_path}")
    if archive_path.suffix.lower() != ".7z" or archive_path.name != Path(archive_path.name).name:
        raise ValueError("Resource archive must be a directly named 7z file.")
    size = archive_path.stat().st_size
    if size <= 0 or size > MAXIMUM_ARCHIVE_SIZE:
        raise ValueError("Resource archive must be non-empty and smaller than 2 GiB.")

    validate_direct_directory_name(archive_root, "archive root")
    seen_members: set[str] = set()
    declared_files: dict[str, int] = {}
    root_prefix = f"{archive_root}/"
    try:
        with py7zr.SevenZipFile(archive_path, mode="r") as archive:
            if archive.needs_password():
                raise ValueError("Encrypted resource archives are not supported.")
            entries = archive.list()
    except ArchiveError as error:
        raise ValueError(f"Resource archive is not a valid 7z file: {archive_path}") from error

    if not entries:
        raise ValueError("Resource archive must not be empty.")
    for entry in entries:
        member = entry.filename.rstrip("/")
        validate_relative_path(member, "7z member path")
        key = member.casefold()
        if key in seen_members:
            raise ValueError(f"Duplicate 7z member path: {entry.filename}")
        seen_members.add(key)
        if entry.is_symlink:
            raise ValueError(f"Symbolic links are not permitted in resource archives: {entry.filename}")
        if not entry.is_file and not entry.is_directory:
            raise ValueError(f"Unsupported special entry in resource archive: {entry.filename}")
        if member == archive_root:
            if not entry.is_directory:
                raise ValueError("The declared archive root must be a directory.")
            continue
        if not member.startswith(root_prefix):
            raise ValueError(f"7z member is outside the declared archive root: {entry.filename}")
        relative = member[len(root_prefix) :]
        validate_relative_path(relative, "resource file path")
        if entry.is_file:
            if entry.uncompressed < 0:
                raise ValueError(f"Resource file has an invalid size: {relative}")
            declared_files[relative] = entry.uncompressed

    if not declared_files:
        raise ValueError("Resource archive contains no files.")
    extracted_size = sum(declared_files.values())
    if extracted_size > MAXIMUM_EXTRACTED_SIZE:
        raise ValueError("Resource archive exceeds the 64 GiB extracted-size limit.")

    with tempfile.TemporaryDirectory(prefix="levelup-resource-") as temporary_root:
        extraction_root = Path(temporary_root)
        try:
            with py7zr.SevenZipFile(archive_path, mode="r") as archive:
                archive.extractall(path=extraction_root)
        except ArchiveError as error:
            raise ValueError(f"Resource archive extraction failed: {archive_path}") from error

        top_level = list(extraction_root.iterdir())
        content_root = extraction_root / archive_root
        if len(top_level) != 1 or top_level[0] != content_root or not content_root.is_dir() or content_root.is_symlink():
            raise ValueError("Extracted resource archive does not contain exactly the declared root directory.")

        extracted_files: dict[str, Path] = {}
        for current_root, directory_names, file_names in os.walk(content_root, followlinks=False):
            current = Path(current_root)
            for directory_name in directory_names:
                directory = current / directory_name
                if directory.is_symlink():
                    raise ValueError(f"Extracted resource contains a symbolic link: {directory}")
            for file_name in file_names:
                file_path = current / file_name
                if file_path.is_symlink() or not file_path.is_file():
                    raise ValueError(f"Extracted resource contains an unsupported entry: {file_path}")
                relative = file_path.relative_to(content_root).as_posix()
                validate_relative_path(relative, "extracted resource path")
                key = relative.casefold()
                if key in extracted_files:
                    raise ValueError(f"Duplicate extracted resource path: {relative}")
                extracted_files[key] = file_path

        if set(extracted_files) != {path.casefold() for path in declared_files}:
            raise ValueError("Extracted resource file inventory does not match the 7z directory.")

        records: list[dict[str, object]] = []
        for relative, declared_size in sorted(declared_files.items(), key=lambda item: item[0].casefold()):
            file_path = extracted_files[relative.casefold()]
            actual_size = file_path.stat().st_size
            if actual_size != declared_size:
                raise ValueError(f"Extracted resource size differs from the archive: {relative}")
            records.append(
                {
                    "path": relative,
                    "size": actual_size,
                    "sha256": sha256_file(file_path),
                }
            )

    return records


def validate_identity(package_id: str, package_version: str, release_tag: str) -> None:
    for label, value, maximum in (
        ("package ID", package_id, 128),
        ("package version", package_version, 64),
        ("release tag", release_tag, 128),
    ):
        if not value or len(value) > maximum:
            raise ValueError(f"Resource {label} is empty or too long.")
    if not SAFE_SEGMENT.fullmatch(package_id):
        raise ValueError("Resource package ID contains unsupported characters.")
    if not SAFE_SEGMENT.fullmatch(release_tag):
        raise ValueError("Resource release tag contains unsupported characters.")


def generate_release_files(
    archive_path: Path,
    output_directory: Path,
    package_id: str,
    package_version: str,
    release_tag: str,
    channel: str,
    archive_root: str,
    target_directory: str | None = None,
    force: bool = False,
) -> tuple[Path, Path]:
    archive_path = archive_path.resolve()
    output_directory = output_directory.resolve()
    target_directory = target_directory or archive_root
    validate_identity(package_id, package_version, release_tag)
    validate_direct_directory_name(target_directory, "target directory")
    files = validate_archive(archive_path, archive_root)
    if channel not in {"stable", "beta"}:
        raise ValueError("Resource channel must be stable or beta.")

    manifest_path = output_directory / f"{archive_path.stem}-manifest.json"
    checksums_path = output_directory / "SHA256SUMS.txt"
    if not force:
        existing = [path for path in (manifest_path, checksums_path) if path.exists()]
        if existing:
            raise FileExistsError(f"Refusing to overwrite generated release file: {existing[0]}")

    archive_size = archive_path.stat().st_size
    archive_sha256 = sha256_file(archive_path)
    manifest = {
        "schemaVersion": 1,
        "packageType": "resource",
        "packageId": package_id,
        "packageVersion": package_version,
        "releaseTag": release_tag,
        "channel": channel,
        "repository": REPOSITORY_URL,
        "supportedProducts": [SUPPORTED_PRODUCT],
        "deliveryMode": "extract",
        "archiveRoot": archive_root,
        "targetDirectory": target_directory,
        "extractedSize": sum(int(file["size"]) for file in files),
        "files": files,
        "archive": {
            "fileName": archive_path.name,
            "size": archive_size,
            "sha256": archive_sha256,
        },
    }

    output_directory.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    manifest_sha256 = sha256_file(manifest_path)
    checksums_path.write_text(
        f"{archive_sha256}  {archive_path.name}\n"
        f"{manifest_sha256}  {manifest_path.name}\n",
        encoding="utf-8",
    )
    return manifest_path, checksums_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Final resource 7z archive")
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--package-id", required=True)
    parser.add_argument("--package-version", required=True)
    parser.add_argument("--release-tag", required=True)
    parser.add_argument("--channel", choices=("stable", "beta"), default="stable")
    parser.add_argument("--archive-root", required=True, help="Single top-level directory stored in the 7z")
    parser.add_argument("--target-directory", help="Installed directory name; defaults to archive root")
    parser.add_argument("--force", action="store_true", help="Replace existing generated metadata")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest_path, checksums_path = generate_release_files(
            args.archive,
            args.output_directory,
            args.package_id,
            args.package_version,
            args.release_tag,
            args.channel,
            args.archive_root,
            args.target_directory,
            args.force,
        )
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"Generated {manifest_path}")
    print(f"Generated {checksums_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
