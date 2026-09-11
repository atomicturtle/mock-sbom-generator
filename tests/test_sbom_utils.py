# -*- coding: utf-8 -*-
"""RpmQueryHelper / shared util unit tests reconstructed from mock pycache."""
import os
from unittest.mock import patch

import pytest

from conftest import FakeBuildroot
from mockbuild.sbom_utils import (
    RpmQueryHelper,
    is_sha256_hex,
    nevra_key,
    resolve_rpm_dependency,
    should_include_rpm_file,
)


def test_generate_purl_includes_epoch_and_distro():
    helper = RpmQueryHelper(FakeBuildroot())
    purl = helper.generate_purl(
        "curl", "7.50.3-1.fc25", distro_obj="fedora",
        arch="x86_64", epoch="1", distro_version="25",
    )
    assert purl.startswith("pkg:rpm/fedora/curl@7.50.3-1.fc25?")
    assert "arch=x86_64" in purl
    assert "epoch=1" in purl
    assert "distro=fedora-25" in purl


def test_generate_purl_omits_zero_epoch():
    helper = RpmQueryHelper(FakeBuildroot())
    purl = helper.generate_purl(
        "bash", "5.0-1", distro_obj="rocky", arch="noarch", epoch="0",
    )
    assert "epoch=" not in purl
    assert "arch=noarch" in purl


def test_generate_cpe_is_heuristic_tuple():
    helper = RpmQueryHelper(FakeBuildroot())
    cpe, confidence = helper.generate_cpe("httpd", "2.4.57-1", "Fedora Project")
    assert confidence == "heuristic"
    assert cpe.startswith("cpe:2.3:a:fedora_project:httpd:2.4.57:")


def test_purl_and_cpe_sanitize_injection_characters():
    helper = RpmQueryHelper(FakeBuildroot())
    purl = helper.generate_purl("foo?bar", "1.0&x=y", distro_obj="rocky")
    assert "?" in purl  # qualifier separator only after @
    assert "foo-bar" in purl
    assert "&" not in purl.split("@", 1)[0]
    cpe, _ = helper.generate_cpe("a:b", "1:2", "evil:vendor")
    assert cpe.count(":") >= 5
    assert ":a_b:" in cpe


def test_parse_signature_data_does_not_claim_valid():
    helper = RpmQueryHelper(FakeBuildroot())
    info = helper.parse_signature_data(
        "RSA/SHA256, Mon Jul 29 10:12:32 2024, Key ID 2322d3d94bf0c9db"
    )
    assert info["signature_type"] == "GPG"
    assert info["signature_algorithm"] == "RSA/SHA256"
    assert info["signature_key"] == "2322d3d94bf0c9db"
    assert info["signature_status"] == "present-unverified"
    assert info["signature_valid"] is False


def test_signature_info_from_installed_stays_unverified():
    helper = RpmQueryHelper(FakeBuildroot())
    info = helper._signature_info_from_installed(
        "RSA/SHA256, Tue Apr 9 13:20:09 2024, Key ID 702d426d350d275d"
    )
    assert info["signature_status"] == "present-unverified"
    assert info["signature_valid"] is False
    assert info["signature_key"] == "702d426d350d275d"
    assert info["signature_algorithm"] == "RSA/SHA256"


def test_merge_source_files_preserves_provenance_fields():
    merged = RpmQueryHelper.merge_source_files(
        [
            {
                "filename": "httpd-2.4.62-7.el9_7.2.src.rpm",
                "sha256": "abc123",
                "digital_signature": {
                    "signature_status": "present-unverified",
                },
                "source_type": "source_rpm",
                "role": "input",
            }
        ],
        [{"filename": "httpd-2.4.62-7.el9_7.2.src.rpm", "sha256": "other"}],
    )
    assert len(merged) == 1
    assert merged[0]["source_type"] == "source_rpm"
    assert merged[0]["role"] == "input"
    assert merged[0]["sha256"] == "abc123"


def test_resolve_rpm_dependency_provides_and_version():
    name_map = {"glibc": "pkg:rpm/rocky/glibc@2.34", "bash": "ref:bash"}
    provides = {"libc.so.6": "pkg:rpm/rocky/glibc@2.34"}
    assert resolve_rpm_dependency("libc.so.6()(64bit)", name_map, provides) == (
        "pkg:rpm/rocky/glibc@2.34"
    )
    assert resolve_rpm_dependency("bash >= 5.0", name_map, provides) == "ref:bash"
    assert resolve_rpm_dependency("unknown", name_map, provides) is None


def test_should_include_rpm_file_filters():
    assert should_include_rpm_file("/usr/bin/bash") is True
    assert should_include_rpm_file("/usr/lib/debug/foo.debug") is False
    assert should_include_rpm_file("/usr/share/man/man1/ls.1.gz") is True
    assert should_include_rpm_file(
        "/usr/share/man/man1/ls.1.gz", include_man_pages=False
    ) is False
    assert should_include_rpm_file(
        "/usr/lib/debug/foo", include_debug_files=True
    ) is True


def test_path_stays_in_chroot_and_rejects_symlink_escape(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    inside = root / "builddir" / "build" / "SPECS"
    inside.mkdir(parents=True)
    outside = tmp_path / "evil_specs"
    outside.mkdir()
    helper = RpmQueryHelper(FakeBuildroot(rootdir=str(root)))
    assert helper.path_stays_in_chroot(str(inside)) is True
    assert helper.path_stays_in_chroot(str(outside)) is False


def test_specs_outside_chroot_is_rejected_by_path_helper(tmp_path):
    root = tmp_path / "root"
    (root / "builddir" / "build" / "SPECS").mkdir(parents=True)
    outside = tmp_path / "evil_specs"
    outside.mkdir()
    helper = RpmQueryHelper(FakeBuildroot(rootdir=str(root)))
    assert helper.path_stays_in_chroot(str(outside)) is False


def test_make_chroot_path_via_fake_rejects_nothing_simple(tmp_path):
    br = FakeBuildroot(rootdir=str(tmp_path / "root"))
    assert br.make_chroot_path("usr", "bin").endswith("usr/bin")


def test_is_sha256_hex():
    assert is_sha256_hex("a" * 64) is True
    assert is_sha256_hex("zzzz") is False
    assert is_sha256_hex(None) is False


def test_nevra_key_omits_zero_epoch():
    assert nevra_key("bash", "5.0", "1.el9", "x86_64", epoch="0") == (
        "bash-5.0-1.el9.x86_64"
    )
    assert "1:" in nevra_key("bash", "5.0", "1.el9", "x86_64", epoch="1")


def test_parse_spec_falls_back_when_rpmspec_raises(tmp_path):
    spec = tmp_path / "pkg.spec"
    spec.write_text(
        "Name: httpd\nVersion: 2.4.62\nRelease: 7%{?dist}.2\n"
        "License: ASL 2.0\nSource0: httpd-%{version}.tar.bz2\n",
        encoding="utf-8",
    )
    helper = RpmQueryHelper(FakeBuildroot())
    with patch.object(helper, "_run_out_chroot", side_effect=OSError("rpmspec failed")):
        with patch.object(helper, "detect_chroot_distribution", return_value="rocky"):
            with patch.object(helper, "get_distribution_version", return_value="9"):
                metadata, sources = helper.parse_spec_file(str(spec))
    assert metadata["name"] == "httpd"
    assert metadata["version"] == "2.4.62"
    assert any(s.get("filename") == "httpd-2.4.62.tar.bz2" for s in sources)


def test_expand_dist_macro_from_chroot_identity():
    helper = RpmQueryHelper(FakeBuildroot())
    with patch.object(helper, "detect_chroot_distribution", return_value="rocky"):
        with patch.object(helper, "get_distribution_version", return_value="9.8"):
            assert helper._expand_simple_spec_macros("7%{?dist}.2", "2.4.62") == "7.el9.2"
            assert helper._expand_simple_spec_macros(
                "httpd-%{version}.tar.bz2", "2.4.62"
            ) == "httpd-2.4.62.tar.bz2"
