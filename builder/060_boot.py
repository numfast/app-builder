# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""Bootloader — exec() всех .py директории, сбор PUBLIC в MAIN Registry."""

from pathlib import Path


def boot(builder_dir=None):
    """Сканирует директорию, exec() все .py, собирает MAIN (файлы получают MAIN в globals)."""
    if builder_dir is None:
        builder_dir = Path(__file__).parent

    builder_dir = Path(builder_dir).resolve()

    MAIN = {}

    # Сортируем файлы по имени (010_, 020_, ...)
    py_files = sorted(builder_dir.glob("*.py"))
    # Исключаем __init__.py
    py_files = [f for f in py_files if not f.name.startswith("__")]

    for f in py_files:
        # Инжектим MAIN в namespace — так функции могут делать MAIN["name"]
        ns = {"MAIN": MAIN, "__builtins__": __builtins__}
        try:
            exec(f.read_text(encoding="utf-8"), ns)
        except Exception as e:
            raise RuntimeError(f"Boot failed loading {f.name}: {e}")

        if "PUBLIC" in ns:
            for key, value in ns["PUBLIC"].items():
                if key in MAIN:
                    raise RuntimeError(
                        f"Duplicate PUBLIC key '{key}' in {f.name} "
                        f"(already defined in another file)"
                    )
                MAIN[key] = value

    return MAIN


PUBLIC = {"boot": boot}
