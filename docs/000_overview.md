# app-builder Architecture

**Version:** 1.0 | **Status:** Draft

---

## Philosophy

**Builder is not a language. Builder is a DSL.**

The same `full.toml` works for Python, JavaScript, Rust — any runtime.
Languages are just backends. The specification is one.

---

## Core idea

```
full.toml           DSL (language-agnostic)
    │
    ▼
Builder Runtime     Python / JavaScript / ...
    │
    ▼
Kernel              Flat namespace of aliases
```

Extensions are flat function files. No imports. No classes. No packages.
They are **linked** into a single Kernel with a flat alias map.

---

## Architecture diagram

```
┌─────────────────────────────────────────────────┐
│                   Application                    │
│                                                   │
│  full.toml                                        │
│    [kernel] name = "MyApp"                        │
│    [[extensions]] path = "src/Greeting"          │
│    [[extensions]] path = "src/Bondiana"          │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ _main    │  │ Greeting │  │ Bondiana │  ...  │
│  │ .toml    │  │ .toml    │  │ .toml    │       │
│  │ .py      │  │ .py      │  │ .py      │       │
│  │ _lib/    │  │ _lib/    │  │ _lib/    │       │
│  └──────────┘  └──────────┘  └──────────┘       │
│         │            │             │              │
│         ▼            ▼             ▼              │
│  ┌─────────────────────────────────────────────┐  │
│  │             Builder Runtime                  │  │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────────┐  │  │
│  │  │ Loader  │ │Resolver │ │  Scanner     │  │  │
│  │  └─────────┘ └─────────┘ └──────────────┘  │  │
│  └─────────────────────────────────────────────┘  │
│         │                                          │
│         ▼                                          │
│  ┌─────────────────────────────────────────────┐  │
│  │              Kernel                          │  │
│  │  alias: {name, setName, greeting, ...}       │  │
│  │  metadata: {Greeting: {...}, ...}            │  │
│  │  variables: {name, last_name}                │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## Layering (docker-style)

Extensions are loaded in dependency order.
Later extensions **shadow** aliases from earlier ones.

```
Order:  _kernel → _main → Greeting → Bondiana

After loading:
  kernel.alias["name"]     = Bondiana.name      # shadows Greeting
  kernel.alias["greeting"] = Bondiana.greeting   # shadows Greeting
  kernel.alias["setName"]  = Bondiana.setName    # shadows Greeting
  kernel.alias["last_name"] = Bondiana.last_name # new
```

This is identical to Docker overlay layers:
- Each extension is a layer
- Layers stack in order
- Upper layers override lower layers
- All layers merge into one filesystem (alias namespace)

---

## No imports. Ever.

Extensions NEVER import each other. Cross-extension access:
- `setup(kernel)` → `kernel.alias.get("name")`
- `kernel.metadata["ExtensionName"]`

Module-level imports in extension code are FORBIDDEN.
Builder scans the AST and rejects any extension with module-level imports.

```python
# ❌ REJECTED at build time
from _lib.greet import name

# ✅ Allowed — lazy import inside function
def name():
    from _lib.greet import name as _name
    return _name()
```

---

## Language backends

| Backend | Directory | Command |
|---------|-----------|---------|
| Python | `python/app_builder/` | `python -m app_builder run full.toml` |
| JavaScript | `javascript/app-builder/` | `npx app-builder run full.toml` |

### Multi-language extension

```
Trading/
  Trading.toml          # Same DSL for all
  python/
    Trading.py          # Python implementation
  javascript/
    Trading.js          # JS implementation
```

Selection by `language` field in `{Name}.toml` or auto-detected.

---

## Self-hosting (bootstrap)

```
Stage 0:  Hand-written Builder           (framework-builder)
             ↓
Stage 1:  Builder builds itself          (app-builder in Python)
             ↓
Stage 2:  app-builder builds NumFast     (+ JS backend)
             ↓
Stage 3:  app-builder builds itself in JS
```

---

## Directory structure

```
app-builder/
  SPEC.md              # Root specification
  README.md            # Quick start
  specs/               # DSL grammar (language-agnostic)
    app.md             # App manifest spec
    extension.md       # Extension manifest spec
    builder.md         # Builder config spec
  docs/
    000_overview.md    # This file
    010_manifest.md    # Manifest deep-dive
    020_language_backends.md
    030_self_hosting.md
  python/
    app_builder/       # Python runtime
      __init__.py
      builder.py
      kernel.py
      loader.py
      manifest.py
      scanner.py
      resolver.py
      test.py
      cli.py
  javascript/
    app-builder/       # JS runtime
      package.json
      index.js
      builder.js
      kernel.js
  examples/
    hello-python/
    hello-js/
    calculator-python/
    calculator-js/
  tests/
```

---

## Key numbers

| Metric | Target |
|--------|--------|
| Python core | < 2000 lines |
| JS core | < 2000 lines |
| Extension .py | < 50 lines per file |
| Build time | < 100ms for 20 extensions |
| Test runtime | < 5s for full suite |

---

## See also

- `specs/app.md` — App manifest grammar
- `specs/extension.md` — Extension manifest grammar
- `specs/builder.md` — Builder configuration
- `010_manifest.md` — Manifest inheritance and merging
- `020_language_backends.md` — Backend implementation guide
- `030_self_hosting.md` — Bootstrap plan
