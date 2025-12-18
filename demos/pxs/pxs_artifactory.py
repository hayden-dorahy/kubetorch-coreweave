"""Minimal pxs Opora test on CPU with Kubetorch."""
import os
import tomllib
from pathlib import Path

import kubetorch as kt


def load_artifactory_creds():
    """Load artifactory credentials from uv's credential store."""
    creds_file = Path.home() / ".local/share/uv/credentials/credentials.toml"
    with open(creds_file, "rb") as f:
        data = tomllib.load(f)
    
    for cred in data.get("credential", []):
        if "physicsx.jfrog.io" in cred.get("service", ""):
            return cred["username"], cred["password"]
    
    raise ValueError("No PhysicsX artifactory credentials found in uv credentials")


def run_opora_mlp():
    """Run a simple Opora MLP model on CPU."""
    import numpy as np
    from pxs.models.opora.pytorch.base import OporaPyTorch
    from pxs.models.opora.pytorch.config.config import OporaPyTorchConfig

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
    model = OporaPyTorch(OporaPyTorchConfig(**config))
    model.is_trained = True  # Skip training check for inference

    # Dummy data: 100 points with 3D coordinates
    n_points = 100
    sample = {
        "points": np.random.normal(size=(n_points, 3)).astype(np.float32),
        "target": np.random.normal(size=(n_points, 1)).astype(np.float32),
    }

    # Run forward pass
    output = model.predict_one(data=sample)

    return f"Opora MLP output shape: {output['target'].shape}, first 3 values: {output['target'][:3].flatten()}"


if __name__ == "__main__":
    print("Running pxs Opora test on Kubetorch (CPU)...")

    # Load artifactory credentials from uv
    username, password = load_artifactory_creds()

    # Create image: use Debian base to avoid pydantic conflicts, install everything fresh
    image = (
        kt.images.Debian()
        .set_env_vars({
            "UV_EXTRA_INDEX_URL": f"https://{username}:{password}@physicsx.jfrog.io/artifactory/api/pypi/px-pypi-release/simple",
            "UV_PRERELEASE": "allow",
            "UV_INDEX_STRATEGY": "unsafe-best-match",
        })
        .run_bash("pip install uv")
        .run_bash("uv pip install --system 'physicsx.pxs[opora]==0.29.0-dev.11'")
    )

    compute = kt.Compute(cpus="0.5", memory="4Gi", image=image)
    
    # Run the Opora MLP test (separate pod - different image from editable demos)
    remote_fn = kt.fn(run_opora_mlp, name="pxs_artifactory").to(compute)
    result = remote_fn()
    print(result)

