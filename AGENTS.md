# Agent instructions

This repository is the source for **Atomic BOM** 2.0.0: Atomicorp's Software Bill of Materials for RPM packages built with Mock. The overlay RPM/CLI is `mock-sbom-generator`; the Mock plugin is `sbom_generator`. Read `README.md` and `SOURCES/Plugin-SBOM.md` before changing generator behavior.

## Project purpose

Atomic BOM is a build-time inventory of sources, toolchain, hardening, and resulting RPMs. On disk it is CycloneDX 1.6 JSON or SPDX 2.3 JSON. Prefer **Atomic BOM** in docs, comments, and user-facing strings for the generated document. Keep package, CLI, plugin, and file names as they are (`mock-sbom-generator`, `sbom_generator`, `.sbom` / `.spdx.json`). Do not invent a private media type, file extension, or schema named "atomic-bom".

Installs next to distro `mock >= 6.1` by placing files into mock's `mockbuild` package. Packaged RPMs ship from the Atomic repository (`dnf install mock-sbom-generator` after https://updates.atomicorp.com/installers/atomic). Mock auto-discovers `SOURCES/plugins/sbom_generator.py`. Do not patch Mock's `PLUGIN_LIST`.

## Layout

- `SOURCES/plugins/sbom_generator.py` — Mock plugin; runs at postbuild; copies host-trusted generator into bootstrap when bootstrap is on
- `SOURCES/mock-sbom-generator.py` — `/usr/bin/mock-sbom-generator` (Atomic BOM CLI)
- `SOURCES/mockbuild/sbom_generate.py` — collection/orchestration
- `SOURCES/mockbuild/sbom_utils.py` — RPM and file helpers
- `SOURCES/mockbuild/sbom_cyclonedx.py` / `sbom_spdx.py` — Atomic BOM writers
- `VERSION` — project release (`2.0.0`); keep in sync with `mock-sbom-generator.spec` `Version:` and `CHANGELOG.md`
- `CHANGELOG.md` — release notes; add an entry when `VERSION` changes
- `mock-sbom-generator.spec` — overlay RPM; `%setup` then `make` / `make install`
- GitLab packaging (mock configs, `.gitlab-ci.yml`) lives in a separate pipeline repo, not here

## Invariants

- Keep both transports: plugin (Mock hook) and CLI (no rebuild required).
- Default CycloneDX Atomic BOM is `<name>-<version>-<release>.sbom` plus `.sha256`. SPDX is `<name>-<version>-<release>.spdx.json`.
- With bootstrap enabled, postbuild must run the host-trusted generator inside bootstrap, never in the target buildroot. `--root /` is rejected.
- An explicit `command` on `sbom_generator_opts` overrides the plugin default CLI.
- CPE stays off by default (`--generate-cpe false`).
- Cache none of this as a Mock core feature; it is an overlay until upstream PR 1682 ships.

## Validation

```sh
make test
```

That runs `python3 -m pytest tests/ -q`. Tests stub Mock-only imports. The Makefile is `all`, `test`, `install`, `clean`, and `help`. RPM packaging lives in `mock-sbom-generator.spec` (`Source0` tarball, then `make` / `make install`).

Do not add GitLab CI, distro mock configs, or secrets. Do not change license away from GPL-2.0-or-later.
