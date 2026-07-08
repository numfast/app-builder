# Self-hosting Bootstrap Plan

**Version:** 1.0 | **Status:** Draft

---

## The bootstrap problem

Builder builds applications from extensions.
But who builds Builder itself?

Answer: Builder builds itself, in stages.

---

## Stage 0: Hand-written prototype

Location: `framework-builder/` (dev-env)

Hand-written Python code that implements the full Builder protocol.
No self-hosting. Used to validate the DSL and build initial apps.

```
framework-builder/
  framework_builder/
    __init__.py    # Builder class (re-export)
    builder.py     # build(), inline(), package()
    kernel.py      # Kernel class
    loader.py      # load_extension()
    manifest.py    # load_app(), ExtensionManifest
    scanner.py     # resolve_paths()
    resolver.py    # resolve_order()
    test.py        # run_tests()
    cli.py         # CLI entry point
    package.py     # .zip packaging
```

**Can build:** Hello, Calculator  
**Cannot build:** itself (not yet)

---

## Stage 1: Builder builds app-builder

The `python/app_builder/` package IS the Stage 1 target.

Each component is an extension:

```
python/app_builder/
  full.toml                          # App manifest for app-builder itself
  src/
    _main/                           # Entry point
    Builder/                         # build(), inline(), package()
    Kernel/                          # Kernel class
    Loader/                          # load_extension()
    Manifest/                        # load_app()
    Scanner/                         # resolve_paths()
    Resolver/                        # resolve_order()
    Test/                            # run_tests()
```

Command:

```bash
# Stage 0 builds Stage 1
cd python
python -m framework_builder build app_builder/full.toml

# Output: self-built Kernel
```

When this works, app-builder can build itself:

```bash
cd python
python -m app_builder build app_builder/full.toml
```

This is the **bootstrap moment**.

---

## Stage 2: NumFast + JS backend

Once app-builder is self-hosting in Python:

1. Port the Builder to JavaScript (`javascript/app-builder/`)
2. Write JS examples (hello-js, calculator-js)
3. Build NumFast with app-builder (replaces framework-builder)

```bash
# Python builder builds NumFast
python -m app_builder run numfast/full.toml
```

---

## Stage 3: JavaScript self-hosting

JavaScript backend builds itself:

```bash
# JS builder builds JS builder
npx app-builder run javascript/app-builder/full.toml
```

---

## Bootstrap diagram

```
  Hand-written (framework-builder)
       │
       │ builds
       ▼
  app-builder Python  ─── builds NumFast ─── builds JS backend
       │                                              │
       │ builds                                       │ builds
       ▼                                              ▼
  app-builder Python   (self-hosting)         JS backend (self-hosting)
```

---

## Verification milestones

| Stage | Check | Command |
|-------|-------|---------|
| 0 | Calculator works | `python -m framework_builder test examples/calc/test.toml` |
| 1 | Self-build works | `python -m app_builder build app_builder/full.toml` |
| 2 | JS Hello works | `npx app-builder run examples/hello-js/full.toml` |
| 3 | JS self-build works | `npx app-builder run javascript/app-builder/full.toml` |

---

## Key constraint

Stage 0 (hand-written) must be minimal — just enough to bootstrap.
Once Stage 1 works, all future development happens in Builder-built code.

The hand-written code is throwaway after bootstrap.
