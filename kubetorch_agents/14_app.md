# App & CLI Execution

> **Official Docs:** [App API Reference](https://www.run.house/kubetorch/api-reference/python/app)
> **Source:** `kubetorch.resources.compute.app.App`

`kt.App` wraps a command-line script for remote execution via `kt run`.

## kt.app() Factory

Use `kt.app()` in your script to define its remote requirements.

```python
# train.py
import kubetorch as kt
import argparse

# Define infrastructure at the top
kt.app(
    name="training-job",
    cpus="4",
    memory="16Gi",
    gpus=1,
    image=kt.images.pytorch()
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=10)
    args = parser.parse_args()
    
    print(f"Training for {args.epochs} epochs...")
```

## Running with `kt run`

Execute the script remotely using the CLI:

```bash
kt run python train.py --epochs 50
```

### What Happens:
1. CLI parses `kt run`.
2. Sets `KT_RUN=1` env var.
3. Executes `train.py` locally **until `kt.app()`**.
4. `kt.app()` detects `KT_RUN=1`:
   - Reads arguments from `kt.app()` (Compute spec).
   - Syncs the current directory to the cluster.
   - Launches a job/pod on the cluster.
   - Executes the command (`python train.py --epochs 50`) inside the pod.
   - Streams logs back to your terminal.
5. Local execution exits (replaced by remote stream).

## Overriding in CLI

You can override `kt.app()` settings via CLI flags:

```bash
kt run --gpus 2 --memory 32Gi python train.py
```

## Running Without `kt.app()`

If your script doesn't contain `kt.app()`, `kt run` uses default resources (CPU-only).

```bash
kt run python simple_script.py
```

## Use Cases

- **Ad-hoc Scripts**: Run local scripts on cluster without modifying code structure much.
- **Legacy Code**: Wrap existing ML scripts.
- **CI/CD**: `kt run` in GitHub Actions to execute training jobs.

## App Class Reference

`kt.App` inherits from `Module`.

```python
class App(Module):
    def __init__(
        self,
        compute: Compute,
        cli_command: str,
        pointers: tuple,
        name: str = None,
        run_async: bool = False,
    ): ...
```

It behaves like a function that executes a shell command instead of a Python function call.

