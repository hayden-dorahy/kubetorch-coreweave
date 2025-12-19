# Advanced Demos

More complex Kubetorch features.

| Demo | Description |
|------|-------------|
| `secrets_demo.py` | Securely pass API keys/tokens to pods |
| `resource_requests.py` | Request specific memory, disk, and shared memory sizes |

## Secrets

Kubetorch can sync local environment variables to Kubernetes Secrets.

```python
# Sync local env var "MY_KEY" to remote pod
secret = kt.Secret.from_env(["MY_KEY"], name="my-secret")
compute = kt.Compute(secrets=[secret])
```

## Resource Requests

You can request specific hardware resources:

```python
compute = kt.Compute(
    cpus="4",
    memory="16Gi",
    disk_size="50Gi",           # Ephemeral storage
    shared_memory_limit="2Gi",  # /dev/shm (critical for PyTorch loaders)
)
```

## Other Features

- **Distributed Training**: `compute.distribute()` - Requires multi-GPU setup.
- **Autoscaling**: `compute.autoscale()` - Requires Knative (not installed on this cluster).
- **Custom Images**: `kt.Image` - See `demos/pxs/` for examples of custom image building.
