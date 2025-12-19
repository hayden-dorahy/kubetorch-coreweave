"""Demo warm start - second call is much faster"""
import time
import kubetorch as kt


def get_time():
    import datetime
    return f"Called at {datetime.datetime.now()}"


if __name__ == "__main__":
    compute = kt.Compute(cpus="0.1", launch_timeout=60, inactivity_ttl="10m")
    remote_fn = kt.fn(get_time, name="warmstart_timing").to(compute)

    # First call - cold start (deploys pod)
    print("First call (cold start)...")
    start = time.time()
    result1 = remote_fn()
    cold_time = time.time() - start
    print(f"  Result: {result1}")
    print(f"  Time: {cold_time:.2f}s\n")

    # Second call - warm start (pod already running)
    print("Second call (warm start)...")
    start = time.time()
    result2 = remote_fn()
    warm_time = time.time() - start
    print(f"  Result: {result2}")
    print(f"  Time: {warm_time:.2f}s\n")

    print(f"Speedup: {cold_time/warm_time:.1f}x faster!")

