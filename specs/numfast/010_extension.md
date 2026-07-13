# Extension Manifest

**{Name}.toml** — описывает расширение.

---

## Поля

| Поле | Обязательное | Описание |
|------|-------------|----------|
| `name` | да | Имя расширения (совпадает с папкой) |
| `alias` | да | Публичные имена в Kernel |
| `mods` | да | Имена функций из PUBLIC |
| `depends` | нет | Зависимости от других расширений |
| `variables` | нет | Алиасы без аргументов (автовызов) |

---

## Пример

```toml
name = "Greeting"
alias = ["hello", "name"]
mods = ["hello_fn", "name_fn"]
variables = ["name"]
```

```python
def hello_fn(who):
    return f"Hello, {who}!"

def name_fn():
    return "World"

PUBLIC = {"hello_fn": hello_fn, "name_fn": name_fn}
```

После сборки:
```python
kernel.alias["hello"]("World")  # → "Hello, World!"
kernel.alias["name"]()           # → "World"
kernel.name                      # → "World"  (автовызов)
```

---

## Ограничения

- `len(alias) == len(mods)` — обязательно
- `alias` должны быть уникальными (последний wins)
- `depends` ссылаются на `name` других расширений
- Циклические зависимости запрещены
