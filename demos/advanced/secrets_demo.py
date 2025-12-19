"""Demo: Using Secrets in Kubetorch.

Demonstrates securely passing secrets (API keys, tokens) to the remote pod.
"""
import os
import kubetorch as kt

# Set a dummy secret locally (in real usage, this would be your HF_TOKEN, etc.)
os.environ["MY_SUPER_SECRET_KEY"] = "sk-live-1234567890"


def check_secret():
    """Verify the secret is available in the remote environment."""
    import os
    secret_val = os.environ.get("MY_SUPER_SECRET_KEY")
    
    if secret_val == "sk-live-1234567890":
        return f"✅ SUCCESS: Secret found! Value starts with {secret_val[:7]}..."
    elif secret_val:
        return f"❌ FAILURE: Secret found but wrong value: {secret_val}"
    else:
        return "❌ FAILURE: Secret NOT found in environment vars."


if __name__ == "__main__":
    print(f"Local secret: {os.environ['MY_SUPER_SECRET_KEY']}")
    
    # Create a Kubetorch secret from the local environment variable
    # This creates a K8s Secret and mounts it to the pod
    api_secret = kt.Secret.from_env(["MY_SUPER_SECRET_KEY"], name="demo-secret")
    
    compute = kt.Compute(
        cpus="0.1",
        launch_timeout=60,
        inactivity_ttl="10m",
        secrets=[api_secret]  # Attach secret to compute
    )
    
    print("Deploying with secret...")
    remote_fn = kt.fn(check_secret, name="advanced_secrets").to(compute)
    
    result = remote_fn()
    print("\n" + result)

