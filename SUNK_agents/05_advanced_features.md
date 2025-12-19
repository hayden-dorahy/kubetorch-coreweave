# Advanced Features

> **Source**: [Optimize Workloads](https://docs.coreweave.com/docs/products/sunk/optimize_workloads), [Topology/Block Scheduling](https://docs.coreweave.com/docs/products/sunk/optimize_workloads/topology-block-scheduling), [Use sidecar containers with SUNK](https://docs.coreweave.com/docs/products/sunk/manage_sunk/use_sidecar_containers_with_sunk), [Introduction to GPU Straggler Detection](https://docs.coreweave.com/docs/products/sunk/manage_sunk/introduction_to_gpu_straggler_detection)

## Topology-Aware Scheduling

SUNK supports Slurm's topology plugins to optimize job placement, which is critical for multi-node training on high-speed fabrics (InfiniBand/NCCL).

- **Mechanism**: The `topology.conf` file is automatically generated or managed by SUNK.
- **Goal**: Place tasks that communicate frequently on nodes that are "close" in the network topology (e.g., same rack, same IB switch) to minimize latency.
- **Configuration**: Often enabled by default in CoreWeave's environment for GPU clusters.

## GPU Affinity and Binding

For multi-GPU nodes, correct binding of processes to GPUs and their nearest NUMA (CPU) nodes is essential for performance.

- **Auto-Detection**: `slurmd` in SUNK auto-detects GRES (Generic Resources) like GPUs.
- **Task Plugin**: SUNK configures `task/cgroup` and `task/affinity`.
- **User Usage**:
  ```bash
  # Example: Bind to closest core
  srun --cpu-bind=verbose,closest ...
  ```

## MLOps Features

### Straggler Detection
SUNK integrates with node health checks to identify "stragglers" (nodes performing significantly slower than peers).

-   **Mechanism**:
    -   **Prolog**: Often includes a GPU bandwidth/latency test (e.g., `dcgmi diag`).
    -   **Runtime**: Can use a **`cache-dropper` sidecar** to manage page cache and ensure consistent memory performance.
-   **Action**: Can automatically drain a node if it fails a prolog health check or runtime metric check.

### Sidecar Containers

You can inject sidecar containers into Slurm nodes (Login or Compute) to run auxiliary services (metrics agents, log shippers, proxies).

- **Configuration**:
  ```yaml
  # values.yaml
  compute:
    nodeDefinitions:
      - name: gpu-h100
        sidecars:
          - name: my-sidecar
            image: my-sidecar:latest
  ```

### Rolling Upgrades
K8s allows for rolling upgrades of the `slurmd` DaemonSet/StatefulSet.
- **SUNK Behavior**: Smart logic to wait for jobs to finish (drain) or requeue them before upgrading a node's image, minimizing disruption to long-running training jobs.

### Multi-Tenancy
- **Partitions**: Isolate teams or workloads (e.g., `prod-partition`, `dev-partition`).
- **QOS (Quality of Service)**: Enforce priority, preemption, and resource limits per user or group.

