# Decorators

Kubetorch provides decorators to define infrastructure alongside code. This enables the "Infrastructure as Code" pattern for Python.

## `@kt.compute`

Defines the compute resources for a function or class.

```python
import kubetorch as kt

@kt.compute(
    cpus="2",
    memory="16Gi",
    gpus=1,
    image=kt.images.pytorch()
)
def train_model():
    ...
```

## `@kt.distribute`

Enables distributed execution. Chains with `@kt.compute`.

```python
@kt.compute(gpus=8)
@kt.distribute(
    framework="pytorch",
    workers=4
)
def distributed_train():
    ...
```

## `@kt.autoscale`

Enables Knative autoscaling. Chains with `@kt.compute`.

```python
@kt.compute(cpus="1")
@kt.autoscale(
    min_replicas=0,
    max_replicas=10
)
def inference_handler(request):
    ...
```

## `@kt.async_`

Marks a function to run asynchronously by default.

```python
@kt.compute(cpus="1")
@kt.async_
def background_task():
    ...
```

## Using Decorated Functions

### 1. Import and Call
When you import the decorated function in Python, it becomes a `kt.Fn` or `kt.Cls` object automatically connected to a `kt.Compute` spec.

```python
# In main.py
from my_tasks import train_model

# Deploys and runs
result = train_model()
```

### 2. CLI Deployment (`kt deploy`)
You can deploy all decorated functions in a file without running them.

```bash
kt deploy my_tasks.py
```

This ensures the services are up and ready for requests.

---

## PartialModule Pattern

Internally, decorators return a `PartialModule` that accumulates configuration. The outermost decorator (usually `@kt.compute`) finalizes the `Module` object.

**Order Matters:**
`@kt.compute` should generally be the outermost (top) decorator.

```python
# Correct
@kt.compute(...)
@kt.distribute(...)
def func(): ...

# Incorrect (distribute needs compute context)
@kt.distribute(...)
@kt.compute(...)  # Might work due to implementation details, but not recommended
def func(): ...
```

