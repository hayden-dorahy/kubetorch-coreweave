# Volumes

> **Official Docs:** [Supporting Primitives](https://www.run.house/kubetorch/concepts/supporting-primitives)
> **Source:** `kubetorch.resources.volumes.volume.Volume`

Kubetorch `Volume` provides persistent storage for services via Kubernetes PersistentVolumeClaims (PVCs).

## Overview

Volumes persist data beyond pod lifecycle:
- Training checkpoints
- Model weights
- Datasets
- Shared caches (uv, pip, HuggingFace)

---

## Constructor

```python
kt.Volume(
    name: str,                    # Volume/PVC name
    size: str,                    # Size (e.g., "10Gi")
    mount_path: str,              # Where to mount in container
    storage_class: str = None,    # K8s storage class
    access_mode: str = None,      # ReadWriteOnce, ReadWriteMany, etc.
    namespace: str = None,        # K8s namespace
)
```

### Parameters

#### `name`
Name for the PVC. Must be unique within namespace.

#### `size`
Storage size. Same format as memory: `"1Gi"`, `"100Mi"`, `"1Ti"`.

#### `mount_path`
Absolute path where volume mounts in container. Must start with `/`.

```python
kt.Volume(name="data", size="10Gi", mount_path="/data")
kt.Volume(name="models", size="50Gi", mount_path="/mnt/models")
```

#### `storage_class`
Kubernetes StorageClass name. If not specified:
- For `ReadWriteMany`: Looks for RWX-capable classes (JuiceFS, NFS, CephFS)
- For others: Uses cluster default storage class

```python
kt.Volume(
    name="shared",
    size="100Gi",
    mount_path="/shared",
    storage_class="juicefs-sc-shared"  # RWX-capable
)
```

#### `access_mode`
PVC access mode:
- `"ReadWriteOnce"` (RWO) - Single node read/write
- `"ReadWriteMany"` (RWX) - Multi-node read/write (requires special storage)
- `"ReadOnlyMany"` (ROX) - Multi-node read-only

Default: `"ReadWriteMany"`

#### `namespace`
K8s namespace. Defaults to config namespace.

---

## Class Methods

### `Volume.from_name()`

Load an existing PVC:

```python
vol = kt.Volume.from_name(
    name="existing-pvc",
    namespace="my-namespace",     # Optional
    mount_path="/data"            # Optional override
)
```

If `mount_path` not provided, uses the annotation from PVC (if set).

---

## Methods

### `create()`

Create the PVC if it doesn't exist:

```python
vol = kt.Volume(name="my-data", size="10Gi", mount_path="/data")
pvc = vol.create()  # Returns V1PersistentVolumeClaim
```

**Note:** Kubetorch automatically creates volumes when used with Compute.

### `delete()`

Delete the PVC:

```python
vol.delete()
```

### `exists()`

Check if PVC exists:

```python
if vol.exists():
    print("Volume ready")
```

### `ssh(image="alpine:latest")`

Launch interactive debug shell with volume mounted:

```python
vol = kt.Volume.from_name("my-data", mount_path="/data")
vol.ssh()  # Opens shell with /data mounted
```

Use for:
- Inspecting volume contents
- Manual data management
- Debugging storage issues

### `config()`

Get configuration dict:

```python
vol.config()
# {
#     "name": "my-data",
#     "size": "10Gi",
#     "access_mode": "ReadWriteMany",
#     "mount_path": "/data",
#     "storage_class": "standard",
#     "namespace": "default"
# }
```

---

## Properties

```python
vol.name           # Volume name
vol.pvc_name       # PVC name (same as name)
vol.size           # Storage size
vol.access_mode    # Access mode
vol.mount_path     # Mount path
vol.storage_class  # Storage class
vol.namespace      # Namespace
```

---

## Using with Compute

### Create New Volume

```python
compute = kt.Compute(
    cpus="1",
    volumes=[
        kt.Volume(name="training-data", size="100Gi", mount_path="/data"),
        kt.Volume(name="checkpoints", size="50Gi", mount_path="/checkpoints"),
    ]
)
```

### Use Existing Volume

```python
compute = kt.Compute(
    cpus="1",
    volumes=[
        kt.Volume.from_name("shared-data", namespace="ml-team", mount_path="/mnt/shared"),
    ]
)
```

### String Reference to Existing PVC

```python
# Simple string reference (mount path from annotation)
compute = kt.Compute(
    cpus="1",
    volumes=["existing-pvc-name"]
)
```

### Mixed

```python
compute = kt.Compute(
    cpus="2",
    memory="8Gi",
    volumes=[
        kt.Volume(name="scratch", size="100Gi", mount_path="/scratch"),
        kt.Volume.from_name("datasets", mount_path="/datasets"),
        "model-cache",  # Existing PVC
    ]
)
```

---

## Examples

### Training with Checkpoints

```python
def train(epochs: int):
    import os
    checkpoint_dir = "/checkpoints"
    
    # Resume from checkpoint if exists
    latest = os.path.join(checkpoint_dir, "latest.pt")
    if os.path.exists(latest):
        model.load_state_dict(torch.load(latest))
    
    for epoch in range(epochs):
        # Train...
        torch.save(model.state_dict(), latest)
    
    return "Training complete"

checkpoint_vol = kt.Volume(
    name="training-checkpoints",
    size="50Gi",
    mount_path="/checkpoints"
)

compute = kt.Compute(
    gpus=1,
    memory="32Gi",
    volumes=[checkpoint_vol]
)

train_fn = kt.fn(train).to(compute)
train_fn(epochs=100)
```

### Shared Cache

```python
cache_vol = kt.Volume(
    name="kt-global-cache",
    size="100Gi",
    mount_path="/cache",
    access_mode="ReadWriteMany"  # Shared across pods
)

compute = kt.Compute(
    cpus="1",
    env_vars={
        "UV_CACHE_DIR": "/cache/uv",
        "HF_HOME": "/cache/huggingface",
        "PIP_CACHE_DIR": "/cache/pip",
    },
    volumes=[cache_vol]
)
```

### Dataset Volume

```python
# Load pre-existing dataset volume
dataset_vol = kt.Volume.from_name(
    "imagenet-dataset",
    namespace="ml-datasets",
    mount_path="/datasets/imagenet"
)

compute = kt.Compute(
    gpus=8,
    memory="256Gi",
    volumes=[dataset_vol],
    namespace="ml-datasets"  # Must match PVC namespace or have cross-namespace access
)
```

### Debug Volume Contents

```python
vol = kt.Volume.from_name("my-data", mount_path="/data")

# Open shell
vol.ssh()

# In shell:
# ls -la /data
# du -sh /data/*
# cat /data/logs/training.log
```

### Different Images for SSH

```python
# Use Ubuntu for more tools
vol.ssh(image="ubuntu:22.04")

# Use Python image
vol.ssh(image="python:3.12-slim")
```

---

## Storage Classes

### Common Storage Classes

| Class | Type | RWX | Notes |
|-------|------|-----|-------|
| `standard` | Cloud default | No | GKE, EKS, AKS |
| `gp2`, `gp3` | AWS EBS | No | EKS |
| `pd-standard`, `pd-ssd` | GCE PD | No | GKE |
| `juicefs-sc` | JuiceFS | Yes | Shared storage |
| `nfs-client` | NFS | Yes | NFS provisioner |
| `cephfs` | CephFS | Yes | Ceph storage |

### RWX for Distributed Training

For multi-node access, use RWX-capable storage:

```python
vol = kt.Volume(
    name="distributed-data",
    size="1Ti",
    mount_path="/data",
    storage_class="juicefs-sc-shared",
    access_mode="ReadWriteMany"
)

compute = kt.Compute(
    gpus=8,
    volumes=[vol]
).distribute(framework="pytorch", workers=4)
```

---

## Cross-Namespace Access

PVCs are namespace-scoped. To access from another namespace:

1. **Deploy to same namespace as PVC:**
   ```python
   vol = kt.Volume.from_name("data", namespace="data-ns", mount_path="/data")
   compute = kt.Compute(cpus="1", namespace="data-ns", volumes=[vol])
   ```

2. **Use cluster-wide storage (if available):**
   Some storage backends support cross-namespace access via PV/PVC binding.

---

## Best Practices

1. **Use meaningful names:** `training-checkpoints-v1`, not `vol1`
2. **Size appropriately:** Oversizing wastes resources, undersizing causes failures
3. **Use RWX for shared access:** Required for distributed training
4. **Cache directories:** Mount shared caches for faster startup
5. **Clean up:** Delete unused volumes to save costs
6. **Namespace consistency:** Keep PVC and workloads in same namespace

