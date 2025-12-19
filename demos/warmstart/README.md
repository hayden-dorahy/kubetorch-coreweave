# Warm Start Feature Demos

Demonstrations of Kubetorch's warm start capabilities - pods stay running
between calls for fast iteration and preserved state.

| Demo | Description |
|------|-------------|
| `timing_demo.py` | Compare cold start vs warm start timing |
| `hot_reload.py` | Edit code and see changes without pod restart |
| `state_persistence.py` | Global variables persist between calls |
| `breakpoint_debug.py` | Remote debugging with breakpoint() |
| `ssh_into_pod.py` | Open interactive SSH session in the pod |
| `concurrent_calls.py` | Multiple concurrent calls to the same pod |

## Running

```bash
# Timing comparison
python demos/warmstart/timing_demo.py

# Hot reload - run twice, edit MESSAGE between runs
python demos/warmstart/hot_reload.py

# State persistence - run multiple times
python demos/warmstart/state_persistence.py set name Alice
python demos/warmstart/state_persistence.py set color blue
python demos/warmstart/state_persistence.py list
python demos/warmstart/state_persistence.py get name

# Remote debugging (interactive)
python demos/warmstart/breakpoint_debug.py

# SSH into pod (interactive)
python demos/warmstart/ssh_into_pod.py

# Concurrent calls
python demos/warmstart/concurrent_calls.py
```

## How It Works

When you run a Kubetorch function:
1. **Cold Start:** If the service doesn't exist, Kubetorch creates a Deployment + Service. This takes ~30s-2m (image pull, pod startup).
2. **Warm Start:** The pod stays running (HTTP server). Subsequent calls just hit the API endpoint. This takes ~100-300ms.
3. **Code Sync:** When you re-run your script, Kubetorch syncs *only* the changed Python files to the running pod. The server hot-reloads the module.

## Capabilities

- **Fast Iteration:** Edit code locally, run instantly (sub-second).
- **State Persistence:** Global variables (`CACHE = {}`) and loaded models (`model.to("cuda")`) stay in memory between calls. No need to reload heavy weights every time.
- **Interactive Debugging:** Use `breakpoint()` to drop into a remote debugger session.
- **Shell Access:** `compute.ssh()` gives you a terminal inside the running environment.

## Limitations & Gotchas

### 1. Single Entrypoint per Service
A running service is bound to a specific Python function/module.
If you reuse `name="my_service"` for `func_A` and then try to run `func_B` on it, you'll get:
`Callable 'func_B' not found... Found 'func_A' instead`

**Fix:** Use unique names (`name="service_a"`, `name="service_b"`) or restart the service.

### 2. Global State Pollution
Since the process persists, global state accumulates.
- **Good:** Caching models/datasets.
- **Bad:** Memory leaks, stale configuration, uncleared lists.
**Fix:** Explicitly clear state or use fresh services for clean tests.

### 3. Resource Holding
Warm pods hold resources (GPUs/CPUs) even when idle.
**Fix:** Configure `inactivity_ttl` to auto-terminate idle pods.

## Configuration

All demos in this folder use:
```python
kt.Compute(
    launch_timeout=60,      # Give up if pod takes >60s to start
    inactivity_ttl="10m"    # Kill pod after 10 minutes of inactivity
)
```
