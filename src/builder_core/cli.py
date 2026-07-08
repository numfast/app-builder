# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""CLI — интерфейс командной строки.

Использование:
    python -m builder_core run <app_dir>
    python -m builder_core build <app_dir>
"""

import sys
from pathlib import Path

from builder_core.builder import Builder


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python -m builder_core run|build <app_dir>")
        return

    command = args[0]
    app_dir = args[1] if len(args) > 1 else "."

    if command == "run":
        kernel = Builder.build(app_dir)
        start_fn = kernel.alias.get("start")
        if start_fn:
            result = start_fn()
            if result is not None:
                print(result)
        else:
            print(f"Kernel ready. Aliases: {list(kernel.alias.keys())}")

    elif command == "build":
        kernel = Builder.build(app_dir)
        print(f"Build OK: {len(kernel.alias)} aliases")
        print(f"  Kernel: {kernel.metadata['_kernel']['name']}")
        print(f"  Aliases: {list(kernel.alias.keys())}")

    else:
        print(f"Unknown command: {command}")
        print("Usage: python -m builder_core run|build <app_dir>")


if __name__ == "__main__":
    main()
