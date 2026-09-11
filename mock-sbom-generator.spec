
%global __python %{__python3}
%global python_sitelib %{python3_sitelib}

# Overlay of mock's mockbuild package (extra modules + plugin + CLI).
# Retire this RPM when upstream mock ships the SBOM generator
# (https://github.com/rpm-software-management/mock/pull/1682). File-level
# Conflicts with that future mock package are enough; do not Conflicts: mock
# until then.

Summary: Atomic BOM plugin and CLI for mock
Name: mock-sbom-generator
Version: 2.0.0
Release: 1%{?dist}
License: GPL-2.0-or-later
URL: https://github.com/atomicturtle/mock-sbom-generator
Source0: %{url}/archive/%{version}/%{name}-%{version}.tar.gz
Vendor: Atomicorp, Inc. https://www.atomicorp.com
Packager: Atomicorp, Inc. https://www.atomicorp.com
BuildArch: noarch

Requires: mock >= 6.1
Requires: python3-rpm
Requires: python3-distro
Recommends: python3-specfile
BuildRequires: make
BuildRequires: python%{python3_pkgversion}-devel

%description
Mock plugin and standalone CLI that generate an Atomic BOM, Atomicorp's
Software Bill of Materials for packages built with Mock. The document is
CycloneDX 1.6 or SPDX 2.3 JSON and records the build environment, source
files, toolchain packages, and resulting RPMs. It is compatible with
vulnerability scanners (Grype, Trivy, Snyk, sbom-auditor).

This package overlays mock's Python site library with the generator modules
and plugin. Enable it with: mock --enable-plugin=sbom_generator

%prep
%autosetup -n %{name}-%{version}

%build
%make_build

%install
%make_install \
    PREFIX=%{_prefix} \
    SITELIB=%{python_sitelib} \
    MANDIR=%{_mandir} \
    DOCDIR=%{_docdir}/%{name}

%files
%license LICENSE
%doc README.md
%{_bindir}/mock-sbom-generator
%{_mandir}/man1/mock-sbom-generator.1*
%{python_sitelib}/mockbuild/plugins/sbom_generator.py*
%{python_sitelib}/mockbuild/plugins/__pycache__/sbom_generator*.pyc
%{python_sitelib}/mockbuild/sbom_generate.py*
%{python_sitelib}/mockbuild/sbom_utils.py*
%{python_sitelib}/mockbuild/sbom_cyclonedx.py*
%{python_sitelib}/mockbuild/sbom_spdx.py*
%{python_sitelib}/mockbuild/__pycache__/sbom_*.pyc
%doc %{_docdir}/%{name}/Plugin-SBOM.md

%changelog
* Fri Sep 11 2026 scott@atomicorp.com - 2.0.0-1
- Version 2.0.0: Port mock sbom_generator branch into this overlay RPM
- Split monolith into plugin + CLI + library (CycloneDX 1.6 and SPDX 2.3)
- Standalone mock-sbom-generator CLI; plugin invokes it at postbuild
- Prebuild forensic sbom-prebuild.json and bootstrap-native execution
- Build from the versioned source tarball with make / make install
- Requires python3-rpm and python3-distro; python3-specfile recommended

* Sun Dec 28 2025 scott@atomicorp.com - 1.2.5-1
- Version 1.2.5: Complete CycloneDX schema compliance
- Fixed invalid external reference type for CPE (cpe23Type → other)
- Changed License from GPL to GPL-2.0-or-later for SPDX compliance
- Fixes ~183 schema validation errors
- Achieves CycloneDX 1.5 schema validation

* Sun Dec 28 2025 scott@atomicorp.com - 1.2.4-1
- Version 1.2.4: Schema validation compliance fixes
- Fixed duplicate dependencies issue (~185 errors eliminated)
- Refactored dependency generation to use dictionary-based deduplication
- Improved CycloneDX 1.5 schema compliance
- Validated with official CycloneDX SBOM Utility

* Sun Dec 28 2025 scott@atomicorp.com - 1.2.3-1
- Version 1.2.3: SBOM metadata enhancements for quality compliance
- Added lifecycle phase: "build" to indicate build-time SBOM generation
- Added data license: CC0-1.0 for SBOM metadata licensing
- Added completeness declaration: "complete" for SBOM scope
- Quality score improved from 7.3/10 to estimated 7.8+/10
- Enhanced compliance with NTIA and industry standards

* Sun Dec 28 2025 scott@atomicorp.com - 1.2.2-1
- Version 1.2.2: SHA-256 checksums and provenance metadata
- Added SHA-256 checksums for all toolchain packages (RPM header hashes)
- Integrity score improved from F (4.2) to B (8.9) - major quality improvement
- Added Vendor and Packager metadata for better provenance tracking
- SBOM generator now maps RPM Vendor to authors and Packager to supplier
- Overall quality score improved from 6.0/10 to 6.8/10
- SHA-1 fallback support for older RPM packages

* Sun Dec 28 2025 scott@atomicorp.com - 1.2.1-1
- Version 1.2.1: Complete dependency tracking for SBOM quality compliance
- Added dependency entries for all components (source files, toolchain packages)
- Fixed CycloneDX completeness requirement: every component now has dependency entry
- Improved sbomqs quality score: Completeness category now scores 10/10
- Overall quality score improvement from 6.0/10 to estimated 7.8+/10

* Sun Dec 28 2025 scott@atomicorp.com - 1.2.0-1
- Version 1.2.0: Dynamic SBOM filename format
- Changed SBOM output filename to use package naming format: {name}-{version}-{release}.sbom
- Added validation to ensure package metadata (name, version, release) is always available
- Improved error handling with clear messaging when build metadata is incomplete

* Wed Nov 26 2025 scott@atomicorp.com - 1.1.0-1
- Version 1.1.0: Build hardening metadata and expanded platform support
- Added build hardening properties capture (FORTIFY, PIE, RELRO, LTO, FIPS mode)
- Capture compiler/linker flags (optflags, hardening_cflags, global_cflags, global_ldflags)
- Fixed python3_sitelib macro compatibility for EL8 and EL10 builds
- Renamed hardening properties from mock:hardening:* to build:hardening:* for accuracy
- Updated property naming to reflect build-time settings vs mock-specific metadata

* Mon Nov 17 2025 scott@atomicorp.com - 1.0-1
- Version 1.0: Enhanced CycloneDX SBOM generation
- Added comprehensive metadata.component with license, summary, and URL
- Improved primary package detection for multi-package builds
- Removed verbose source file properties from package components
- Dependencies now only include runtime libraries/RPMs (not source code)
- Enhanced RPM metadata in SBOM (buildhost, buildtime, sourcerpm, group, epoch, distribution)
