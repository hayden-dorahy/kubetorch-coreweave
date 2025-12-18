# Installation & Setup

> **Official Docs:** [Kubernetes Installation Guide](https://www.run.house/kubetorch/kubernetes-install)

## Prerequisites

- Python 3.11+ (specifically 3.11.x for best compatibility)
- Access to a Kubernetes cluster (kubeconfig)
- `kubectl` installed and configured
- `rsync` 3.x (macOS default is 2.x, install via Homebrew)
- `helm` (for cluster-side installation)

## Client Installation

### Using pip
```bash
pip install "kubetorch[client]"
```

### Using uv
```bash
uv add "kubetorch[client]"
```

### Extras
- `kubetorch[client]` - Full client with CLI (typer, rich, httpx)
- `kubetorch` - Minimal, no CLI dependencies

## Cluster Installation

Kubetorch requires an operator installed on your cluster via Helm.

### Option A: Helmfile (Recommended)

```yaml
# helmfile.yaml
repositories: []  # Using OCI registry directly

releases:
  - name: kubetorch
    namespace: kubetorch
    createNamespace: true
    chart: oci://ghcr.io/run-house/charts/kubetorch
    version: 0.2.9
    values:
      - nginx:
          # CoreWeave uses coredns, not kube-dns
          resolver: "coredns.kube-system.svc.cluster.local"
      - kubetorchConfig:
          deployment_namespaces:
            - "default"
            - "kubetorch"
            - "your-namespace"
```

```bash
brew install helmfile
helmfile sync
```

### Option B: Helm CLI

```bash
helm upgrade --install kubetorch oci://ghcr.io/run-house/charts/kubetorch \
  --version 0.2.9 \
  -n kubetorch \
  --create-namespace \
  --set nginx.resolver=coredns.kube-system.svc.cluster.local
```

### Verify Installation

```bash
kubectl get pods -n kubetorch
# Should see: kubetorch-proxy, kubetorch-rsync, etc.
```

## macOS-Specific Setup

### Install Newer rsync
```bash
brew install rsync

# Verify brew rsync is used
/opt/homebrew/bin/rsync --version  # Should be 3.x

# Add to PATH if needed
export PATH="/opt/homebrew/bin:$PATH"
```

### Fix TLS Errors (if needed)
If you get certificate errors, add to your kubeconfig:
```yaml
clusters:
  - cluster:
      insecure-skip-tls-verify: true  # For POC only
      server: https://...
```

## Configuration

### Set Your Username (Required!)

```bash
kt config set username your-name
```

**Why?** Without a username:
- Your services are anonymous
- `kt teardown --all` won't work
- Hard to identify your pods in shared clusters

With a username:
- Services prefixed: `yourname-my_function`
- Safe cleanup: `kt teardown --all`
- Easy filtering: `kubectl get pods -l user=yourname`

### Config File Location
```
~/.kt/config.yaml
```

### All Config Options

```bash
# Set values
kt config set username your-name
kt config set namespace my-namespace
kt config set stream_logs true
kt config set queue my-queue

# Get values
kt config get username

# List all
kt config list

# Unset
kt config unset queue
```

### Environment Variables

All config can be overridden via environment variables:

| Config Key | Environment Variable |
|------------|---------------------|
| `username` | `KT_USERNAME` |
| `namespace` | `KT_NAMESPACE` |
| `stream_logs` | `KT_STREAM_LOGS` |
| `stream_metrics` | `KT_STREAM_METRICS` |
| `queue` | `KT_QUEUE` |
| `install_namespace` | `KT_INSTALL_NAMESPACE` |
| `install_url` | `KT_INSTALL_URL` |
| `api_url` | `KT_API_URL` |

## Kubeconfig Setup

### Default Location
Kubetorch uses `~/.kube/config` by default.

### Custom Path
```bash
export KUBECONFIG=~/.kube/my-cluster-config
```

Or in Python:
```python
compute = kt.Compute(kubeconfig_path="~/.kube/my-cluster")
```

### In-Cluster Authentication
When running inside Kubernetes, Kubetorch automatically uses the service account credentials.

## Namespace Configuration

### Default Namespace Resolution Order
1. Explicit `namespace=` parameter in `kt.Compute()`
2. `KT_NAMESPACE` environment variable
3. `~/.kt/config.yaml` namespace setting
4. Current kubeconfig context namespace
5. `"default"`

### Allowed Namespaces
The Helm chart must be configured to allow deployments in your namespace:
```yaml
kubetorchConfig:
  deployment_namespaces:
    - "default"
    - "kubetorch"
    - "my-namespace"  # Add your namespace
```

## Verification

### Test Installation
```python
import kubetorch as kt

def hello():
    import platform
    return f"Hello from {platform.node()}!"

compute = kt.Compute(cpus="0.1")
remote = kt.fn(hello).to(compute)
print(remote())  # "Hello from pod-xyz!"
```

### Check Service
```bash
kt list
kt check your-service-name
```

### Cleanup
```bash
kt teardown your-service-name
# or
kt teardown --all  # All YOUR services (requires username)
```

## Troubleshooting Installation

### "No module named 'typer'"
```bash
pip install "kubetorch[client]"  # Not just kubetorch
```

### rsync version errors
```bash
# macOS
brew install rsync
export PATH="/opt/homebrew/bin:$PATH"
```

### kubectl port-forward errors
```bash
# Check kubeconfig
kubectl cluster-info

# Check kubetorch pods
kubectl get pods -n kubetorch
```

### DNS resolution errors (CoreWeave, etc.)
Set the correct resolver in Helm values:
```yaml
nginx:
  resolver: "coredns.kube-system.svc.cluster.local"
```

