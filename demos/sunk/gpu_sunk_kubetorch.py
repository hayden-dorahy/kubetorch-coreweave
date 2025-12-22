"""GPU access via SUNK scheduler using Kubetorch's service_template.

Uses service_template to set schedulerName and annotations for SUNK integration.
Docs: https://docs.coreweave.com/docs/products/sunk/run_workloads/schedule-kubernetes-pods
"""

import kubetorch as kt


def check_gpu():
    """Check if GPU is available."""
    try:
        import torch

        if torch.cuda.is_available():
            return {
                "cuda_available": True,
                "device_count": torch.cuda.device_count(),
                "device_name": torch.cuda.get_device_name(0),
            }
        return {"cuda_available": False, "reason": "CUDA not available"}
    except Exception as e:
        return {"cuda_available": False, "error": str(e)}


if __name__ == "__main__":
    # SUNK scheduler name (check with: kubectl get schedulers -n tenant-slurm)
    SUNK_SCHEDULER = "tenant-slurm-slurm-scheduler"

    # Use service_template to inject schedulerName into pod spec
    service_template = {
        "spec": {
            "template": {
                "spec": {
                    "schedulerName": SUNK_SCHEDULER,
                    # SUNK requires terminationGracePeriodSeconds < Slurm KillWait - 5s
                    # If missing, pod stays Pending with "SchedulingFailed"
                    "terminationGracePeriodSeconds": 5,
                }
            }
        }
    }

    # SUNK annotations (required for proper scheduling)
    sunk_annotations = {
        "sunk.coreweave.com/account": "root",
        "sunk.coreweave.com/comment": "Kubetorch GPU test via SUNK",
        "sunk.coreweave.com/exclusive": "user",  # Allows sharing with other K8s pods
    }

    # Tolerations to allow scheduling on GPU nodes
    gpu_tolerations = [{"key": "nvidia.com/gpu", "operator": "Exists", "effect": "NoSchedule"}]

    # Note: Nodes advertise both 'nvidia.com/gpu' and 'sunk.coreweave.com/accelerator'.
    # If 'nvidia.com/gpu' stays Pending, try requesting 'sunk.coreweave.com/accelerator' instead.

    # Use NVIDIA PyTorch image with CUDA support
    image = kt.Image().from_docker("nvcr.io/nvidia/pytorch:24.08-py3")

    compute = kt.Compute(
        cpus="1",
        memory="8Gi",
        gpus="1",
        # CoreWeave uses gpu.nvidia.com/class label, not nvidia.com/gpu.product
        node_selector={"gpu.nvidia.com/class": "B200"},
        namespace="tenant-slurm",  # SUNK namespace
        launch_timeout=180,  # Longer timeout for Slurm scheduling
        annotations=sunk_annotations,
        tolerations=gpu_tolerations,
        service_template=service_template,
        image=image,
    )

    print("Requesting GPU via SUNK scheduler...")
    print(f"  Scheduler: {SUNK_SCHEDULER}")
    print("  Namespace: tenant-slurm")
    print("  GPU type: B200")

    remote_fn = kt.fn(check_gpu, name="gpu_sunk").to(compute)
    result = remote_fn()
    print(f"\nResult: {result}")
