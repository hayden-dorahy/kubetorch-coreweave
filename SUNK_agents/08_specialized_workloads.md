# Specialized Workloads

> **Source**: [Tutorials](https://docs.coreweave.com/docs/products/sunk/tutorials), [Run Ray on SUNK](https://docs.coreweave.com/docs/products/sunk/tutorials/run-ray-on-sunk), [Run torchforge on SUNK](https://docs.coreweave.com/docs/products/sunk/tutorials/run-torchforge-on-sunk), [Create custom images](https://docs.coreweave.com/docs/products/sunk/development-on-slurm/custom-images)

## Distributed Training Frameworks

SUNK excels at running distributed training frameworks like Ray, TorchDistributed, and specialized RL libraries.

### Ray on SUNK

Running Ray on Slurm involves setting up a "head" node and "worker" nodes within a Slurm allocation.

**Pattern**:
1.  **Submit a single Slurm job** requesting $N$ nodes.
2.  **Head Node**: The first node in the allocation (`SLURM_NODELIST`[0]) starts `ray start --head`.
3.  **Worker Nodes**: The other nodes (`srun` --overlap) start `ray start --address <head-ip>`.

**Example Script**:
```bash
#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:8

# Get the head node IP
head_node=$(hostname)
head_node_ip=$(hostname --ip-address)
port=6379

# Start Head
ray start --head --node-ip-address=$head_node_ip --port=$port --num-gpus=8 --block &

# Wait for head to start
sleep 10

# Start Workers
srun --nodes=3 --ntasks=3 --exclude=$head_node \
     ray start --address $head_node_ip:$port --num-gpus=8 --block &

# Submit the actual python script to the Ray cluster
python my_ray_script.py
```

### veRL (Volcano Engine RL) / TorchForge

Reinforcement Learning workloads (like those using `veRL` or `torchforge`) often require massive scale and specialized networking (InfiniBand).

-   **InfiniBand Support**: CoreWeave SUNK nodes are typically pre-configured with IB passthrough.
-   **MPI / NCCL**: These frameworks rely on NCCL for inter-node communication.
-   **Environment Variables**:
    Ensure these are set in your sbatch script or image:
    ```bash
    export NCCL_DEBUG=INFO
    export NCCL_IB_DISABLE=0
    export NCCL_SOCKET_IFNAME=eth0 # Or ib0, depending on CNI setup
    ```
    *Note: In some SUNK configurations using "Secondary Networks" for IB, the interface might be explicitly named (e.g., `net1`).*

## Custom Images

While base images are provided, specialized workloads often require custom dependencies.

1.  **Build**: Use a standard Dockerfile inheriting from `coreweave/slurm-compute`.
    ```dockerfile
    FROM coreweave/slurm-compute:v7.0.0-cuda12.2
    RUN pip install ray[default] torch
    ```
2.  **Push**: Push to a registry accessible by the cluster (e.g., Docker Hub, GCR, or an internal harbor).
3.  **Usage**:
    -   **Global Override**: Update `values.yaml` `compute.nodeDefinitions[].image`.
    -   **Per-Job Override**: Use `--container-image` (if Pyxis is configured to allow arbitrary images, which is common).
    ```bash
    sbatch --container-image=my-registry/my-ray-image:latest ...
    ```

## Custom Login Pods

Sometimes different teams need different tools on their login nodes (e.g., one team needs Java, another needs extensive Python data tools).

**Configuration**:
In `values.yaml`, you can define multiple login deployments.

```yaml
login:
  - name: "data-science"
    replicas: 2
    image: "my-registry/sunk-login-ds:latest"
    service:
      type: LoadBalancer
  - name: "core-dev"
    replicas: 1
    image: "coreweave/sunk-login:latest"
```
*Note: This specific multi-login-deployment syntax depends on the exact version of the SUNK Helm chart, but the concept of deploying separate login pools is supported.*

