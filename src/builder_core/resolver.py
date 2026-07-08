# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""Resolver — топологическая сортировка расширений по зависимостям.

Использует алгоритм Кана (Kahn's algorithm) для ацикличных графов.
"""


def resolve_order(extensions: list[dict]) -> list[dict]:
    """Топологическая сортировка расширений.

    Принимает список dict-ов с полями name и depends.
    Возвращает отсортированный список: зависимости раньше зависимых.

    Raises:
        RuntimeError: если обнаружен цикл или отсутствующая зависимость.
    """
    if not extensions:
        return []

    deps_map: dict[str, list[str]] = {}
    name_to_ext: dict[str, dict] = {}

    for ext in extensions:
        name = ext.get("name", "")
        if not name:
            continue
        name_to_ext[name] = ext
        deps_map[name] = list(ext.get("depends", []))

    all_names = set(deps_map.keys())

    # Проверка: все зависимости существуют
    for name, deps in deps_map.items():
        for dep in deps:
            if dep not in all_names:
                raise RuntimeError(
                    f"Extension '{name}' depends on '{dep}', "
                    f"but '{dep}' is not in the extension list"
                )

    # Степень входа (сколько зависимостей ждёт)
    in_degree: dict[str, int] = {n: len(d) for n, d in deps_map.items()}

    # Зависимые (кто от нас зависит)
    dependents: dict[str, list[str]] = {n: [] for n in deps_map}
    for name, deps in deps_map.items():
        for dep in deps:
            dependents[dep].append(name)

    # Очередь: расширения без зависимостей
    queue = [n for n, deg in in_degree.items() if deg == 0]
    sorted_names: list[str] = []

    while queue:
        queue.sort()  # детерминированный порядок
        name = queue.pop(0)
        sorted_names.append(name)
        for dep in dependents[name]:
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    if len(sorted_names) != len(deps_map):
        cycle = set(deps_map.keys()) - set(sorted_names)
        raise RuntimeError(f"Circular dependency detected: {cycle}")

    return [name_to_ext[n] for n in sorted_names]


def read_depends(manifest_path) -> list[str]:
    """Читает поле depends из .toml файла расширения."""
    import tomllib
    from pathlib import Path
    path = Path(manifest_path)
    if not path.exists():
        return []
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return data.get("depends", [])
