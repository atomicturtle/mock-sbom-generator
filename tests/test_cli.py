# -*- coding: utf-8 -*-
"""CLI, layout, and StandaloneContext tests."""
import json
import os
import subprocess
import sys

import pytest

from conftest import ROOT, SOURCES, load_cli


def test_source_layout():
    assert (SOURCES / "plugins" / "sbom_generator.py").is_file()
    for name in (
        "sbom_generate.py",
        "sbom_utils.py",
        "sbom_cyclonedx.py",
        "sbom_spdx.py",
    ):
        assert (SOURCES / "mockbuild" / name).is_file()
    assert (SOURCES / "mock-sbom-generator.py").is_file()
    assert (SOURCES / "Plugin-SBOM.md").is_file()
    assert (ROOT / "mock-sbom-generator.spec").is_file()


def test_cli_help():
    script = str(SOURCES / "mock-sbom-generator.py")
    proc = subprocess.run(
        [sys.executable, script, "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "resultdir" in proc.stdout


def test_cli_parse_bool_and_defaults():
    cli = load_cli()
    assert cli._parse_bool("true") is True
    assert cli._parse_bool("false") is False
    assert cli._parse_bool("yes") is True
    assert cli._parse_bool("off") is False
    with pytest.raises(ValueError):
        cli._parse_bool("flase")
    args = cli._argparser().parse_args(["--resultdir", "/tmp"])
    assert args.type == "cyclonedx"
    assert args.generate_cpe == "false"


def test_make_chroot_path_rejects_dotdot_escape(tmp_path):
    cli = load_cli()
    ctx = cli.StandaloneContext(str(tmp_path), str(tmp_path))
    with pytest.raises(ValueError):
        ctx.make_chroot_path("..", "etc", "passwd")


def test_standalone_builddir_matches_buildroot_semantics(tmp_path):
    cli = load_cli()
    ctx = cli.StandaloneContext(str(tmp_path / "root"), str(tmp_path))
    (tmp_path / "root").mkdir()
    assert ctx.builddir == "/builddir/build"
    ctx2 = cli.StandaloneContext(
        str(tmp_path / "root"), str(tmp_path), builddir="/custom/build"
    )
    assert ctx2.builddir == "/custom/build"


def test_standalone_do_out_chroot_honors_return_stderr(tmp_path):
    cli = load_cli()
    ctx = cli.StandaloneContext(str(tmp_path), str(tmp_path))
    output, rc = ctx.doOutChroot(
        [sys.executable, "-c", "import sys; sys.stderr.write('NOKEY\\n')"],
        returnStderr=True,
    )
    assert rc == 0
    assert "NOKEY" in output


def test_prebuild_json_rejects_bad_nested_types(tmp_path):
    cli = load_cli()
    resultdir = tmp_path / "result"
    resultdir.mkdir()
    bad_sources = tmp_path / "bad-sources.json"
    with bad_sources.open("w", encoding="utf-8") as handle:
        json.dump({"source_files": "not a list"}, handle)
    rc = cli.main(
        ["--resultdir", str(resultdir), "--prebuild-json", str(bad_sources)]
    )
    assert rc == 1
    bad_env = tmp_path / "bad-env.json"
    with bad_env.open("w", encoding="utf-8") as handle:
        json.dump({"build_env": ["not", "an object"]}, handle)
    rc = cli.main(["--resultdir", str(resultdir), "--prebuild-json", str(bad_env)])
    assert rc == 1


def test_modules_compile():
    files = [
        SOURCES / "plugins" / "sbom_generator.py",
        SOURCES / "mock-sbom-generator.py",
        SOURCES / "mockbuild" / "sbom_generate.py",
        SOURCES / "mockbuild" / "sbom_utils.py",
        SOURCES / "mockbuild" / "sbom_cyclonedx.py",
        SOURCES / "mockbuild" / "sbom_spdx.py",
    ]
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile"] + [str(p) for p in files],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
