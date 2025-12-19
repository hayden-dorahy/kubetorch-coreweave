# Reference

> **Source**: [SUNK parameter reference](https://docs.coreweave.com/docs/products/sunk/reference/sunk-parameter-reference), [Slurm images](https://docs.coreweave.com/docs/products/sunk/reference/slurm-images), [Slurm parameter reference](https://docs.coreweave.com/docs/products/sunk/reference/slurm-parameter-reference)

## SUNK Parameters (Helm Values)

This is a non-exhaustive list of key parameters available in the SUNK Helm chart.

### `global`
-   `global.clusterName`: Name of the Slurm cluster.
-   `global.persistence.home`: PVC configuration for `/home`.
-   `global.timeZone`: Cluster timezone (e.g., `America/New_York`).

### `compute`
-   `compute.nodeDefinitions`: List of compute partitions (see [Deployment](./02_deployment_and_configuration.md)).
-   `compute.commonMounts`: List of volumes to mount on all compute nodes.
-   `compute.prolog`: Global prolog script content.
-   `compute.epilog`: Global epilog script content.

### `login`
-   `login[].name`: Name of the login pool.
-   `login[].replicas`: Number of login pods.
-   `login[].service.type`: Service type (`LoadBalancer`, `ClusterIP`).
-   `login[].ssh.hostKeys`: Reference to Secret/PVC containing host keys.

### `controller`
-   `controller.replicas`: Defaults to 1 (HA handled by K8s) or 2 (Active/Passive).
-   `controller.resources`: Resource requests/limits for `slurmctld`.

## Slurm Images

CoreWeave maintains base images containing:
-   Slurm Daemons (`slurmd`, `slurmctld`, `slurmdbd`)
-   Munge
-   NVIDIA Drivers / CUDA
-   InfiniBand stack (MOFED/UCX)

**Naming Convention**:
`coreweave/slurm-compute:<sunk-version>-<cuda-version>`

**Examples**:
-   `coreweave/slurm-compute:v7.0.0-cuda12.2`
-   `coreweave/slurm-login:v7.0.0`

## Slurm Parameters (`slurm.conf`)

Many `slurm.conf` parameters can be overridden via `values.yaml` under `slurm.config`.

-   `slurm.config.SchedulerType`: `sched/backfill` (Default)
-   `slurm.config.SelectType`: `select/cons_tres` (Required for GPU tracking)
-   `slurm.config.GresTypes`: `gpu`

