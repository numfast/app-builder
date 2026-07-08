# app-builder

**Language-agnostic application builder.**

Builder is a DSL (TOML) + runtime (Python, JavaScript, ...) for composing
applications from modular extensions.

```
full.toml  →  Builder  →  Kernel{aliases[], metadata[], variables[]}
```

Extensions are flat `.py`/`.js` files with functions.
No imports between extensions. No classes. No packages.
All communication through `kernel.alias`.

---

## Repository structure

```
app-builder/
  SPEC.md           # This file
  README.md         # Quick start
  specs/            # DSL grammar (language-agnostic)
    app.md
    extension.md
    builder.md
  docs/             # Architecture, patterns, cheatsheet
    000_overview.md
    010_manifest.md
    020_language_backends.md
    030_self_hosting.md
  python/
    app_builder/    # Python runtime implementation
  javascript/
    app-builder/    # JavaScript runtime implementation
  examples/
    hello-python/   # Python hello app
    hello-js/       # JavaScript hello app
    calculator-python/
    calculator-js/
  tests/            # Cross-language test suite
```

---

## Core concepts

### 1. Application = manifest + extensions

```
my-app/
  full.toml            # App manifest
  src/
    _main/             # Entry point (must)
      _main.toml + _main.{py|js}
    Greeting/          # Extension
      Greeting.toml + Greeting.{py|js} + _lib/
    Bondiana/          # Extension (shadows Greeting)
      Bondiana.toml + Bondiana.{py|js} + _lib/
```

### 2. Flat alias namespace

All mods from all extensions end up in one flat `kernel.alias` dict.
No nesting. No packages.

```
kernel.alias["name"]     = Bondiana.name     # shadows Greeting.name
kernel.alias["greeting"] = Bondiana.greeting # shadows Greeting.greeting
kernel.alias["setName"]  = Bondiana.setName  # shadows Greeting.setName
```

### 3. Layering (Docker-style shadowing)

Extensions loaded later SHADOW aliases from earlier ones.
Order determined by `depends` field (topological sort).

```
Layer 0: _kernel      (system)
Layer 1: _main        (entry point)
Layer 2: Greeting     (base: name, greeting)
Layer 3: Bondiana     (override: name, greeting, + last_name)
```

### 4. No imports between extensions

Extensions NEVER import each other.
Cross-extension access is ONLY through `kernel.alias` in `setup(kernel)`.

```python
# ❌ WRONG
from Runtime import compile

# ✅ CORRECT
def setup(kernel):
    compile_fn = kernel.alias.get("compile")
    if compile_fn:
        compile_fn(task)
```

### 5. Module-level imports forbidden

Extension `{Name}.py`/`{Name}.js` files MUST NOT have module-level import/require statements.
Only lazy (function-level) imports are allowed.

```python
# ❌ WRONG (module-level)
from _lib.greet import name

# ✅ CORRECT (function-level)
def name():
    from _lib.greet import name as _name
    return _name()
```

---

## DSL grammar

Two manifest types:

### App manifest (`full.toml`)

```toml
[kernel]
name = "MyApp"          # Application name
singleton = true        # Single instance

[[extensions]]
name = "Greeting"       # Extension display name
path = "src/Greeting"   # Path relative to manifest

[extensions_meta.Greeting]
initial_name = "World"  # Metadata passed to extension setup()

[tests]                 # Test definitions (optional)
add = { mod = "eval", args = ["2+2"], expected = "4" }

extends = "base.toml"   # Manifest inheritance (optional)
```

### Extension manifest (`{Name}.toml`)

```toml
name = "Greeting"
version = "1.0.0"
depends = []            # Dependency list
language = "python"     # Runtime backend (auto-detected if single file)
alias = ["name", "setName", "greeting"]
mods = ["name", "setName", "greeting"]
variables = ["name"]    # Auto-call on read

[metadata]
initial_name = "World"
```

---

## Language backends

### Python (`python/app_builder/`)

Reads TOML manifests, loads `.py` extensions, produces Python Kernel.

```bash
python -m app_builder run full.toml
python -m app_builder test test.toml
python -m app_builder build full.toml
python -m app_builder package full.toml output.zip
```

### JavaScript (`javascript/app-builder/`)

Reads TOML manifests (same DSL), loads `.js` extensions, produces JS Kernel.

```bash
npx app-builder run full.toml
npx app-builder test test.toml
```

### Extension code per language

```
Trading/
  Trading.toml          # DSL (same for all languages)
  python/
    Trading.py          # Python implementation
  javascript/
    Trading.js          # JS implementation
```

Or flat (single language):

```
Trading/
  Trading.toml
  Trading.py
```

---

## Build process

```
1. load_app("full.toml")
   → AppManifest{kernel, extensions[], extensions_meta, tests}

2. resolve_paths(base, extensions)
   → ExtensionRef[]{name, path, metadata}

3. resolve_order(refs, depends)
   → Topological sort → ordered ExtensionRef[]

4. For each extension in order:
   a. Parse {Name}.toml
   b. Merge metadata into kernel.metadata
   c. Check for forbidden module-level imports
   d. Add extension dir to language path
   e. Load {Name}.{py|js}
   f. Register aliases: kernel.alias[name] = mod.fn
   g. Call setup(kernel) if exists

5. Clean up: remove extension modules from language cache

6. Return Kernel
```

---

## Kernel API

```python
kernel = Builder.build("full.toml")

# Access aliases
kernel.alias["name"]()          # Direct call
kernel.name                     # Auto-call (if variable)

# Metadata
kernel.metadata["Greeting"]     # → {"initial_name": "World"}

# Info
kernel.info()                   # → {"name": "MyApp", "aliases": 42}
```

---

## Self-hosting bootstrap

```
Stage 0: Hand-written Builder v0 (framework-builder)
         Can build simple apps (Hello, Calculator).

Stage 1: Builder v0 builds app-builder itself
         python -m app_builder run .  (from self-build manifest)

Stage 2: app-builder v1 builds NumFast, Backtest, ...
         + JavaScript backend implemented

Stage 3: app-builder builds itself in JavaScript
         npx app-builder run .
```

---

## Rules (enforced by Builder)

| Rule | Description |
|------|-------------|
| NO class | Only flat functions in extension code |
| NO __init__.py | Extension roots must not have `__init__.py` |
| NO module-level imports | Imports only inside function bodies |
| NO cross-extension import | Only `kernel.alias` for cross-extension access |
| YES setup(kernel) | Single integration point per extension |
| YES CamelCase dirs | Extension directory = `{Name}/` |
| YES `_lib/` | Internal implementation (can have `__init__.py`) |
| YES depends | Dependencies declared in `{Name}.toml` |

---

## Why language-agnostic

Builder is NOT Python. Builder is NOT JavaScript.

Builder is a DSL.

```
full.toml
```

is the same regardless of runtime.

This means:

- One spec for all languages
- One documentation set
- Cross-language examples
- Extensions can be polyglot (Python + JS + Rust)
- LLVM-like: one IR, many backends
