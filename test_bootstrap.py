# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""Bootstrap Test -- self-hosting verification.

Проверяет, что App Builder может загрузить себя и собрать приложение.

Запуск:
    python test_bootstrap.py
"""

import sys
import os

# Добавляем корень проекта в путь
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def test_import():
    """1. Импорт builder'а."""
    from builder import MAIN
    required = {"Kernel", "boot", "build", "load_app_manifest",
                 "load_extension_manifest", "load_extension",
                 "resolve_order", "main"}
    found = set(MAIN.keys())
    assert required.issubset(found), f"Missing: {required - found}"
    print(f"  OK: {len(MAIN)} components in MAIN Registry")
    print(f"  Components: {sorted(MAIN.keys())}")


def test_build_hello():
    """2. Сборка hello"""
    from builder import MAIN
    build = MAIN["build"]
    app_dir = os.path.join(HERE, "examples", "hello")
    kernel = build(app_dir)
    assert kernel.metadata["_kernel"]["name"] == "HelloApp"
    result = kernel.alias["hello"]("World")
    assert result == "Hello, World!", f"Got: {result}"
    print(f"  OK: HelloApp built, hello('World') = '{result}'")


def test_build_calculator():
    """3. Сборка calculator"""
    from builder import MAIN
    build = MAIN["build"]
    app_dir = os.path.join(HERE, "examples", "calculator")
    kernel = build(app_dir)
    assert kernel.metadata["_kernel"]["name"] == "Calc"
    assert kernel.alias["add"](2, 3) == 5
    assert kernel.alias["mul"](3, 5) == 15
    assert kernel.alias["sin"](0) == 0.0
    pi = kernel.alias["pi"]()
    assert abs(pi - 3.141592653589793) < 1e-15
    print(f"  OK: Calc built, add(2,3)=5, mul(3,5)=15, sin(0)=0.0, pi={pi}")


def test_duplicate_public():
    """4. Дубликаты PUBLIC ключей запрещены."""
    from builder import MAIN
    boot = MAIN["boot"]
    import tempfile
    tmpdir = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmpdir, "010_a.py"), "w") as f:
            f.write('PUBLIC = {"x": 1}\n')
        with open(os.path.join(tmpdir, "020_b.py"), "w") as f:
            f.write('PUBLIC = {"x": 2}\n')
        boot(tmpdir)
        print("  FAIL: duplicate PUBLIC key not detected")
        assert False
    except RuntimeError as e:
        if "Duplicate PUBLIC key" in str(e):
            print(f"  OK: duplicate detected: {e}")
        else:
            raise
    finally:
        import shutil
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)


def test_cycle_detection():
    """5. Циклические зависимости обнаруживаются."""
    from builder import MAIN
    resolve_order = MAIN["resolve_order"]
    exts = [
        {"name": "A", "depends": ["B"]},
        {"name": "B", "depends": ["C"]},
        {"name": "C", "depends": ["A"]},
    ]
    try:
        resolve_order(exts)
        print("  FAIL: cycle not detected")
        assert False
    except RuntimeError as e:
        if "Circular" in str(e):
            print(f"  OK: cycle detected: {e}")
        else:
            raise


def test_missing_dep():
    """6. Отсутствующая зависимость обнаруживается."""
    from builder import MAIN
    resolve_order = MAIN["resolve_order"]
    exts = [
        {"name": "A", "depends": ["B"]},
        {"name": "C", "depends": []},
    ]
    try:
        resolve_order(exts)
        print("  FAIL: missing dep not detected")
        assert False
    except RuntimeError as e:
        if "not in the extension list" in str(e):
            print(f"  OK: missing dep detected: {e}")
        else:
            raise


def test_extension_with_import():
    """7. Расширение с import отклоняется."""
    from builder import MAIN
    load_extension = MAIN["load_extension"]
    Kernel = MAIN["Kernel"]
    import tempfile

    tmpdir = tempfile.mkdtemp()
    ext_dir = os.path.join(tmpdir, "BadImport")
    os.makedirs(ext_dir)
    with open(os.path.join(ext_dir, "BadImport.toml"), "w") as f:
        f.write('name = "BadImport"\nalias = ["bad"]\nmods = ["bad_fn"]\n')
    with open(os.path.join(ext_dir, "BadImport.py"), "w") as f:
        f.write('import os\n\ndef bad_fn():\n    return "bad"\n\nPUBLIC = {"bad_fn": bad_fn}\n')

    try:
        kernel = Kernel(name="Test")
        load_extension(kernel, ext_dir)
        print("  FAIL: import in extension not detected")
        assert False
    except RuntimeError as e:
        if "ImportError" in str(e) or "must NOT have imports" in str(e):
            print(f"  OK: import detected: {e}")
        else:
            raise
    finally:
        import shutil
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)


def run():
    print("=" * 50)
    print("App Builder Bootstrap Test")
    print("=" * 50)

    tests = [
        ("Import", test_import),
        ("Build Hello", test_build_hello),
        ("Build Calculator", test_build_calculator),
        ("Duplicate PUBLIC", test_duplicate_public),
        ("Cycle Detection", test_cycle_detection),
        ("Missing Dep", test_missing_dep),
        ("Import Rejection", test_extension_with_import),
    ]

    passed = 0
    failed = 0
    for name, func in tests:
        print(f"\n[{name}]")
        try:
            func()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*50}")
    print(f"Result: {passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
    print("OK: App Builder is self-hosting.")


if __name__ == "__main__":
    run()
