# PXS (PhysicsX) Demos

Demonstrations of running the `pxs` library on Kubetorch, including
private package installation from Artifactory and local development workflows.

| Demo | Description |
|------|-------------|
| `pxs_artifactory.py` | Install pxs from Artifactory (uses uv store or .env.secrets) |
| `pxs_local_editable.py` | Rsync local pxs repo + pip install from local path |

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

# Local install (uses local ~/gitrepos/product/libraries/pxs)
python demos/pxs/pxs_local_editable.py
```

## Approaches Compared

### 1. Artifactory Install (`pxs_artifactory.py`)
- Installs `physicsx.pxs[opora]` from private registry
- Best for: Using released versions

### 2. Local Install (`pxs_local_editable.py`)
- Rsyncs full pxs repo with `contents=True`
- Uses `pip_install()` from local path
- Best for: Testing local pxs changes
