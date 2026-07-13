# Calc

Calculator on Builder Framework. Demonstrates:
- Multi-extension architecture (Math, Trig, Test, _main)
- Two app manifests: full (with trig) and lite (without trig)
- Self-testing via metadata test cases
- Alias shadowing (Trig.eval_expr shadows Math.eval_expr)

## Quick Start

```bash
make run       # run full build
make test      # run lite build
make package   # package both into releases/
make clean     # remove caches and zips
```

Or directly:

```bash
python -m framework_builder run full.toml
python -m framework_builder run lite.toml
```

## Structure

- `full.toml` / `lite.toml` -- app manifests (root)
- `src/Math/`, `src/Trig/`, `src/Test/`, `src/_main/` -- extensions
- `releases/` -- built .zip packages
- `SPEC.md` -- full specification
