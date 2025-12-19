"""Demo: Install PXS using credentials from .env.secrets.

This script demonstrates the recommended pattern for handling private
package credentials:
1. Load credentials from local .env.secrets (gitignored)
2. Pass them to the remote image via environment variables
3. Use them in the install command
"""

import kubetorch as kt

from demos.pxs.utils import load_artifactory_creds


def run_opora_mlp():
    """Run a simple Opora MLP model (same as other demos)."""
    import numpy as np
    from pxs.models.opora.pytorch.base import OporaPyTorch
    from pxs.models.opora.pytorch.config.config import OporaPyTorchConfig

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
                {"block_type": "MLP", "in_channels": 64, "out_channels": 1, "hidden_channels": []},
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

    return f"PXS installed successfully via secrets! Output shape: {output['target'].shape}"


if __name__ == "__main__":
    # 1. Load secrets locally
    user, token = load_artifactory_creds()

    print(f"Loaded credentials for user: {user}")

    # 2. Configure image with credentials
    # We pass the full index URL as an environment variable to the build process
    index_url = (
        f"https://{user}:{token}@physicsx.jfrog.io/artifactory/api/pypi/px-pypi-release/simple"
    )

    image = (
        kt.images.Debian()
        .set_env_vars(
            {
                # uv looks for this env var automatically if configured, or we can use it in the command
                "UV_EXTRA_INDEX_URL": index_url,
                "UV_PRERELEASE": "allow",
                "UV_INDEX_STRATEGY": "unsafe-best-match",
            }
        )
        # uv is already installed in the base image
        # uv will use UV_EXTRA_INDEX_URL to find the package
        .run_bash("uv pip install --system 'physicsx.pxs[opora]==0.29.0-dev.11'")
    )

    compute = kt.Compute(
        cpus="0.5",
        memory="4Gi",
        image=image,
        launch_timeout=600,  # PXS install can take >5 mins
        inactivity_ttl="10m",
    )

    print("Deploying PXS install demo...")
    remote_fn = kt.fn(run_opora_mlp, name="pxs_secrets").to(compute)

    result = remote_fn()
    print("\n" + result)
