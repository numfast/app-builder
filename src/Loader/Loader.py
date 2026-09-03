# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""Loader -- exec() загрузчик расширений."""

from pathlib import Path


def load_extension(kernel, ext_dir, override_metadata=None):
    """Загружает расширение через exec(), регистрирует функции в Kernel.

    1. Читает {Name}.toml
    2. exec({Name}.py) -> получает PUBLIC
    3. Регистрирует alias[i] -> PUBLIC[mods[i]] в kernel
    """
    ext_dir = Path(ext_dir).resolve()
    ext_name = ext_dir.name

    # Читаем манифест
    manifest_path = ext_dir / f"{ext_name}.toml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Extension manifest not found: {manifest_path}")

    load_extension_manifest = MAIN["load_extension_manifest"]
    em = load_extension_manifest(str(manifest_path))

    # Мерж метаданных
    meta_section = em["name"]
    if meta_section not in kernel.metadata:
        kernel.metadata[meta_section] = {}
    kernel.metadata[meta_section].update(em["metadata"])
    if override_metadata:
        kernel.metadata[meta_section].update(override_metadata)

    # Версия
    if "_versions" not in kernel.metadata:
        kernel.metadata["_versions"] = {}
    kernel.metadata["_versions"][em["name"]] = em["version"]

    if not em["mods"]:
        return

    # Загружаем .py через exec (читаем один раз)
    py_path = ext_dir / f"{ext_name}.py"
    if not py_path.exists():
        raise FileNotFoundError(f"Extension module not found: {py_path}")

    source = py_path.read_text(encoding="utf-8")

    # Проверка на импорты ДО exec (только module-level, не внутри функций)
    for line in source.split("\n"):
        if line.startswith((" ", "\t")):
            continue
        stripped = line.strip()
        # Разрешён только import tomllib в manifest-файлах
        if stripped.startswith(("import ", "from ")) and "tomllib" not in stripped:
            raise RuntimeError(
                f"ImportError: {py_path.name} has '{stripped}'. "
                f"Extensions must NOT have imports."
            )

    ns = {}
    exec(source, ns)

    # Проверяем PUBLIC
    ext_public = ns.get("PUBLIC", {})
    if not ext_public:
        raise RuntimeError(f"{py_path.name} has no PUBLIC dict")

    # Регистрируем алиасы
    for alias_name, mod_name in zip(em["alias"], em["mods"]):
        func = ext_public.get(mod_name)
        if func is None:
            continue
        kernel.register(alias_name, func, owner=em["name"])
        if alias_name in em["variables"]:
            kernel.variables.add(alias_name)


PUBLIC = {"load_extension": load_extension}
