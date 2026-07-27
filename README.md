# LevelUp 737NG Updates

This repository is the public release endpoint for LevelUp 737NG aircraft
packages and update metadata. It is intentionally separate from the private
aircraft source repository.

Aircraft files are published only as explicit assets on the
[Releases](https://github.com/petrolpram/737NG-Updates/releases) page. They are
not committed to the `main` branch.

## Downloads

Use a published GitHub Release. Do not use the repository branch or GitHub's
automatically generated source archives as an aircraft package.

Once the first stable release is available, updater clients can discover it
through this stable endpoint:

<https://github.com/petrolpram/737NG-Updates/releases/latest/download/release-index.json>

Every production release is expected to provide:

- a full LevelUp package and its manifest;
- a cumulative patch from the active full-package baseline and its manifest;
- `release-index.json` for updater discovery; and
- `SHA256SUMS.txt` for independent integrity verification.

The exact format and publication rules are documented in
[docs/RELEASE_CONTRACT.md](docs/RELEASE_CONTRACT.md) and
[docs/RELEASE_PROCESS.md](docs/RELEASE_PROCESS.md).

## Repository Boundary

The Git tree contains only public documentation, schemas, and repository
policy automation. It must not contain:

- private LevelUp aircraft source;
- raw or packaged aircraft payloads;
- AC3D source files;
- updater-generated manifests or checksums; or
- copied source archives from the private repository.

GitHub may display automatic "Source code" ZIP and TAR links for this public
repository. Those archives contain only this repository's documentation and
automation and are not LevelUp aircraft downloads.

## Licensing

This repository does not grant a separate license for LevelUp aircraft assets.
Each published aircraft package remains subject to the copyright and license
documents included with that package. A repository-wide license must not be
assumed where no explicit license has been published.

## Support

Release-specific limitations and known issues belong in the corresponding
GitHub Release notes. Aircraft source changes and release approval remain under
LevelUp project ownership.
