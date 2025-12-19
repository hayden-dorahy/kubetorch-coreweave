# Kubetorch Setup on CoreWeave

Kubetorch is a Python interface for running ML workloads on Kubernetes - write PyTorch code locally, run it on cluster GPUs.

## Prerequisites

- Access to CoreWeave K8s cluster (kubeconfig)
- Helm (K8s package manager)
- Python environment

## 1. Install Helm & Update rsync

```bash
# macOS
brew install helm
brew install rsync   # macOS rsync is outdated, kubetorch needs newer version for code syncing

# Verify
helm version
/opt/homebrew/bin/rsync --version   # should be 3.x (brew version)
rsync --version                      # may still show 2.x (macOS default)
```

> **PATH note:** Brew rsync installs to `/opt/homebrew/bin/rsync`. If kubetorch uses the wrong version, add to your shell profile:
> ```bash
> export PATH="/opt/homebrew/bin:$PATH"
> ```

## 2. Install Kubetorch Python Client

```bash
uv init                      # if starting fresh
uv add "kubetorch[client]"   # quotes required
```

## 3. Configure Your Username

> ⚠️ **Why set a username?**
> 
> Without a username, your services are anonymous and `kt teardown --all` won't work.
> With a username, your services get prefixed (e.g., `hayden-hello_world`) so you can:
> - Identify your pods in `kt list` and `kubectl get pods`
> - Safely run `kt teardown --all` without killing other people's work
> - Filter resources: `kubectl get pods -l user=hayden`

```bash
kt config set username <your-name>
```

Stored in `~/.kt/config.yaml`. Can also set via env var:
```bash
export KT_USERNAME=<your-name>
```

Verify with:
```bash
kt config list
```

## 4. Deploy Kubetorch to Cluster

### Option A: Helmfile (recommended)

```bash
brew install helmfile
# Uses default ~/.kube/config automatically
helmfile sync
```

Config is in `helmfile.yaml` - declarative, version-controlled, reproducible.

### Option B: Helm CLI

```bash
# Uses default ~/.kube/config automatically

helm upgrade --install kubetorch oci://ghcr.io/run-house/charts/kubetorch \
  --version 0.2.9 -n kubetorch --create-namespace \
  --set nginx.resolver=coredns.kube-system.svc.cluster.local
```

> **CoreWeave DNS fix**: Must set `nginx.resolver=coredns.kube-system.svc.cluster.local` (CoreWeave uses `coredns`, not `kube-dns`).

## 4. Verify Installation

```bash
# Check pods are running
kubectl get pods -n kubetorch
```

## 5. Test with Simple Example

```python
import kubetorch as kt

def hello_world():
    return "Hello from Kubetorch!"

if __name__ == "__main__":
    # Define compute (CPU only for testing)
    compute = kt.Compute(cpus="0.1")

    # Send function to cluster
    remote_fn = kt.fn(hello_world).to(compute)

    # Run remotely
    result = remote_fn()
    print(result)  # "Hello from Kubetorch!"
```

## 6. Custom Images & Private Packages

### Using a Custom Base Image

```python
# Use Debian base (avoids dependency conflicts)
image = kt.images.Debian()

# Or use a Docker image
image = kt.Image().from_docker("nvcr.io/nvidia/pytorch:24.08-py3")
```

### Installing Packages

```python
image = (
    kt.images.Debian()
    .run_bash("pip install uv")
    .run_bash("uv pip install --system numpy torch mypackage")
)
```

### Private Package Registry (e.g., Artifactory)

For private packages, pass credentials via environment variables:

```python
image = (
    kt.images.Debian()
    .set_env_vars({
        "UV_EXTRA_INDEX_URL": f"https://{username}:{password}@your.registry.com/simple",
        "UV_PRERELEASE": "allow",
    })
    .run_bash("pip install uv")
    .run_bash("uv pip install --system 'your-private-package==1.0.0'")
)
```

See `test_pxs.py` for a working example with Artifactory credentials loaded from `~/.local/share/uv/credentials/credentials.toml`.

### Mounting Shared Storage (PVC)

```python
vol = kt.Volume.from_name(
    name="slurm-data",
    namespace="tenant-slurm",
    mount_path="/mnt/data"
)
compute = kt.Compute(
    cpus="0.5",
    namespace="tenant-slurm",  # Must match PVC namespace
    volumes=[vol]
)
```

### Identifying Workloads by User

Use labels to track who owns which pods (useful for shared clusters):

```python
compute = kt.Compute(
    cpus="1",
    labels={"user": "hayden", "team": "research"}
)
```

Query by user with kubectl:
```bash
kubectl get pods -l user=hayden              # Find user's pods
kubectl get pods -l team=research            # Find team's pods
kubectl delete pods -l user=hayden           # Clean up user's pods
```

> **Note:** `kt list` doesn't show labels, but they're on the pods. Kubetorch also adds its own labels like `kubetorch.com/service` and `kubetorch.com/module`.

## ⚠️ GPU Access Note

Currently, all GPUs are reserved by SUNK (Slurm). Kubetorch's default scheduler can't allocate them.

**Current GPU allocation:**
- 16x B200 GPUs total (2 nodes × 8)
- All reserved via `sunk.coreweave.com/accelerator`

### Potential Solution: SUNK Scheduler

CoreWeave's SUNK can schedule Kubernetes Pods alongside Slurm jobs using a custom scheduler.
See: [Schedule Kubernetes Pods with Slurm](https://docs.coreweave.com/docs/products/sunk/run_workloads/schedule-kubernetes-pods)

**Requirements:**
1. Set `schedulerName` to `tenant-slurm-slurm-scheduler`
2. Add SUNK annotations for GPU allocation
3. Request resources (CPU, memory, GPUs)

**Example Pod annotations:**
```yaml
annotations:
  sunk.coreweave.com/exclusive: "user"  # Allow GPU sharing between K8s pods
  sunk.coreweave.com/account: "root"
```

**Kubetorch limitation:** Currently no direct way to set `schedulerName`. Options:
1. Request feature from Kubetorch maintainers
2. Use raw K8s manifests for GPU workloads (see `test_gpu_sunk_raw.yaml`)
3. Use Slurm directly for GPU jobs

## Managing Deployments

Kubetorch keeps pods running ("warm start") for fast iteration.

### Auto-Termination Options

**Option 1: Knative Autoscaling (recommended)**

With Knative installed, use `.autoscale()` for true scale-to-zero:
```python
remote_fn = kt.fn(my_func).to(compute).autoscale(
    min_replicas=0,      # Scale to zero when idle
    max_replicas=1,
    target_concurrency=1
)
```
Pods terminate after ~30s idle and cold-start on next request.

**Option 2: Manual Teardown**

For development, manually clean up:
```bash
kt teardown <service-name>   # Delete specific service
kt teardown -ya              # Delete all your services
```

### Hot-Reload (automatic)

Code changes to your function are patched automatically - no restart needed:
```python
# Just run again - changes sync in ~1-2s
remote_fn = kt.fn(my_function).to(compute)
result = remote_fn()
```

### When You Need to Delete

Must delete deployment when changing:
- Base container image (e.g., Debian → NVIDIA)
- Compute resources (CPUs, memory, GPUs)
- Namespace

### How to Delete (safe methods)

```python
# Force fresh deployment (deletes existing first)
remote_fn = kt.fn(my_function).to(compute, reuse=False)
```

```bash
# CLI
kt list              # List running services
kt teardown NAME           # Delete a service
kt teardown --prefix PFX   # Delete all with prefix
```

Avoid raw `kubectl delete` - Kubetorch commands handle both Deployment and Service together.

## Useful Commands

```bash
# Check kubetorch namespace
kubectl get all -n kubetorch

# View kubetorch logs
kubectl logs -n kubetorch -l app=kubetorch

# Uninstall kubetorch
helm uninstall kubetorch -n kubetorch
```

## Resources

- [Kubetorch Kubernetes Install Guide](https://www.run.house/kubetorch/kubernetes-install) ← official docs
- [Kubetorch Docs](https://www.run.house/kubetorch)
- [Kubetorch GitHub](https://github.com/run-house/kubetorch)
- [PyPI](https://pypi.org/project/kubetorch/)

