# Release Contract

This document defines the public release boundary for `levelup-737ng`.

## Repository Roles

- `petrolpram/737NG-Series` is the private aircraft source and package producer.
- `petrolpram/737NG-Updates` is the public release and download endpoint.
- The X-Plane 737NG Maintenance Toolkit is one possible consumer. The release
  format is not coupled to one updater implementation.

The public Git branch contains no aircraft payload. Package archives, generated
manifests, checksums, and release indexes are GitHub Release assets only.

## Versioning

Each public release has:

- a unique immutable tag, for example `v2.S1.50C`;
- a display version matching the packaged LevelUp version;
- a positive, monotonically increasing `releaseSequence` for reliable updater
  ordering; and
- a channel: `stable` or `beta`.

A stable release must not be silently replaced. Corrections require a new tag
and release sequence.

## Required Assets

A production release contains these metadata assets:

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

## Package Manifest

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

## Release Index

`release-index.json` conforms to
[`schemas/release-index.schema.json`](../schemas/release-index.schema.json).
It is the updater discovery document and lists only assets from the same GitHub
Release.

The stable discovery URL is:

```text
https://github.com/petrolpram/737NG-Updates/releases/latest/download/release-index.json
```

Clients must validate the index schema and package compatibility before
downloading or changing an aircraft installation.

## Verification Order

An updater must:

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

## Publication Allowlist

The producer may upload only:

- the validated full archive and full manifest;
- the validated cumulative patch and patch manifest;
- `release-index.json`;
- `SHA256SUMS.txt`; and
- an explicitly generated offline release-notes file, when used.

The publication workflow must never copy:

- private GitHub source ZIP or TAR archives;
- arbitrary assets from another release;
- Actions logs or intermediate build artifacts;
- AC3D `.ac` files or private source directories; or
- an archive without a matching validated manifest.

GitHub's automatic source archives for this public documentation repository are
not publication inputs and must not be used by updater clients.
