def hello_fn(who):
    return "Hello, " + str(who) + "!"

def default_fn():
    return "Hello, World!"

PUBLIC = {"hello_fn": hello_fn, "default_fn": default_fn}
