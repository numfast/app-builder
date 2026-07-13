def add_fn(a, b):
    return a + b

def sub_fn(a, b):
    return a - b

def mul_fn(a, b):
    return a * b

def div_fn(a, b):
    if b == 0:
        return "Error: division by zero"
    return a / b

def pow_fn(a, b):
    return a ** b

PUBLIC = {"add_fn": add_fn, "sub_fn": sub_fn, "mul_fn": mul_fn, "div_fn": div_fn, "pow_fn": pow_fn}
