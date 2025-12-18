# Autoscaling

> **Official Docs:** [Autoscaling & Distribution](https://www.run.house/kubetorch/concepts/distributed)

Kubetorch supports autoscaling via **Knative Serving**. This enables:
- Scale-to-zero when idle
- Scale-up on request concurrency
- Request buffering

## Enabling Autoscaling

Use the `.autoscale()` method on `Compute` or the module.

```python
import kubetorch as kt

def my_model(inputs):
    # Heavy inference...
    pass

compute = kt.Compute(cpus="4", memory="16Gi", gpus=1)

remote_model = kt.fn(my_model).to(compute).autoscale(
    min_replicas=0,      # Scale to zero allowed
    max_replicas=10,     # Max pods
    target_concurrency=1 # 1 request per pod (common for GPUs)
)
```

## Parameters

### `min_replicas`
Minimum number of pods.
- `0`: Scale to zero enabled. Pods terminate after idle window. Cold start on next request.
- `1`: Keep at least one warm pod. No cold starts.

### `max_replicas`
Maximum number of pods. Limits cost and resource usage.

### `target_concurrency`
Target number of concurrent requests per pod (hard limit for Knative).
- `1`: Process requests strictly sequentially (common for heavy GPU models to avoid OOM).
- `N`: Allow N concurrent requests per pod.

## Scale-to-Zero

When `min_replicas=0`:
1. After `scale-down-delay` (default ~30s), idle pods terminate.
2. Next request triggers **cold start**:
   - Pod scheduled
   - Image pulled
   - Container started
   - Function/Class loaded
3. Request processed.

**Optimizing Cold Start:**
- Use smaller images (Alpine/Debian vs full Ubuntu)
- Pre-install dependencies in image (avoid runtime `pip install`)
- Use `kt.Image().from_docker()` with pre-baked image

## Decorator Syntax

```python
@kt.compute(cpus="2")
@kt.autoscale(min_replicas=1, max_replicas=5)
def serve_traffic(request):
    ...
```

## Requirements

Requires **Knative Serving** installed on the cluster. The Kubetorch Helm chart supports Knative integration.

## Autoscaling vs. Distribution

| Feature | Autoscaling | Distribution |
|---------|-------------|--------------|
| **Goal** | Handle variable request load | Scale single workload across nodes |
| **Trigger** | HTTP Request Concurrency | Fixed number of workers |
| **Communication** | Independent requests | All-reduce / P2P communication |
| **Backend** | Knative Service | K8s Deployment / RayCluster |
| **State** | Stateless (mostly) | Stateful (training state) |

## Example: LLM Serving

```python
class LLMServer:
    def __init__(self):
        # Load model (takes 10s of seconds)
        self.model = load_model()
    
    def generate(self, prompt):
        return self.model.generate(prompt)

# Keep 1 replica warm to avoid model load latency
# Scale up to 10 for traffic spikes
# 1 request per GPU to avoid OOM
remote_llm = kt.cls(LLMServer).to(
    kt.Compute(gpus=1)
).autoscale(
    min_replicas=1,
    max_replicas=10,
    target_concurrency=1
)
```

