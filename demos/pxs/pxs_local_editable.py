"""Minimal pxs Opora test on CPU with Kubetorch - editable install from local source."""

from pathlib import Path

import kubetorch as kt
from utils import load_artifactory_creds


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

    # Show which pxs we're using
    import pxs

    return f"pxs location: {pxs.__file__}\nOutput shape: {output['target'].shape}, first 3: {output['target'][:3].flatten()}"


if __name__ == "__main__":
    print("Running pxs editable install test on Kubetorch (CPU)...")

    # Load artifactory creds for dependencies
    username, password = load_artifactory_creds()
    index_url = f"https://{username}:{password}@physicsx.jfrog.io/artifactory/api/pypi/px-pypi-release/simple"

    # Sync whole pxs repo (needs pyproject.toml for install)
    PXS_PATH = Path("~/gitrepos/product/libraries/pxs").expanduser()
    PXS_DEST = "/pxs_local"

    image = (
        kt.images.Debian()
        .set_env_vars(
            {
                "UV_EXTRA_INDEX_URL": index_url,  # Still needed for pxs dependencies
                "UV_PRERELEASE": "allow",
                "UV_INDEX_STRATEGY": "unsafe-best-match",
            }
        )
        # Sync the whole pxs repo (with pyproject.toml) - contents=True puts files directly in dest
        .rsync(source=str(PXS_PATH), dest=PXS_DEST, contents=True)
        # Editable install from synced source
        .pip_install([f"{PXS_DEST}[opora]"])
    )

    compute = kt.Compute(
        cpus="2",
        memory="4Gi",
        image=image,
        launch_timeout=600,  # PXS install takes ~5min
    )

    # Run the Opora MLP test (separate pod - different image from editable demos)
    remote_fn = kt.fn(run_opora_mlp, name="pxs_editable").to(compute)
    result = remote_fn()
    print(result)
