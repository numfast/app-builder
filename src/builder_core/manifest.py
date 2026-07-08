# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""Manifest — парсер TOML манифестов расширений и приложений."""

import tomllib
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ExtensionManifest:
    """Описание расширения из {Name}.toml."""
    name: str = ""
    version: str = "0.1.0"
    alias: list[str] = field(default_factory=list)
    mods: list[str] = field(default_factory=list)
    depends: list[str] = field(default_factory=list)
    variables: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class AppManifest:
    """Описание приложения из full.toml."""
    kernel_name: str = "App"
    singleton: bool = True
    extensions: list[dict] = field(default_factory=list)
    extensions_meta: dict = field(default_factory=dict)


def load_extension_manifest(path: str | Path) -> ExtensionManifest:
    """Читает {Name}.toml, возвращает ExtensionManifest."""
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Extension manifest not found: {path}")

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    ext_name = data.get("name", path.parent.name)

    return ExtensionManifest(
        name=ext_name,
        version=data.get("version", "0.1.0"),
        alias=data.get("alias", []),
        mods=data.get("mods", []),
        depends=data.get("depends", []),
        variables=data.get("variables", []),
        metadata=data.get("metadata", {}),
    )


def load_app_manifest(path: str | Path) -> AppManifest:
    """Читает full.toml, возвращает AppManifest.

    Поддерживает наследование через поле extends:
      - Дочерний манифест наследует [[extensions]] от родителя.
      - Ребёнок может исключить расширение: exclude = true
      - extensions_meta ребёнка переопределяют родительские.
    """
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"App manifest not found: {path}")

    data = tomllib.loads(path.read_text(encoding="utf-8"))

    # Наследование
    extends = data.get("extends")
    base = None
    if extends:
        base_path = path.parent / extends
        if not base_path.exists():
            raise FileNotFoundError(f"Base manifest '{extends}' not found")
        base = load_app_manifest(base_path)

    # Kernel
    k_data = data.get("kernel", {})
    if base and not k_data:
        kernel_name = base.kernel_name
        singleton = base.singleton
    else:
        kernel_name = k_data.get("name", base.kernel_name if base else "App")
        singleton = k_data.get("singleton", base.singleton if base else True)

    # Extensions
    raw_exts = data.get("extensions", [])
    if base and not raw_exts:
        extensions = list(base.extensions)
    elif base:
        exclude = {e["name"] for e in raw_exts if e.get("exclude")}
        ext_map = {e["name"]: e for e in base.extensions if e["name"] not in exclude}
        for e in raw_exts:
            if e.get("exclude"):
                continue
            ext_map[e["name"]] = e
        extensions = list(ext_map.values())
    else:
        extensions = list(raw_exts)

    # Extensions meta
    child_meta = data.get("extensions_meta", {})
    if base:
        merged = dict(base.extensions_meta)
        merged.update(child_meta)
        extensions_meta = merged
    else:
        extensions_meta = child_meta

    return AppManifest(
        kernel_name=kernel_name,
        singleton=singleton,
        extensions=extensions,
        extensions_meta=extensions_meta,
    )
