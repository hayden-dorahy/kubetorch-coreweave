# Exceptions

Kubetorch defines several custom exceptions for error handling.

## Exception Registry

| Exception | Description |
|-----------|-------------|
| `ImagePullError` | Failed to pull container image (auth, typo, missing). |
| `KubernetesCredentialsError` | Missing or invalid Kubeconfig. |
| `PodContainerError` | Pod crashed or failed to start (CrashLoopBackOff). |
| `ResourceNotAvailableError` | Cluster cannot satisfy resource request (CPU/GPU). |
| `ServiceHealthError` | Service started but failed health checks. |
| `ServiceTimeoutError` | Service took too long to become ready (`launch_timeout`). |
| `StartupError` | Error during container startup command execution. |
| `PodTerminatedError` | Pod was terminated (OOM, eviction, preemption) during execution. |
| `QueueUnschedulableError` | Queue limits exceeded or queue invalid. |
| `KnativeServiceConflictError` | Conflict modifying Knative service. |
| `RsyncError` | Failed to sync code to the cluster. |
| `VersionMismatchError` | Client/Server version mismatch. |
| `SecretNotFound` | Referenced secret does not exist. |
| `WorkerMembershipChanged` | Distributed worker nodes changed unexpectedly. |

## Handling Errors

### OOM (Out of Memory)

If a function fails due to OOM, Kubetorch raises `PodTerminatedError`. You can catch this and retry with more memory:

```python
try:
    result = remote_fn()
except kt.PodTerminatedError as e:
    if "OOMKilled" in str(e):
        print("OOM detected! Retrying with more memory...")
        # Create new compute with more memory
        new_compute = kt.Compute(memory="32Gi")
        remote_fn = remote_fn.to(new_compute)
        result = remote_fn()
```

### Preemption

Spot instances/preemptible nodes can be reclaimed. Kubetorch detects this.

### Connection Errors

Transient network issues usually raise `ConnectionError` or `ReadTimeout`. The HTTP client has built-in retries for connection establishment, but not for execution (as it's non-idempotent).

