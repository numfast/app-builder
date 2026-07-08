# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""Kernel — ядро приложения.

Хранит алиасы (имя → функция), метаданные и переменные.
"""


class Kernel:
    """Ядро приложения. Плоское пространство имён для всех модов.

    После сборки содержит:
      alias    — dict[str, callable]  все функции приложения
      metadata — dict[str, dict]      метаданные расширений
      variables — set[str]            алиасы-переменные (автовызов)
    """

    def __init__(self, name: str = "App", singleton: bool = True):
        self.alias: dict[str, callable] = {}
        self._owner: dict[str, str] = {}
        self.metadata: dict[str, dict] = {"_kernel": {"name": name, "singleton": singleton}}
        self.variables: set[str] = set()

    def register(self, alias_name: str, func: callable, owner: str = ""):
        """Регистрирует функцию под алиасом."""
        self.alias[alias_name] = func
        if owner:
            self._owner[alias_name] = owner
        # Системный алиас с префиксом расширения
        if owner:
            sys_alias = f"_{owner}_{alias_name}"
            self.alias[sys_alias] = func
            self._owner[sys_alias] = owner

    def __getattr__(self, name: str):
        """Позволяет вызывать kernel.func_name()."""
        if name.startswith("_"):
            raise AttributeError(name)
        fn = self.alias.get(name)
        if fn is None:
            raise AttributeError(f"alias '{name}' not found")
        if name in self.variables:
            return fn()
        return fn

    def __repr__(self) -> str:
        fn = self.alias.get("_default")
        if fn:
            try:
                return str(fn())
            except Exception:
                pass
        return f"Kernel({self.metadata['_kernel']['name']})"
