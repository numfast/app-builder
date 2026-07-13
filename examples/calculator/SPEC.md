# Calc Spec

Calculator app demonstrating Builder Framework.

## Mode: Inline SPEC

## Extensions

| Name | Alias | Depends | Description |
|------|-------|---------|-------------|
| Math | eval_expr | - | Basic math: +, -, *, /, pow, sqrt, log |
| Trig | eval_expr | - | Trig: sin, cos, tan, degrees, radians (shadows Math) |
| Test | test, test_all | - | Self-testing: runs test cases from metadata |
| _main | start, test | - | Entry point: REPL loop |

## Manifests

| File | Extensions |
|------|------------|
| `full.toml` (root) | _kernel, Math, Trig, Test, _main |
| `lite.toml` (root) | _kernel, Math, Test, _main |

## Usage

```bash
make run
make test
make package
```

## Tests

Test cases defined in `extensions_meta.Test.tests` and `extensions_meta.Trig.tests` in app manifests.
Runner: Test extension scans all metadata sections for `tests` key.
