# Logging, Debugging & Metrics

> **Official Docs:** [Monitoring & Observability](https://www.run.house/kubetorch/concepts/monitoring)
> **Source:** `kubetorch.globals.LoggingConfig`, `kubetorch.servers.http.pdb_websocket`, `kubetorch.servers.http.server_metrics`

## Logging

### Log Streaming
By default, Kubetorch streams logs from the remote pod to your local console using **Loki**.

**Configuration:**
- Global: `kt config set stream_logs true`
- Per-Compute: `kt.Compute(logging_config=kt.LoggingConfig(stream_logs=True))`
- Per-Call: `remote_fn(stream_logs=False)`

### LoggingConfig

```python
from kubetorch import LoggingConfig

logging_config = LoggingConfig(
    stream_logs=True,
    level="info",               # Filter level: debug, info, warning, error
    include_system_logs=False,  # Hide framework logs (uvicorn, etc.)
    include_events=True,        # Show K8s events (Pulling image, Scheduled, etc.)
    include_name=True,          # Prefix logs with "(service-name)"
)
```

### Log Structure
Logs are formatted as:
```
(service-name) INFO | 2024-12-18 10:00:00 | Log message content
```

### Events
K8s events are shown during startup:
```
[EVENT] Normal reason=Scheduled "Successfully assigned default/pod-xyz to node-1"
[EVENT] Normal reason=Pulling "Pulling image..."
```

---

## Remote Debugging

Kubetorch supports interactive remote debugging using `pdb`.

### Usage

1. Add `breakpoint()` in your code.
2. Call with `debug=True`.

```python
def buggy_function():
    x = 10
    breakpoint()  # <--- Execution pauses here
    return x

remote_fn = kt.fn(buggy_function).to(compute)
remote_fn(debug=True)
```

### Interaction
Your terminal becomes a PTY connected to the remote pdb session.
- `n` (next), `s` (step), `c` (continue), `p variable` (print) work as expected.

### Deep Breakpoint
For breakpoints in nested calls or libraries:

```python
from kubetorch import deep_breakpoint

# Inside nested code
deep_breakpoint()
```

---

## Metrics (Prometheus)

Kubetorch integrates with Prometheus to collect and stream metrics.

**Configuration:**
- Global: `kt config set stream_metrics true`
- Per-Call: `remote_fn(stream_metrics=True)`

### Streamed Metrics
When enabled, metrics are printed to the console during execution:
- CPU Usage
- Memory Usage
- GPU Utilization
- GPU Memory

### Dashboard
If configured, metrics are available in the cluster Grafana dashboard.

---

## SSH Access

Launch an interactive shell for manual debugging:

```python
compute.ssh()
```

Or via CLI:
```bash
kt ssh my-service
```

Inside the pod:
- Code is at `.` (working directory)
- Environment variables are set
- `nvidia-smi` to check GPUs
- `top` / `htop` for processes

