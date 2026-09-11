# -*- coding: utf-8 -*-
"""Generator / CycloneDX / SPDX helper tests reconstructed from mock pycache."""
import json
import os
from unittest.mock import MagicMock, patch

import pytest

from conftest import FakeBuildroot
from mockbuild.sbom_cyclonedx import CycloneDxGenerator
from mockbuild.sbom_generate import SBOMGenerator
from mockbuild.sbom_spdx import SpdxGenerator
from mockbuild.sbom_utils import RpmQueryHelper


def test_cyclonedx_serial_stable_under_source_date_epoch():
    gen = CycloneDxGenerator(MagicMock(), FakeBuildroot())
    os.environ["SOURCE_DATE_EPOCH"] = "1700000000"
    try:
        a = gen.create_cyclonedx_document(serial_seed="httpd-1.0-1")
        b = gen.create_cyclonedx_document(serial_seed="httpd-1.0-1")
        c = gen.create_cyclonedx_document(serial_seed="httpd-1.0-2")
    finally:
        del os.environ["SOURCE_DATE_EPOCH"]
    assert a["specVersion"] == "1.6"
    assert a["serialNumber"] == b["serialNumber"]
    assert a["serialNumber"] != c["serialNumber"]


def test_spdx_document_uuid_seed_includes_arch_and_distro():
    seed_x86 = SpdxGenerator._document_uuid_seed(
        "1700000000", "httpd", "2.4.62", "7.el9", "rocky", "x86_64"
    )
    seed_aarch = SpdxGenerator._document_uuid_seed(
        "1700000000", "httpd", "2.4.62", "7.el9", "rocky", "aarch64"
    )
    seed_fedora = SpdxGenerator._document_uuid_seed(
        "1700000000", "httpd", "2.4.62", "7.el9", "fedora", "x86_64"
    )
    assert seed_x86 != seed_aarch
    assert seed_x86 != seed_fedora
    assert ":rocky:x86_64" in seed_x86
    assert ":rocky:aarch64" in seed_aarch
    assert ":fedora:x86_64" in seed_fedora


def test_spdx_signer_group_unknown_key_vs_unsigned():
    unsigned_key, unsigned_name, _ = SpdxGenerator._toolchain_signer_group(
        {"signature_status": "unsigned"}
    )
    assert unsigned_key == "unsigned"
    assert "Unsigned" in unsigned_name
    unknown_key, unknown_name, _ = SpdxGenerator._toolchain_signer_group(
        {"signature_status": "present-unverified", "signature_key": None}
    )
    assert unknown_key == "unknown-key"
    keyed, keyed_name, _ = SpdxGenerator._toolchain_signer_group(
        {"signature_status": "present-unverified", "signature_key": "aabbccdd"}
    )
    assert keyed == "aabbccdd"


def test_id_hardening_distinguishes_sanitized_collisions():
    gen = CycloneDxGenerator(MagicMock(), FakeBuildroot())
    ref_a = gen.generate_file_bom_ref("pkg", "1.0", "a/b")
    ref_b = gen.generate_file_bom_ref("pkg", "1.0", "a:b")
    assert ref_a != ref_b
    assert ref_a.startswith("file:pkg-1.0:a-b:")
    id_a = SpdxGenerator._spdx_id_from_purl(
        "pkg:rpm/rocky/foo@1.0?arch=x86_64"
    )
    id_b = SpdxGenerator._spdx_id_from_purl(
        "pkg:rpm/rocky/foo@1.0?arch=x86:64"
    )
    assert id_a != id_b


def test_source_file_bom_ref_distinguishes_sanitized_collisions():
    gen = CycloneDxGenerator(MagicMock(), FakeBuildroot())
    ref_a = gen.create_source_file_component({"filename": "a/b"})["bom-ref"]
    ref_b = gen.create_source_file_component({"filename": "a:b"})["bom-ref"]
    assert ref_a != ref_b
    assert ref_a.startswith("source-file:a-b-unknown:")


def test_unknown_file_algo_omits_cdx_hashes():
    helper = MagicMock()
    helper.get_rpm_file_info.return_value = {
        "/usr/bin/foo": {"hash": "a" * 64, "algo": 99},
        "/usr/bin/bar": {
            "hash": "b" * 64,
            "algo": 8,
            "digest_algorithm": "SHA256",
        },
    }
    gen = CycloneDxGenerator(
        helper, FakeBuildroot(), conf={"include_file_components": True}
    )
    comps = gen.create_file_components("/tmp/pkg.rpm", "pkg", "1.0")
    by_name = {c["name"]: c for c in comps}
    assert "hashes" not in by_name["/usr/bin/foo"]
    assert by_name["/usr/bin/bar"]["hashes"][0]["alg"] == "SHA-256"


def test_sha224_omitted_from_cdx_file_hashes():
    helper = MagicMock()
    helper.get_rpm_file_info.return_value = {
        "/usr/bin/old": {
            "hash": "c" * 56,
            "algo": 11,
            "digest_algorithm": "SHA224",
        },
    }
    gen = CycloneDxGenerator(
        helper, FakeBuildroot(), conf={"include_file_components": True}
    )
    comps = gen.create_file_components("/tmp/pkg.rpm", "pkg", "1.0")
    assert comps
    assert "hashes" not in comps[0]


def test_sha3_mapped_in_cdx_file_hashes():
    helper = MagicMock()
    helper.get_rpm_file_info.return_value = {
        "/usr/bin/a": {
            "hash": "a" * 64,
            "algo": 12,
            "digest_algorithm": "SHA3-256",
        },
        "/usr/bin/b": {
            "hash": "b" * 128,
            "algo": 14,
            "digest_algorithm": "SHA3-512",
        },
    }
    gen = CycloneDxGenerator(
        helper, FakeBuildroot(), conf={"include_file_components": True}
    )
    comps = gen.create_file_components("/tmp/pkg.rpm", "pkg", "1.0")
    algs = {c["name"]: c["hashes"][0]["alg"] for c in comps}
    assert algs["/usr/bin/a"] == "SHA3-256"
    assert algs["/usr/bin/b"] == "SHA3-512"


def test_atomic_write_preserves_existing_on_failure(tmp_path):
    out = tmp_path / "out.sbom"
    out.write_text('{"keep": true}\n', encoding="utf-8")
    with patch("mockbuild.sbom_generate.json.dumps", side_effect=ValueError("boom")):
        with pytest.raises(ValueError):
            SBOMGenerator._atomic_write_json(str(out), {"new": True})
    body = out.read_text(encoding="utf-8")
    assert '"keep": true' in body
    assert json.loads(body)["keep"] is True


def test_prebuild_errors_seed_incomplete_collection_status():
    gen = SBOMGenerator(
        {"generate_sbom": True},
        FakeBuildroot(),
        prebuild_capture_errors=["SPECS missing", "no input SRPM"],
    )
    assert gen.collection_status.get("prebuild") is False
    assert gen._compute_completeness() == "minimal"
    gen._record_collector("artifacts", True)
    assert gen._compute_completeness() == "partial"


def test_primary_dependency_excludes_self_ref():
    gen = CycloneDxGenerator(
        MagicMock(), FakeBuildroot(),
        conf={"include_source_dependencies": True},
    )
    primary = "pkg:rpm/rocky/httpd@1.0?arch=x86_64"
    bom = {
        "metadata": {"component": {"bom-ref": primary, "name": "httpd"}},
        "components": [
            {"bom-ref": primary, "name": "httpd", "purl": primary},
        ],
        "dependencies": [],
    }
    gen.finalize_dependencies(
        bom,
        [{"filename": "httpd.tar.bz2", "bom-ref": "file:sources/httpd.tar.bz2"}],
        [],
        [primary],
        [],
    )
    primary_deps = next(d for d in bom["dependencies"] if d["ref"] == primary)
    depends_on = primary_deps.get("dependsOn") or []
    assert primary not in depends_on
    assert "file:sources/httpd.tar.bz2" in depends_on


def test_find_build_artifacts_without_rootdir(tmp_path):
    (tmp_path / "foo-1.0-1.x86_64.rpm").write_bytes(b"rpm")
    (tmp_path / "foo-1.0-1.src.rpm").write_bytes(b"srpm")
    gen = SBOMGenerator({"generate_sbom": True}, FakeBuildroot(resultdir=str(tmp_path)))
    rpm_files, src_rpm_files, _spec = gen._find_build_artifacts(str(tmp_path))
    assert "foo-1.0-1.x86_64.rpm" in rpm_files
    assert "foo-1.0-1.src.rpm" in src_rpm_files
