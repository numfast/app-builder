# App Builder Specification

**Zero Import Architecture** — приложения собираются из функций, не из модулей.

---

## 1. Концепция

App Builder — это компоновщик функций.

Единица архитектуры — **не Python-модуль**, а **зарегистрированная функция**.

```
файлы.py  →  Registry  →  Kernel.alias
```

- Каждый `.py` файл экспортирует функции через словарь `PUBLIC`
- Builder читает файлы через `exec()` (не `import`)
- Registry — единое пространство имён для всех компонентов
- Kernel — плоский dict алиасов для пользователя

---

## 2. Zero Import Rule (Железное правило)

**В файлах приложений и расширений НОЛЬ импортов.**

Запрещены:
```python
import os                          # ❌
from pathlib import Path           # ❌
from ._lib.helper import func      # ❌
from builder_core.kernel import K  # ❌
```

Разрешены:
```python
# Ничего. Вообще.

def add(a, b):
    return a + b

PUBLIC = {"add": add}
```

**Единственное исключение** — стандартная библиотека в файлах, которые парсят TOML:
```python
import tomllib    # можно только в manifest-файлах
```

Больше никаких импортов. Нигде. Никогда.

---

## 3. Registry Pattern

Каждый файл заканчивается словарём `PUBLIC`:

```python
# 010_kernel.py
class Kernel:
    def __init__(self):
        self.alias = {}
        self.metadata = {}

PUBLIC = {"Kernel": Kernel}
```

```python
# 020_manifest.py
import tomllib

def load_app_manifest(path):
    ...

PUBLIC = {"load_app_manifest": load_app_manifest}
```

Builder собирает Registry через bootloader:

```python
MAIN = {}
for f in sorted(files):
    ns = {}
    exec(open(f).read(), ns)
    if "PUBLIC" in ns:
        MAIN.update(ns["PUBLIC"])
```

---

## 4. Extension Pattern

Расширение приложения — папка с `{Name}.toml` и `{Name}.py`.

### {Name}.py
```python
def add(a, b):
    return a + b

def mul(a, b):
    return a * b

PUBLIC = {"add": add, "mul": mul}
```

### {Name}.toml
```toml
name = "Math"
alias = ["add", "mul"]
mods = ["add", "mul"]
```

**Никаких `from _lib.xxx import`**. Никаких `import`. Никаких `setup(kernel)`.
Только плоские функции + PUBLIC.

---

## 5. Build Process

```
Bootloader:
  for each .py in builder/:
    exec() → MAIN.update(PUBLIC)

Builder.build(app_dir):
  1. Читает full.toml (через MAIN["load_app_manifest"])
  2. Для каждого [[extensions]]:
     a. Читает {Name}.toml
     b. exec({Name}.py) → ext_PUBLIC
     c. Регистрирует alias[i] → ext_PUBLIC[mods[i]] в Kernel
  3. Возвращает Kernel
```

---

## 6. Структура приложения

```
MyApp/
  full.toml
  src/
    _main/
      _main.toml
      _main.py          # PUBLIC = {"start": start, ...}
    Math/
      Math.toml
      Math.py           # PUBLIC = {"add": add, ...}
```

---

## 7. Правила кода

| Правило | Описание |
|---------|----------|
| Zero Import | Ни одного `import` в файлах приложений |
| PUBLIC | Каждый файл экспортирует `PUBLIC = {name: func, ...}` |
| No classes | Только плоские функции (исключение: Kernel — внутри Builder) |
| No cross-ref | Расширения не знают друг о друге |
| No setup() | Инициализация в PUBLIC, не через колбэк |
| Flat alias | Все моды в одном плоском Kernel.alias |

---

## 8. Архитектура Builder

```
app-builder/
  builder/
    010_kernel.py      PUBLIC = {"Kernel": Kernel}
    020_manifest.py    PUBLIC = {"load_app_manifest": ..., "load_extension_manifest": ...}
    030_resolver.py    PUBLIC = {"resolve_order": ...}
    040_loader.py      PUBLIC = {"load_extension": ...}
    050_builder.py     PUBLIC = {"build": ...}
    060_boot.py        PUBLIC = {"boot": ...}  (собирает MAIN)
    070_cli.py         PUBLIC = {"main": ...}
    __init__.py         # вызывает boot(), экспортирует MAIN
```

**Внутри builder/ нет импортов.** Только `PUBLIC`.

---

## 9. NumFast application

Приложение, написанное для App Builder, называется **NumFast application**.
Спецификация — в `specs/numfast/`.

---

## 10. Поправка v0.2.1 (иерархия + import-guard, заменяет §2/§4 частично)

- Extension = `{Name}.toml` + `{Name}.py` + `_lib/*.py`. Entry: `from _lib... import` + `PUBLIC` + `setup(kernel)` (только metadata, вызывается после регистрации алиасов).
- Вложенность: пути в `full.toml` могут быть вложенными (`src/Core`, `src/Compute/Reduce`); общие хелперы — один раз на родительском/общем уровне, reuse — только через `depends` + вызов по `kernel.alias` в runtime.
- Import-guard (AST, до exec, entry + весь `_lib`): запрещены `import <ДругойExt>._lib` / `from <ДругойExt>._lib import` / `from <ДругойExt> import` и `from ..` (побег). Ошибка громкая: что запрещено + как правильно (`depends` + `kernel.alias`). Разрешены: свой `_lib`, relative level 1, stdlib, third-party (numpy). `depends` НЕ легализует Python-импорт.
- Загрузка изолирована: `sys.path` только свой каталог на время exec, `_lib` вычищается из `sys.modules` после (коллизий между Extensions нет).
