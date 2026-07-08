# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""Loader — загрузчик расширений.

Динамически импортирует {Name}.py, регистрирует функции в Kernel.
"""

import sys
import importlib.util
from pathlib import Path

from builder_core.kernel import Kernel
from builder_core.manifest import load_extension_manifest


def import_dir(path: Path):
    """Добавляет директорию в sys.path, если её там нет."""
    path = path.resolve()
    sp = str(path)
    if sp not in sys.path:
        sys.path.insert(0, sp)


def import_module(name: str, path: Path):
    """Импортирует Python-файл как модуль."""
    sys.modules.pop(name, None)
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load module: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_extension(kernel: Kernel, ext_dir: str | Path, override_metadata: dict | None = None):
    """Загружает расширение из директории в Kernel.

    1. Читает {Name}.toml
    2. Добавляет директорию в sys.path
    3. Импортирует {Name}.py
    4. Регистрирует alias[i] → mods[i] в kernel
    5. Вызывает setup(kernel) если есть
    """
    ext_dir = Path(ext_dir).resolve()
    ext_name = ext_dir.name

    manifest_path = ext_dir / f"{ext_name}.toml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Extension manifest not found: {manifest_path}")

    em = load_extension_manifest(manifest_path)

    # Мерж метаданных
    metadata_section = em.name
    if metadata_section not in kernel.metadata:
        kernel.metadata[metadata_section] = {}
    kernel.metadata[metadata_section].update(em.metadata)
    if override_metadata:
        kernel.metadata[metadata_section].update(override_metadata)

    # Версия
    if "_versions" not in kernel.metadata:
        kernel.metadata["_versions"] = {}
    kernel.metadata["_versions"][em.name] = em.version

    if not em.mods:
        return

    # Импорт модуля
    import_dir(ext_dir)
    mod_path = ext_dir / f"{ext_name}.py"
    if not mod_path.exists():
        raise FileNotFoundError(f"Extension module not found: {mod_path}")

    mod = import_module(ext_name, mod_path)
    mod.kernel = kernel  # инъекция kernel в модуль (для setup)

    # Регистрация алиасов
    for alias_name, mod_name in zip(em.alias, em.mods):
        func = getattr(mod, mod_name, None)
        if func is None:
            continue
        kernel.register(alias_name, func, owner=em.name)
        if alias_name in em.variables:
            kernel.variables.add(alias_name)

    # Вызов setup
    setup_fn = getattr(mod, "setup", None)
    if setup_fn:
        setup_fn(kernel)
