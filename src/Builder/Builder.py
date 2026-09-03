# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""Builder — оркестратор сборки приложений.

Ноль импортов. Всё через MAIN (Registry).
"""

from pathlib import Path


def build(app_dir):
    """Собирает приложение из директории с full.toml.

    Алгоритм:
      1. Парсит full.toml (через MAIN["load_app_manifest"])
      2. Для каждого [[extensions]]:
         a. Читает {Name}.toml
         b. Загружает {Name}.py через exec() → PUBLIC
         c. Регистрирует alias[i] → mods[i] в Kernel
      3. Возвращает Kernel
    """
    # Берём компоненты из Registry
    Kernel = MAIN["Kernel"]
    load_app_manifest = MAIN["load_app_manifest"]
    load_extension_manifest = MAIN["load_extension_manifest"]
    resolve_order = MAIN["resolve_order"]
    load_extension = MAIN["load_extension"]

    base = Path(app_dir).resolve()
    manifest_path = base / "full.toml"

    if not manifest_path.exists():
        raise FileNotFoundError(f"full.toml not found in {base}")

    # Парсим манифест
    app = load_app_manifest(str(manifest_path))

    # Создаём Kernel
    kernel = Kernel(name=app["kernel"]["name"], singleton=app["kernel"]["singleton"])

    # Собираем extension refs с depends
    ext_refs = []
    for ext_cfg in app["extensions"]:
        name = ext_cfg.get("name", "")
        path = ext_cfg.get("path", "")
        if not path:
            continue

        ext_dir = (base / path).resolve()
        ext_manifest_path = ext_dir / f"{ext_dir.name}.toml"

        depends = []
        if ext_manifest_path.exists():
            em = load_extension_manifest(str(ext_manifest_path))
            depends = em.get("depends", [])

        ext_refs.append({
            "name": name,
            "path": str(ext_dir),
            "depends": depends,
            "metadata": ext_cfg.get("metadata", {}),
        })

    # Топологическая сортировка
    ordered = resolve_order(ext_refs)

    # Загрузка расширений по порядку
    for ref in ordered:
        ext_path = Path(ref["path"])
        override = {**ref.get("metadata", {}),
                    **app.get("extensions_meta", {}).get(ext_path.name, {})}

        load_extension(kernel, str(ext_path),
                       override_metadata=override or None)

    if app.get("tests"):
        kernel.metadata["_tests"] = app["tests"]

    return kernel


PUBLIC = {"build": build}
