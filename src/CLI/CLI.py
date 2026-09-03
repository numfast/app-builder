# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""CLI — точка входа командной строки.

Использование:
    python -m builder [command]

Команды:
    build <app-dir>   — собрать приложение
    test <app-dir>    — собрать и запустить тесты
    list              — показать зарегистрированные компоненты
"""

import sys


def main():
    """Точка входа CLI."""
    build = MAIN["build"]

    args = sys.argv[1:]
    if not args:
        print("Usage: python -m builder build <app-dir>", file=sys.stderr)
        print("       python -m builder list", file=sys.stderr)
        sys.exit(1)

    command = args[0]
    app_dir = args[1] if len(args) > 1 else "."

    if command == "build":
        kernel = build(app_dir)
        print(f"Built: {kernel.metadata['_kernel']['name']}")
        print(f"Aliases: {len(kernel.alias)}")

        # Если есть _default — вызвать для отображения
        default = kernel.alias.get("_default")
        if default:
            result = default()
            if result is not None:
                print(result)

    elif command == "list":
        print("MAIN Registry components:")
        for name in sorted(MAIN.keys()):
            print(f"  {name}")

    elif command == "test":
        kernel = build(app_dir)
        tests = kernel.metadata.get("_tests", {})
        if not tests:
            print("No tests found in manifest.")
            return
        failed = 0
        for tname, tspec in tests.items():
            mod_name = tspec.get("mod")
            args_list = tspec.get("args", [])
            expected = tspec.get("expected")
            expr = tspec.get("expr")

            if expr:
                result = str(eval(expr, {"kernel": kernel}))
            elif mod_name:
                fn = kernel.alias.get(mod_name)
                if fn is None:
                    print(f"  FAIL {tname}: alias '{mod_name}' not found")
                    failed += 1
                    continue
                result = str(fn(*args_list))
            else:
                print(f"  FAIL {tname}: no mod or expr")
                failed += 1
                continue

            if result == expected:
                print(f"  OK  {tname}")
            else:
                print(f"  FAIL {tname}: got '{result}', expected '{expected}'")
                failed += 1

        if failed:
            print(f"FAILED: {failed} of {len(tests)}")
            sys.exit(1)
        else:
            print(f"ALL OK: {len(tests)} tests passed")

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


PUBLIC = {"main": main}
