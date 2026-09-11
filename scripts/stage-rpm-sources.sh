#!/bin/bash
# Flatten nested SOURCES/ into an rpmbuild SOURCES directory (basenames).
set -euo pipefail

DEST="${1:-${HOME}/rpmbuild/SOURCES}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p "$DEST"
cp "$ROOT/SOURCES/plugins/sbom_generator.py" "$DEST/"
cp "$ROOT/SOURCES/mockbuild/sbom_generate.py" "$DEST/"
cp "$ROOT/SOURCES/mockbuild/sbom_utils.py" "$DEST/"
cp "$ROOT/SOURCES/mockbuild/sbom_cyclonedx.py" "$DEST/"
cp "$ROOT/SOURCES/mockbuild/sbom_spdx.py" "$DEST/"
cp "$ROOT/SOURCES/mock-sbom-generator.py" "$DEST/"
cp "$ROOT/SOURCES/Plugin-SBOM.md" "$DEST/"
cp "$ROOT/SOURCES/mock-sbom-generator.1" "$DEST/"
