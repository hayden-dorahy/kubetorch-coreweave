# Kubetorch Demo Suite

A collection of demos showcasing [Kubetorch](https://www.run.house/kubetorch) features on CoreWeave's Kubernetes cluster.

## Quick Start

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Authenticate to Artifactory (so we can install PXS). Enter your Artifactory user and token as the username and password:
uv auth login https://physicsx.jfrog.io/artifactory/api/pypi/px-pypi-release/simple

# Activate environment
source .venv/bin/activate

# First time: set your username (required!)
kt config set username <your-name>

# Run a basic demo
python demos/basics/hello_world.py

# Clean up when done
kt list              # See running services
kt teardown <name>   # Delete specific service
kt teardown --all    # Delete all YOUR services
```

## Repository Structure

```
├── demos/                    # Demo scripts
│   ├── basics/              # Core Kubetorch functionality
│   │   ├── hello_world.py   # Minimal example
│   │   ├── pvc_access.py    # Shared storage access
│   │   └── user_labels.py   # Workload identification
│   │
│   ├── warmstart/           # Warm start features
│   │   ├── timing_demo.py   # Cold vs warm timing
│   │   ├── hot_reload.py    # Code changes without restart
│   │   ├── state_persistence.py  # Persistent globals
│   │   ├── breakpoint_debug.py   # Remote debugging
│   │   ├── ssh_into_pod.py       # Interactive SSH
│   │   └── concurrent_calls.py   # Parallel requests
│   │
│   ├── pxs/                 # PhysicsX library demos
│   │   ├── pxs_artifactory.py    # Install from Artifactory
│   │   ├── pxs_editable_rsync.py # Editable via rsync
│   │   └── pxs_editable_install.py  # Full editable install
│   │
│   └── gpu/                 # GPU demos (WIP)
│       ├── gpu_sunk_scheduler.py # Kubetorch + SUNK
│       └── gpu_sunk_raw.yaml     # Raw K8s manifest
│
├── admin/                   # Cluster administration
│   ├── docs/               # Setup documentation
│   │   ├── kubetorch_setup.md   # Kubetorch installation guide
│   │   └── coreweave_k8s.md     # CoreWeave connection guide
│   └── helmfile.yaml       # Kubetorch Helm deployment
│
├── pyproject.toml          # Python dependencies
└── README.md               # This file
```

## Demos by Category

### Basics
| Demo | Description | CPU | GPU |
|------|-------------|:---:|:---:|
| `hello_world.py` | Run a function on the cluster | ✅ | - |
| `pvc_access.py` | Access shared storage | ✅ | - |
| `user_labels.py` | Label workloads by user | ✅ | - |

### Warm Start Features
| Demo | Description | CPU | GPU |
|------|-------------|:---:|:---:|
| `timing_demo.py` | Compare cold vs warm start | ✅ | - |
| `hot_reload.py` | Edit code, no restart | ✅ | - |
| `state_persistence.py` | Globals persist between calls | ✅ | - |
| `breakpoint_debug.py` | Remote pdb debugging | ✅ | - |
| `ssh_into_pod.py` | Interactive shell in pod | ✅ | - |
| `concurrent_calls.py` | Parallel function calls | ✅ | - |

### PXS (PhysicsX)
| Demo | Description | CPU | GPU |
|------|-------------|:---:|:---:|
| `pxs_artifactory.py` | Install pxs from Artifactory | ✅ | - |
| `pxs_editable_rsync.py` | Dev mode via rsync | ✅ | - |
| `pxs_editable_install.py` | Full editable install | ✅ | - |

### GPU (Work in Progress)
| Demo | Description | CPU | GPU |
|------|-------------|:---:|:---:|
| `gpu_sunk_scheduler.py` | Kubetorch + SUNK | - | 🚧 |
| `gpu_sunk_raw.yaml` | Raw K8s GPU test | - | 🚧 |

## Cluster Info

- **Provider:** CoreWeave
- **Region:** US West 9B (`usw9b`)
- **GPUs:** 16x NVIDIA B200 (reserved by Slurm/SUNK)
- **Storage:** 30TB shared at `/mnt/data`

## Key Concepts

### Warm Start
Kubetorch keeps pods running after your script ends:
- Python process stays alive → imports cached
- Global state persists between calls
- Code changes hot-reload without reimporting

### Pod Lifecycle
```
Script runs → Pod created → Script ends → Pod stays running
                                              ↓
                            Next run → Reuses warm pod (fast!)
```
Pods auto-terminate after 10 minutes of inactivity (configured via `inactivity_ttl="10m"`).

### Cleanup
Pods run indefinitely unless deleted:
```bash
kt list                      # List all services
kt teardown <name>           # Delete specific service
kt teardown --prefix <pfx>   # Delete all matching prefix
```

## Documentation

- [Kubetorch Setup Guide](admin/docs/kubetorch_setup.md) - Installation & configuration
- [CoreWeave Connection](admin/docs/coreweave_k8s.md) - Cluster access & SSH
- [Kubetorch Official Docs](https://www.run.house/kubetorch)
