# Quickstart Guide

## Prerequisites

- Kubetorch installed: `pip install "kubetorch[client]"`
- Cluster access configured (kubeconfig)
- Kubetorch operator deployed to cluster
- Username set: `kt config set username your-name`

## Hello World

```python
import kubetorch as kt

def hello_world():
    import platform
    return f"Hello from Kubetorch! Running on {platform.node()}"

if __name__ == "__main__":
    # Define compute resources
    compute = kt.Compute(cpus="0.1")

    # Send function to cluster
    remote_fn = kt.fn(hello_world, name="hello").to(compute)

    # Run remotely
    result = remote_fn()
    print(result)  # "Hello from Kubetorch! Running on pod-xyz"
```

## Understanding the Flow

```
1. kt.Compute(cpus="0.1")
   └── Defines: 0.1 CPU cores, default memory, no GPU

2. kt.fn(hello_world, name="hello")
   └── Wraps function for remote execution
   └── Name becomes part of service name: "yourname-hello"

3. .to(compute)
   └── Creates K8s Deployment
   └── Rsyncs your code to cluster
   └── Starts HTTP server in pod
   └── Waits for pod to be ready

4. remote_fn()
   └── Serializes arguments (JSON by default)
   └── Sends HTTP POST to pod
   └── Deserializes and returns result
```

## Warm Start Demo

```python
import kubetorch as kt
import time

def get_time():
    import datetime
    return f"Called at {datetime.datetime.now()}"

if __name__ == "__main__":
    compute = kt.Compute(cpus="0.1")
    remote_fn = kt.fn(get_time, name="warmstart").to(compute)

    # First call - cold start (creates pod)
    print("First call (cold start)...")
    start = time.time()
    result1 = remote_fn()
    cold_time = time.time() - start
    print(f"  Result: {result1}")
    print(f"  Time: {cold_time:.2f}s")

    # Second call - warm start (pod already running)
    print("\nSecond call (warm start)...")
    start = time.time()
    result2 = remote_fn()
    warm_time = time.time() - start
    print(f"  Result: {result2}")
    print(f"  Time: {warm_time:.2f}s")

    print(f"\nSpeedup: {cold_time/warm_time:.1f}x faster!")
```

**Expected output:**
```
First call (cold start)...
  Result: Called at 2024-12-18 10:30:00.123456
  Time: 15.23s

Second call (warm start)...
  Result: Called at 2024-12-18 10:30:01.234567
  Time: 0.12s

Speedup: 127x faster!
```

## Hot Reload Demo

```python
# hot_reload.py
import kubetorch as kt

# ============================================
# EDIT THIS MESSAGE AND RE-RUN THE SCRIPT!
# ============================================
MESSAGE = "Hello from v1!"

def get_message():
    return f"Message: {MESSAGE}"

if __name__ == "__main__":
    compute = kt.Compute(cpus="0.1")
    remote_fn = kt.fn(get_message, name="hotreload").to(compute)
    
    print(remote_fn())  # "Message: Hello from v1!"
    print("\nTry editing MESSAGE and running again!")
```

1. Run once → "Message: Hello from v1!"
2. Edit `MESSAGE = "Hello from v2!"`
3. Run again → "Message: Hello from v2!" (in ~1-2 seconds!)

## State Persistence Demo

```python
import kubetorch as kt

# These persist on the pod between calls!
CACHE = {}
CALL_COUNT = 0

def cache_operation(action: str, key: str = None, value: str = None):
    global CACHE, CALL_COUNT
    CALL_COUNT += 1
    
    if action == "set" and key and value:
        CACHE[key] = value
        return f"[Call #{CALL_COUNT}] Set {key}={value}. Cache: {CACHE}"
    elif action == "get" and key:
        return f"[Call #{CALL_COUNT}] {key}={CACHE.get(key, 'NOT FOUND')}"
    elif action == "list":
        return f"[Call #{CALL_COUNT}] Cache: {CACHE}"
    elif action == "clear":
        CACHE.clear()
        return f"[Call #{CALL_COUNT}] Cleared!"

if __name__ == "__main__":
    compute = kt.Compute(cpus="0.1")
    remote = kt.fn(cache_operation, name="cache").to(compute)
    
    print(remote("set", "name", "Alice"))
    print(remote("set", "color", "blue"))
    print(remote("list"))
    print(remote("get", "name"))
```

**Output:**
```
[Call #1] Set name=Alice. Cache: {'name': 'Alice'}
[Call #2] Set color=blue. Cache: {'name': 'Alice', 'color': 'blue'}
[Call #3] Cache: {'name': 'Alice', 'color': 'blue'}
[Call #4] name=Alice
```

## GPU Example

```python
import kubetorch as kt

def check_gpu():
    import torch
    
    if torch.cuda.is_available():
        return f"GPU: {torch.cuda.get_device_name(0)}"
    return "No GPU available"

if __name__ == "__main__":
    compute = kt.Compute(
        cpus="2",
        memory="8Gi",
        gpus=1,
        gpu_type="L4",  # Request specific GPU type
    )
    
    remote = kt.fn(check_gpu, name="gpu-test").to(compute)
    print(remote())
```

## With Custom Image

```python
import kubetorch as kt

def run_numpy():
    import numpy as np
    return f"NumPy version: {np.__version__}"

if __name__ == "__main__":
    image = (
        kt.images.Debian()
        .pip_install(["numpy>=1.24", "pandas"])
        .set_env_vars({"OMP_NUM_THREADS": "4"})
    )
    
    compute = kt.Compute(cpus="1", memory="2Gi", image=image)
    remote = kt.fn(run_numpy, name="numpy-test").to(compute)
    print(remote())
```

## Remote Debugging

```python
import kubetorch as kt

def debug_me():
    x = 10
    y = 20
    
    # This opens an interactive debugger!
    breakpoint()
    
    return x + y

if __name__ == "__main__":
    compute = kt.Compute(cpus="0.1")
    remote = kt.fn(debug_me, name="debug").to(compute)
    
    # Pass debug=True to enable remote pdb
    result = remote(debug=True)
    print(result)
```

When `breakpoint()` is hit, you get an interactive pdb session connected to the remote pod!

## SSH into Pod

```python
import kubetorch as kt

def setup():
    import socket
    return f"Pod ready: {socket.gethostname()}"

if __name__ == "__main__":
    compute = kt.Compute(cpus="0.1")
    remote = kt.fn(setup, name="ssh-demo").to(compute)
    
    print(remote())  # Ensure pod is running
    
    # Open interactive shell
    compute.ssh()
```

## Cleanup

```bash
# List your services
kt list

# Delete specific service
kt teardown yourname-hello

# Delete all YOUR services
kt teardown --all

# Delete by prefix
kt teardown --prefix yourname-
```

## Common Patterns

### Reusing Compute
```python
compute = kt.Compute(cpus="1", memory="4Gi")

fn1 = kt.fn(function1, name="fn1").to(compute)
fn2 = kt.fn(function2, name="fn2").to(compute)
# Each gets its own service, same resource spec
```

### Shared Service (Multiple Functions)
```python
# Both functions share the same pod
fn1 = kt.fn(function1, name="shared").to(compute)
fn2 = kt.fn(function2, name="shared").to(compute)
```

### Check if Service Exists
```python
remote = kt.fn(my_fn, name="my-service").to(
    compute,
    get_if_exists=True  # Reuse if already deployed
)
```

### Force Fresh Deployment
```python
# Delete existing and redeploy
compute = kt.Compute(cpus="1")
compute.service_name = "yourname-my-service"
compute.service_manager.teardown_service("yourname-my-service")

remote = kt.fn(my_fn, name="my-service").to(compute)
```

