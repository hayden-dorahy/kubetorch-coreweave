# Advanced Topics

## Service Templates & Overrides

For full control over the Kubernetes manifest, use `service_template`. This dictionary is merged into the generated K8s spec.

```python
compute = kt.Compute(
    cpus="1",
    service_template={
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {
                        "karpenter.sh/do-not-evict": "true"
                    }
                },
                "spec": {
                    "topologySpreadConstraints": [
                        {
                            "maxSkew": 1,
                            "topologyKey": "topology.kubernetes.io/zone",
                            "whenUnsatisfiable": "DoNotSchedule",
                            "labelSelector": {"matchLabels": {"app": "foo"}}
                        }
                    ]
                }
            }
        }
    }
)
```

## Pod Lifecycle & Caching

### Cold Start
1. **Manifest Applied**: Deployment/Service created.
2. **Scheduling**: Pod assigned to node (may trigger autoscaling).
3. **Image Pull**: Container image downloaded.
4. **Startup**: Container starts, installs deps (if dynamic), starts HTTP server.
5. **Rsync**: Code synced to pod.
6. **Ready**: Health check passes.

### Warm Start
1. **Reuse**: Existing pod found.
2. **Rsync**: Only changed files synced (fast).
3. **Hot Reload**: Python module reloaded in-memory.
4. **Ready**: Immediate execution.

### Inactivity TTL
To save costs, set `inactivity_ttl`. A sidecar/controller watches metrics and scales down/deletes services after X minutes of no requests.

```python
kt.Compute(inactivity_ttl="30m")
```

Requires Cluster-side configuration (OpenTelemetry/Prometheus).

## Security

### Serialization
By default, `json` serialization is safe. `pickle` allows arbitrary code execution.
- Restrict allowed serialization on Compute:
  ```python
  kt.Compute(allowed_serialization=["json"])
  ```

### Secrets
Secrets are mounted as K8s Secrets. They are secure in transit and at rest (if K8s encryption enabled).

### Network Policies
Kubetorch pods respect namespace NetworkPolicies. Ensure ingress/egress is allowed for:
- API Server (K8s)
- Rsync pod
- Other workers (for distributed)

## Serialization Details

### Pickle
Uses `dill` (extended pickle) to serialize complex objects (functions, lambdas, classes).
- **Pros**: Works with almost anything.
- **Cons**: Security risk, slower, Python version sensitive.

### JSON
Uses standard `json`.
- **Pros**: Fast, secure, language-agnostic.
- **Cons**: Only supports primitives, lists, dicts.

## Production Best Practices

1. **Freeze Compute**: Use `freeze=True` to disable code syncing/hot reload. Bake code into the Docker image.
2. **Use Docker Images**: Don't rely on runtime `pip install`. Build custom images.
   ```python
   image = kt.Image().from_docker("my-org/production-image:v1.2.3")
   ```
3. **Resource Limits**: Always set memory/CPU limits to prevent noisy neighbor issues.
4. **Health Checks**: Implement robust health checks in your app.
5. **Inactivity TTL**: Set appropriate TTLs to avoid zombie costs.
6. **Namespaces**: Use dedicated namespaces for prod workloads (e.g. `prod-inference`).

