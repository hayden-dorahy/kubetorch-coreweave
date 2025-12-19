"""Demo: Remote breakpoint debugging.

When the function hits breakpoint(), an interactive debugger opens
in your terminal, connected to the remote pod.

Use standard pdb commands: n (next), s (step), c (continue), p <var> (print), q (quit)
"""


def debug_example():
    """A function with a breakpoint for remote debugging."""
    data = {"x": 10, "y": 20}

    # Calculate something
    result = data["x"] * data["y"]

    # ========================================
    # BREAKPOINT - debugger will open here!
    # ========================================
    breakpoint()

    # Continue after debugging
    final = result + 100

    return f"Final result: {final}"


if __name__ == "__main__":
    import kubetorch as kt

    print("=" * 60)
    print("REMOTE DEBUGGING DEMO")
    print("=" * 60)
    print("When the breakpoint hits, you'll get an interactive debugger.")
    print("Commands: n (next), s (step), c (continue), p <var>, q (quit)")
    print("=" * 60)
    print()

    compute = kt.Compute(cpus="0.1", labels={"demo": "breakpoint"})
    remote_fn = kt.fn(debug_example, name="warmstart_debug").to(compute)

    result = remote_fn()
    print(f"\nResult: {result}")
