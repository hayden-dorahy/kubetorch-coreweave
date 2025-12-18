# GPU Demos

⚠️ **GPU access requires SUNK scheduler** - these demos may not work until
the cluster is configured for Kubernetes GPU scheduling via SUNK.

| Demo | Description |
|------|-------------|
| `gpu_sunk_scheduler.py` | Kubetorch with SUNK scheduler (WIP) |
| `gpu_sunk_raw.yaml` | Raw K8s manifest for SUNK GPU scheduling |

## Current Status

GPUs on this cluster are reserved by SUNK (Slurm). To access them from
Kubernetes pods, you need to use the SUNK scheduler.

See: [CoreWeave SUNK Docs](https://docs.coreweave.com/docs/products/sunk/run_workloads/schedule-kubernetes-pods)

## Running Raw K8s Test

```bash
# Apply the raw manifest (uses SUNK scheduler)
kubectl apply -f demos/gpu/gpu_sunk_raw.yaml

# Watch pod status
kubectl get pod gpu-sunk-test -n tenant-slurm -w

# Check logs
kubectl logs gpu-sunk-test -n tenant-slurm

# Clean up
kubectl delete pod gpu-sunk-test -n tenant-slurm
```

## Kubetorch Limitation

Kubetorch currently doesn't support setting `schedulerName` directly.
Options:
1. Use raw K8s manifests for GPU workloads
2. Use Slurm directly for GPU jobs
3. Request feature from Kubetorch maintainers

