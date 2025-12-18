# Distributed Training

> **Official Docs:** [Distributed Training](https://www.run.house/kubetorch/concepts/distributed)

Kubetorch makes multi-node distributed training simple. It supports **PyTorch DDP** (Distributed Data Parallel) and **Ray** clusters.

## PyTorch Distributed (DDP)

Kubetorch automatically handles:
- Creating a headless service for peer discovery
- Setting up `MASTER_ADDR` and `MASTER_PORT`
- Generating `rank` and `world_size`
- Configuring `torchrun` environment

### Basic Usage

```python
import kubetorch as kt

def train_fn():
    import torch
    import os
    
    # Kubetorch sets up these env vars for you
    rank = int(os.environ["RANK"])
    world_size = int(os.environ["WORLD_SIZE"])
    local_rank = int(os.environ["LOCAL_RANK"])
    
    # Initialize process group
    torch.distributed.init_process_group(backend="nccl")
    
    # Verify
    return f"Rank {rank}/{world_size} initialized on {os.uname().nodename}"

# Define compute for ONE worker
compute = kt.Compute(
    gpus=8,                # 8 GPUs per node
    memory="512Gi",
    image=kt.images.pytorch("24.08-py3")
)

# Enable distribution
# workers=4 means 4 nodes (total 32 GPUs)
remote_train = kt.fn(train_fn).to(compute).distribute(
    framework="pytorch",
    workers=4,
)

# Run
results = remote_train()
# Returns list of results from all ranks (or head rank)
```

### How It Works

1. **Worker 0 (Head)**: The "driver" pod created by `.to(compute)`.
2. **Workers 1..N**: Additional replicas created by `.distribute()`.
3. **Headless Service**: Created for DNS discovery (e.g. `service-name-headless`).
4. **Environment**:
   - `MASTER_ADDR`: IP of the head pod
   - `MASTER_PORT`: 29500
   - `WORLD_SIZE`: Total workers
   - `RANK`: Global rank of current pod

### Custom Launch Command

By default, Kubetorch runs your python function directly. For complex setups (e.g., `torchrun`), use `kt.App`:

```python
# Using kt.App with torchrun command
app = kt.app(
    name="ddp-training",
    cli_command="torchrun --nnodes=4 --nproc_per_node=8 train.py",
    gpus=8,
    replicas=4  # Total nodes
)
# Deploy
# kt run python my_script.py
```

---

## Ray Clusters

Kubetorch can deploy ephemeral Ray clusters for distributed workloads.

### Usage

```python
import kubetorch as kt
import ray

def run_ray_job():
    # Connect to the local Ray cluster
    ray.init(address="auto")
    
    @ray.remote(num_gpus=1)
    def gpu_task(i):
        return f"Task {i} on GPU"
        
    refs = [gpu_task.remote(i) for i in range(100)]
    return ray.get(refs)

# Define head node resources
compute = kt.Compute(
    cpus="4",
    memory="16Gi",
    image=kt.images.Ray("2.32.0-py311")
)

# Distribute as Ray cluster
remote_ray = kt.fn(run_ray_job).to(compute).distribute(
    framework="ray",
    workers=4,  # 4 worker nodes (plus 1 head node)
    worker_node_options={
        "gpus": 1,
        "cpus": "4",
        "memory": "16Gi"
    }
)

result = remote_ray()
```

### Components
- **Head Node**: Runs your function and Ray head services (GCS, Dashboard).
- **Worker Nodes**: Additional pods connected to the head.
- **KubeRay**: (Optional) Can integrate with KubeRay operator if available, or manually manages pods.

---

## Peer Discovery Utility

If you need low-level pod IP discovery (e.g. for custom distributed frameworks):

```python
from kubetorch.distributed import pod_ips

# Get all pod IPs for current service
ips = pod_ips()

# Wait for quorum
ips = pod_ips(quorum_workers=4, quorum_timeout=60)
```

---

## The `@distribute` Decorator

Use decorators for cleaner syntax:

```python
@kt.compute(gpus=8)
@kt.distribute(framework="pytorch", workers=2)
def train():
    ...
```

Deploy with `kt deploy my_script.py`.

---

## Networking Requirements

Distributed training requires pod-to-pod communication.
- **Ports**: 
  - PyTorch: 29500 (default)
  - Ray: 6379, 8265, 10001+
- **DNS**: Kubetorch creates a headless service for stable DNS resolution.
- **Network Policy**: Ensure pods in your namespace can talk to each other.

---

## Fault Tolerance

- **Restart Policy**: By default, pods restart on failure.
- **Elasticity**: Ray handles worker failures automatically.
- **PyTorch Elastic**: `torchrun` handles worker failures/restarts.

## Shared Storage for Distributed Training

Almost always required for datasets and checkpoints:

```python
vol = kt.Volume(
    name="shared-data",
    size="1Ti",
    mount_path="/data",
    access_mode="ReadWriteMany",  # Critical for multi-node
    storage_class="juicefs-sc"    # Or NFS/CephFS
)

compute = kt.Compute(
    gpus=8,
    volumes=[vol]
).distribute(framework="pytorch", workers=4)
```

