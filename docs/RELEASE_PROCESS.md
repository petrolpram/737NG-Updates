# Release Process

This process keeps package generation, approval, and public distribution
separate.

## Prerequisites

Before a production release:

- the target release tag exists in the private aircraft source repository;
- the active full-package baseline is mapped to a verified source commit;
- the target is a descendant of that baseline;
- the package exclusion policy and tests pass;
- the full package and cumulative patch both have manifests;
- the public release index and checksum file have been generated; and
- an authorized LevelUp reviewer has approved the public release.

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

## Production Steps

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

## Stable And Beta Channels

- Stable releases are normal GitHub Releases and may become `latest`.
- Beta releases are marked as prereleases and must declare `beta` in the
  release index.
- The `/releases/latest/download/...` endpoint is reserved for stable content.

## Failure Handling

Before publication, delete or replace a failed draft release after correcting
the producer output.

After publication, do not mutate a stable release in place. Publish a corrected
tag and higher release sequence. If a release is unsafe, mark it clearly as
withdrawn, remove it from updater discovery, and publish a replacement.

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

Do not publish private source listings, build logs containing credentials, or
unfiltered intermediate artifacts.
