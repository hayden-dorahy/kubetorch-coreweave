"""Test GPU access via SUNK scheduler on CoreWeave.

Uses the SUNK scheduler to allocate GPUs through Slurm, as documented at:
https://docs.coreweave.com/docs/products/sunk/run_workloads/schedule-kubernetes-pods
"""


def check_gpu():
    """Check GPU availability and run a simple PyTorch operation."""
    import torch
    
    if torch.cuda.is_available():
        num_gpus = torch.cuda.device_count()
        gpu_name = torch.cuda.get_device_name(0)
        
        # Simple GPU operation
        x = torch.randn(1000, 1000, device='cuda')
        y = torch.matmul(x, x)
        
        return f"GPU access successful!\n  GPUs: {num_gpus}x {gpu_name}\n  Test matmul shape: {y.shape}"
    else:
        return "No GPU available"


if __name__ == "__main__":
    import kubetorch as kt

    print("Testing GPU access via SUNK scheduler...")

    # SUNK scheduler configuration
    # See: https://docs.coreweave.com/docs/products/sunk/run_workloads/schedule-kubernetes-pods
    SUNK_SCHEDULER = "tenant-slurm-slurm-scheduler"
    
    compute = kt.Compute(
        cpus="8",
        memory="128Gi",
        gpus=1,
        namespace="tenant-slurm",
        scheduler_name=SUNK_SCHEDULER,
        # SUNK annotations for GPU scheduling
        annotations={
            "sunk.coreweave.com/exclusive": "user",  # Allow GPU sharing between K8s pods
            "sunk.coreweave.com/account": "root",
        },
    )
    
    print(f"Using scheduler: {SUNK_SCHEDULER}")
    print(f"Requesting 1 GPU in namespace tenant-slurm")
    
    remote_fn = kt.fn(check_gpu, name="gpu").to(compute)
    result = remote_fn()
    print(result)

