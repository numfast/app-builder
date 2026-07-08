"""BuilderCore — расширение-обёртка для самосборки.

Оборачивает функции builder_core в алиасы приложения.
"""

from builder_core.builder import Builder as _Builder


def build_app(path: str) -> dict:
    """Собрать приложение. Возвращает информацию о Kernel."""
    kernel = _Builder.build(path)
    return {
        "name": kernel.metadata["_kernel"]["name"],
        "aliases": len(kernel.alias),
        "alias_list": list(kernel.alias.keys()),
    }


def run_app(path: str):
    """Собрать и запустить приложение."""
    kernel = _Builder.build(path)
    start_fn = kernel.alias.get("start")
    if start_fn:
        result = start_fn()
        if result is not None:
            print(result)
    else:
        print(f"Kernel ready. Aliases: {list(kernel.alias.keys())}")
    return kernel
