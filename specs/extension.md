# Extension Manifest (`{Name}.toml`)

**Version:** 1.0 | **Status:** Draft

Each extension is a directory with a manifest, code file, and optional `_lib/`.

---

## Directory structure

```
{Name}/
  {Name}.toml       # Extension manifest (this spec)
  {Name}.{py|js}    # Extension code (one per language backend)
  _lib/             # Internal implementation (optional)
    __init__.py     # Allowed — _lib/ is not an extension root
    helper.py
```

---

## Fields

### `name` (required)

Extension name. Must match the directory name.

```toml
name = "Greeting"
```

### `version` (optional, default: `"0.1.0"`)

Semantic version.

### `language` (required)

Runtime backend. One of: `"python"`, `"javascript"`.

```toml
language = "python"
```

If the extension directory has only one `{Name}.py` or `{Name}.js`, language is auto-detected.

### `depends` (optional, default: `[]`)

List of extension names that must be loaded first.

```toml
depends = ["Runtime", "Storage"]
```

### `alias` (required)

Public names for the mods. These become `kernel.alias[name]`.

```toml
alias = ["name", "setName", "greeting", "_default"]
```

### `mods` (required, same length as `alias`)

Function names in the code file. One-to-one mapping with aliases.

```toml
mods = ["name", "setName", "greeting", "greeting"]
```

Multiple aliases can point to the same mod.

### `variables` (optional, default: `[]`)

Aliases that are "variables" — no-argument functions that auto-call on read.

```toml
variables = ["name"]
```

### `[metadata]` (optional)

Static metadata accessible via `kernel.metadata["{Name}"]`.

```toml
[metadata]
initial_name = "World"
template = "Hello, {name}!"
```

### `metadata_section` (optional, default: extension name)

Key in `kernel.metadata` under which this extension's metadata is stored.

---

## Grammar (formal)

```
extension-manifest = name-field [version] [language] [depends]
                     alias-field mods-field [variables]
                     [metadata] [metadata-section]

name-field  = "name" "=" string
version     = "version" "=" string
language    = "language" "=" ("python" / "javascript")
depends     = "depends" "=" "[" *string "]"
alias-field = "alias" "=" "[" 1*string "]"
mods-field  = "mods" "=" "[" 1*string "]"
variables   = "variables" "=" "[" *string "]"
metadata    = "[metadata]" key-value-pairs
metadata-section = "metadata_section" "=" string
```

---

## Constraints

| Rule | Description |
|------|-------------|
| `len(alias) == len(mods)` | Must match |
| `alias` must be unique | No duplicates across all extensions (last wins) |
| `depends` must exist | All dependencies must be in the app manifest |
| No circular deps | Dependency graph must be acyclic |
| `{Name}.{py\|js}` must exist | Code file required |
| `{Name}.toml` must exist | Manifest required |

---

## Errors

| Error | Cause |
|-------|-------|
| MismatchError | `alias` and `mods` have different lengths |
| ManifestNotFoundError | `{Name}.toml` not found |
| ModuleNotFoundError | `{Name}.{py\|js}` not found |
| MissingDependencyError | `depends` references unknown extension |
| CircularDependencyError | Cycle in `depends` graph |
| DuplicateAliasError | Same alias registered by two extensions (warning only) |
