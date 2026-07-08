# Language Backends

**Version:** 1.0 | **Status:** Draft

---

## How backends work

Each backend implements the same Builder protocol:

1. Read `full.toml` → `AppManifest`
2. Resolve extension paths → `ExtensionRef[]`
3. Sort by `depends` → topological order
4. For each extension: load code, register aliases, call `setup()`
5. Return `Kernel`

The protocol is language-agnostic. TOML parsing, path resolution, and
topological sort are the same in every backend. Only the code loading
differs.

---

## Python backend

Directory: `python/app_builder/`

### Entry point

```python
from app_builder import Builder
kernel = Builder.build("full.toml")
kernel.start()  # if "start" alias registered
```

### CLI

```bash
python -m app_builder run full.toml
python -m app_builder test test.toml
python -m app_builder build full.toml
python -m app_builder package full.toml output.zip
python -m app_builder init my-app
```

### Extension loader

1. Add extension directory to `sys.path`
2. Import `{Name}.py` as a top-level module via `importlib`
3. Get functions by name from module
4. Register in kernel
5. Call `setup(kernel)` if exists

### Import check

Builder scans `{Name}.py` with `ast.parse()` and rejects any
module-level `import` or `from ... import` statements.

Only function-level (lazy) imports are allowed.

---

## JavaScript backend

Directory: `javascript/app-builder/`

### Entry point

```javascript
const { Builder } = require('app-builder');
const kernel = Builder.build('full.toml');
kernel.start();  // if "start" alias registered
```

### CLI

```bash
npx app-builder run full.toml
npx app-builder test test.toml
```

### Extension loader

1. Add extension directory to `require` resolution path
2. `require('./{Name}.js')` → module
3. Get functions by name from module exports
4. Register in kernel
5. Call `setup(kernel)` if exists

### Import check

Builder scans `{Name}.js` for top-level `require()` or `import` statements.
Only function-level requires are allowed.

---

## Multi-language extensions

An extension can have implementations in multiple languages:

```
Trading/
  Trading.toml
  python/
    Trading.py
  javascript/
    Trading.js
```

The `language` field in `Trading.toml` selects which file to load:

```toml
name = "Trading"
language = "python"
```

If `language` is not specified, auto-detect:
- If only `Trading.py` exists → python
- If only `Trading.js` exists → javascript
- If both exist → error (must specify language)

---

## Adding a new backend

1. Implement the Builder protocol in the target language
2. Place in `{language}/app-builder/`
3. Add loader for the language's module system
4. Add import check for the language's import syntax
5. Create examples in `examples/`

### Builder protocol

```
Input:  full.toml path
Steps:
  1. Parse TOML → extensions list + metadata
  2. For each extension:
     a. Parse {Name}.toml
     b. Resolve path → {Name}.{ext}
     c. Check for forbidden imports
     d. Load code file
     e. Map alias[i] → mods[i] in kernel
     f. Call setup(kernel)
  3. Return kernel
Output: Kernel with alias, metadata, variables
```

---

## LLVM analogy

```
       TOML (IR)
     /     |     \
    ▼     ▼      ▼
 Python  JS    Rust ...
   │      │      │
   ▼      ▼      ▼
 Kernel  Kernel Kernel
```

One DSL. Many backends. Same semantics.
