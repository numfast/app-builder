# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""App Builder — Zero Import Architecture.

При импорте automically запускает boot() и собирает MAIN Registry.
Использование:
    from builder import MAIN
    MAIN["build"]("my-app/")
"""

import builtins
import pathlib

_builder_dir = pathlib.Path(__file__).parent
_MAIN = {}

for _f in sorted(_builder_dir.glob("*.py")):
    if _f.name.startswith("__"):
        continue
    # Инжектим MAIN + builtins
    _ns = {"MAIN": _MAIN, "__builtins__": builtins}
    exec(_f.read_text(encoding="utf-8"), _ns)
    if "PUBLIC" in _ns:
        for _k, _v in _ns["PUBLIC"].items():
            if _k in _MAIN:
                raise RuntimeError(f"Duplicate PUBLIC key: {_k}")
            _MAIN[_k] = _v

MAIN = _MAIN
