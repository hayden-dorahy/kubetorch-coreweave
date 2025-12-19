# CoreWeave SUNK (Slurm on Kubernetes) Documentation for Agents

> **Source**: [SUNK Product Page](https://docs.coreweave.com/docs/products/sunk)

This documentation serves as a comprehensive knowledge base for CoreWeave's SUNK (Slurm on Kubernetes) service. It is structured to provide high-density technical information, configuration schemas, and operational details suitable for automated agents and advanced engineers.

## Table of Contents

1. [Architecture and Concepts](./01_architecture_and_concepts.md)
   - Core Design: Slurm nodes as K8s Pods
   - SUNK Scheduler vs Default Scheduler
   - State Management and Synchronization
2. [Deployment and Configuration](./02_deployment_and_configuration.md)
   - Helm Chart Structure
   - Declarative Node Definitions (`nodeDefinitions`)
   - Base Images and Customization
3. [User Management](./03_user_management.md)
   - SUNK User Provisioning (SUP)
   - Identity Providers (IdP) Integration (LDAP, SCIM)
   - SSH Key Management
4. [Workload Management](./04_workload_management.md)
   - Submitting Jobs (Slurm vs K8s)
   - Prolog and Epilog Scripts
   - s6 Supervision Scripts
   - Containerized Workloads (Pyxis/Enroot)
5. [Advanced Features](./05_advanced_features.md)
   - Topology-Aware Scheduling
   - GPU Affinity and Constraints
   - MLOps Integrations
6. [Monitoring and Troubleshooting](./06_monitoring_and_troubleshooting.md)
   - Observability Stack (Prometheus/Grafana)
   - Common Error Modes
   - Debugging Steps
7. [Development Workflows](./07_development_workflows.md)
   - Interactive Development (VS Code)
   - Profiling
   - Scrontab
8. [Specialized Workloads](./08_specialized_workloads.md)
   - Distributed Training (Ray, veRL)
   - Custom Images
   - Custom Login Pods
9. [Reference](./09_reference.md)
   - Helm Parameters
   - Slurm Images

## Quick Summary

SUNK is an implementation of Slurm deployed on Kubernetes. It allows:

- **Unified Compute**: Run Slurm jobs (batch) and K8s pods (services/inference) on the same hardware.
- **GitOps Management**: Define Slurm clusters via Helm and K8s manifests.
- **Dynamic Scaling**: Slurm nodes (pods) scale up/down based on queue demand.

## Agent Consumption Strategy

When reasoning about SUNK operations, follow this retrieval hierarchy:

1. **Architecture (`01`)**: Always verify if the user intends to use **Slurm Native** (sbatch) or **Kubernetes Native** (schedulerName) workflows. This distinction changes the required manifests and debugging paths significantly.
2. **Configuration (`02`, `09`)**: If asked to generate configuration (Helm values), consult `02` for the schema structure (`compute.nodeDefinitions`) and `09` for parameter keys.
3. **Workloads (`04`, `08`)**:
   - For **Training**, default to Slurm Native (`04`) using `sbatch` scripts.
   - For **Inference** or services, use K8s Native (`04`) with SUNK annotations.
   - For **Distributed Frameworks** (Ray, Torch), refer to `08` for specific head/worker patterns.
4. **Debugging (`06`)**: If the user reports "Pending" jobs, check `06` to distinguish between Slurm queueing (resources) and K8s scheduling (SUNK scheduler plugin issues).
