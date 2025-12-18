# Kubetorch Demos

All demos are CPU-only unless marked otherwise.

## Categories

| Folder | Description |
|--------|-------------|
| [`basics/`](basics/) | Core Kubetorch functionality |
| [`warmstart/`](warmstart/) | Warm start features (hot reload, state, debugging) |
| [`pxs/`](pxs/) | PhysicsX library integration |
| [`gpu/`](gpu/) | GPU demos (WIP - requires SUNK scheduler) |

## Quick Start

```bash
# From repo root
source .venv/bin/activate

# Run any demo
python demos/basics/hello_world.py
python demos/warmstart/timing_demo.py
python demos/pxs/pxs_artifactory.py

# View running services
kt list

# Clean up
kt delete <name>
```

## See Also

- [Main README](../README.md) - Full demo list and cluster info
- [Kubetorch Setup](../admin/docs/kubetorch_setup.md) - Installation guide

