# Release Process

This process keeps package generation, approval, and public distribution
separate for aircraft and optional resource releases.

## Prerequisites

Before an aircraft production release:

- the target release tag exists in the private aircraft source repository;
- the active full-package baseline is mapped to a verified source commit;
- the target is a descendant of that baseline;
- the package exclusion policy and tests pass;
- the full package and cumulative patch both have manifests;
- the public release index and checksum file have been generated; and
- an authorized LevelUp reviewer has approved the public release.

Before a resource release:

- the final 7z archive and package version have been selected;
- LevelUp has confirmed that the resource may be publicly redistributed;
- the archive contains the applicable license and attribution material;
- archive paths and structure have passed resource-package validation;
- the resource manifest and checksum file have been generated; and
- an authorized LevelUp reviewer has approved publication.

Install the pinned release-helper dependencies with Python 3.10 or newer:

```bash
python3 -m pip install -r requirements-release.txt
```

Resource manifest generation fully extracts the archive in a temporary
directory to calculate every payload hash. The build host therefore needs free
space for both the compressed archive and its complete extracted contents.

## Credentials And Approval

Publication runs from the private source repository. It requires a credential
that can write Releases in `petrolpram/737NG-Updates` and has no broader access
than necessary.

Preferred long-term ownership is a GitHub App installation. A fine-grained
personal access token scoped only to the public updates repository is an
acceptable interim mechanism. Store it as an Actions secret in the private
source repository; never commit it or place it in the public repository.

The publishing job should use a protected `public-release` environment with
required LevelUp reviewers.

## Aircraft Production Steps

1. Select the verified baseline reference and target release tag.
2. Run package-policy and manifest tests.
3. Build the full package from the target reference.
4. Build the cumulative patch from the active baseline to the target.
5. Generate and validate both package manifests.
6. Generate public manifests without internal exclusion inventories.
7. Generate `release-index.json` and `SHA256SUMS.txt` from those exact files.
8. Verify archive contents, per-file hashes, excluded paths, and deleted paths.
9. Upload only the explicit assets listed by the release contract to a draft
   release in `petrolpram/737NG-Updates`.
10. Verify the draft release title, tag, notes, asset names, sizes, and hashes.
11. Obtain the required approval and publish the release.
12. Verify the stable index URL and perform a clean updater dry-run against the
    published assets.

The workflow should use the GitHub CLI or GitHub API directly and pass explicit
asset paths. It must not clone every asset from a private release or depend on a
broad third-party mirroring action.

## Resource Production Steps

1. Place the final resource 7z archive in an untracked release-staging directory.
2. Run `tools/generate_resource_release.py` with the package ID, package
   version, release tag, channel, and output directory.
3. Validate the generated manifest against
   `schemas/resource-package-manifest.schema.json`.
4. Independently verify the archive and manifest hashes in `SHA256SUMS.txt`.
5. Create a draft `resource-*` GitHub Release and upload only the 7z archive,
   manifest, and checksum file.
6. Confirm title, tag, channel, asset names, sizes, hashes, licensing, and
   release notes.
7. Obtain LevelUp approval and publish with `latest=false`.
8. Perform a quiet online discovery, download, verification, cancellation, and
   destination-conflict test before announcing the resource.

Example metadata generation command:

```bash
python3 tools/generate_resource_release.py \
  /path/to/LevelUp-737NG-Paintkit-1.1.0.7z \
  --output-directory /path/to/release-staging \
  --package-id levelup.paintkit \
  --package-version 1.1.0 \
  --release-tag resource-paintkit-v1.1.0 \
  --channel stable \
  --archive-root "737NG V2_Paintkit"
```

## Stable And Beta Channels

- Stable aircraft releases are normal GitHub Releases and may become `latest`.
- Beta aircraft releases are marked as prereleases and must declare `beta` in
  the release index.
- Stable resource releases are normal releases published with `latest=false`.
- Beta resource releases are prereleases and declare `beta` in their resource
  manifest.
- The `/releases/latest/download/...` endpoint is reserved for stable aircraft
  content.

## Failure Handling

Before publication, delete or replace a failed draft release after correcting
the producer output.

After publication, do not mutate a stable release in place. Publish a corrected
tag and, for aircraft releases, a higher release sequence. If a release is
unsafe, mark it clearly as withdrawn, remove it from updater discovery, and
publish a replacement.

No updater should apply a package when index, manifest, archive, or per-file
verification fails.

## Post-Release Evidence

Retain the following evidence in the private producer workflow:

- source baseline and target commits;
- package-policy test result;
- generated asset inventory;
- full internal exclusion inventory;
- archive and manifest SHA-256 values;
- file, deletion, and exclusion counts;
- approval identity and timestamp; and
- public Release URL.

For resource releases, evidence must include the final archive inventory,
package version, release tag, archive and manifest hashes, redistribution
approval, and public Release URL.

Do not publish private source listings, build logs containing credentials, or
unfiltered intermediate artifacts.
