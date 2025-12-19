# Architecture and Concepts

> **Source**: [About SUNK](https://docs.coreweave.com/docs/products/sunk), [How SUNK works](https://docs.coreweave.com/docs/products/sunk#how-sunk-works-with-kubernetes)

## Core Design

SUNK allows Slurm to run natively on Kubernetes by mapping Slurm concepts to Kubernetes primitives.

- **Slurm Nodes = Kubernetes Pods**: Each compute node in the Slurm cluster is a Kubernetes Pod running the `slurmd` daemon.
- **Slurm Controller = Kubernetes Pod**: The `slurmctld` runs as a highly available deployment in Kubernetes.
- **Database = StatefulSet/Operator**: Slurm accounting (slurmdbd) is backed by MySQL, often managed via the MOCO MySQL Operator.

### Comparison: Traditional vs SUNK

| Feature | Traditional Slurm | SUNK (Slurm on Kubernetes) |
| :--- | :--- | :--- |
| **Compute Units** | Bare Metal or VMs | K8s Pods (Containerized) |
| **Scaling** | Slow (minutes/hours) | Fast (seconds/minutes) |
| **Image Mgmt** | Disk Images / PXE | OCI Container Images |
| **HA** | Complex (Corosync/Pacemaker) | Native K8s (ReplicaSets, Probes) |
| **Scheduler** | Slurm only | Dual-Head (Slurm + K8s via Plugin) |

## The SUNK Scheduler

SUNK introduces a custom Kubernetes Scheduler plugin. This is critical for the "unified" cluster concept.

1. **Directionality**:
   - **K8s -> Slurm**: You can schedule standard K8s Pods using the Slurm scheduler logic (preemption, priority, fair-share).
   - **Slurm -> K8s**: Slurm jobs launch pods (Slurm nodes) which are scheduled by K8s on actual hardware.

2. **Synchronization**:
   - A `syncer` component ensures state consistency.
   - Events in Slurm (e.g., node drain) propagate to K8s.
   - Events in K8s (e.g., node failure) propagate to Slurm.

## Networking and Storage

- **Networking**: Uses standard K8s CNI. Slurm communication happens over the pod network.
- **Interconnect**: For high-performance workloads (HPC/AI), SUNK supports passing through InfiniBand (IB) interfaces to the `slurmd` pods.
- **Storage**:
   - **Shared Filesystem**: Typically assumes a shared filesystem (like Weka or Ceph) mounted at `/home` or `/data` across all login and compute pods.
   - **Persistent Volumes**: Utilizes K8s PV/PVCs for persistent state.

## Components

- **`slurmctld`**: The central controller.
- **`slurmdbd`**: Database daemon for accounting.
- **`slurmd`**: The compute node daemon (runs in compute pods).
- **`login` nodes**: Pods accessible via SSH for users to submit jobs (`sbatch`, `srun`).
- **`syncer`**: Custom component synchronizing state between Slurm and K8s.
- **`munge`**: Authentication service, shared key via K8s Secret.

