# Builder Configuration (`builder.toml`)

**Version:** 1.0 | **Status:** Draft

Optional configuration file for the Builder runtime itself.

---

## Fields

### `[backend]`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `language` | string | `"python"` | Default runtime backend |
| `python_path` | string | — | Python interpreter path |
| `node_path` | string | — | Node.js path |

### `[build]`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `strict_imports` | bool | `true` | Reject module-level imports |
| `check_classes` | bool | `true` | Reject class definitions |
| `max_extensions` | int | `100` | Maximum extension count |
| `cache_modules` | bool | `true` | Cache loaded modules in memory |

### `[package]`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `compress` | bool | `true` | Compress .zip packages |
| `include_tests` | bool | `false` | Include test definitions in package |

---

## Grammar (formal)

```
builder-config = "[backend]" backend-fields
                 "[build]" build-fields
                 "[package]" package-fields

backend-fields = [language] [python-path] [node-path]

language    = "language" "=" string
python-path = "python_path" "=" string
node-path   = "node_path" "=" string

build-fields = [strict-imports] [check-classes]
               [max-extensions] [cache-modules]

strict-imports = "strict_imports" "=" boolean
check-classes  = "check_classes" "=" boolean
max-extensions = "max_extensions" "=" integer
cache-modules  = "cache_modules" "=" boolean

package-fields = [compress] [include-tests]

compress      = "compress" "=" boolean
include-tests = "include_tests" "=" boolean
```

---

## Default configuration

If no `builder.toml` is present, the Builder uses these defaults:

```toml
[backend]
language = "python"

[build]
strict_imports = true
check_classes = true
max_extensions = 100
cache_modules = true

[package]
compress = true
include_tests = false
```
