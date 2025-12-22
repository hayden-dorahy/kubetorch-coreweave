"""Verify PXS and GPU setup on SUNK scheduler.

Uses pre-built image with:
- CUDA 13.0 (B200 support)
- Python 3.11
- PyTorch 2.7.1+cu126
- PXS with Opora
"""

import kubetorch as kt


def check_pxs_gpu():
    """Verify PXS is installed and GPU works."""
    import torch

    result = {
        "cuda_available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }

    # Check PXS import
    try:
        import pxs

        result["pxs_installed"] = True
        result["pxs_location"] = pxs.__file__
    except ImportError as e:
        result["pxs_installed"] = False
        result["pxs_error"] = str(e)

    # Check Opora import
    try:
        from pxs.models.opora.pytorch.base import OporaPyTorch  # noqa

        result["opora_available"] = True
    except ImportError as e:
        result["opora_available"] = False
        result["opora_error"] = str(e)

    return result


if __name__ == "__main__":
    print("Verifying PXS + GPU setup on SUNK...")

    # Pre-built image with PXS, PyTorch, CUDA 13.0, kubetorch[server]
    # Using digest to bypass cluster cache
    image = kt.Image().from_docker(
        "ghcr.io/physicsxltd/pxs-gpu@sha256:084110e266aad4134d031a839db67f38c0da7e1aedba4c58554200fb4fdf0dae"
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
        launch_timeout=600,  # PXS install takes a while
        annotations=sunk_annotations,
        tolerations=gpu_tolerations,
        service_template=service_template,
        image=image,
    )

    print(f"  Scheduler: {SUNK_SCHEDULER}")
    print("  Namespace: tenant-slurm")
    print("  GPU: B200")
    print("  Image: ghcr.io/physicsxltd/pxs-gpu:latest")

    remote_fn = kt.fn(check_pxs_gpu, name="pxs_gpu_train").to(compute)
    result = remote_fn()

    print("\n" + "=" * 50)
    print("VERIFICATION RESULTS")
    print("=" * 50)
    for k, v in result.items():
        print(f"  {k}: {v}")
