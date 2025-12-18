# Kubetorch Overview

> **Official Docs:** [Introduction](https://www.run.house/kubetorch/introduction)

## What is Kubetorch?

Kubetorch is a modern Python interface for running ML workloads on Kubernetes. It provides simple, Pythonic APIs that give researchers and ML engineers access to compute, enable fast iteration, and ensure reproducibility.

**Key insight**: Write Python locally, run it on cluster GPUs with 1-2 second iteration cycles.

## Core Value Propositions

### 1. Rapid Iteration (1-2 seconds)
- **Magic caching**: Dependencies cached, only code changes sync
- **Hot redeployment**: Code changes apply without container rebuilds
- **Warm pods**: Python process persists between calls, imports cached

### 2. Reproducibility
- Same code runs identically from:
  - Developer laptop
  - CI/CD pipelines
  - Production applications
  - Teammate's environment

### 3. Fault Tolerance
- Programmatic handling of:
  - Hardware faults
  - Preemptions
  - Out-of-memory errors
- Dynamic retry with larger compute after OOM
- Graceful degradation on preemption

### 4. Cost Efficiency
- 50% compute cost savings through:
  - Improved bin packing
  - Intelligent resource optimization
  - Scale-to-zero for inference
  - Idle workload eviction

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Your Python Code                         │
│                    (Local machine / CI / Prod)                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Kubetorch Python Client                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ kt.fn()  │ │kt.cls()  │ │kt.Compute│ │ kt.Image │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
                                │
                    kubectl port-forward / ingress
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Kubetorch Operator (Helm Chart)             │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │    │
│  │  │  NGINX   │ │  Rsync   │ │   Loki   │ │Prometheus│    │    │
│  │  │  Proxy   │ │   Pod    │ │ (logs)   │ │(metrics) │    │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Your Services                         │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │    │
│  │  │  Deployment  │  │   Knative    │  │  RayCluster  │   │    │
│  │  │   (basic)    │  │ (autoscale)  │  │(distributed) │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## How It Works

### 1. Define Compute Requirements
```python
import kubetorch as kt

compute = kt.Compute(
    cpus="2",
    memory="8Gi",
    gpus=1,
    image=kt.images.Debian().pip_install(["torch"])
)
```

### 2. Wrap Your Function/Class
```python
def train_model(data, epochs=10):
    import torch
    # Your training code
    return model

remote_train = kt.fn(train_model).to(compute)
```

### 3. Call Remotely
```python
result = remote_train(my_data, epochs=20)
```

### What Happens Under the Hood

1. **First call (cold start)**:
   - Kubetorch creates a K8s Deployment/Knative Service
   - Rsyncs your code to the cluster
   - Starts an HTTP server in the pod
   - Serializes args, sends HTTP request
   - Deserializes response

2. **Subsequent calls (warm start)**:
   - Pod already running, Python process alive
   - Code changes hot-reload (1-2 seconds)
   - Same imports cached in `sys.modules`
   - Global state persists

## Deployment Modes

| Mode | Use Case | Backend |
|------|----------|---------|
| **Deployment** | Default, single replica | K8s Deployment |
| **Knative** | Autoscaling, scale-to-zero | Knative Serving |
| **RayCluster** | Distributed Ray workloads | KubeRay Operator |

## Use Cases

### Training
- PyTorch multi-node distributed training
- Fine-tuning LLMs
- Hyperparameter optimization

### Inference
- LLM serving with autoscaling
- Multi-step inference pipelines
- Batch predictions

### Reinforcement Learning
- GRPO training
- Multi-actor coordination
- Async evaluation

### Batch Processing
- Ray/Dask/Spark data pipelines
- Offline embeddings
- Large-scale ETL

## Why Not Just Use...

| Alternative | Kubetorch Advantage |
|-------------|---------------------|
| **Raw K8s YAML** | Python-native, no YAML, 1-2s iteration vs 30+ min |
| **Kubeflow** | Simpler, faster iteration, production-ready by design |
| **SageMaker/Vertex** | No vendor lock-in, no markup, your own cluster |
| **Dev Pods/Notebooks** | Can scale, supports distribution, production-ready |

## Key Concepts Summary

| Concept | Description |
|---------|-------------|
| **Warm Start** | Pods stay running, Python process persists |
| **Hot Reload** | Code changes sync without reimporting deps |
| **Rsync Pod** | Central storage for synced code/artifacts |
| **NGINX Proxy** | Routes requests to correct service |
| **Service Name** | `{username}-{function_name}` by default |

