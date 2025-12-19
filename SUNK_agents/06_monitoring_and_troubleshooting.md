# Monitoring and Troubleshooting

> **Source**: [Monitor SUNK](https://docs.coreweave.com/docs/products/sunk/manage_sunk/observability)

## Observability Stack

SUNK is designed to be fully observable using standard cloud-native tools.

- **Prometheus**: Scrapes metrics from `slurmctld`, `slurmdbd`, and `slurmd`.
- **Grafana**: Visualizes the metrics. CoreWeave provides pre-built dashboards.
- **Logs**: Aggregated via standard K8s logging (e.g., Fluentbit -> Loki/Elasticsearch).

### Key Metrics to Watch

- `slurm_job_state`: Number of jobs in Pending, Running, Failed, Completed.
- `slurm_node_state`: Number of nodes in Idle, Allocated, Down, Drained.
- `slurm_scheduler_queue_size`: Backlog of jobs.
- `hardware_gpu_utilization`: From DCGM/NVML exporters on the nodes.

## Common Issues & Debugging

### 1. Node Stuck in `drain` or `down`
- **Cause**: Failed Prolog script, K8s pod failure, or explicit admin action.
- **Debug**:
  - Check Slurm reason: `sinfo -R`
  - Check K8s Pod status: `kubectl get pods -l app=slurmd`
  - Check Pod logs: `kubectl logs <pod-name>`

### 2. Jobs Stuck in `Pending` (Resources)
- **Cause**: Requested resources (GPUs/CPUs) not available or constraints not met.
- **Debug**:
  - `squeue -j <jobid> --start` (Estimate start time)
  - Check partition limits: `scontrol show partition`

### 3. K8s Pods not Scheduling (SUNK Scheduler)
- **Cause**: SUNK Scheduler plugin not running or misconfigured.
- **Debug**:
  - Check scheduler logs: `kubectl logs -n sunk -l app=sunk-scheduler`
  - Ensure Pod annotation `schedulerName` matches the deployed scheduler name.

### 4. User/Group Sync Issues (SUP)
- **Cause**: IdP connection failure or mapping error.
- **Debug**:
  - Check SUP controller logs: `kubectl logs -l app=sunk-user-provisioning`
  - Verify user on login node: `id <username>`

## Accessing Logs

Since `slurmd` runs in a pod, you use `kubectl` to access logs, not `/var/log/slurm` on a host.

```bash
# Get logs for a specific compute node
kubectl logs slurm-compute-gpu-h100-0 -n sunk-namespace

# Get logs for the controller
kubectl logs -l app=slurmctld -n sunk-namespace
```

