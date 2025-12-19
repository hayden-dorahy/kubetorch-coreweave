# Workload Management

> **Source**: [Run Workloads](https://docs.coreweave.com/docs/products/sunk/run_workloads), [Schedule Kubernetes Pods with Slurm](https://docs.coreweave.com/docs/products/sunk/run_workloads/schedule-kubernetes-pods), [Run Prolog and Epilog scripts on SUNK](https://docs.coreweave.com/docs/products/sunk/run_workloads/run-prolog-and-epilog-scripts-on-sunk), [Run custom scripts with s6](https://docs.coreweave.com/docs/products/sunk/development-on-slurm/run-scripts-with-s6)

## Submitting Jobs

SUNK supports two primary ways to run workloads:

1. **Slurm Native**: Users SSH into a login node and use `sbatch`, `srun`, `salloc`.
2. **Kubernetes Native**: Users submit K8s Pods annotated to use the SUNK scheduler.

### Slurm Native (Recommended for Training)

Standard Slurm commands work as expected.

```bash
# Example sbatch script
#!/bin/bash
#SBATCH --job-name=training
#SBATCH --partition=gpu
#SBATCH --nodes=2
#SBATCH --gres=gpu:8

srun python train.py
```

### Kubernetes Native (Scheduler Integration)

You can schedule standard K8s pods via Slurm by setting the `schedulerName` to the SUNK scheduler (e.g., `<namespace>-<release>-slurm-scheduler`). This creates a placeholder job in Slurm, and once allocated, the K8s Pod is bound to the corresponding node.

#### Pod Configuration

**Required**:

1. `spec.schedulerName`: Must match your SUNK scheduler deployment.
2. `spec.terminationGracePeriodSeconds`: Must be `< (slurm-kill-wait - 5s)`. Default `KillWait` is often 30s, so use `< 25`.
3. `resources`: Must define requests.

**Resource Constraints**:

- **Shared Resources**: CPU and Memory are shared between the `slurmd` daemon and the K8s Pod.
  - *Best Practice*: Ensure `slurmd` requests are low (e.g., 10Gi mem, 10 CPU) in `nodeDefinitions` to leave room for K8s pods, but keep limits high.
- **GPUs**: Cannot be shared simultaneously. A node runs *either* Slurm jobs *or* a K8s Pod if GPUs are requested, unless using specific exclusivity modes.

#### SUNK Annotations Reference

Use these annotations in `metadata.annotations` to control Slurm behavior:

| Annotation | Description | Example |
| :--- | :--- | :--- |
| `sunk.coreweave.com/account` | Slurm account to charge. | `my-team-account` |
| `sunk.coreweave.com/partition` | Target Slurm partition. | `gpu-h100` |
| `sunk.coreweave.com/qos` | Quality of Service. | `high-priority` |
| `sunk.coreweave.com/exclusive` | Exclusivity mode: `none` (shared), `user` (share with same user), or implied full node. | `user` |
| `sunk.coreweave.com/user-id` | Run job as this UID (must exist in Slurm). | `1001` |
| `sunk.coreweave.com/group-id` | Run job as this GID. | `1001` |
| `sunk.coreweave.com/comment` | Comment string visible in squeue. | `Inference-Pod-1` |
| `sunk.coreweave.com/timeout` | Time limit in seconds (overrides partition default). | `3600` |
| `sunk.coreweave.com/reservation` | Target a specific Slurm reservation. | `maintenance-window` |

#### GPU Exclusivity Modes

When scheduling K8s Pods on GPU nodes:

1. **Full Node (Default)**: Pod takes the whole node if it requests GPUs, preventing other Slurm jobs.
2. **`exclusive: "none"`**: Allows sharing the node with other workloads (if resources permit).
3. **`exclusive: "user"`**: Allows sharing only with other K8s pods/jobs owned by the same `user-id`.

**Example Pod Manifest**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: slurm-k8s-inference
  annotations:
    sunk.coreweave.com/account: "production"
    sunk.coreweave.com/exclusive: "user"
    sunk.coreweave.com/user-id: "1001"
spec:
  schedulerName: tenant-slurm-scheduler
  terminationGracePeriodSeconds: 10
  containers:
    - name: model-server
      image: vllm/vllm-openai:latest
      resources:
        requests:
          nvidia.com/gpu: 1
          cpu: 16
          memory: 64Gi
        limits:
          nvidia.com/gpu: 1
          cpu: 16
          memory: 64Gi
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: gpu.nvidia.com/class
                operator: In
                values: ["H100"]
```

## Scripting and Hooks

SUNK provides powerful hooks to customize node behavior and job lifecycle.

### Prolog and Epilog Scripts

These run on the compute nodes before and after jobs.
- **Prolog**: Runs as `root`. Used to prepare the environment (e.g., check GPU health, mount volumes, clear caches).
- **Epilog**: Runs as `root`. Used to cleanup (e.g., kill stray processes, unmount).

**Configuration in Helm**:
Usually defined as multi-line strings in `values.yaml` or loaded from ConfigMaps.

```yaml
# Conceptual values.yaml snippet
slurm:
  prolog: |
    #!/bin/bash
    echo "Running Prolog"
    # Health check example
    nvidia-smi > /dev/null 2>&1
    if [ $? -ne 0 ]; then
      echo "GPU Check Failed"
      exit 1 # Drains the node
    fi
```

### s6 Supervision Scripts

SUNK uses `s6` for process supervision within the `slurmd` container. You can inject custom services or "oneshot" scripts that run when the pod starts.

- **Location**: `/etc/s6/` (inside the container image) or injected via ConfigMaps.
- **Use Cases**:
    - Starting a sidecar daemon (e.g., a monitoring agent).
    - performing complex initialization that must happen before `slurmd` starts.

## Containerized Workloads (Pyxis + Enroot)

Modern AI training on Slurm uses containers, not bare-metal installs. SUNK typically enables **Pyxis** (Slurm plugin) and **Enroot** (Container runtime) by default.

**Usage**:
```bash
srun --container-image=pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime \
     --container-mounts=/data:/data \
     python train.py
```

- **Efficiency**: Enroot uses squashfs for fast startup.
- **Isolation**: Clean environment per job.

