"""Demo: Distributed Data Parallel (DDP) Training Simulation.

Demonstrates Kubetorch's distributed training capabilities.
Since this demo runs on CPU, it simulates DDP logic (env vars, process groups)
without actual GPU training.

################
CURRENTLY BROKEN
################

"""

import os

import kubetorch as kt
import torch
import torch.distributed as dist


def train_ddp():
    """Simulate a distributed training step."""
    # Kubetorch sets these env vars automatically when .distribute() is used
    rank = int(os.environ["RANK"])
    world_size = int(os.environ["WORLD_SIZE"])
    master_addr = os.environ["MASTER_ADDR"]
    master_port = os.environ["MASTER_PORT"]

    print(f"[Rank {rank}/{world_size}] Initializing process group...")
    print(f"[Rank {rank}] Master: {master_addr}:{master_port}")

    # Initialize process group (using gloo for CPU compatibility)
    # In real GPU training, you'd use backend="nccl"
    dist.init_process_group(backend="gloo", rank=rank, world_size=world_size)

    print(f"[Rank {rank}] Process group initialized. Doing all-reduce...")

    # Create a tensor unique to this rank
    # Rank 0 -> [1.0], Rank 1 -> [2.0], etc.
    tensor = torch.tensor([float(rank + 1)])

    # All-reduce: Sum tensors from all ranks
    dist.all_reduce(tensor, op=dist.ReduceOp.SUM)

    # Expected sum for 2 workers: 1 + 2 = 3
    result = tensor.item()
    print(f"[Rank {rank}] All-reduce result: {result}")

    dist.destroy_process_group()

    return f"Rank {rank} finished. Result: {result}"


if __name__ == "__main__":
    num_workers = 2

    # Use an image with PyTorch installed
    image = kt.images.Python311().pip_install(["torch"])

    compute = kt.Compute(
        cpus="0.5",
        memory="1Gi",
        image=image,
        launch_timeout=120,  # Longer for torch install
    )

    # Enable distributed mode
    # This creates 'num_workers' pods and configures the DDP environment
    compute.distribute(
        framework="pytorch",
        workers=num_workers,
    )

    print(f"Deploying {num_workers} workers for DDP simulation...")
    remote_fn = kt.fn(train_ddp, name="advanced_ddp").to(compute)

    # In distributed mode, the function runs on all workers
    # The return value is a list of results from all ranks
    results = remote_fn()

    print("\nResults from all workers:")
    for res in results:
        print(f"  {res}")
