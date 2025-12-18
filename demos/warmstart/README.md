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

## Key Concepts

- **Pods stay running** after your script ends
- **Python process persists** - imports are cached in `sys.modules`
- **Global state persists** - useful for caching models, data
- **Code hot-reloads** - changes sync without reimporting dependencies

