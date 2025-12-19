"""Demo: Multiple concurrent calls to the same warm pod.

The Kubetorch HTTP server can handle multiple requests concurrently,
all hitting the same warm pod.
"""
import time


def slow_computation(task_id: int, delay: float = 1.0):
    """Simulate a slow computation."""
    import socket
    time.sleep(delay)
    return f"Task {task_id} completed on {socket.gethostname()}"


if __name__ == "__main__":
    import kubetorch as kt
    import concurrent.futures
    
    print("Setting up Kubetorch...")
    compute = kt.Compute(cpus="0.5", launch_timeout=60, inactivity_ttl="10m", labels={"demo": "concurrent"})
    remote_fn = kt.fn(slow_computation, name="warmstart_concurrent").to(compute)
    
    # Warm up
    print("Warming up pod...")
    remote_fn(0, 0.1)
    
    # Run concurrent tasks
    num_tasks = 5
    delay = 1.0
    
    print(f"\nRunning {num_tasks} tasks concurrently (each takes {delay}s)...")
    print("If sequential, this would take {:.1f}s".format(num_tasks * delay))
    
    start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_tasks) as executor:
        futures = [executor.submit(remote_fn, i, delay) for i in range(1, num_tasks + 1)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    elapsed = time.time() - start
    
    print("\nResults:")
    for result in results:
        print(f"  {result}")
    
    print(f"\nTotal time: {elapsed:.2f}s")
    print(f"Speedup: {(num_tasks * delay) / elapsed:.1f}x (vs sequential)")

