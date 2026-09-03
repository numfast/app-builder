# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""App Builder — Zero Import Architecture.

При импорте собирает MAIN Registry через Boot.boot() (060_boot.py — единый код).
Использование:
    from builder import MAIN
    MAIN["build"]("my-app/")
"""

import builtins
import pathlib

_builder_dir = pathlib.Path(__file__).parent
_ns = {"MAIN": {}, "__builtins__": builtins}
exec((_builder_dir / "060_boot.py").read_text(encoding="utf-8"), _ns)
MAIN = _ns["boot"](_builder_dir)
