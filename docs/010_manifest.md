# Manifest Inheritance and Merging

**Version:** 1.0 | **Status:** Draft

---

## Inheritance

A manifest can inherit from another via `extends`:

```toml
# test.toml
extends = "full.toml"

[tests]
add = { mod = "eval", args = ["2+2"], expected = "4" }
```

Child inherits:
- All `[[extensions]]` from parent
- All `[extensions_meta.*]` from parent
- `[kernel]` name/singleton (if not overridden)

Child can:
- Exclude inherited extensions: `name = "X" exclude = true`
- Override inherited extensions (by name)
- Add new extensions

### Rules

- Only **one level** of inheritance (`extends` → base, base cannot extend)
- Child `[extensions_meta.*]` fully overrides parent sections by name
- Child `[tests]` merges with parent (child overrides same-named tests)

---

## Extension merging

When two extensions define the same alias, the LAST one loaded wins.

This is by design — it enables layering:

```toml
# Lite version
extends = "full.toml"

[[extensions]]
name = "Bondiana"
exclude = true
```

Without Bondiana, `name` returns `Greeting.name()` → `"World"`.
With Bondiana, `name` returns `Bondiana.name()` → `"James Bond"`.

---

## Metadata merging

`kernel.metadata["Greeting"]` is built from two sources:

1. `[metadata]` in `Greeting/Greeting.toml`
2. `[extensions_meta.Greeting]` in `full.toml`

Source 2 overrides source 1 (by key).

```toml
# Greeting.toml
[metadata]
initial_name = "World"

# full.toml
[extensions_meta.Greeting]
initial_name = "Universe"   # overrides "World"
```

---

## Test merging

When a child manifest defines `[tests]`, they merge with parent tests.
Child tests with the same name override parent tests.

```toml
# full.toml
[tests]
add = { mod = "eval", args = ["2+2"], expected = "4" }

# test.toml
extends = "full.toml"

[tests]
add = { mod = "eval", args = ["2+3"], expected = "5" }  # overrides
sub = { mod = "eval", args = ["10-3"], expected = "7" }  # new
```

---

## Example: layered manifests

```toml
# full.toml — full app with Bondiana
[extensions]
name = "Greeting"
name = "Bondiana"
```

```toml
# lite.toml — without Bondiana
extends = "full.toml"
[[extensions]]
name = "Bondiana"
exclude = true
```

```toml
# test.toml — extends lite, adds tests
extends = "lite.toml"
[tests]
name = { mod = "name", expected = "World" }
```
