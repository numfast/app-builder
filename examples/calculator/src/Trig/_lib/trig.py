import math

_TRIG = {
    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
    'atan2': math.atan2,
    'degrees': math.degrees, 'radians': math.radians,
    'pi': math.pi, 'e': math.e, 'tau': math.tau,
    'sqrt': math.sqrt, 'pow': pow,
    'abs': abs, 'round': round,
    'log': math.log, 'log10': math.log10, 'exp': math.exp,
}

def trig_eval(expr: str) -> str:
    expr = expr.strip()
    if not expr:
        return ""
    result = eval(expr, {"__builtins__": {}}, _TRIG)
    if isinstance(result, float):
        return str(result)
    return str(result)
