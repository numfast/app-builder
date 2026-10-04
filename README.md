# App Builder

**Zero-Import Architecture** — Build applications from manifest-driven extensions.

```
pip install app-builder           # Python
npm install @numfast/app-builder  # Node.js (TypeScript)
```

---

## What is App Builder?

App Builder is a meta-framework for assembling applications from **Extension** components.

### Core principles:

- **Zero imports** — Extensions never `import` or `require` anything (checked at load time).
- **Manifest-driven** — Every extension has a `.toml` or `.json` manifest declaring name, version, aliases, dependencies.
- **Flat namespace** — All functions are registered in a `Kernel` object by alias name.
- **Topological sort** — Extensions are loaded in dependency order via Kahn's algorithm.

---

## How it works

```
full.toml                    Kernel (flat namespace)
├── Extension A              ┌─────────────────────┐
├── Extension B       ──►   │ get("Map")  -> fn   │
├── Extension C              │ get("Reduce") -> fn │
└── ...                      │ get("compile") -> fn│
                             └─────────────────────┘
```

Each extension is a directory with:
```
my-extension/
├── MyExtension.toml    # Manifest: name, version, alias, mods, depends
├── MyExtension.js      # Entry: module.exports.PUBLIC = { ... }
└── _lib/               # Implementation (optional, loaded by entry)
```

---

## Extension Manifest

```toml
name = "Compute"
alias = ["Map", "Reduce", "ScanLocal", "ScanTotals", "ScanFinal"]
mods = ["Map", "Reduce", "ScanLocal", "ScanTotals", "ScanFinal"]
depends = ["Runtime"]

[metadata]
description = "Compute kernels: Map, Reduce, Scan, Sort, FFT..."
```

- `alias` — Names to register in the Kernel
- `mods` — Corresponding function names from the extension's `PUBLIC` export
- `depends` — Dependencies (used for topological sort)

---

## Extension Entry (JS)

```javascript
// MyExtension.js
function Map(params) { /* ... */ }
function Reduce(params) { /* ... */ }

module.exports.PUBLIC = { Map, Reduce };
```

The entry file **must not** have bare `require(` or `import ` statements at the start of a line (checked by Loader).

---

## App Manifest (full.toml)

```toml
[kernel]
name = "my-app"
singleton = true

[[extensions]]
name = "Runtime"
path = "lib/Runtime"

[[extensions]]
name = "Compute"
path = "lib/Compute"

[[extensions]]
name = "App"
path = "."
```

---

## Building an Application

### JavaScript (Node.js/TypeScript)

```javascript
const { boot } = require('@numfast/app-builder');

// Boot builder components into global registry
const MAIN = boot('./node_modules/@numfast/app-builder/dist');

// Build application from full.toml
const kernel = MAIN.build('./my-app');

// Use registered functions
const result = kernel.call('Map', { func: 7, data: [1, 2, 3] });
```

### Python

```bash
python -m builder build .
```

---

## CLI

```
node dist/070_CLI.js build <app-dir>
node dist/070_CLI.js list
node dist/070_CLI.js test <app-dir>
```

---

## Why Zero Import?

1. **AI-friendly** — LLMs can generate extensions without knowing internal module paths.
2. **Hot-reload ready** — No import chains to invalidate.
3. **Cross-language** — Same manifest works for Python, JS, and future languages.
4. **Auditable** — All dependencies are explicit in `.toml`.

---

## License

**AGPL-3.0-only.** The full licence text is in [`LICENSE`](LICENSE) at the root of
this repository — a verbatim copy of the GNU AGPL-3.0 text, also published at
<https://www.gnu.org/licenses/agpl-3.0.txt>.

Third-party licences in use are listed in [`NOTICE`](NOTICE). This package has no
third-party runtime dependencies.

A separate proprietary commercial licence covering the same source is planned and
is **not yet finalised**; no commercial terms are published here. The only grant
currently available is the AGPL-3.0-only grant above.
