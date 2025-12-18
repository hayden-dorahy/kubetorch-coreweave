# Compute Class Reference

> **Official Docs:** [Compute API Reference](https://www.run.house/kubetorch/api-reference/python/compute)
> **Source:** `kubetorch.resources.compute.compute.Compute`

The `kt.Compute` class is the core resource specification for Kubetorch services. It defines CPU, memory, GPU, volumes, secrets, and all Kubernetes-level configuration.

## Constructor

```python
kt.Compute(
    # ─────────────────────────────────────────────────────────────
    # RESOURCE REQUESTS
    # ─────────────────────────────────────────────────────────────
    cpus: Union[str, int] = None,
    memory: str = None,
    disk_size: str = None,
    gpus: Union[str, int] = None,
    gpu_type: str = None,
    gpu_memory: str = None,
    shared_memory_limit: str = None,
    
    # ─────────────────────────────────────────────────────────────
    # KUBERNETES CONFIGURATION
    # ─────────────────────────────────────────────────────────────
    namespace: str = None,
    labels: Dict = None,
    annotations: Dict = None,
    node_selector: Dict = None,
    tolerations: List[Dict] = None,
    service_account_name: str = None,
    service_template: Dict = None,
    
    # ─────────────────────────────────────────────────────────────
    # IMAGE & ENVIRONMENT
    # ─────────────────────────────────────────────────────────────
    image: Image = None,
    env_vars: Dict = None,
    secrets: List[Union[str, Secret]] = None,
    volumes: List[Union[str, Volume]] = None,
    working_dir: str = None,
    
    # ─────────────────────────────────────────────────────────────
    # SCHEDULING
    # ─────────────────────────────────────────────────────────────
    queue: str = None,
    priority_class_name: str = None,
    
    # ─────────────────────────────────────────────────────────────
    # BEHAVIOR
    # ─────────────────────────────────────────────────────────────
    replicas: int = 1,
    freeze: bool = False,
    inactivity_ttl: str = None,
    launch_timeout: int = None,
    image_pull_policy: str = None,
    gpu_anti_affinity: bool = None,
    
    # ─────────────────────────────────────────────────────────────
    # OBSERVABILITY
    # ─────────────────────────────────────────────────────────────
    logging_config: LoggingConfig = None,
    
    # ─────────────────────────────────────────────────────────────
    # ADVANCED
    # ─────────────────────────────────────────────────────────────
    kubeconfig_path: str = None,
    allowed_serialization: List[str] = None,
)
```

## Parameter Details

### Resource Requests

#### `cpus`
CPU resource request. 

**Formats:**
- Decimal cores: `"0.5"`, `"1.0"`, `"2.0"`
- Millicores: `"500m"`, `"1000m"`, `"2000m"`
- Integer: `1`, `2` (converted to string)

```python
kt.Compute(cpus="0.5")      # Half a core
kt.Compute(cpus="500m")     # Same as above
kt.Compute(cpus=2)          # 2 cores
```

#### `memory`
Memory resource request.

**Formats:**
- Binary units: `"1Ki"`, `"1Mi"`, `"1Gi"`, `"1Ti"`
- Decimal units: `"1K"`, `"1M"`, `"1G"`, `"1T"`
- Bytes: `"1000000"`

```python
kt.Compute(memory="4Gi")    # 4 gibibytes
kt.Compute(memory="4G")     # 4 gigabytes (slightly less)
kt.Compute(memory="4096Mi") # Same as 4Gi
```

#### `disk_size`
Ephemeral storage request. Same format as memory.

```python
kt.Compute(disk_size="10Gi")
```

#### `gpus`
Number of GPUs to request.

```python
kt.Compute(gpus=1)          # 1 GPU
kt.Compute(gpus="2")        # 2 GPUs
kt.Compute(gpus=0)          # No GPU (same as None)
```

#### `gpu_type`
GPU product type selector. Maps to `nvidia.com/gpu.product` node label.

```python
kt.Compute(gpus=1, gpu_type="L4")
kt.Compute(gpus=1, gpu_type="A100")
kt.Compute(gpus=1, gpu_type="V100")
kt.Compute(gpus=1, gpu_type="H100")
```

This adds a `nodeSelector`:
```yaml
nodeSelector:
  nvidia.com/gpu.product: L4
```

#### `gpu_memory`
GPU memory limit (still requests whole GPU).

```python
kt.Compute(gpu_memory="4Gi", cpus="1")  # Request GPU with 4GB limit
```

Uses KAI scheduler GPU sharing annotations.

#### `shared_memory_limit`
Size of `/dev/shm` (shared memory filesystem). Critical for PyTorch DataLoader with `num_workers > 0`.

```python
kt.Compute(shared_memory_limit="2Gi")  # 2GB /dev/shm
```

Default: Pod's memory limit or half of node RAM.

---

### Kubernetes Configuration

#### `namespace`
Kubernetes namespace for deployment.

```python
kt.Compute(namespace="my-namespace")
```

**Resolution order:**
1. Explicit parameter
2. `KT_NAMESPACE` env var
3. `~/.kt/config.yaml`
4. Kubeconfig current context
5. `"default"`

#### `labels`
Custom Kubernetes labels.

```python
kt.Compute(labels={
    "user": "alice",
    "team": "ml-research",
    "project": "llm-training"
})
```

Query with kubectl:
```bash
kubectl get pods -l user=alice
kubectl get pods -l team=ml-research
```

#### `annotations`
Custom Kubernetes annotations.

```python
kt.Compute(annotations={
    "prometheus.io/scrape": "true",
    "my-annotation": "my-value"
})
```

#### `node_selector`
Constrain pods to specific nodes.

```python
kt.Compute(node_selector={
    "node.kubernetes.io/instance-type": "g4dn.xlarge",
    "topology.kubernetes.io/zone": "us-west-2a"
})
```

#### `tolerations`
Kubernetes tolerations for taints.

```python
kt.Compute(tolerations=[
    {
        "key": "nvidia.com/gpu",
        "operator": "Exists",
        "effect": "NoSchedule"
    },
    {
        "key": "dedicated",
        "operator": "Equal",
        "value": "ml-workloads",
        "effect": "NoSchedule"
    }
])
```

**Note:** GPU tolerations are added automatically when `gpus > 0`.

#### `service_account_name`
Kubernetes service account.

```python
kt.Compute(service_account_name="my-service-account")
```

Default: `"kubetorch-service-account"`

#### `service_template`
Raw Kubernetes manifest overrides (advanced).

```python
kt.Compute(service_template={
    "spec": {
        "template": {
            "spec": {
                "nodeSelector": {"custom": "value"},
                "affinity": {...}
            }
        }
    }
})
```

---

### Image & Environment

#### `image`
Container image configuration. See [05_image.md](05_image.md).

```python
kt.Compute(image=kt.images.Debian())
kt.Compute(image=kt.images.Python312().pip_install(["torch"]))
kt.Compute(image=kt.Image().from_docker("nvcr.io/nvidia/pytorch:24.08-py3"))
```

#### `env_vars`
Environment variables for containers.

```python
kt.Compute(env_vars={
    "OMP_NUM_THREADS": "4",
    "CUDA_VISIBLE_DEVICES": "0,1",
    "MY_API_KEY": "secret-value",
    "PATH": "$PATH:/custom/bin",  # Variable expansion supported
})
```

#### `secrets`
Secrets to mount or expose. See [08_secrets.md](08_secrets.md).

```python
kt.Compute(secrets=[
    kt.Secret.from_provider("aws"),
    kt.Secret.from_provider("huggingface"),
    "existing-k8s-secret-name"
])
```

#### `volumes`
Persistent volumes to attach. See [07_volumes.md](07_volumes.md).

```python
kt.Compute(volumes=[
    kt.Volume(name="data", size="10Gi", mount_path="/data"),
    kt.Volume.from_name("existing-pvc", mount_path="/mnt/data"),
    "pvc-name"  # String reference to existing PVC
])
```

#### `working_dir`
Container working directory. Must be absolute path.

```python
kt.Compute(working_dir="/app")
```

---

### Scheduling

#### `queue`
KAI scheduler queue name.

```python
kt.Compute(queue="high-priority")
kt.Compute(queue="batch-jobs")
```

This sets `schedulerName: kai-scheduler` and adds `kai.scheduler/queue` label.

#### `priority_class_name`
Kubernetes priority class.

```python
kt.Compute(priority_class_name="high-priority")
```

---

### Behavior

#### `replicas`
Number of pod replicas. For distributed training, use `.distribute()` instead.

```python
kt.Compute(replicas=3)
```

#### `freeze`
Production mode - disables hot reload and code syncing.

```python
kt.Compute(freeze=True)
```

Use for production deployments where code is baked into the image.

#### `inactivity_ttl`
Auto-terminate after inactivity period. Requires OTEL enabled.

```python
kt.Compute(inactivity_ttl="30m")  # 30 minutes
kt.Compute(inactivity_ttl="1h")   # 1 hour
kt.Compute(inactivity_ttl="1d")   # 1 day
```

**Warning:** Values below 1m may cause premature deletion.

#### `launch_timeout`
Maximum time to wait for service to become ready.

```python
kt.Compute(launch_timeout=1800)  # 30 minutes
```

Default: 900 seconds (15 minutes). Can also set via `KT_LAUNCH_TIMEOUT` env var.

#### `image_pull_policy`
When to pull container image.

```python
kt.Compute(image_pull_policy="Always")
kt.Compute(image_pull_policy="IfNotPresent")
kt.Compute(image_pull_policy="Never")
```

#### `gpu_anti_affinity`
Prevent scheduling on GPU nodes when no GPU requested.

```python
kt.Compute(cpus="1", gpu_anti_affinity=True)
```

Can also set via `KT_GPU_ANTI_AFFINITY` env var.

---

### Observability

#### `logging_config`
Configure log streaming behavior.

```python
from kubetorch import LoggingConfig

kt.Compute(logging_config=LoggingConfig(
    stream_logs=True,           # Enable log streaming
    level="info",               # "debug", "info", "warning", "error"
    include_system_logs=False,  # Exclude uvicorn.access, etc.
    include_events=True,        # Include K8s events during startup
    grace_period=2.0,           # Seconds to catch late logs
    include_name=True,          # Prepend service name to logs
    poll_timeout=1.0,           # WebSocket receive timeout
    shutdown_grace_period=0,    # Block main thread on shutdown
))
```

---

### Advanced

#### `kubeconfig_path`
Custom kubeconfig file path.

```python
kt.Compute(kubeconfig_path="~/.kube/my-cluster")
```

#### `allowed_serialization`
Restrict serialization formats for security.

```python
kt.Compute(allowed_serialization=["json"])  # Only allow JSON
kt.Compute(allowed_serialization=["json", "pickle"])  # Allow both
```

---

## Properties (Read from deployed service)

After deployment, these properties reflect the actual K8s state:

```python
compute.service_name        # "yourname-my-function"
compute.namespace           # "default"
compute.endpoint           # Internal service URL
compute.cpus               # "0.5"
compute.memory             # "4Gi"
compute.gpus               # "1"
compute.gpu_type           # "L4"
compute.replicas           # 1
compute.deployment_mode    # "deployment" | "knative" | "raycluster"
compute.distributed_config # {...} if distributed
compute.autoscaling_config # {...} if autoscaling
compute.pod_spec           # Full pod spec dict
compute.manifest           # Full K8s manifest dict
```

---

## Methods

### `distribute()`
Enable distributed training. See [09_distributed.md](09_distributed.md).

```python
compute.distribute(
    framework="pytorch",  # "pytorch" | "ray"
    workers=4,
    distribution_args={...}
)
```

### `autoscale()`
Enable Knative autoscaling. See [10_autoscaling.md](10_autoscaling.md).

```python
compute.autoscale(
    min_replicas=0,
    max_replicas=10,
    target_concurrency=5
)
```

### `ssh()`
Open interactive shell in the pod.

```python
compute.ssh()
```

### `logs()`
Stream logs from the service.

```python
compute.logs(follow=True, tail=100)
```

### `pods()`
List pods for this service.

```python
pods = compute.pods()
for pod in pods:
    print(pod.metadata.name, pod.status.phase)
```

### `is_up()`
Check if service is running.

```python
if compute.is_up():
    print("Service is ready")
```

### `rsync(paths)`
Sync files to the rsync pod.

```python
compute.rsync(["./src", "./data"])
```

### `client_port()`
Get the local port for kubectl port-forward.

```python
port = compute.client_port()  # e.g., 38080
```

---

## Class Methods

### `Compute.from_template(service_info)`
Create Compute from existing K8s service.

```python
# Used internally when reloading services
compute = kt.Compute.from_template({"resource": k8s_manifest})
```

---

## Examples

### Basic CPU Service
```python
compute = kt.Compute(cpus="0.5", memory="1Gi")
```

### GPU Training
```python
compute = kt.Compute(
    cpus="4",
    memory="32Gi",
    gpus=1,
    gpu_type="A100",
    shared_memory_limit="16Gi",
    image=kt.images.pytorch()
)
```

### Production Service
```python
compute = kt.Compute(
    cpus="2",
    memory="8Gi",
    freeze=True,
    inactivity_ttl="1h",
    labels={"env": "production"},
    image=kt.Image().from_docker("my-registry/my-image:v1.0")
)
```

### With Volumes and Secrets
```python
compute = kt.Compute(
    cpus="1",
    memory="4Gi",
    volumes=[
        kt.Volume.from_name("shared-data", mount_path="/data"),
        kt.Volume(name="scratch", size="50Gi", mount_path="/scratch")
    ],
    secrets=[
        kt.Secret.from_provider("aws"),
        kt.Secret.from_provider("huggingface")
    ],
    namespace="ml-workloads"
)
```

### Custom Scheduling
```python
compute = kt.Compute(
    cpus="8",
    memory="64Gi",
    gpus=4,
    queue="high-priority",
    priority_class_name="critical",
    node_selector={"node-pool": "gpu-a100"},
    tolerations=[
        {"key": "gpu-reserved", "operator": "Exists", "effect": "NoSchedule"}
    ]
)
```

