def sin_fn(x):
    term = x
    result = term
    for n in range(1, 10):
        term = -term * x * x / ((2*n) * (2*n + 1))
        result += term
    return result

def cos_fn(x):
    term = 1.0
    result = term
    for n in range(1, 10):
        term = -term * x * x / ((2*n-1) * (2*n))
        result += term
    return result

def tan_fn(x):
    s = sin_fn(x)
    c = cos_fn(x)
    if abs(c) < 1e-15:
        return "Error: tan undefined"
    return s / c

def pi_fn():
    return 3.141592653589793

PUBLIC = {"sin_fn": sin_fn, "cos_fn": cos_fn, "tan_fn": tan_fn, "pi_fn": pi_fn}
