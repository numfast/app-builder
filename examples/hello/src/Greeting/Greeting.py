# Greeting extension
def hello_fn(who):
    return "Hello, " + str(who) + "!"

PUBLIC = {"hello_fn": hello_fn}
