"""Test pxs Opora with editable/local version synced to cluster."""


def run_opora_mlp():
    """Run a simple Opora MLP model using local pxs."""
    import sys
    # Add synced pxs to path (BEFORE site-packages)
    sys.path.insert(0, "/pxs_sync")
    
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
    model.is_trained = True

    # Dummy data
    n_points = 100
    sample = {
        "points": np.random.normal(size=(n_points, 3)).astype(np.float32),
        "target": np.random.normal(size=(n_points, 1)).astype(np.float32),
    }

    output = model.predict_one(data=sample)
    
    # Show which pxs we're using
    import pxs
    import pxs.models.opora.pytorch.base as base_module
    return (
        f"pxs.__file__: {pxs.__file__}\n"
        f"OporaPyTorch module: {base_module.__file__}\n"
        f"sys.path[0]: {sys.path[0]}\n"
        f"Output shape: {output['target'].shape}"
    )


if __name__ == "__main__":
    import tomllib
    from pathlib import Path
    import kubetorch as kt

    # Path to local pxs
    PXS_PATH = Path.home() / "gitrepos/product/libraries/pxs"

    # Load artifactory creds
    creds_file = Path.home() / ".local/share/uv/credentials/credentials.toml"
    with open(creds_file, "rb") as f:
        data = tomllib.load(f)
    for cred in data.get("credential", []):
        if "physicsx.jfrog.io" in cred.get("service", ""):
            username, password = cred["username"], cred["password"]
            break

    print(f"Syncing local pxs from {PXS_PATH}...")

    # Strategy: install pxs[opora] deps from Artifactory, then rsync local pxs code
    image = (
        kt.images.Debian()
        .set_env_vars({
            "UV_EXTRA_INDEX_URL": f"https://{username}:{password}@physicsx.jfrog.io/artifactory/api/pypi/px-pypi-release/simple",
            "UV_PRERELEASE": "allow",
            "UV_INDEX_STRATEGY": "unsafe-best-match",
        })
        .run_bash("pip install uv")
        # Install pxs[opora] to get all deps, then we'll override with local code
        .run_bash("uv pip install --system 'physicsx.pxs[opora]==0.29.0-dev.11'")
        # Sync local pxs source (overrides installed pxs)
        .rsync(str(PXS_PATH / "pxs"), dest="/pxs_sync/pxs", contents=True)
    )

    compute = kt.Compute(cpus="0.5", memory="4Gi", image=image, launch_timeout=300, inactivity_ttl="10m")
    
    remote_fn = kt.fn(run_opora_mlp, name="pxs_rsync").to(compute)  # separate - different image setup
    result = remote_fn()
    print(result)
