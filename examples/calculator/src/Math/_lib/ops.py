import math

_SAFE = {
    'abs': abs, 'round': round,
    'sqrt': math.sqrt, 'pow': pow,
    'log': math.log, 'log10': math.log10, 'exp': math.exp,
    'pi': math.pi, 'e': math.e, 'tau': math.tau,
}

def safe_eval(expr: str) -> str:
    expr = expr.strip()
    if not expr:
        return ""
    result = eval(expr, {"__builtins__": {}}, _SAFE)
    if isinstance(result, float):
        return str(result)
    return str(result)
