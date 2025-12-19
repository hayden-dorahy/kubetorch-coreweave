"""Test pxs Opora with editable install via uv pip install -e."""


def run_opora_mlp():
    """Run a simple Opora MLP model."""
    import sys
    
    # Add the rsynced pxs repo to path (editable install .pth not loaded in running server)
    sys.path.insert(0, "/pxs_repo")
    
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

    model = OporaPyTorch(OporaPyTorchConfig(**config))
    model.is_trained = True

    n_points = 100
    sample = {
        "points": np.random.normal(size=(n_points, 3)).astype(np.float32),
        "target": np.random.normal(size=(n_points, 1)).astype(np.float32),
    }

    output = model.predict_one(data=sample)
    
    import pxs
    import pxs.models.opora.pytorch.base as base_module
    return (
        f"pxs.__file__: {pxs.__file__}\n"
        f"OporaPyTorch module: {base_module.__file__}\n"
        f"Output shape: {output['target'].shape}"
    )


if __name__ == "__main__":
    import tomllib
    from pathlib import Path
    import kubetorch as kt

    # Path to local pxs repo (entire repo, not just pxs/ subfolder)
    PXS_REPO = Path.home() / "gitrepos/product/libraries/pxs"

    # Load artifactory creds
    creds_file = Path.home() / ".local/share/uv/credentials/credentials.toml"
    with open(creds_file, "rb") as f:
        data = tomllib.load(f)
    for cred in data.get("credential", []):
        if "physicsx.jfrog.io" in cred.get("service", ""):
            username, password = cred["username"], cred["password"]
            break

    print(f"Rsyncing pxs repo from {PXS_REPO} and installing with uv pip install -e...")

    # Rsync entire pxs repo, then install in editable mode
    image = (
        kt.images.Debian()
        .set_env_vars({
            "UV_EXTRA_INDEX_URL": f"https://{username}:{password}@physicsx.jfrog.io/artifactory/api/pypi/px-pypi-release/simple",
            "UV_PRERELEASE": "allow",
            "UV_INDEX_STRATEGY": "unsafe-best-match",
        })
        .run_bash("pip install uv")
        # Rsync entire pxs repo (pyproject.toml + pxs/ folder)
        .rsync(str(PXS_REPO), dest="/pxs_repo", contents=True)
        # Install in editable mode with opora extras
        .run_bash('uv pip install --system -e "/pxs_repo[opora]"')
    )

    compute = kt.Compute(cpus="0.5", memory="4Gi", image=image, launch_timeout=300, inactivity_ttl="10m")
    
    remote_fn = kt.fn(run_opora_mlp, name="pxs_install").to(compute)  # separate - different image setup
    result = remote_fn()
    print(result)

