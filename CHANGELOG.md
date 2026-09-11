# Changelog

Notable changes to **Atomic BOM** (`mock-sbom-generator`). Version numbers match
`VERSION` and the spec `Version:`.

## 2.0.0 - 2026-09-11

Atomicorp's name for the generated document is **Atomic BOM**. Files remain
CycloneDX 1.6 JSON or SPDX 2.3 JSON.

- Split the 1.x monolith into a Mock plugin, standalone CLI, and library modules
- Add SPDX 2.3 JSON (`<name>-<version>-<release>.spdx.json`) next to CycloneDX 1.6
- Raise CycloneDX spec version from 1.5 to 1.6
- Plugin invokes `/usr/bin/mock-sbom-generator` at postbuild; CLI works without a rebuild
- Keep `sbom-prebuild.json` as a forensic snapshot of pre-build sources and spec metadata
- Run the host-trusted generator inside bootstrap when bootstrap is enabled (never in the target buildroot)
- Require `python3-rpm` and `python3-distro`; recommend `python3-specfile`
- Build the overlay RPM from the versioned GitHub source tarball with `make` / `make install`
- Ship the packaged plugin from the Atomic repository

## 1.2.5 - 2025-12-28

- CycloneDX schema compliance: invalid CPE external reference type (`cpe23Type` → `other`)
- License identifier `GPL-2.0-or-later` for SPDX compliance
- CycloneDX 1.5 schema validation (clears ~183 schema errors)

## 1.2.4 - 2025-12-28

- Deduplicate dependency entries (dictionary-based generation)
- Improved CycloneDX 1.5 schema compliance

## 1.2.3 - 2025-12-28

- Lifecycle phase `build` on the generated document
- Data license CC0-1.0 for SBOM metadata
- Completeness declaration `complete`

## 1.2.2 - 2025-12-28

- SHA-256 checksums for toolchain packages (RPM header hashes; SHA-1 fallback on older RPMs)
- Map RPM Vendor to authors and Packager to supplier

## 1.2.1 - 2025-12-28

- Dependency entries for every component (source files and toolchain packages)

## 1.2.0 - 2025-12-28

- Output filename `<name>-<version>-<release>.sbom` (replaces `sbom.cyclonedx.json`)
- Fail clearly when package name, version, or release is missing from the build

## 1.1.0 - 2025-11-26

- Capture build hardening (FORTIFY, PIE, RELRO, LTO, FIPS) and compiler/linker flags
- Rename hardening properties from `mock:hardening:*` to `build:hardening:*`
- `python3_sitelib` compatibility for EL8 and EL10

## 1.0 - 2025-11-17

- Initial overlay: CycloneDX SBOM for Mock RPM builds
- `metadata.component` with license, summary, and URL
- Improved primary-package detection for multi-package builds
- Runtime RPM dependencies only (not source files) on package components
- RPM metadata: buildhost, buildtime, sourcerpm, group, epoch, distribution
