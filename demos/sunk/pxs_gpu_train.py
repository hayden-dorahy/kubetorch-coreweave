"""Train a PXS Opora model on GPU using SUNK scheduler.

Uses pre-built image with:
- CUDA 13.0 (B200 support)
- Python 3.11
- PyTorch 2.7.1+cu128
- PXS with Opora
"""

import kubetorch as kt


def train_opora_gpu():
    """Train a simple Opora MLP model on GPU."""
    import time
    import traceback

    import torch
    from pxs.models.opora.pytorch.base import OporaPyTorch
    from pxs.models.opora.pytorch.config.config import OporaPyTorchConfig

    # Check GPU
    if not torch.cuda.is_available():
        return {"error": "CUDA not available!", "device_count": 0}

    device = torch.device("cuda")
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

    # Create model
    try:
        model = OporaPyTorch(OporaPyTorchConfig(**config))
        print(f"Model type: {type(model)}")

        # Attempt to move to GPU
        if hasattr(model, "cuda"):
            try:
                model.cuda()
                print("Moved to GPU via .cuda()")
            except Exception as e:
                print(f".cuda() failed: {e}")

        # If model is not on GPU yet, check parameters
        is_on_gpu = False
        try:
            param = next(model.parameters())
            is_on_gpu = param.is_cuda
            print(f"Model parameters on GPU: {is_on_gpu}")
        except:
            print("Could not check model parameters")

        try:
            # model.train() expects train_data in PXS, so we skip it or call pytorch's base
            # torch.nn.Module.train(model, True)
            pass
        except Exception:
            pass

    except Exception as e:
        return {"error": f"Model setup failed: {e}", "traceback": traceback.format_exc()}

    # Create optimizer
    try:
        # Check if model has parameters()
        if hasattr(model, "parameters"):
            params = model.parameters()
        elif hasattr(model, "model") and hasattr(model.model, "parameters"):
            params = model.model.parameters()
            print("Using model.model.parameters()")
        elif hasattr(model, "net") and hasattr(model.net, "parameters"):
            params = model.net.parameters()
            print("Using model.net.parameters()")
        elif hasattr(model, "_model") and hasattr(model._model, "parameters"):
            params = model._model.parameters()
            print("Using model._model.parameters()")
        else:
            return {"error": f"Cannot find parameters in {type(model)}. Attributes: {dir(model)}"}

        optimizer = torch.optim.Adam(params, lr=0.01)
        loss_fn = torch.nn.MSELoss()
    except Exception as e:
        return {"error": f"Optimizer creation failed: {e}"}

    # Dummy training loop
    n_steps = 100
    batch_size = 32

    print("Starting training...")
    start_time = time.time()

    losses = []

    try:
        for i in range(n_steps):
            # Generate dummy batch on GPU
            points = torch.randn(batch_size, 3, device=device)
            targets = torch.randn(batch_size, 1, device=device)

            # Opora forward() expects 'x' as the input key (see model_input_names in base.py)
            inputs = {"x": points}

            optimizer.zero_grad()

            # Forward pass - use internal _model which is the actual Opora nn.Module
            outputs = model._model(inputs)

            # If model returns dict (common in PXS), extract target.
            # If tensor, use directly.
            if isinstance(outputs, dict):
                pred = outputs.get(
                    "target", list(outputs.values())[0]
                )  # Try 'target' or first value
            else:
                pred = outputs

            loss = loss_fn(pred, targets)
            loss.backward()
            optimizer.step()

            losses.append(loss.item())

            if i % 10 == 0:
                print(f"Step {i}: Loss = {loss.item():.4f}")

    except Exception as e:
        return {"error": f"Training loop failed: {e}", "traceback": traceback.format_exc()}

    end_time = time.time()

    return {
        "device": device_name,
        "steps": n_steps,
        "final_loss": losses[-1] if losses else None,
        "avg_loss": sum(losses) / len(losses) if losses else None,
        "duration": end_time - start_time,
        "pxs_version": getattr(model, "__module__", "unknown"),
    }


if __name__ == "__main__":
    print("Training PXS Opora model on GPU via SUNK...")

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

    remote_fn = kt.fn(train_opora_gpu, name="pxs_gpu_train").to(compute)
    result = remote_fn()

    print("\n" + "=" * 50)
    print("TRAINING RESULTS")
    print("=" * 50)
    if isinstance(result, dict):
        for k, v in result.items():
            print(f"  {k}: {v}")
    else:
        print(result)
