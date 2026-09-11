# -*- coding: utf-8 -*-
"""Load this repo's SBOM modules; stub Mock-only imports and rpm if needed."""
from __future__ import print_function

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "SOURCES"


def _ensure_module(name):
    mod = sys.modules.get(name)
    if mod is not None:
        return mod
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod


def _load_source(modname, path):
    spec = importlib.util.spec_from_file_location(modname, str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module
    spec.loader.exec_module(module)
    if "." in modname:
        parent_name, attr = modname.rsplit(".", 1)
        parent = sys.modules.get(parent_name)
        if parent is not None:
            setattr(parent, attr, module)
    return module


try:
    import rpm  # noqa: F401
except ImportError:
    sys.modules["rpm"] = MagicMock()

try:
    import mockbuild  # noqa: F401
except ImportError:
    pkg = _ensure_module("mockbuild")
    pkg.__path__ = []

if "mockbuild.mounts" not in sys.modules:
    mounts = _ensure_module("mockbuild.mounts")

    class BindMountPoint(object):
        def __init__(self, *args, **kwargs):
            pass

        def having_mounted(self):
            return _NullCtx()

    mounts.BindMountPoint = BindMountPoint

if "mockbuild.file_util" not in sys.modules:
    file_util = _ensure_module("mockbuild.file_util")
    file_util.mkdirIfAbsent = MagicMock()

if "mockbuild.util" not in sys.modules:
    util = _ensure_module("mockbuild.util")
    util.do = MagicMock()
    util.USE_NSPAWN = False

    def host_path_to_chroot_path(host_path, rootdir):
        if not rootdir or rootdir == "/":
            return host_path
        root = str(rootdir).rstrip("/")
        host = str(host_path)
        if host == root:
            return "/"
        prefix = root + "/"
        if host.startswith(prefix):
            return host[len(root):]
        return host_path

    util.host_path_to_chroot_path = host_path_to_chroot_path


class _NullCtx(object):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


_load_source(
    "mockbuild.sbom_utils",
    SOURCES / "mockbuild" / "sbom_utils.py",
)
_load_source(
    "mockbuild.sbom_cyclonedx",
    SOURCES / "mockbuild" / "sbom_cyclonedx.py",
)
_load_source(
    "mockbuild.sbom_spdx",
    SOURCES / "mockbuild" / "sbom_spdx.py",
)
_load_source(
    "mockbuild.sbom_generate",
    SOURCES / "mockbuild" / "sbom_generate.py",
)


def load_plugin():
    """Import the overlay plugin module (not site-packages mock)."""
    return _load_source(
        "sbom_generator_plugin",
        SOURCES / "plugins" / "sbom_generator.py",
    )


def load_cli():
    """Import the standalone CLI module."""
    return _load_source(
        "mock_sbom_generator_cli",
        SOURCES / "mock-sbom-generator.py",
    )


class FakeLog(object):
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


class FakeBuildroot(object):
    """Minimal Buildroot duck-type for unit tests."""

    def __init__(self, rootdir=None, resultdir=None, builddir="/builddir/build"):
        self.rootdir = rootdir
        self.resultdir = resultdir
        self.builddir = builddir
        self.root_log = FakeLog()
        self.state = None
        self.config = {}
        self.bootstrap_buildroot = None
        self.uid_manager = MagicMock()
        self.uid_manager.unprivUid = 1000
        self.uid_manager.unprivGid = 1000

    def make_chroot_path(self, *paths):
        if not self.rootdir:
            return None
        root = str(self.rootdir)
        new_path = root
        for path in paths:
            relative = str(path).lstrip("/")
            if not relative:
                continue
            new_path = str(Path(new_path) / relative)
        return new_path


@pytest.fixture
def fake_buildroot(tmp_path):
    root = tmp_path / "root"
    result = tmp_path / "result"
    root.mkdir()
    result.mkdir()
    return FakeBuildroot(rootdir=str(root), resultdir=str(result))
