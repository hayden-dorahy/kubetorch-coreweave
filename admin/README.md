# Admin / Infrastructure

Cluster administration files. Regular users shouldn't need to modify these.

## Contents

| File | Description |
|------|-------------|
| `helmfile.yaml` | Kubetorch + Knative Operator + KubeRay deployment |
| `knative-serving.yaml` | KnativeServing CR (from kubetorch chart) - deploys autoscaler |
| `docs/kubetorch_setup.md` | Full Kubetorch installation guide |
| `docs/coreweave_k8s.md` | CoreWeave cluster connection notes |

## Deploying/Updating

```bash
cd admin/

# 1. Deploy all Helm releases (kubetorch, knative-operator, kuberay)
helmfile sync

# 2. Create Knative Serving (enables scale-to-zero)
kubectl create namespace knative-serving
kubectl apply -f knative-serving.yaml

# Preview / Remove
helmfile diff        # Preview changes
helmfile destroy     # Remove all
```

## What's Installed

| Component | Purpose |
|-----------|---------|
| **Kubetorch** | Core platform - rsync, proxy, metrics, logging |
| **Knative Operator** | Enables autoscaling & scale-to-zero via `.autoscale()` |
| **KubeRay** | Enables Ray distributed workloads |

## Key Config

The `helmfile.yaml` sets:
- DNS resolver: `coredns.kube-system.svc.cluster.local`
- Allowed namespaces: `default`, `kubetorch`, `tenant-slurm`

## Using Autoscaling (Scale-to-Zero)

With Knative installed, use `.autoscale()` on **Compute** (not Fn):

```python
# .autoscale() goes on Compute, deploys as Knative Service
compute = kt.Compute(cpus="1", gpus=1).autoscale(
    min_scale=0,         # Scale to zero when idle
    max_scale=5,         # Max pods for concurrent requests
    concurrency=1,       # 1 request per pod (critical for GPU inference)
    scale_to_zero_pod_retention_period="30s",  # Fast for dev (default 10m)
)

remote_fn = kt.fn(my_func).to(compute)
```

**How it works:**
- Pods terminate after idle period (default 10m, set lower for dev)
- New request → cold start (~5-10s) → pod created
- Concurrent requests → scales up to `max_scale` pods
- `concurrency=1` forces 1 request per pod (prevents GPU OOM)

**Demo:** `python demos/advanced/autoscale_demo.py`

> **Note:** `inactivity_ttl` on regular `kt.Compute` does NOT work for auto-termination.
> You must use `.autoscale()` which deploys as a Knative Service.

