# GPU Demos

GPU access on CoreWeave requires the **SUNK scheduler** (Slurm on Kubernetes).

## Demos

| Demo | Description |
|------|-------------|
| `test_sunk_cpu.py` | CPU-only SUNK test (verify setup works) |
| `gpu_sunk_kubetorch.py` | GPU via SUNK scheduler |

## How SUNK Integration Works

Kubetorch's `Compute` class supports custom pod spec via `service_template`:

```python
compute = kt.Compute(
    gpus="1",
    gpu_type="B200",
    namespace="tenant-slurm",
    launch_timeout=60,  # Shorter timeout for testing
    
    # Inject schedulerName AND terminationGracePeriodSeconds
    service_template={
        "spec": {
            "template": {
                "spec": {
                    "schedulerName": "tenant-slurm-slurm-scheduler",
                    "terminationGracePeriodSeconds": 5,  # Required by SUNK!
                }
            }
        }
    },
    
    # SUNK annotations
    annotations={
        "sunk.coreweave.com/account": "root",
        "sunk.coreweave.com/exclusive": "user",
    },
    
    # Allow scheduling on GPU nodes (for GPU workloads)
    tolerations=[
        {"key": "nvidia.com/gpu", "operator": "Exists", "effect": "NoSchedule"}
    ],
)
```

> ⚠️ **Critical:** SUNK requires `terminationGracePeriodSeconds` to be less than
> Slurm's KillWait timeout minus 5 seconds. Without this, pods will fail with:
> `termination grace period must be less than Slurm KillWait - 5s`

## Running

```bash
# Test SUNK with CPU first (verifies setup)
python demos/gpu/test_sunk_cpu.py

# GPU via SUNK (when GPUs are available)
python demos/gpu/gpu_sunk_kubetorch.py
```

## If GPUs Are Busy

If all GPUs are allocated, pods will stay `Pending` until resources free up.
Check status with:
```bash
kubectl get pods -n tenant-slurm
squeue  # via SSH to login node
```

## Reference

- [CoreWeave SUNK Docs](https://docs.coreweave.com/docs/products/sunk/run_workloads/schedule-kubernetes-pods)
