# App Builder Specification

## 1. Концепция
App Builder — это инструмент сборки приложений из микро-расширений.
- **Extension:** Папка с `{Name}.toml`, `{Name}.py` и `_lib/`.
- **Manifest ({Name}.toml):** Описывает имя, алиасы, моды (функции) и зависимости.
- **Module ({Name}.py):** Плоский файл-адаптер. Только реэкспорт функций из `_lib/`. Никаких классов, никаких импортов других расширений.
- **App Manifest (full.toml):** Описывает, какие расширения включить в приложение.

## 2. Правила Кода
1. **Flat Functions Only:** В публичных файлах (`{Name}.py`) только функции.
2. **No Cross-Imports:** Расширения не знают друг о друге. Зависимости решаются через `depends` в TOML и порядок загрузки.
3. **Lib Isolation:** Вся реализация лежит в `_lib/`.
4. **Setup Hook:** Опциональная функция `setup(kernel)` для инициализации метаданных.

## 3. Структура Приложения
```text
MyApp/
├── full.toml          # App Manifest
├── src/
│   ├── _main/         # Entry Point
│   │   ├── _main.toml
│   │   ├── _main.py
│   │   └── _lib/
│   └── MyExt/         # Extension
│       ├── MyExt.toml
│       ├── MyExt.py
│       └── _lib/
```

## 4. Формат TOML

### Extension Manifest
```toml
name = "MyExt"
alias = ["func1", "func2"]
mods = ["func1_impl", "func2_impl"]
depends = ["OtherExt"]
```

### App Manifest
```toml
[kernel]
name = "MyApp"
singleton = true
[[extensions]]
name = "MyExt"
path = "src/MyExt"
```

## 5. Процесс Сборки (Builder Logic)
1. Парсинг `full.toml`.
2. Топологическая сортировка зависимостей.
3. Загрузка расширений по порядку.
4. Регистрация алиасов в едином Kernel (dict).
5. Вызов `setup()` если есть.
