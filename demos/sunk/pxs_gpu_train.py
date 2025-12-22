"""Run a PXS Opora model on GPU using SUNK scheduler.

Uses pre-built image with:
- CUDA 13.0 (B200 support)
- Python 3.11
- PyTorch 2.7.1+cu128
- PXS with Opora
"""

import kubetorch as kt


def run_opora_gpu():
    """Run a simple Opora MLP model on GPU (same pattern as pxs_artifactory.py)."""
    import numpy as np
    import torch
    from pxs.models.opora.pytorch.base import OporaPyTorch
    from pxs.models.opora.pytorch.config.config import OporaPyTorchConfig

    # Check GPU
    if not torch.cuda.is_available():
        return {"error": "CUDA not available!", "device_count": 0}

    device_name = torch.cuda.get_device_name(0)
    print(f"Using device: {device_name}")

    # Simple config: MLP that maps 3D points -> 1D target
    config = {
        "features": ["points"],
        "target": "target",
        "opora": {
            "architecture": "default",
            "blocks": [
                {
                    "block_type": "MLP",
                    "in_channels": 3,
                    "out_channels": 64,
                    "hidden_channels": [32],
                },
                {
                    "block_type": "MLP",
                    "in_channels": 64,
                    "out_channels": 1,
                    "hidden_channels": [],
                },
            ],
        },
    }

    # Create model on GPU (same as pxs_artifactory.py but with device="cuda")
    model = OporaPyTorch(OporaPyTorchConfig(**config), device="cuda")
    model.is_trained = True  # Skip training check for inference

    # Dummy data: 100 points with 3D coordinates (numpy, like pxs_artifactory.py)
    n_points = 100
    sample = {
        "points": np.random.normal(size=(n_points, 3)).astype(np.float32),
        "target": np.random.normal(size=(n_points, 1)).astype(np.float32),
    }

    # Run forward pass (same API as pxs_artifactory.py)
    output = model.predict_one(data=sample)

    return {
        "device": device_name,
        "output_shape": str(output["target"].shape),
        "first_3_values": str(output["target"][:3].flatten()),
        "success": True,
    }


if __name__ == "__main__":
    print("Running PXS Opora model on GPU via SUNK...")

    # Pre-built image with PXS, PyTorch, CUDA 13.0, kubetorch[server]
    # Use digest to force fresh pull (bypasses cached :latest)
    # This digest corresponds to the image we just pushed with kubetorch included
    image = kt.Image().from_docker(
        "ghcr.io/physicsxltd/pxs-gpu@sha256:6ab9fa3573ed0c406c0a2229d557d2ebffccf84d9aa975701fe0da4962bc99ec"
    )

    # SUNK scheduler config
    SUNK_SCHEDULER = "tenant-slurm-slurm-scheduler"

    service_template = {
        "spec": {
            "template": {
                "spec": {
                    "schedulerName": SUNK_SCHEDULER,
                    "terminationGracePeriodSeconds": 5,
                    "imagePullSecrets": [{"name": "ghcr-secret"}],  # For private registry
                }
            }
        }
    }

    sunk_annotations = {
        "sunk.coreweave.com/account": "root",
        "sunk.coreweave.com/comment": "PXS GPU training via Kubetorch",
        "sunk.coreweave.com/exclusive": "user",
    }

    gpu_tolerations = [{"key": "nvidia.com/gpu", "operator": "Exists", "effect": "NoSchedule"}]

    compute = kt.Compute(
        cpus="16",
        memory="128Gi",  # SUNK requires memory request
        gpus="1",
        node_selector={"gpu.nvidia.com/class": "B200"},
        namespace="tenant-slurm",
        launch_timeout=600,
        annotations=sunk_annotations,
        tolerations=gpu_tolerations,
        service_template=service_template,
        image=image,
    )

    print(f"  Scheduler: {SUNK_SCHEDULER}")
    print("  Namespace: tenant-slurm")
    print("  GPU: B200")
    print("  Image: ghcr.io/physicsxltd/pxs-gpu:latest")

    remote_fn = kt.fn(run_opora_gpu, name="pxs_gpu_train").to(compute)
    result = remote_fn()

    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    if isinstance(result, dict):
        for k, v in result.items():
            print(f"  {k}: {v}")
    else:
        print(result)
