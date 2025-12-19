# PXS (PhysicsX) Demos

Demonstrations of running the `pxs` library on Kubetorch, including
private package installation from Artifactory and editable development workflows.

| Demo | Description |
|------|-------------|
| `pxs_artifactory.py` | Install pxs from Artifactory (uses uv store or .env.secrets) |
| `pxs_secrets_install.py` | Dedicated example using .env.secrets for install |
| `pxs_editable_rsync.py` | Rsync local pxs code + install deps separately |
| `pxs_editable_install.py` | Full editable install via `uv pip install -e` |

## Prerequisites

### Option 1: Env Vars (Recommended)
Create a `.env.secrets` file in the repo root:
```bash
export ARTIFACTORY_USER="your.name"
export ARTIFACTORY_TOKEN="your-token"
```

### Option 2: uv auth
Run `uv auth login` to store credentials in `~/.local/share/uv/credentials/credentials.toml`.

## Running

```bash
# Standard pxs from Artifactory
python demos/pxs/pxs_artifactory.py

# Editable mode (uses local ~/gitrepos/product/libraries/pxs)
python demos/pxs/pxs_editable_rsync.py
python demos/pxs/pxs_editable_install.py
```

## Approaches Compared

### 1. Artifactory Install (`pxs_artifactory.py`)
- Installs `physicsx.pxs[opora]` from private registry
- Best for: Using released versions

### 2. Rsync + Deps (`pxs_editable_rsync.py`)
- Installs deps from Artifactory
- Rsyncs local pxs source code
- Uses `sys.path.insert()` to prioritize local code
- Best for: Quick iteration on pxs code

### 3. Editable Install (`pxs_editable_install.py`)
- Rsyncs full pxs repo
- Runs `uv pip install -e` for proper editable install
- Still needs `sys.path.insert()` (Kubetorch server already running)
- Best for: Full dev workflow with dependency resolution

