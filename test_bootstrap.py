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


def _write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _make_ext(parent, name, toml_body, py_body, lib_files=None):
    """Создаёт папку Extension/{Name}.toml + {Name}.py + _lib/*.py. Возвращает путь."""
    ext_dir = os.path.join(parent, name)
    os.makedirs(os.path.join(ext_dir, "_lib"), exist_ok=True)
    _write(os.path.join(ext_dir, f"{name}.toml"), toml_body)
    _write(os.path.join(ext_dir, f"{name}.py"), py_body)
    for rel, body in (lib_files or {}).items():
        full = os.path.join(ext_dir, "_lib", rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        _write(full, body)
    return ext_dir


def test_extension_with_import():
    """7. Приватный cross-Extension импорт отклоняется (3 формы, громкая ошибка)."""
    from builder import MAIN
    load_extension = MAIN["load_extension"]
    Kernel = MAIN["Kernel"]
    import tempfile
    import shutil

    cases = [
        ("from Greeting._lib import greet", "from Greeting._lib import greet\n"),
        ("import Greeting._lib", "import Greeting._lib\n"),
        ("from Greeting import hello_fn", "from Greeting import hello_fn\n"),
    ]
    for title, stmt in cases:
        tmpdir = tempfile.mkdtemp()
        try:
            ext_dir = _make_ext(
                tmpdir, "BadImport",
                'name = "BadImport"\nalias = ["bad"]\nmods = ["bad_fn"]\n',
                f'{stmt}\n'
                f'def bad_fn():\n    return "bad"\n\nPUBLIC = {{"bad_fn": bad_fn}}\n',
            )
            try:
                kernel = Kernel(name="Test")
                load_extension(kernel, ext_dir,
                               known_extensions={"BadImport", "Greeting"})
                print(f"  FAIL: cross-import not detected ({title})")
                assert False
            except RuntimeError as e:
                msg = str(e)
                assert "ImportError" in msg, msg
                assert "FORBIDDEN" in msg, msg
                assert "depends" in msg and "alias" in msg, msg
                assert "Greeting" in msg, msg
                print(f"  OK: rejected ({title}): {msg[:100]}...")
        finally:
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)


def test_guard_allows_own_and_thirdparty():
    """8. Guard разрешает: свой _lib, relative внутри, stdlib, third-party (numpy)."""
    from builder import MAIN
    load_extension = MAIN["load_extension"]
    Kernel = MAIN["Kernel"]
    import tempfile
    import shutil

    tmpdir = tempfile.mkdtemp()
    try:
        ext_dir = _make_ext(
            tmpdir, "Good",
            'name = "Good"\nalias = ["calc"]\nmods = ["calc_fn"]\n',
            'import math\n'
            'from _lib.arith import calc_fn\n\n'
            'def setup(kernel):\n'
            '    kernel.metadata.setdefault("Good", {})["version"] = "0.1.0"\n\n'
            'PUBLIC = {"calc_fn": calc_fn}\n',
            lib_files={
                "__init__.py": "",
                "arith.py": (
                    "import math\n"
                    "import numpy as np\n"
                    "from .helper import double\n\n"
                    "def calc_fn(x):\n"
                    "    return double(x) + int(math.floor(0.5)) + int(np.int64(1))\n"
                ),
                "helper.py": "def double(x):\n    return x * 2\n",
            },
        )
        kernel = Kernel(name="Test")
        load_extension(kernel, ext_dir, known_extensions={"Good", "Other"})
        assert kernel.alias["calc"](21) == 43, kernel.alias["calc"](21)
        assert kernel.metadata["Good"]["version"] == "0.1.0"
        print("  OK: own _lib + relative + math/numpy allowed, setup() ran")
    finally:
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)


def test_nested_hierarchy_depends():
    """9. Иерархия: общий Core в корне, ребёнок Compute/Reduce глубже.

    depends сверху вниз через depends/alias/setup, хелпер один раз на родителе,
    порядок из depends (в full.toml ребёнок ПЕРВЫМ — Resolver всё равно ставит Core первым).
    """
    from builder import MAIN
    build = MAIN["build"]
    import tempfile
    import shutil

    tmpdir = tempfile.mkdtemp()
    try:
        app_dir = os.path.join(tmpdir, "hier")
        core_dir = os.path.join(app_dir, "src", "Core")
        red_dir = os.path.join(app_dir, "src", "Compute", "Reduce")
        os.makedirs(os.path.join(core_dir, "_lib"))
        os.makedirs(os.path.join(red_dir, "_lib"))
        _write(os.path.join(app_dir, "full.toml"),
               '[kernel]\nname = "HierApp"\n\n'
               '[[extensions]]\nname = "Reduce"\npath = "src/Compute/Reduce"\n\n'
               '[[extensions]]\nname = "Core"\npath = "src/Core"\n')
        _write(os.path.join(core_dir, "Core.toml"),
               'name = "Core"\nversion = "0.1.0"\n'
               'alias = ["shared_add"]\nmods = ["shared_add_fn"]\n')
        _write(os.path.join(core_dir, "Core.py"),
               'from _lib.common import shared_add_fn\n\n'
               'def setup(kernel):\n'
               '    kernel.metadata.setdefault("Core", {})["version"] = "0.1.0"\n\n'
               'PUBLIC = {"shared_add_fn": shared_add_fn}\n')
        _write(os.path.join(core_dir, "_lib", "common.py"),
               'def shared_add_fn(a, b):\n    return a + b\n')
        _write(os.path.join(red_dir, "Reduce.toml"),
               'name = "Reduce"\nversion = "0.1.0"\ndepends = ["Core"]\n'
               'alias = ["radd"]\nmods = ["radd_fn"]\n')
        _write(os.path.join(red_dir, "Reduce.py"),
               'from _lib.reuse import radd_impl\n\n'
               '_box = {}\n\n'
               'def radd_fn(a, b):\n'
               '    return radd_impl(a, b, _box["kernel"].alias["shared_add"])\n\n'
               'def setup(kernel):\n'
               '    _box["kernel"] = kernel\n'
               '    kernel.metadata.setdefault("Reduce", {})["version"] = "0.1.0"\n\n'
               'PUBLIC = {"radd_fn": radd_fn}\n')
        _write(os.path.join(red_dir, "_lib", "reuse.py"),
               'def radd_impl(a, b, add):\n    return add(a, b)\n')

        kernel = build(app_dir)
        assert kernel.alias["radd"](2, 3) == 5
        assert kernel.alias["shared_add"](2, 3) == 5
        # depends-порядок: Core загружен первым несмотря на порядок в full.toml
        assert list(kernel.metadata["_versions"]) == ["Core", "Reduce"], \
            kernel.metadata["_versions"]
        # setup() обоих отработал
        assert kernel.metadata["Core"]["version"] == "0.1.0"
        assert kernel.metadata["Reduce"]["version"] == "0.1.0"
        # хелпер один раз: в Reduce нет копии реализации
        for root, _, files in os.walk(red_dir):
            for fn in files:
                if fn.endswith(".py"):
                    src = open(os.path.join(root, fn), encoding="utf-8").read()
                    assert "a + b" not in src, f"duplicate helper in {fn}"
        print("  OK: nested Core->Reduce via depends/alias/setup, helper once")
    finally:
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
        ("Cross-Import Rejection", test_extension_with_import),
        ("Guard Allows Own/3rd-party", test_guard_allows_own_and_thirdparty),
        ("Nested Hierarchy depends", test_nested_hierarchy_depends),
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
