# Copyright (c) 2026 NumFast
# SPDX-License-Identifier: AGPL-3.0-only

"""Loader -- exec() загрузчик расширений + AST import-guard."""

import ast
import importlib.util
import sys
from pathlib import Path


def _cross_msg(label, ext_name, target, stmt):
    """Громкая ошибка: что запрещено + как правильно через depends/alias."""
    return (
        f"ImportError: {label} in extension '{ext_name}' has forbidden '{stmt}'. "
        f"Private import from another extension '{target}'. "
        f"Cross-Extension Python imports are FORBIDDEN. "
        f"Correct reuse via Builder: depends = [\"{target}\"] in {ext_name}.toml "
        f"+ call at runtime via kernel alias (kernel.alias[\"<alias>\"]), "
        f"never 'from {target}... import'. "
        f"Allowed: own _lib (from _lib... / from . ...), stdlib, third-party (numpy)."
    )


def _is_installed(top):
    """True если top — установленный модуль (stdlib/third-party), а не Extension."""
    try:
        return importlib.util.find_spec(top) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def _check_top(label, ext_name, own_names, others, *, top, dotted, stmt):
    """Один абсолютный импорт: свой/сторонний — ok, чужой Extension — REJECT."""
    if not top or top in own_names or top == "_lib":
        return
    parts = dotted.split(".")
    if top in others or (len(parts) > 1 and parts[1] == "_lib" and not _is_installed(top)):
        raise RuntimeError(_cross_msg(label, ext_name, top, stmt))


def _evict_lib_modules():
    """Выкидывает из sys.modules ключи _lib/_lib.*.

    Инвариант изоляции симметричен: чужое расширение (или тест, дергающий
    sys.path) мог оставить sys.modules['_lib'] привязанным к СВОЕМУ
    каталогу _lib. Импорт ищет _lib.<mod> по уже закешированному
    sys.modules['_lib'].__path__ и НЕ пересматривает sys.path, поэтому
    exec() ниже подхватил бы чужой каталог. Вычистка до exec делает
    видимым ровно свой _lib (свой ext_dir уже в sys.path[0]).
    """
    for mod in [m for m in sys.modules if m == "_lib" or m.startswith("_lib.")]:
        del sys.modules[mod]


def _check_extension_imports(source, *, ext_name, own_names, known_extensions, label):
    """AST-скан одного файла: запрещает приватные cross-Extension импорты."""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise RuntimeError(f"SyntaxError: {label}: {e}")
    others = set(known_extensions or ()) - set(own_names)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                _check_top(label, ext_name, own_names, others,
                           top=(a.name or "").split(".")[0],
                           dotted=a.name or "", stmt=f"import {a.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                if node.level > 1:
                    raise RuntimeError(
                        f"ImportError: {label} in extension '{ext_name}' escapes "
                        f"its folder ('from ..', level {node.level}). "
                        f"Relative imports must stay inside own Extension "
                        f"('from .x import' / 'from ._lib import'). "
                        f"Cross-Extension reuse — only via depends + kernel alias."
                    )
                continue
            mod = node.module or ""
            _check_top(label, ext_name, own_names, others,
                       top=mod.split(".")[0], dotted=mod,
                       stmt=f"from {mod} import ...")


def load_extension(kernel, ext_dir, override_metadata=None, known_extensions=None):
    """Загружает расширение через exec(), регистрирует функции в Kernel.

    1. Читает {Name}.toml (depends/alias/mods)
    2. AST-скан {Name}.py + _lib/**/*.py (import-guard: чужие Extensions запрещены,
       свой _lib/relative/stdlib/third-party разрешены)
    3. exec({Name}.py) с изолированным sys.path (свой _lib виден, чужие — нет)
    4. Регистрирует alias[i] -> PUBLIC[mods[i]], вызывает setup(kernel)
    """
    ext_dir = Path(ext_dir).resolve()
    ext_name = ext_dir.name

    # Читаем манифест
    manifest_path = ext_dir / f"{ext_name}.toml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Extension manifest not found: {manifest_path}")

    load_extension_manifest = MAIN["load_extension_manifest"]
    em = load_extension_manifest(str(manifest_path))

    # Мерж метаданных
    meta_section = em["name"]
    if meta_section not in kernel.metadata:
        kernel.metadata[meta_section] = {}
    kernel.metadata[meta_section].update(em["metadata"])
    if override_metadata:
        kernel.metadata[meta_section].update(override_metadata)

    # Версия
    if "_versions" not in kernel.metadata:
        kernel.metadata["_versions"] = {}
    kernel.metadata["_versions"][em["name"]] = em["version"]

    if not em["mods"]:
        return

    # Загружаем .py (читаем один раз)
    py_path = ext_dir / f"{ext_name}.py"
    if not py_path.exists():
        raise FileNotFoundError(f"Extension module not found: {py_path}")

    source = py_path.read_text(encoding="utf-8")

    # Import-guard ДО exec: entry + весь свой _lib
    own = {ext_name, em["name"]}
    known = set(known_extensions or ()) | own
    _check_extension_imports(source, ext_name=em["name"], own_names=own,
                             known_extensions=known, label=py_path.name)
    lib_dir = ext_dir / "_lib"
    if lib_dir.is_dir():
        for f in sorted(lib_dir.rglob("*.py")):
            if "__pycache__" in f.parts:
                continue
            rel = f.relative_to(lib_dir).as_posix()
            _check_extension_imports(f.read_text(encoding="utf-8"), ext_name=em["name"],
                                     own_names=own, known_extensions=known,
                                     label=f"{ext_name}/_lib/{rel}")

    # exec с изоляцией: свой _lib виден через sys.path, чужие Extensions — нет
    added = str(ext_dir)
    _evict_lib_modules()
    sys.path.insert(0, added)
    try:
        ns = {}
        exec(compile(source, str(py_path), "exec"), ns)
    finally:
        try:
            sys.path.remove(added)
        except ValueError:
            pass
        _evict_lib_modules()

    # Проверяем PUBLIC
    ext_public = ns.get("PUBLIC", {})
    if not ext_public:
        raise RuntimeError(f"{py_path.name} has no PUBLIC dict")

    # Регистрируем алиасы
    for alias_name, mod_name in zip(em["alias"], em["mods"]):
        func = ext_public.get(mod_name)
        if func is None:
            continue
        kernel.register(alias_name, func, owner=em["name"])
        if alias_name in em["variables"]:
            kernel.variables.add(alias_name)

    # setup(kernel): только metadata, вызывается после регистрации алиасов
    setup_fn = ns.get("setup")
    if callable(setup_fn):
        setup_fn(kernel)


PUBLIC = {"load_extension": load_extension}
