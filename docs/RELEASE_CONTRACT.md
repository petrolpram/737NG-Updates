# Release Contract

This document defines the public release boundary for `levelup-737ng` aircraft
packages and explicitly approved optional resources.

## Repository Roles

- `petrolpram/737NG-Series` is the private aircraft source and package producer.
- `petrolpram/737NG-Updates` is the public release and download endpoint for
  aircraft packages and approved resources.
- The X-Plane 737NG Maintenance Toolkit is one possible consumer. The release
  format is not coupled to one updater implementation.

The public Git branch contains no aircraft or resource payload. Package
archives, generated manifests, checksums, and release indexes are GitHub
Release assets only.

## Versioning

Each aircraft release has:

- a unique immutable tag, for example `v2.S1.50C`;
- a display version matching the packaged LevelUp version;
- a positive, monotonically increasing `releaseSequence` for reliable updater
  ordering; and
- a channel: `stable` or `beta`.

A stable release must not be silently replaced. Corrections require a new tag
and release sequence.

Each resource release has:

- a unique tag beginning with `resource-`, for example
  `resource-paintkit-v1.1.0`;
- an independent resource package version;
- a channel: `stable` or `beta`; and
- an explicit `latest=false` publication setting.

Resource versions are independent from aircraft versions and do not use the
aircraft `releaseSequence`. A resource release must never replace the latest
aircraft release used by the stable discovery endpoint.

## Required Assets

An aircraft production release contains these metadata assets:

- `release-index.json`
- `SHA256SUMS.txt`

It also contains one or both of the following package pairs:

1. Full package
   - `737NG Series_<releaseVersion>.7z`
   - `737NG Series_<releaseVersion>.manifest.json`
2. Cumulative patch
   - `737NG Series_<baselineVersion>_to_<releaseVersion>_patch.7z`
   - `737NG Series_<baselineVersion>_to_<releaseVersion>_patch.manifest.json`

The exact archive name is declared by its adjacent manifest. Updaters must not
derive an archive URL only from a naming convention.

Release notes are stored in the GitHub Release body. They may also be uploaded
as a text or Markdown asset when an offline copy is required.

A resource release contains exactly one resource package pair plus checksums:

- one 7z archive;
- one adjacent `<archive-stem>-manifest.json` resource manifest; and
- `SHA256SUMS.txt` covering both files.

For example, Paintkit 1.1.0 uses:

- `LevelUp-737NG-Paintkit-1.1.0.7z`;
- `LevelUp-737NG-Paintkit-1.1.0-manifest.json`; and
- `SHA256SUMS.txt`.

## Full Packages And Cumulative Patches

A full package establishes a supported baseline. A cumulative patch contains
all public changes between that baseline and the target release. Intermediate
patches are not required.

The patch manifest declares added or replaced files and paths that must be
deleted. A consumer must process the manifest transactionally. Blind archive
overlay is not a supported update method because an archive cannot remove
retired paths safely.

When a new full baseline is introduced, the release index points to the new
full package and to the cumulative patch associated with that baseline.

## Aircraft Package Manifest

Package manifests use schema version 1 and conform to
[`schemas/aircraft-package-manifest.schema.json`](../schemas/aircraft-package-manifest.schema.json).

At minimum they bind:

- product and package type;
- release and baseline versions;
- source references and commits;
- archive filename, size, and SHA-256;
- content root;
- every written file with operation, size, and SHA-256; and
- every deleted path.

All archive and manifest paths are relative. Absolute paths, parent traversal,
and path separators inside archive filenames are invalid.
Written and deleted paths must also be unique under case-insensitive comparison
and must never refer to the same target.

The public manifest lists only distributed files and target paths to delete.
Internal source-only or excluded path inventories, including AC3D source names,
remain private producer evidence and are not published as manifest fields.

## Resource Package Manifest

Resource manifests use schema version 1 and conform to
[`schemas/resource-package-manifest.schema.json`](../schemas/resource-package-manifest.schema.json).

The manifest binds:

- package identity and independent package version;
- exact release tag and stable/beta channel;
- canonical repository;
- compatible LevelUp product ID;
- archive filename, byte size, and SHA-256;
- extraction mode, archive root, and final target-directory name;
- total extracted size; and
- every extracted file path, byte size, and SHA-256.

The resource 7z is downloaded into a hidden temporary file under the
user-selected parent directory, verified, and extracted into a hidden staging
directory. It is not an aircraft update archive and is never extracted into an
aircraft. Unknown destination directories and modified managed resources must
not be overwritten.

## Release Index

The aircraft `release-index.json` conforms to
[`schemas/release-index.schema.json`](../schemas/release-index.schema.json).
It is the updater discovery document and lists only assets from the same GitHub
Release.

The stable discovery URL is:

```text
https://github.com/petrolpram/737NG-Updates/releases/latest/download/release-index.json
```

Clients must validate the index schema and package compatibility before
downloading or changing an aircraft installation.

Resource releases do not contain an aircraft `release-index.json`. Compatible
clients discover them by their trusted manifest asset pattern through the
GitHub Releases API and validate the resource manifest before downloading the
archive.

## Verification Order

For an aircraft release, an updater must:

1. Download `release-index.json` over HTTPS.
2. Validate its schema, product, channel, release tag, and release sequence.
3. Download the selected manifest from the same release.
4. Verify the manifest SHA-256 recorded by the index.
5. Validate the package manifest schema and compatibility rules.
6. Download the declared archive.
7. Verify archive size and SHA-256.
8. Verify every extracted file against the manifest before applying it.

`SHA256SUMS.txt` permits independent verification but does not replace the
machine-readable hashes in the index and manifests.

For a resource release, a client must:

1. Select a release matching the trusted repository, channel, and manifest
   asset pattern.
2. Verify the GitHub asset digest and validate the resource manifest schema.
3. Require the manifest identity, release tag, repository, channel, and
   supported product to match the trusted client catalog.
4. Stream the declared archive to a temporary file in the selected destination.
5. Verify its exact byte size and SHA-256.
6. Validate that every archive member is under the declared archive root and
   reject traversal, links, duplicates, case collisions, special entries, and
   undeclared files.
7. Extract into a hidden staging directory and verify every file against the
   manifest before moving the complete directory into its final name.

## Publication Allowlist

The producer may upload only:

- the validated full archive and full manifest;
- the validated cumulative patch and patch manifest;
- one validated resource 7z and its matching resource manifest;
- `release-index.json`;
- `SHA256SUMS.txt`; and
- an explicitly generated offline release-notes file, when used.

The publication workflow must never copy:

- private GitHub source ZIP or TAR archives;
- arbitrary assets from another release;
- Actions logs or intermediate build artifacts;
- AC3D `.ac` files or private source directories; or
- an aircraft or resource archive without a matching validated manifest.

GitHub's automatic source archives for this public documentation repository are
not publication inputs and must not be used by updater clients.
