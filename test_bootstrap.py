# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""Bootstrap Test — проверяет, что Builder может собрать сам себя.

1. Добавляет src/ в sys.path (ядро билдера).
2. Собирает приложение из self-host/ (сам себя).
3. Проверяет, что Kernel содержит алиас "build".
4. Вызывает kernel.build("self-host/") — вторая ступень.
"""

import sys
import pathlib

# Добавляем src/ в путь, чтобы работал import builder_core
SRC = pathlib.Path(__file__).parent / "src"
sys.path.insert(0, str(SRC.resolve()))

from builder_core.builder import Builder

APP_DIR = pathlib.Path(__file__).parent / "self-host"

print("=" * 60)
print("App Builder Bootstrap Test")
print("=" * 60)

# Шаг 1: Собираем self-host приложение
print(f"\n[1] Building self-host app from: {APP_DIR}")
kernel = Builder.build(str(APP_DIR))

print(f"    Kernel name: {kernel.metadata['_kernel']['name']}")
print(f"    Aliases: {len(kernel.alias)}")
print(f"    Alias list: {list(kernel.alias.keys())}")

# Шаг 2: Проверяем, что алиас "build" существует
assert "build" in kernel.alias, "FAIL: 'build' alias not found"
print("\n[2] 'build' alias found: OK")

# Шаг 3: Вызываем build через kernel
print(f"\n[3] Calling kernel.build('self-host/')...")
result = kernel.alias["build"]("self-host/")
print(f"    Result: {result}")

# Шаг 4: Проверяем, что результат валидный
assert isinstance(result, dict), "FAIL: result is not a dict"
assert "name" in result, "FAIL: result has no 'name'"
assert result["name"] == "SelfHostedBuilder", f"FAIL: name mismatch: {result['name']}"
assert result["aliases"] >= 2, f"FAIL: too few aliases: {result['aliases']}"

print("\n" + "=" * 60)
print("BOOTSTRAP SUCCESSFUL")
print("=" * 60)
print(f"\nSelf-hosted kernel has {result['aliases']} aliases:")
for a in result["alias_list"]:
    print(f"  - {a}")
