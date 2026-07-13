"""
concat.py — App Builder: concatenator.

Читает full.toml, находит расширения, склеивает .py файлы,
добавляет Kernel + alias-регистрацию.

Использование:
    python scripts/concat.py examples/hello/
    python scripts/concat.py examples/hello/full.bondiana.toml

Выход: examples/hello/dist/hello.py  (или dist/hello_bondiana.py)
"""

import sys
import os
import tomllib
from pathlib import Path


def load_toml(path):
    with open(path, "rb") as f:
        return tomllib.load(f)


def resolve_order(extensions):
    """Топологическая сортировка. Сохраняет порядок из манифеста если нет зависимостей."""
    deps = {e["name"]: e.get("depends", []) for e in extensions}
    names = set(deps.keys())

    for name, dd in deps.items():
        for d in dd:
            if d not in names:
                raise RuntimeError(f"Extension '{name}' depends on '{d}', not found")

    # Позиция в манифесте — определяет порядок при равных зависимостях
    position = {e["name"]: i for i, e in enumerate(extensions)}

    in_deg = {n: len(d) for n, d in deps.items()}
    children = {n: [] for n in names}
    for name, dd in deps.items():
        for d in dd:
            children[d].append(name)

    # Стартуем с вершин без зависимостей, но в порядке манифеста
    queue = sorted(
        [n for n, d in in_deg.items() if d == 0],
        key=lambda n: position.get(n, 999)
    )
    ordered = []

    while queue:
        n = queue.pop(0)
        ordered.append(n)
        for c in children[n]:
            in_deg[c] -= 1
            if in_deg[c] == 0:
                queue.append(c)
                queue.sort(key=lambda n: position.get(n, 999))

    if len(ordered) != len(names):
        cycle = names - set(ordered)
        raise RuntimeError(f"Circular dependency: {cycle}")

    name_map = {e["name"]: e for e in extensions}
    return [name_map[n] for n in ordered]


def build(app_path):
    app_path = Path(app_path).resolve()
    
    # Определяем директорию приложения
    if app_path.name == "full.toml" or app_path.suffix == ".toml":
        app_dir = app_path.parent
        manifest_path = app_path
        manifest_name = app_path.stem  # full or full.bondiana
    else:
        app_dir = app_path
        manifest_path = app_dir / "full.toml"
        manifest_name = "full"
    
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Building: {manifest_path}")
    
    # Парсим манифест
    manifest = load_toml(manifest_path)
    kernel_name = manifest.get("kernel", {}).get("name", "App")
    raw_extensions = manifest.get("extensions", [])
    
    if not raw_extensions:
        print("No extensions defined", file=sys.stderr)
        sys.exit(1)
    
    # Собираем пути
    extensions = []
    for ext in raw_extensions:
        ext_dir = (app_dir / ext["path"]).resolve()
        ext_name = ext_dir.name
        toml_path = ext_dir / f"{ext_name}.toml"
        py_path = ext_dir / f"{ext_name}.py"
        
        if not toml_path.exists():
            print(f"  WARN: {toml_path} not found", file=sys.stderr)
            continue
        if not py_path.exists():
            print(f"  WARN: {py_path} not found", file=sys.stderr)
            continue
        
        ext_manifest = load_toml(toml_path)
        extensions.append({
            "name": ext_name,
            "path": str(ext_dir),
            "py_path": py_path,
            "toml": ext_manifest,
            "depends": ext_manifest.get("depends", []),
        })
    
    # Сортируем
    ordered = resolve_order(extensions)
    
    # Формируем выходной файл
    output_name = f"{kernel_name.lower()}.py"
    if manifest_name != "full":
        output_name = f"{manifest_name}.py"
    
    dist_dir = app_dir / "dist"
    dist_dir.mkdir(exist_ok=True)
    output_path = dist_dir / output_name
    
    lines = []
    
    # Header
    lines.append("#")
    lines.append(f"# {kernel_name} — built by App Builder")
    lines.append(f"# Source: {app_dir}")
    lines.append(f"# Manifest: {manifest_path.name}")
    lines.append("#")
    lines.append("")
    
    # Extension code (concatenated)
    for ext in ordered:
        py_path = ext["py_path"]
        rel_path = py_path.relative_to(app_dir.parent)  # relative to app-builder/
        
        lines.append(f"# ==== {rel_path} ====")
        code = py_path.read_text(encoding="utf-8")
        lines.append(code.rstrip())
        lines.append("")
    
    # Kernel class
    lines.append("# ==== Kernel ====")
    kernel_code = """
class Kernel:
    \"\"\"Ядро приложения. alias[name] -> function.\"\"\"
    def __init__(self, name="App"):
        self.alias = {}
        self._owner = {}
        self.metadata = {"_kernel": {"name": name}}
        self.variables = set()

    def register(self, alias_name, func, owner=""):
        self.alias[alias_name] = func
        if owner:
            self._owner[alias_name] = owner
            sys_alias = f"_{owner}_{alias_name}"
            self.alias[sys_alias] = func

    def call(self, name, *args):
        fn = self.alias[name]
        if name in self.variables:
            return fn()
        return fn(*args)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        fn = self.alias.get(name)
        if fn is None:
            raise AttributeError(f"alias '{name}' not found")
        if name in self.variables:
            return fn()
        return fn

    def __repr__(self):
        fn = self.alias.get("_default")
        if fn:
            try:
                return str(fn())
            except Exception:
                pass
        return f"Kernel({self.metadata['_kernel']['name']})"
"""
    lines.append(kernel_code.strip())
    lines.append("")
    
    # Build app
    lines.append("# ==== Build app ====")
    lines.append(f'APP = Kernel("{kernel_name}")')
    lines.append("")
    
    for ext in ordered:
        ext_name = ext["name"]
        ext_toml = ext["toml"]
        aliases = ext_toml.get("alias", [])
        mods = ext_toml.get("mods", [])
        variables = ext_toml.get("variables", [])
        
        for alias_name, mod_name in zip(aliases, mods):
            lines.append(f'APP.register("{alias_name}", {mod_name}, "{ext_name}")')
        
        for var_name in variables:
            lines.append(f'APP.variables.add("{var_name}")')
    
    lines.append("")
    
    # Footer
    lines.append("# ==== End ====")
    lines.append("")
    
    output = "\n".join(lines)
    output_path.write_text(output, encoding="utf-8")
    
    print(f"Output: {output_path}")
    print(f"Size: {len(output)} bytes, {len(lines)} lines")
    print("Done.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/concat.py <app-dir-or-manifest>", file=sys.stderr)
        sys.exit(1)
    build(sys.argv[1])