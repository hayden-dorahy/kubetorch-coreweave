# Image Class Reference

> **Official Docs:** [Image API Reference](https://www.run.house/kubetorch/api-reference/python/image)
> **Source:** `kubetorch.resources.images.image.Image`

The `kt.Image` class defines container image configuration and setup steps. It uses a builder pattern for chaining configuration.

## Constructor

```python
kt.Image(
    name: str = None,           # Optional name for the image config
    image_id: str = None,       # Docker image URI
    python_path: str = None,    # Path to Python executable
    install_cmd: str = None,    # Custom pip/uv install command
)
```

## Built-in Image Factories

Kubetorch provides convenient factory functions in `kt.images`:

### Base Images

```python
# Debian-based (default Kubetorch server image)
kt.images.Debian()      # ghcr.io/run-house/server:v3
kt.images.debian()      # Same as above

# Ubuntu-based
kt.images.Ubuntu()      # ghcr.io/run-house/ubuntu:v1
kt.images.ubuntu()      # Same as above
```

### Python Images

```python
# Specific Python versions (python:X.Y-slim)
kt.images.Python310()   # python:3.10-slim
kt.images.Python311()   # python:3.11-slim
kt.images.Python312()   # python:3.12-slim

# Dynamic version
kt.images.python("3.12")  # python:3.12-slim
kt.images.python("3.11")  # python:3.11-slim
```

### ML Framework Images

```python
# Ray
kt.images.Ray()               # rayproject/ray:latest
kt.images.ray("2.32.0")       # rayproject/ray:2.32.0
kt.images.ray("2.32.0-py311") # rayproject/ray:2.32.0-py311

# PyTorch (NVIDIA NGC)
kt.images.pytorch()           # nvcr.io/nvidia/pytorch:23.12-py3
kt.images.pytorch("24.08-py3") # nvcr.io/nvidia/pytorch:24.08-py3
kt.images.Pytorch2312()       # nvcr.io/nvidia/pytorch:23.12-py3
```

---

## Methods

### `from_docker(image_id)`

Set a custom Docker image as the base.

```python
image = kt.Image().from_docker("nvcr.io/nvidia/pytorch:24.08-py3")
image = kt.Image().from_docker("my-registry.io/my-image:v1.0")
image = kt.Image().from_docker("python:3.12-slim")
```

**Note:** Cannot combine with machine images (VM images).

---

### `pip_install(reqs, force=False)`

Install Python packages via pip/uv.

**Parameters:**
- `reqs`: List of package specifications
- `force`: Re-install even if already present

```python
# Simple packages
image = kt.images.Debian().pip_install(["numpy", "pandas"])

# Version constraints
image = kt.images.Debian().pip_install([
    "numpy>=1.20",
    "pandas==2.0.0",
    "torch>=2.0,<3.0"
])

# With pip flags (passed directly to pip)
image = kt.images.Debian().pip_install([
    "--pre torch==2.0.0rc1",           # Pre-release
    "--index-url https://pypi.org/simple torch",  # Custom index
    "--extra-index-url https://my-pypi.com/simple mypackage"
])

# Force reinstall
image = kt.images.Debian().pip_install(["numpy"], force=True)
```

---

### `set_env_vars(env_vars)`

Set environment variables with optional variable expansion.

**Parameters:**
- `env_vars`: Dict of environment variable name → value

```python
image = kt.images.Debian().set_env_vars({
    "OMP_NUM_THREADS": "4",
    "CUDA_VISIBLE_DEVICES": "0,1",
    "HF_HOME": "/cache/huggingface",
})

# Variable expansion ($VAR or ${VAR})
image = kt.images.Debian().set_env_vars({
    "BASE_PATH": "/usr/local",
    "BIN_PATH": "$BASE_PATH/bin",        # → /usr/local/bin
    "PATH": "$BIN_PATH:$PATH",           # Prepends to existing PATH
    "LD_LIBRARY_PATH": "/opt/lib:${LD_LIBRARY_PATH}",  # Appends
    "HOME_DATA": "${HOME}/data",         # Uses container's HOME
})
```

**Notes:**
- Variables expanded using `os.path.expandvars()`
- Undefined variables remain as literal strings
- Escape `$` with backslash: `\\$LITERAL`

---

### `run_bash(command, force=False)`

Run shell commands during container setup.

**Parameters:**
- `command`: Shell command string
- `force`: Re-run even if previously executed

```python
# Single command
image = kt.images.Debian().run_bash("apt-get update")

# Chained commands
image = kt.images.Debian().run_bash(
    "apt-get update && apt-get install -y vim curl git"
)

# Multiple run_bash calls (executed in order)
image = (
    kt.images.Debian()
    .run_bash("apt-get update")
    .run_bash("apt-get install -y vim")
    .run_bash("pip install uv")
)

# Background processes (use &)
image = kt.images.Debian().run_bash(
    "jupyter notebook --no-browser --port=8888 &"
)

# Force re-run
image = kt.images.Debian().run_bash("apt-get update", force=True)
```

**Notes:**
- Commands with `&` run in background, don't block setup
- Background processes continue after setup completes
- Use `&&` for dependent commands, `;` for sequential regardless of success
- Setup waits 0.5s to catch immediate failures in background processes

---

### `rsync(source, dest=None, contents=False, filter_options=None, force=False)`

Sync files/directories from local machine to container.

**Parameters:**
- `source`: Local path (absolute, relative, or `~/`)
- `dest`: Remote path (default: basename of source in working dir)
- `contents`: For directories - copy contents only (True) or directory itself (False)
- `filter_options`: Additional rsync filter options
- `force`: Force re-transfer using `--ignore-times`

```python
# File sync
image = kt.images.Debian().rsync("./config.yaml", "/app/config.yaml")

# Directory sync (creates /app/src/)
image = kt.images.Debian().rsync("./src", "/app")

# Directory contents only (contents go directly into /app/)
image = kt.images.Debian().rsync("./src", "/app", contents=True)

# No destination (uses basename in working dir)
image = kt.images.Debian().rsync("~/data/model.pt")  # → ./model.pt

# With exclusions
image = kt.images.Debian().rsync(
    "./project",
    "/app",
    filter_options="--exclude='*.log' --exclude='temp/'"
)

# Force re-sync for development
image = kt.images.Debian().rsync("./rapidly_changing_code", "/app", force=True)
```

**Default Exclusions:**
- Files from `.gitignore` (if present)
- Files from `.ktignore` (if present)
- `*.pyc`, `__pycache__`
- `.venv`
- `.git`

**Path Behavior:**
- Absolute paths (`/path`) → exact location
- Relative paths → relative to container working directory
- `~/path` → stripped to `path`, relative to working dir

---

### `sync_package(package, force=False)`

Sync a local Python package and add to path.

**Parameters:**
- `package`: Package name (if editably installed) or path to package directory
- `force`: Re-sync even if already synced

```python
# Sync editably installed package by name
image = kt.images.Debian().sync_package("my_local_package")

# Sync by path
image = kt.images.Debian().sync_package("./libs/my_package")
image = kt.images.Debian().sync_package("~/gitrepos/my_lib")
```

---

## Chaining Pattern

All methods return `self`, enabling fluent chaining:

```python
image = (
    kt.images.Debian()
    .set_env_vars({
        "UV_EXTRA_INDEX_URL": "https://my-pypi.com/simple",
        "UV_PRERELEASE": "allow",
    })
    .run_bash("pip install uv")
    .run_bash("uv pip install --system torch numpy")
    .pip_install(["pandas", "scikit-learn"])
    .rsync("./src", "/app/src", contents=True)
    .rsync("./config", "/app/config")
    .sync_package("my_local_lib")
)

compute = kt.Compute(cpus="2", memory="8Gi", image=image)
```

---

## Complete Examples

### Basic Python with Dependencies

```python
image = (
    kt.images.Python312()
    .pip_install([
        "numpy>=1.24",
        "pandas>=2.0",
        "scikit-learn",
        "matplotlib"
    ])
)
```

### PyTorch Training

```python
image = (
    kt.images.pytorch("24.08-py3")  # NVIDIA PyTorch image
    .set_env_vars({
        "CUDA_VISIBLE_DEVICES": "0,1,2,3",
        "NCCL_DEBUG": "INFO",
    })
    .pip_install([
        "transformers",
        "datasets",
        "accelerate",
        "wandb"
    ])
    .rsync("./training_scripts", "/workspace/scripts", contents=True)
)

compute = kt.Compute(
    gpus=4,
    memory="128Gi",
    shared_memory_limit="32Gi",
    image=image
)
```

### Private Package Registry

```python
import os

username = os.environ["REGISTRY_USER"]
password = os.environ["REGISTRY_PASS"]

image = (
    kt.images.Debian()
    .set_env_vars({
        "UV_EXTRA_INDEX_URL": f"https://{username}:{password}@my-registry.com/simple",
        "UV_PRERELEASE": "allow",
        "UV_INDEX_STRATEGY": "unsafe-best-match",
    })
    .run_bash("pip install uv")
    .run_bash("uv pip install --system 'my-private-package==1.2.3'")
)
```

### Development with Local Code

```python
# Sync local development code
image = (
    kt.images.Debian()
    .pip_install(["torch", "numpy"])  # Install deps from PyPI
    .rsync("./my_project", "/app/my_project", contents=True)  # Local code
    .set_env_vars({"PYTHONPATH": "/app"})
)
```

### Editable Install Pattern

```python
# Full editable install of local package
image = (
    kt.images.Debian()
    .set_env_vars({
        "UV_EXTRA_INDEX_URL": "https://my-pypi.com/simple",
    })
    .run_bash("pip install uv")
    .rsync("~/gitrepos/my_lib", dest="/my_lib", contents=True)
    .run_bash('uv pip install --system -e "/my_lib[dev]"')
)
```

### Multi-Stage Setup

```python
image = (
    kt.images.Ubuntu()
    # System dependencies
    .run_bash("apt-get update && apt-get install -y build-essential cmake")
    # Python tooling
    .run_bash("pip install --upgrade pip uv")
    # ML dependencies
    .pip_install([
        "torch>=2.0",
        "torchvision",
        "torchaudio",
    ])
    # Application dependencies
    .pip_install([
        "fastapi",
        "uvicorn",
        "pydantic>=2.0",
    ])
    # Application code
    .rsync("./app", "/app", contents=True)
    .rsync("./models", "/models")
    # Environment
    .set_env_vars({
        "MODEL_PATH": "/models",
        "PYTHONPATH": "/app",
    })
)
```

---

## Internal Details

### Image Setup Step Types

Internally, each method creates an `ImageSetupStep` with a type:

| Method | Step Type |
|--------|-----------|
| `pip_install()` | `PIP_INSTALL` |
| `set_env_vars()` | `SET_ENV_VARS` |
| `run_bash()` | `CMD_RUN` |
| `rsync()` | `RSYNC` |
| `sync_package()` | `SYNC_PACKAGE` |

### Setup Execution Order

Steps execute in the order they are defined. This matters for:
- Installing `uv` before using `uv pip install`
- Setting env vars before commands that use them
- Installing deps before syncing code that imports them

### Docker Secret (Private Registries)

For private Docker registries, Kubetorch supports image pull secrets:

```python
image = kt.Image()
image.docker_secret = "my-registry-secret"  # K8s secret name
image = image.from_docker("private-registry.io/my-image:v1")
```

