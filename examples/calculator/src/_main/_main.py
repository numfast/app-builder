def calc_fn(expr):
    expr = str(expr).strip()
    try:
        return str(eval(expr, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error: {e}"

def help_fn():
    return "Calc usage: calc('2+2*3') -> '8'"

def default_fn():
    return help_fn()

def repl_fn():
    while True:
        try:
            expr = input("calc> ")
            if expr.lower() in ("exit", "quit"):
                break
            print(calc_fn(expr))
        except (EOFError, KeyboardInterrupt):
            break
    return "bye"

PUBLIC = {"calc_fn": calc_fn, "help_fn": help_fn, "default_fn": default_fn, "repl_fn": repl_fn}
