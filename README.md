# app-builder

Language-agnostic application builder for modular Python and JavaScript applications.

```
full.toml  →  Builder  →  Kernel{aliases[], metadata[], variables[]}
```

---

## Quick start

```bash
# Install Python backend
cd python
pip install -e .

# Run Hello app
cd examples/hello-python
app-builder run
```

## How it works

1. Write `full.toml` — list your extensions
2. Write `{Name}.toml` + `{Name}.py` — define functions
3. `app-builder run` — builds and executes

## Examples

| Example | Command |
|---------|---------|
| Hello (Python) | `cd examples/hello-python && app-builder run` |
| Calculator (Python) | `cd examples/calculator-python && app-builder run` |
| Hello (JS) | `cd examples/hello-js && npx app-builder run` |

## Why?

- **Zero imports** between extensions — only `kernel.alias`
- **Flat namespace** — all mods in one dict
- **Language-agnostic** — same TOML for Python, JS, Rust
- **Docker-style layering** — later extensions shadow earlier ones
- **Self-hosting** — Builder builds itself

---

## Docs

- `SPEC.md` — full specification
- `specs/` — DSL grammar
- `docs/` — architecture and patterns

## License

AGPL-3.0
