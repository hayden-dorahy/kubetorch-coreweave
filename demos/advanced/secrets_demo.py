"""Demo: Using Secrets in Kubetorch.

Demonstrates securely passing secrets (API keys, tokens) to the remote pod.
"""

import os

import kubetorch as kt
from dotenv import load_dotenv

# Load secrets from .env.secrets if present
load_dotenv(".env.secrets")

# Use ARTIFACTORY_TOKEN as the test secret since we know it's there
TEST_SECRET_KEY = "ARTIFACTORY_TOKEN"


def check_secret():
    """Verify the secret is available in the remote environment."""
    import os
    # We check for the specific key we uploaded
    # Note: kt.Secret.from_env uploads the *value* of the local env var
    # but the key inside the pod matches the local env var name by default.

    secret_val = os.environ.get("ARTIFACTORY_TOKEN")

    if secret_val:
        # Don't print the whole secret in logs
        return f"✅ SUCCESS: Secret {secret_val[:5]}... found!"
    else:
        return "❌ FAILURE: Secret NOT found in environment vars."


if __name__ == "__main__":
    if not os.environ.get(TEST_SECRET_KEY):
        print(f"Please set {TEST_SECRET_KEY} in .env.secrets or environment first.")
        exit(1)

    print(f"Syncing local secret {TEST_SECRET_KEY}...")

    # Create a Kubetorch secret from the local environment variable
    # This creates a K8s Secret and mounts it to the pod as an env var
    api_secret = kt.Secret.from_env([TEST_SECRET_KEY], name="test-env-secret")

    compute = kt.Compute(
        cpus="0.1",
        launch_timeout=60,
        secrets=[api_secret],  # Attach secret to compute
    )

    print("Deploying with secret...")
    remote_fn = kt.fn(check_secret, name="advanced_secrets").to(compute)

    result = remote_fn()
    print("\n" + result)
