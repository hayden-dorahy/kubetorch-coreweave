"""Demo: Hot code reload without pod restart.

Run this script multiple times - edit the MESSAGE below between runs
and see changes reflected instantly without cold start.
"""

# ============================================
# EDIT THIS MESSAGE AND RE-RUN THE SCRIPT!
# ============================================
MESSAGE = "Hello from v1!"


def get_message():
    """Returns the message - edit MESSAGE above and re-run to see hot reload."""
    return f"Message: {MESSAGE}"


if __name__ == "__main__":
    import time

    import kubetorch as kt

    compute = kt.Compute(
        cpus="0.1", launch_timeout=60, labels={"demo": "hot-reload"}
    )
    remote_fn = kt.fn(get_message, name="warmstart_hotreload").to(compute)

    print("=" * 50)
    start = time.time()
    result = remote_fn()
    elapsed = time.time() - start
    print(f"Result: {result}")
    print(f"Time: {elapsed:.2f}s")
    print("=" * 50)
    print("\nTry editing MESSAGE in this file and running again!")
    print("The change will be reflected without a cold start.")
