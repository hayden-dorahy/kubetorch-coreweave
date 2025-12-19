# Deployment and Configuration

> **Source**: [Deploy SUNK](https://docs.coreweave.com/docs/products/sunk/deploy_sunk), [Configure Compute nodes](https://docs.coreweave.com/docs/products/sunk/deploy_sunk/configure_compute_nodes), [Configure individual Login pods](https://docs.coreweave.com/docs/products/sunk/deploy_sunk/configure_individual_login_pods), [Manage deployments with CI and GitOps](https://docs.coreweave.com/docs/products/sunk/deploy_sunk/manage_deployments_with_ci_and_gitops)

SUNK is deployed via a Helm chart. Configuration is primarily done through `values.yaml` which drives the generation of Kubernetes manifests (Deployments, StatefulSets, ConfigMaps) and Slurm configuration files (`slurm.conf`).

## Helm Chart Structure

The SUNK Helm chart typically exposes the following top-level configuration sections:

- **`controller`**: Configuration for `slurmctld` (replicas, resources, service).
- **`accounting`**: Configuration for `slurmdbd` and database connection.
- **`login`**: Configuration for login nodes (deployments, services, SSH).
- **`compute`**: The core section for defining `nodeDefinitions` (compute pools).
- **`images`**: Base image references for different components.
- **`global`**: Shared settings like timezone, cluster name, and common mounts.

## Node Definitions (`nodeDefinitions`)

The `nodeDefinitions` section in `values.yaml` is the declarative source of truth for your Slurm compute nodes. Each entry defines a "partition" or a group of identical nodes.

### Schema (Representative)

```yaml
compute:
  nodeDefinitions:
    - name: "gpu-h100"           # Name prefix for the nodes
      partition: "gpu-partition" # Slurm partition name
      replicas: 4                # Number of static nodes (pods)
      # Dynamic scaling configuration often goes here
      resources:                 # Standard K8s resource requests/limits
        limits:
          nvidia.com/gpu: 8
          memory: "1000Gi"
          cpu: "100"
        requests:
          nvidia.com/gpu: 8
          memory: "1000Gi"
          cpu: "100"
      nodeSelector:              # K8s NodeSelector to target specific hardware
        node.coreweave.cloud/class: "h100"
      tolerations:               # K8s Tolerations for taints
        - key: "nvidia.com/gpu"
          operator: "Exists"
          effect: "NoSchedule"
      image: "coreweave/slurm-compute:latest-cuda" # Custom image override
      # Optional: Sidecars, specialized mounts, etc.
```

### Key Parameters

- **`name`**: Used as the hostname prefix for the pods (e.g., `gpu-h100-0`, `gpu-h100-1`).
- **`partition`**: Maps to the Slurm partition. Multiple node definitions can join the same partition.
- **`resources`**: Critical for scheduling. Must match the physical hardware capabilities if you want 1:1 mapping (which is standard for GPU nodes).
- **`nodeSelector` / `affinity`**: Ensures the Slurm node pods land on the correct physical hardware types (e.g., guaranteeing an H100 pod lands on an H100 node).

## Login Node Configuration

You can configure multiple sets of login nodes, each with distinct settings (images, resources, services).

### Multiple Login Pools

To support different user groups (e.g., "Data Science" vs "General"), define multiple entries in the `login` list.

```yaml
login:
  - name: "general-login"
    replicas: 2
    image: "coreweave/slurm-login:latest"
    service:
      type: LoadBalancer
      annotations:
        service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    resources:
      requests:
        cpu: 2
        memory: 4Gi
      limits:
        cpu: 4
        memory: 8Gi

  - name: "ds-login"
    replicas: 1
    image: "my-registry/data-science-login:latest" # Custom image with Jupyter/Pandas
    service:
      type: LoadBalancer
```

### SSH Configuration

Login nodes are the primary entry point via SSH.
-   **Service Type**: Typically `LoadBalancer` to expose a public IP.
-   **Port**: Maps standard port 22.
-   **Host Keys**: Persisted via Persistent Volumes or Secrets to avoid warnings on pod restart.

## GitOps Management

Managing SUNK via GitOps (ArgoCD/Flux) is the recommended best practice.

-   **Repository Structure**:
    -   `base/`: The raw Helm chart reference.
    -   `overlays/prod/`: `values.yaml` specific to the production cluster.
-   **App of Apps**: Use an "App of Apps" pattern to deploy the SUNK chart alongside other dependencies (like the MySQL Operator).
-   **Secret Management**: Do **not** commit secrets (IdP tokens, DB passwords) to git. Use `ExternalSecrets` or `SealedSecrets` to inject them into the values or K8s secrets referenced by the chart.

## Base Images

CoreWeave provides optimized base images. It is recommended to extend these rather than building from scratch.

- **OS**: Typically Ubuntu-based.
- **Included Software**:
  - Slurm daemons (`slurmd`, `slurmctld`, etc.)
  - Munge
  - CUDA Toolkit (versioned tags available)
  - IB/RDMA drivers and libraries (MOFED, NCCL)
  - `pyxis` and `enroot` for containerized workload support

### Custom Image Example

```dockerfile
# Dockerfile
FROM coreweave/slurm-compute:v7.0.0-cuda12.2

# Install user requirements
RUN apt-get update && apt-get install -y \
    htop \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Add custom scripts
COPY my_prolog.sh /etc/slurm/prolog.sh
```

## Persistent Storage Configuration

Storage is usually configured via `global.persistence` or specific mount lists.

```yaml
global:
  persistence:
    home:
      enabled: true
      claimName: shared-home-pvc
      mountPath: /home
    data:
      enabled: true
      claimName: high-perf-data-pvc
      mountPath: /data
```

This ensures that `/home` is consistent across login nodes and compute nodes, which is a hard requirement for standard Slurm usage.

