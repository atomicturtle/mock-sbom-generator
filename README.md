# Mock SBOM Generator

Overlay plugin and CLI that generate a Software Bill of Materials for packages
built with [Mock](https://github.com/rpm-software-management/mock). Atomicorp
calls that document an **Atomic BOM**: a build-time inventory of sources,
toolchain, hardening, and resulting RPMs, still emitted as standard CycloneDX
or SPDX. 

This has also been submitted to upstream mock ([PR #1682](https://github.com/rpm-software-management/mock/pull/1682))

The packaged plugin is in the [Atomic repository](https://updates.atomicorp.com/channels/atomic/).
Install it next to distro `mock >= 6.1`. Mock auto-discovers the plugin from
`mockbuild/plugins/`; no Mock config patch is required. Retire this RPM when a
distro Mock release ships the same files.

| Name | What it is |
| --- | --- |
| `mock-sbom-generator` | RPM and `/usr/bin` CLI |
| `sbom_generator` | Mock plugin (`--enable-plugin=sbom_generator`) |
| Atomic BOM | Atomicorp's name for the generated SBOM (this tree is 2.0.0) |
| CycloneDX 1.6 / SPDX 2.3 | On-disk formats (not a private schema) |

Agents: start at [llms.txt](llms.txt). Contributors using coding agents: [AGENTS.md](AGENTS.md).

## Features

- CycloneDX **1.6** JSON (`<name>-<version>-<release>.sbom`) and SPDX **2.3** JSON
- Standalone `mock-sbom-generator` CLI (no rebuild required)
- Prebuild forensic snapshot `sbom-prebuild.json`
- Build toolchain inventory, source/patch hashes, runtime deps, hardening metadata
- Scanner-friendly output (Grype, Trivy, Snyk, sbom-auditor)

Full usage, trust model, and configuration: [SOURCES/Plugin-SBOM.md](SOURCES/Plugin-SBOM.md).

## Install

Enable the Atomic repository, then install the overlay RPM. On EL, `mock` comes
from EPEL (and CRB/PowerTools as required by that distro).

```bash
wget -q -O - https://updates.atomicorp.com/installers/atomic | sudo bash
sudo dnf install mock-sbom-generator
```

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

Optional persistent plugin config (override the default generator command):

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

CPE is off by default; pass `--generate-cpe true` to emit heuristic CPEs.

## Building

```bash
make
make test
make install
```

The RPM unpacks the 2.0.0 source tarball and runs `make` / `make install`.
GitLab packaging fetches `Source0` for that release.

Requires `python3-rpm` and `python3-distro` at runtime. `python3-specfile` is
recommended for spec parsing (regex/`rpmspec` fallback is built in).

Atomicorp RPM builds for EL and Fedora are handled in a separate GitLab
packaging pipeline.

## FAQ

### How do I install the plugin?

From the Atomic repository:

```bash
wget -q -O - https://updates.atomicorp.com/installers/atomic | sudo bash
sudo dnf install mock-sbom-generator
```

### Is Atomic BOM a new SBOM format?

No. It is Atomicorp's name for the SBOM this tool writes. Scanners should treat
the files as CycloneDX 1.6 JSON or SPDX 2.3 JSON.

### How do I generate an SBOM during a Mock RPM build?

```bash
mock --enable-plugin=sbom_generator --rebuild package.src.rpm
```

The plugin runs `/usr/bin/mock-sbom-generator` after a successful build.

### Can I generate an Atomic BOM without rebuilding?

Yes. Point the CLI at an existing Mock result directory (and chroot root when
you need toolchain data):

```bash
mock-sbom-generator --type cyclonedx \
    --resultdir /var/lib/mock/rocky-9-x86_64/result \
    --root /var/lib/mock/rocky-9-x86_64/root
```

### Is this a fork of Mock?

No. It overlays files into mock's `mockbuild` Python package. Distro Mock is
unchanged aside from discovering the extra plugin.

## License

GPL-2.0-or-later
