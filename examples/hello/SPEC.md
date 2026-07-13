# HelloWorld Spec

Demo app: multi-manifest build with extension shadowing.

## Structure

```
hello_app/
├── _main/
│   ├── _main.toml            <- extension manifest: name, alias, mods
│   ├── _main.bondiana.toml   <- app manifest: Greeting + Bondiana
│   ├── _main.py              <- entry point
│   └── _lib/
│       └── main_lib.py
├── Greeting/
│   ├── Greeting.toml
│   ├── Greeting.py
│   └── _lib/
│       └── greet.py
└── Bondiana/
    ├── Bondiana.toml
    ├── Bondiana.py
    └── _lib/
        └── bond.py
```

## Manifests

### _main/_main.toml (default: Greeting only)

```toml
name = "_main"
alias = ["_default"]
mods = ["_default"]

[kernel]
name = "HelloWorld"
singleton = true

[[extensions]]
name = "_kernel"
path = "_kernel"

[[extensions]]
name = "_info"
path = "_info"

[[extensions]]
name = "_main"
path = "_main"

[[extensions]]
name = "Greeting"
path = "Greeting"

[extensions_meta.Greeting]
initial_name = "World"
greeting_template = "Hello, {name}!"
```

### _main/_main.bondiana.toml (Greeting + Bondiana)

```toml
name = "_main"
alias = ["_default"]
mods = ["_default"]

[kernel]
name = "HelloWorld"
singleton = true

[[extensions]]
name = "_kernel"
path = "_kernel"

[[extensions]]
name = "_info"
path = "_info"

[[extensions]]
name = "_main"
path = "_main"

[[extensions]]
name = "Greeting"
path = "Greeting"

[[extensions]]
name = "Bondiana"
path = "Bondiana"

[extensions_meta.Greeting]
initial_name = "World"
greeting_template = "Hello, {name}!"

[extensions_meta.Bondiana]
initial_first_name = "James"
initial_last_name = "Bond"
greeting_template = "{last}, {full}! From Russia with love."
```

## Extensions

### Greeting

| Alias | Type | Signature | Description |
|-------|------|-----------|-------------|
| `name` | variable | `()` | Returns current name |
| `setName` | mod | `(v)` | Sets name |
| `greeting` | mod | `()` | Returns greeting string |

`_default` -> `greeting`.

### Bondiana

Depends on Greeting. Shadowing: `name`, `setName`, `greeting` override Greeting's.

| Alias | Type | Signature | Description |
|-------|------|-----------|-------------|
| `last_name` | variable | `()` | Returns last name |
| `setLastName` | mod | `(v)` | Sets last name |
| `setName` | mod | `(full)` | Parses "First Last", calls Greeting.setName + setLastName |
| `name` | variable | `()` | Returns "First Last" |
| `greeting` | mod | `()` | Bond-style greeting |

`_default` -> `greeting`.

## Build & Run

```python
from framework_builder import Builder

# App 1: Greeting only (default manifest)
app = Builder.build("examples/hello_app/")
print(app.name)       # "World"

# App 2: Greeting + Bondiana
app2 = Builder.build("examples/hello_app/_main/_main.bondiana.toml")
print(app2.name)      # "James Bond"
print(app2.greeting)  # "Bond, James Bond! From Russia with love."
```

## Key Rules

1. **Extension manifest** must have `name`, `alias`, `mods` at top level.
2. **App manifest** (`_main.toml` or `_main.{profile}.toml`) has `[kernel]` + `[[extensions]]`.
3. **TOML only** -- no JSON.
4. **Flat functions** -- no classes.
5. `_lib/` -- all implementation. Public file re-exports only.
6. No `__init__.py`.
7. `setup(kernel)` -- optional, for metadata init.
8. `depends` -- dependencies between extensions.
