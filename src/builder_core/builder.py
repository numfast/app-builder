# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""Builder — оркестратор сборки приложений.

Связывает manifest → resolver → loader → kernel.
"""

from pathlib import Path

from builder_core.kernel import Kernel
from builder_core.manifest import load_app_manifest, load_extension_manifest
from builder_core.resolver import resolve_order
from builder_core.loader import load_extension, import_dir


class Builder:
    """Сборщик приложений из расширений."""

    @staticmethod
    def build(app_dir: str | Path) -> Kernel:
        """Собирает приложение из директории с full.toml.

        Args:
            app_dir: Путь к директории приложения (содержит full.toml).

        Returns:
            Kernel — собранное ядро со всеми алиасами и метаданными.
        """
        base = Path(app_dir).resolve()

        # 1. Определяем путь к манифесту
        manifest_path = base / "full.toml"
        if not manifest_path.exists():
            raise FileNotFoundError(f"full.toml not found in {base}")

        # 2. Парсим манифест
        app = load_app_manifest(manifest_path)

        # 3. Создаём Kernel
        kernel = Kernel(name=app.kernel_name, singleton=app.singleton)

        # 4. Добавляем base в sys.path
        import_dir(base)

        # 5. Собираем extension refs с depends
        ext_refs = []
        for ext_cfg in app.extensions:
            name = ext_cfg.get("name", "")
            path = ext_cfg.get("path", "")
            if not path:
                continue

            ext_dir = (base / path).resolve()

            # Читаем depends из манифеста расширения
            ext_manifest_path = ext_dir / f"{ext_dir.name}.toml"
            depends = []
            if ext_manifest_path.exists():
                em = load_extension_manifest(ext_manifest_path)
                depends = em.depends

            ext_refs.append({
                "name": name,
                "path": str(ext_dir),
                "depends": depends,
                "metadata": ext_cfg.get("metadata", {}),
            })

        # 6. Топологическая сортировка
        ordered = resolve_order(ext_refs)

        # 7. Загрузка расширений по порядку
        for ref in ordered:
            ext_path = Path(ref["path"])
            override_meta = ref.get("metadata", {})

            # Добавляем extensions_meta если есть
            meta_section = ext_path.name
            app_meta = app.extensions_meta.get(meta_section, {})
            merged_meta = dict(override_meta)
            merged_meta.update(app_meta)

            load_extension(kernel, ext_path, override_metadata=merged_meta if merged_meta else None)

        return kernel

    @staticmethod
    def build_self(app_dir: str | Path) -> Kernel:
        """То же что build, но для самосборки (алиас)."""
        return Builder.build(app_dir)
