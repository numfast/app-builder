kernel = None

def run_loop():
    print("Calc -- type 'exit' to quit. Type 'test' to run self-tests.")
    while True:
        try:
            expr = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if expr.lower() in ("exit", "quit", "q"):
            break
        if expr.lower() == "test":
            run_tests()
            continue
        if not expr.strip():
            continue
        try:
            result = kernel.alias["eval_expr"](expr)
            print(f"  = {result}")
        except Exception as e:
            print(f"  Error: {e}")

def run_tests():
    """Collect tests from all extension metadata and run them."""
    all_tests = []
    for section, meta in kernel.metadata.items():
        tests = meta.get("tests", {})
        for name, tc in tests.items():
            all_tests.append((f"[{section}] {name}", tc["expr"], tc["expected"]))

    if not all_tests:
        print("No tests found.")
        return

    passed = 0
    failed = 0
    print(f"Running {len(all_tests)} tests...")
    print()
    for label, expr, expected in all_tests:
        try:
            result = kernel.alias["eval_expr"](expr)
        except Exception as e:
            result = f"Error: {e}"
        status = "OK" if result == expected else "FAIL"
        if status == "OK":
            passed += 1
        else:
            failed += 1
            print(f"  FAIL {label}: eval({expr!r}) = {result!r}, expected {expected!r}")
    print()
    print(f"Results: {passed} passed, {failed} failed, {len(all_tests)} total")
