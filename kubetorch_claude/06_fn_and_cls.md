# Functions and Classes (kt.fn, kt.cls)

> **Official Docs:** [Core Python Primitives](https://www.run.house/kubetorch/concepts/core-primitives)

## Overview

Kubetorch provides two main primitives for remote execution:
- `kt.fn()` - Wrap a function for remote execution
- `kt.cls()` - Wrap a class for remote execution

Both inherit from the base `Module` class and share similar patterns.

---

## kt.fn() - Remote Functions

### Basic Usage

```python
import kubetorch as kt

def my_function(x, y):
    return x + y

# Wrap and deploy
compute = kt.Compute(cpus="0.5")
remote_fn = kt.fn(my_function).to(compute)

# Call remotely
result = remote_fn(1, 2)  # Returns 3
```

### Constructor

```python
kt.fn(
    function_obj=None,           # Function to wrap
    name: str = None,            # Service name (default: function.__name__)
    get_if_exists: bool = True,  # Attempt to find existing service
    reload_prefixes: List[str] = None,  # Prefixes for service lookup
)
```

### Parameters

#### `function_obj`
The Python function to execute remotely. If `None`, must provide `name` to reload existing service.

#### `name`
Name for the service. Becomes part of the K8s service name: `{username}-{name}`.

```python
kt.fn(my_func, name="my-service")  # → yourname-my-service
kt.fn(my_func)  # → yourname-my_func (uses function name)
```

#### `get_if_exists`
Controls service lookup behavior:
- `True`: Look for existing service using fallback order
- `False`: Only exact name match

```python
# Try to reuse existing service
remote = kt.fn(my_func, get_if_exists=True).to(compute)

# Always create new
remote = kt.fn(my_func, get_if_exists=False).to(compute)
```

#### `reload_prefixes`
Prefixes to try when looking for existing services.

```python
kt.fn(my_func, reload_prefixes=["prod", "qa", "dev"])
```

### Reloading Existing Services

```python
# Reload by name (no function object)
remote = kt.fn(name="my-service")

# With namespace
remote = kt.fn(name="my-service", namespace="production")

# With prefixes
remote = kt.fn(name="my-service", reload_prefixes=["prod", "staging"])
```

---

## kt.cls() - Remote Classes

### Basic Usage

```python
import kubetorch as kt

class MyModel:
    def __init__(self, size: int):
        self.size = size
        self.data = list(range(size))
    
    def get_sum(self):
        return sum(self.data)
    
    def multiply(self, factor: int):
        return [x * factor for x in self.data]

# Wrap and deploy
compute = kt.Compute(cpus="0.5")
remote_model = kt.cls(MyModel, name="my-model").to(
    compute,
    init_args={"size": 10}  # Constructor arguments
)

# Call methods remotely
total = remote_model.get_sum()
scaled = remote_model.multiply(2)
```

### Constructor

```python
kt.cls(
    class_obj=None,              # Class to wrap
    name: str = None,            # Service name (default: class.__name__)
    get_if_exists: bool = True,  # Attempt to find existing service
    reload_prefixes: List[str] = None,  # Prefixes for service lookup
)
```

### init_args

Constructor arguments are passed via `.to()`:

```python
remote = kt.cls(MyClass).to(compute, init_args={"param1": "value1", "param2": 42})
```

The class is instantiated once on the remote pod and persists between method calls.

---

## The `.to()` Method

Both `kt.fn()` and `kt.cls()` use `.to()` to deploy to compute:

```python
.to(
    compute: Compute,
    init_args: Dict = None,      # For cls only
    stream_logs: bool = None,    # Override log streaming
    get_if_exists: bool = False, # Reuse existing service
    reload_prefixes: List[str] = [],  # Lookup prefixes
    dryrun: bool = False,        # Setup without deploying
)
```

### Parameters

#### `compute`
The `kt.Compute` instance defining resources.

#### `init_args` (cls only)
Dictionary of constructor arguments for the class.

#### `stream_logs`
Override log streaming during deployment:
- `True`: Stream logs
- `False`: Suppress logs
- `None`: Use compute's logging_config or global setting

#### `get_if_exists`
If `True`, check for existing service before deploying.

#### `reload_prefixes`
Prefixes to try when looking for existing services.

#### `dryrun`
If `True`, set up the module without actually deploying. Useful for testing.

---

## Calling Remote Functions/Methods

### Synchronous Call (Default)

```python
result = remote_fn(arg1, arg2, kwarg1="value")
```

### Asynchronous Call

```python
result = await remote_fn(arg1, arg2, async_=True)

# Or using the async property
remote_fn.async_ = True
result = await remote_fn(arg1, arg2)
```

### Call Options

```python
result = remote_fn(
    arg1, arg2,
    # Kubetorch options (popped from kwargs):
    stream_logs=True,       # Override log streaming
    stream_metrics=True,    # Stream metrics during call
    debug=True,             # Enable remote debugging
    serialization="pickle", # Use pickle instead of JSON
)
```

---

## Serialization

### JSON (Default)

Arguments and return values are serialized as JSON. Works with:
- Primitives (int, float, str, bool, None)
- Lists, dicts
- Nested structures of the above

```python
result = remote_fn({"data": [1, 2, 3]})
```

### Pickle

For complex Python objects, use pickle serialization:

```python
import numpy as np

def process_array(arr):
    return arr * 2

remote = kt.fn(process_array).to(compute)
result = remote(np.array([1, 2, 3]), serialization="pickle")
```

Or set as default:
```python
remote.serialization = "pickle"
result = remote(np.array([1, 2, 3]))
```

**Security Note:** Pickle can execute arbitrary code. Use `allowed_serialization` on Compute to restrict.

---

## Debugging

### Remote Breakpoints

```python
def my_function():
    x = 10
    breakpoint()  # Opens remote pdb
    return x

remote = kt.fn(my_function).to(compute)
result = remote(debug=True)  # Required to enable pdb
```

When the function hits `breakpoint()`, an interactive pdb session opens.

### Deep Breakpoint

Use `kt.deep_breakpoint()` for breakpoints in nested code:

```python
from kubetorch import deep_breakpoint

def nested_function():
    for i in range(10):
        if i == 5:
            deep_breakpoint()  # Breakpoint at specific condition
```

---

## Module Properties

Both `Fn` and `Cls` have these properties:

```python
remote.name              # Function/class name
remote.service_name      # Full K8s service name
remote.namespace         # Deployment namespace
remote.compute           # Associated Compute object
remote.pointers          # (file_path, module_name, fn_or_cls_name)
remote.serialization     # "json" or "pickle"
remote.async_            # Default async mode
remote.stream_logs       # Resolved stream_logs setting
remote.logging_config    # LoggingConfig from compute
```

---

## Module Methods

### `teardown()`

Delete the service and associated resources:

```python
remote.teardown()
```

### `deploy()`

Deploy using decorator settings (used by `kt deploy`):

```python
remote.deploy()
```

---

## Shared Services

Multiple functions can share the same pod by using the same name:

```python
compute = kt.Compute(cpus="1")

fn1 = kt.fn(function1, name="shared").to(compute)
fn2 = kt.fn(function2, name="shared").to(compute)

# Both use the same pod
fn1()  # Runs on pod
fn2()  # Runs on same pod
```

This is efficient for:
- Related functions that share imports
- Reducing cold starts
- Caching shared state

---

## Examples

### Machine Learning Inference

```python
class ModelServer:
    def __init__(self, model_path: str):
        import torch
        self.model = torch.load(model_path)
        self.model.eval()
    
    def predict(self, inputs):
        import torch
        with torch.no_grad():
            return self.model(inputs).tolist()

compute = kt.Compute(gpus=1, memory="16Gi")
server = kt.cls(ModelServer).to(
    compute,
    init_args={"model_path": "/models/my_model.pt"}
)

predictions = server.predict(data)
```

### Data Processing Pipeline

```python
def process_batch(batch_id: int, data: list):
    import pandas as pd
    df = pd.DataFrame(data)
    # Process...
    return df.to_dict()

compute = kt.Compute(cpus="4", memory="16Gi")
process = kt.fn(process_batch, name="processor").to(compute)

# Process multiple batches
results = [process(i, batch) for i, batch in enumerate(batches)]
```

### Concurrent Calls

```python
import concurrent.futures

def slow_task(task_id: int):
    import time
    time.sleep(1)
    return f"Task {task_id} done"

compute = kt.Compute(cpus="1")
remote = kt.fn(slow_task).to(compute)

# Warm up
remote(0)

# Run concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(remote, i) for i in range(5)]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

print(results)  # All complete in ~1 second (parallel)
```

### Async Pattern

```python
import asyncio

async def main():
    compute = kt.Compute(cpus="0.5")
    remote = kt.fn(my_function).to(compute)
    
    # Multiple async calls
    tasks = [remote(i, async_=True) for i in range(10)]
    results = await asyncio.gather(*tasks)
    return results

asyncio.run(main())
```

