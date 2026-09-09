# LevelUp 737NG Updates

This repository is the public release endpoint for LevelUp 737NG aircraft
packages, update metadata, and explicitly approved optional resources. It is
intentionally separate from the private aircraft source repository.

Aircraft and resource files are published only as explicit assets on the
[Releases](https://github.com/petrolpram/737NG-Updates/releases) page. They are
not committed to the `main` branch.

## Installation and updates

**Use the [X-Plane 737NG Maintenance Toolkit](https://github.com/wahltho/xplane-737ng-maintenance-toolkit/releases/latest) to install and update the required LevelUp maintenance patches. The Toolkit is the only supported installation method for these patches.**

The **LevelUp maintenance patches** group includes three mandatory items:

- **VNAV Descent Tables**
- **Weight & Balance (W&B)**
- **FANS CDU**

Install all three through the Toolkit as follows:

1. Close X-Plane.
2. Download and install the latest Maintenance Toolkit for your operating system
   (version **0.13.0 or later**).
3. Open the Toolkit and select your installed LevelUp 737NG aircraft folder.
4. Select **LevelUp maintenance patches** and review the installation plan.
   All three required patches are included automatically.
5. Install the group through the Toolkit. It manages the patch downloads,
   validation, backups and installation together.

**Tablet Performance Calculator** and **AUTO JETWAY** are optional members of
this group. They can be selected in addition to the three mandatory patches.

Use the same Toolkit workflow for subsequent patch updates. After updating or
reinstalling the aircraft, close X-Plane and use the Toolkit to check and reapply
the maintenance group as needed before flying. Do not manually copy individual
patch files or run standalone patch installers over a Toolkit-managed installation.
Use the Toolkit's restore function if you need to restore its saved files.

The group is controlled by the Toolkit catalog and uses each patch's existing
release. There is no separate combined patch archive to download, and users do
not need to collect the three patches from their individual repositories.

## Release assets and updater metadata

Use a published GitHub Release. Do not use the repository branch or GitHub's
automatically generated source archives as an aircraft package.

Once the first stable release is available, updater clients can discover it
through this stable endpoint:

<https://github.com/petrolpram/737NG-Updates/releases/latest/download/release-index.json>

Every aircraft production release is expected to provide:

- a full LevelUp package and its manifest;
- a cumulative patch from the active full-package baseline and its manifest;
- `release-index.json` for updater discovery; and
- `SHA256SUMS.txt` for independent integrity verification.

Optional resources such as paintkits use separate `resource-*` release tags.
Each resource release contains one 7z archive, its machine-readable extraction
manifest, and `SHA256SUMS.txt`. Resource releases must not be marked as the
repository's latest release because the `latest` endpoint is reserved for
aircraft update discovery.

The exact format and publication rules are documented in
[docs/RELEASE_CONTRACT.md](docs/RELEASE_CONTRACT.md) and
[docs/RELEASE_PROCESS.md](docs/RELEASE_PROCESS.md).

## Repository Boundary

The Git tree contains only public documentation, schemas, and repository
policy automation. It must not contain:

- private LevelUp aircraft source;
- raw or packaged aircraft and resource payloads;
- AC3D source files;
- updater-generated manifests or checksums; or
- copied source archives from the private repository.

GitHub may display automatic "Source code" ZIP and TAR links for this public
repository. Those archives contain only this repository's documentation and
automation and are not LevelUp aircraft downloads.

## Licensing

This repository does not grant a separate license for LevelUp aircraft or
resource assets. Each published package remains subject to the copyright and
license documents included with that package. A repository-wide license must
not be assumed where no explicit license has been published.

## Support

Release-specific limitations and known issues belong in the corresponding
GitHub Release notes. Aircraft source changes and release approval remain under
LevelUp project ownership.
