# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""Manifest — парсер TOML манифестов.

Единственный файл в проекте, где разрешён import (только tomllib).
"""

import tomllib
from pathlib import Path


def load_app_manifest(path):
    """Читает full.toml. Поддерживает extends (один уровень)."""
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"full.toml not found: {path}")

    data = tomllib.loads(path.read_text(encoding="utf-8"))

    # Inheritance
    extends = data.get("extends")
    base = None
    if extends:
        base_path = path.parent / extends
        if not base_path.exists():
            raise FileNotFoundError(f"Base manifest not found: {base_path}")
        base = load_app_manifest(base_path)

    # Kernel config
    k_data = data.get("kernel", {})
    if base and not k_data:
        kernel_name = base["kernel"]["name"]
        singleton = base["kernel"]["singleton"]
    else:
        kernel_name = k_data.get("name", base["kernel"]["name"] if base else "App")
        singleton = k_data.get("singleton", base["kernel"]["singleton"] if base else True)

    # Extensions
    raw_exts = data.get("extensions", [])
    if base and not raw_exts:
        extensions = list(base["extensions"])
    elif base:
        exclude = {e["name"] for e in raw_exts if e.get("exclude")}
        ext_map = {}
        for e in base["extensions"]:
            if e["name"] not in exclude:
                ext_map[e["name"]] = dict(e)
        for e in raw_exts:
            if e.get("exclude"):
                continue
            ext_map[e["name"]] = dict(e)
        extensions = list(ext_map.values())
    else:
        extensions = [dict(e) for e in raw_exts]

    # Extensions meta
    child_meta = data.get("extensions_meta", {})
    if base:
        merged = dict(base.get("extensions_meta", {}))
        merged.update(child_meta)
        extensions_meta = merged
    else:
        extensions_meta = dict(child_meta)

    # Tests
    tests = data.get("tests", {})

    return {
        "kernel": {"name": kernel_name, "singleton": singleton},
        "extensions": extensions,
        "extensions_meta": extensions_meta,
        "tests": tests,
    }


def load_extension_manifest(path):
    """Читает {Name}.toml."""
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Extension manifest not found: {path}")

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    ext_name = data.get("name", path.parent.name)

    return {
        "name": ext_name,
        "version": data.get("version", "0.1.0"),
        "alias": data.get("alias", []),
        "mods": data.get("mods", []),
        "depends": data.get("depends", []),
        "variables": data.get("variables", []),
        "metadata": data.get("metadata", {}),
    }


PUBLIC = {
    "load_app_manifest": load_app_manifest,
    "load_extension_manifest": load_extension_manifest,
}
