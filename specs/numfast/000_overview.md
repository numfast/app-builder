# NumFast Application Specification

**Как писать приложения для App Builder.**

---

## Что такое NumFast application

NumFast application — это приложение, собранное App Builder'ом из расширений.

Любое приложение — Hello World, Калькулятор, NumFast Core, Backtest — 
все они собираются по одним правилам.

---

## Правила (железные)

### 1. Zero Import
В файлах расширений **ноль импортов**. Вообще.
Ни `import os`, ни `from pathlib import Path`, ни `from ._lib.helper import x`.

```python
# ❌ ЗАПРЕЩЕНО
import math
from decimal import Decimal

# ✅ РАЗРЕШЕНО
def add(a, b):
    return a + b
```

Единственное исключение — файлы, которые читают TOML (manifest'ы).
Там можно `import tomllib`. И больше ничего.

### 2. PUBLIC
Каждый `.py` файл заканчивается словарём `PUBLIC`.

```python
def add(a, b):
    return a + b

def mul(a, b):
    return a * b

PUBLIC = {"add": add, "mul": mul}
```

Builder читает PUBLIC и регистрирует функции в Kernel.

### 3. Только функции
Никаких классов в публичных файлах.
Никаких объектов. Только `def`.

(Классы можно внутри `_lib/`, но сам файл расширения их не экспортирует.)

### 4. Нет cross-import
Расширения не знают друг о друге.
Всё общение — через Kernel.alias после сборки.

### 5. _lib/ — для реализации
Если функция большая — вынеси реализацию в `_lib/helper.py`.
Но файл расширения всё равно без импортов.

Как это работает:
```python
# {Name}.py
def big_func(x):
    # реализация прямо здесь
    # если очень большая — вынеси в _lib/helper.py
    # НО: без import. Либо всё в одном файле, либо PUBLIC из _lib/
    pass

PUBLIC = {"big_func": big_func}
```

Правило: если код не влезает в один файл — расширение слишком большое.
Разбей на несколько маленьких расширений.

---

## Структура расширения

```
MyExt/
  MyExt.toml      # манифест
  MyExt.py        # PUBLIC функции
  _lib/           # опционально: внутренние файлы (тоже PUBLIC)
```

### MyExt.toml
```toml
name = "MyExt"
alias = ["func1", "func2"]
mods = ["func1", "func2"]
depends = []
```

### MyExt.py
```python
def func1(a, b):
    return a + b

PUBLIC = {"func1": func1, "func2": func2}
```

---

## Структура приложения

```
my-app/
  full.toml
  src/
    _main/
      _main.toml
      _main.py
    Math/
      Math.toml
      Math.py
    Trig/
      Trig.toml
      Trig.py
```

### full.toml
```toml
[kernel]
name = "MyApp"

[[extensions]]
name = "_main"
path = "src/_main"

[[extensions]]
name = "Math"
path = "src/Math"
```

---

## Жизненный цикл

1. Разработчик пишет расширения (файлы без импортов + PUBLIC)
2. Разработчик описывает приложение в full.toml
3. Builder читает full.toml, находит расширения, exec() каждое
4. Builder собирает Kernel из PUBLIC каждого расширения
5. Пользователь вызывает kernel.alias["func"]()
