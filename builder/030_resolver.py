# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""Resolver — топологическая сортировка расширений (Kahn's algorithm)."""


def resolve_order(extensions):
    """Kahn: зависимости раньше зависимых. RuntimeError: цикл/нет зависимости."""
    if not extensions:
        return []

    deps_map = {}
    name_to_ext = {}

    for ext in extensions:
        name = ext.get("name", "")
        if not name:
            continue
        name_to_ext[name] = ext
        deps_map[name] = list(ext.get("depends", []))

    all_names = set(deps_map.keys())

    for name, deps in deps_map.items():
        for dep in deps:
            if dep not in all_names:
                raise RuntimeError(
                    f"Extension '{name}' depends on '{dep}', "
                    f"but '{dep}' is not in the extension list"
                )

    in_degree = {n: len(d) for n, d in deps_map.items()}
    dependents = {n: [] for n in deps_map}
    for name, deps in deps_map.items():
        for dep in deps:
            dependents[dep].append(name)

    queue = [n for n, deg in in_degree.items() if deg == 0]
    sorted_names = []

    while queue:
        queue.sort()
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


PUBLIC = {"resolve_order": resolve_order}
