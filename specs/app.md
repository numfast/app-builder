# App Manifest (`full.toml`)

**Version:** 1.0 | **Status:** Draft

The app manifest defines an application: its name, extensions, and metadata.

---

## Fields

### `[kernel]` (required)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | `"App"` | Application name |
| `singleton` | bool | `true` | Single instance mode |

### `[[extensions]]` (required, 1+)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | — | Extension display name |
| `path` | string | — | Path relative to manifest dir |
| `release` | string | — | Path to .zip package |
| `names` | [string] | — | Filter for package contents |
| `exclude` | bool | false | Exclude from inherited manifest |
| `metadata` | table | — | Per-reference metadata override |

### `[extensions_meta.*]` (optional)

Passes metadata to specific extensions.

```toml
[extensions_meta.Greeting]
initial_name = "World"
greeting_template = "Hello, {name}!"
```

### `[tests]` (optional)

Defines tests for the Builder test runner.

```toml
[tests]
add = { mod = "eval", args = ["2+2"], expected = "4" }
sub = { mod = "eval", args = ["10-3"], expected = "7" }
```

| Field | Type | Description |
|-------|------|-------------|
| `mod` | string | Kernel alias to call |
| `expr` | string | Expression (uses `eval` alias) |
| `args` | list | Positional arguments |
| `kwargs` | table | Keyword arguments |
| `expected` | string | Expected string result |
| `tol` | float | Float tolerance |

### `extends` (optional)

Path to a parent manifest. Child inherits all extensions and metadata.

```toml
extends = "base.toml"

# Child can exclude inherited extensions
[[extensions]]
name = "Trig"
exclude = true

# Child can add new extensions
[[extensions]]
name = "Calc"
path = "src/Calc"
```

---

## Grammar (formal)

```
app-manifest = kernel-section 1*(extensions-section)
               [extensions-meta] [tests] [extends]

kernel-section = %x5B "kernel" %x5D
                 kernel-name [kernel-singleton]

kernel-name     = "name" "=" string
kernel-singleton = "singleton" "=" boolean

extensions-section = %x5B%x5B "extensions" %x5D%x5D
                     extension-name extension-path
                     [extension-release] [exclude] [metadata]

extension-name    = "name" "=" string
extension-path    = "path" "=" string
extension-release = "release" "=" string
exclude           = "exclude" "=" boolean

extensions-meta = "[" "extensions_meta" "." name "]" key-value-pairs

tests = "[tests]" 1*(test-definition)
test-definition = identifier "=" "{" test-fields "}"
test-fields = test-mod / test-expr / test-args / test-expected / test-tol

extends = "extends" "=" string
```

---

## Examples

### Minimal

```toml
[kernel]
name = "Minimal"

[[extensions]]
name = "_main"
path = "src/_main"
```

### Full

```toml
[kernel]
name = "Calc"
singleton = true

[[extensions]]
name = "_kernel"
path = "_kernel"

[[extensions]]
name = "Math"
path = "src/Math"

[[extensions]]
name = "_main"
path = "src/_main"

[extensions_meta.Math]
precision = "float64"

[tests]
add = { mod = "eval", args = ["2+2"], expected = "4" }

extends = "base.toml"
```

---

## Errors

| Error | Cause |
|-------|-------|
| KernelSectionMissingError | No `[kernel]` section |
| ExtendsLimitError | `extends` more than 1 level |
| ManifestNotFoundError | Referenced manifest not found |
