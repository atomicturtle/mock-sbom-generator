# -*- coding: utf-8 -*-
"""Plugin command-template defaults and 1.x include_* mapping."""
from conftest import load_plugin


def test_empty_opts_use_default_command():
    plugin = load_plugin()
    cmd = plugin.resolve_generator_command({})
    assert cmd == plugin.DEFAULT_COMMAND
    assert "--type cyclonedx" in cmd
    assert "--generate-cpe false" in cmd


def test_none_opts_use_default_command():
    plugin = load_plugin()
    assert plugin.resolve_generator_command(None) == plugin.DEFAULT_COMMAND


def test_explicit_command_wins_over_legacy_keys():
    plugin = load_plugin()
    custom = "/usr/bin/my-sbom-tool --out %(resultdir)s"
    cmd = plugin.resolve_generator_command(
        {
            "command": custom,
            "include_file_components": False,
            "include_debug_files": True,
        }
    )
    assert cmd == custom


def test_legacy_include_keys_mapped_when_command_unset():
    plugin = load_plugin()
    cmd = plugin.resolve_generator_command(
        {
            "generate_sbom": True,
            "include_file_components": False,
            "include_file_dependencies": True,
            "include_debug_files": True,
            "include_man_pages": False,
            "include_source_dependencies": False,
            "include_toolchain_dependencies": True,
        }
    )
    assert cmd != plugin.DEFAULT_COMMAND
    assert "--include-file-components false" in cmd
    assert "--include-file-dependencies true" in cmd
    assert "--include-debug-files true" in cmd
    assert "--include-man-pages false" in cmd
    assert "--include-source-dependencies false" in cmd
    assert "--include-toolchain-dependencies true" in cmd
    assert "--generate-cpe false" in cmd
    assert "%(resultdir)s" in cmd


def test_legacy_string_booleans_and_generate_cpe():
    plugin = load_plugin()
    cmd = plugin.resolve_generator_command(
        {"include_file_components": "no", "generate_cpe": "yes"}
    )
    assert "--include-file-components false" in cmd
    assert "--generate-cpe true" in cmd


def test_legacy_bool_helper():
    plugin = load_plugin()
    assert plugin._legacy_bool(True, False) is True
    assert plugin._legacy_bool("true", False) is True
    assert plugin._legacy_bool("OFF", True) is False
    assert plugin._legacy_bool("flase", True) is True
    assert plugin._legacy_bool(None, True) is True
    assert plugin._legacy_bool(0, True) is False
