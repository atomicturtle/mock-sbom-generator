# Mock SBOM Generator

Overlay plugin and CLI that generate a Software Bill of Materials for packages
built with [Mock](https://github.com/rpm-software-management/mock). This is
Atomicorp's standalone RPM of the generator developed for upstream mock
([PR #1682](https://github.com/rpm-software-management/mock/pull/1682)), so it
can ship without waiting on that merge.

Install this package next to distro `mock >= 6.1`. Mock auto-discovers the
plugin from `mockbuild/plugins/`; no Mock config patch is required. Retire this
RPM when a distro Mock release ships the same files.

## Features

- CycloneDX **1.6** JSON (`<name>-<version>-<release>.sbom`) and SPDX **2.3** JSON
- Standalone `mock-sbom-generator` CLI (no rebuild required)
- Prebuild forensic snapshot `sbom-prebuild.json`
- Build toolchain inventory, source/patch hashes, runtime deps, hardening metadata
- Scanner-friendly output (Grype, Trivy, Snyk, sbom-auditor)

Full usage, trust model, and configuration: [SOURCES/Plugin-SBOM.md](SOURCES/Plugin-SBOM.md).

## Enablement

```bash
# One-shot
mock --enable-plugin=sbom_generator --rebuild package.src.rpm

# Persistent
# config_opts['plugin_conf']['sbom_generator_enable'] = True
```

After the build:

```text
<resultdir>/<name>-<version>-<release>.sbom
<resultdir>/<name>-<version>-<release>.sbom.sha256
<resultdir>/sbom-prebuild.json
```

Standalone CLI:

```bash
mock-sbom-generator --type cyclonedx \
    --resultdir /var/lib/mock/rocky-9-x86_64/result \
    --root /var/lib/mock/rocky-9-x86_64/root

mock-sbom-generator --type spdx --resultdir /path/to/result --root /path/to/root
```

## Migrating from 1.x plugin options

1.x configs used keys on `sbom_generator_opts`:

```python
config_opts['plugin_conf']['sbom_generator_opts'] = {
    'generate_sbom': True,
    'include_file_components': True,
    'include_file_dependencies': False,
    'include_debug_files': False,
    'include_man_pages': True,
    'include_source_dependencies': True,
    'include_toolchain_dependencies': False,
}
```

Those keys still work when `command` is **unset**: the plugin maps them onto
CLI flags. Prefer the 2.x `command` template for new configs (SPDX, CPE, or an
external generator):

```python
config_opts['plugin_conf']['sbom_generator_opts'] = {
    'generate_sbom': True,
    'command': (
        '/usr/bin/mock-sbom-generator'
        ' --type cyclonedx'
        ' --resultdir %(resultdir)s'
        ' --root %(root)s'
        ' --builddir %(builddir)s'
        ' --include-file-components true'
        ' --include-file-dependencies false'
        ' --include-debug-files false'
        ' --include-man-pages true'
        ' --include-source-dependencies true'
        ' --include-toolchain-dependencies false'
        ' --generate-cpe false'
        ' --online %(online)s'
        ' --rpmbuild-networking %(rpmbuild_networking)s'
        ' --isolation %(isolation)s'
        ' --use-nspawn %(use_nspawn)s'
    ),
}
```

If `command` is set, it wins and the 1.x include keys are ignored.

Output filename changed from `sbom.cyclonedx.json` (docs for 1.0) to
`<n>-<v>-<r>.sbom` in 1.2.0 and remains that in 2.x. CycloneDX spec version
is **1.6** (was 1.5). CPE is off by default; pass `--generate-cpe true` to emit
heuristic CPEs.

## Building

```bash
make test
make rpmbuild-build    # local rpmbuild
```

Requires `python3-rpm` and `python3-distro` at runtime. `python3-specfile` is
recommended for spec parsing (regex/`rpmspec` fallback is built in).

Atomicorp RPM builds for EL and Fedora are handled in a separate GitLab
packaging pipeline.

## License

GPL-2.0-or-later
