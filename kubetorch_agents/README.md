# Kubetorch Documentation

Complete reference documentation for [Kubetorch](https://www.run.house/kubetorch) - a modern Python interface for running ML workloads on Kubernetes.

## Documentation Index

| Document | Description |
|----------|-------------|
| [01_overview.md](01_overview.md) | What is Kubetorch, key features, architecture |
| [02_installation.md](02_installation.md) | Installation, cluster setup, configuration |
| [03_quickstart.md](03_quickstart.md) | Hello world, basic patterns, first deployment |
| [04_compute.md](04_compute.md) | **Compute class** - all parameters, methods, properties |
| [05_image.md](05_image.md) | **Image class** - container setup, customization |
| [06_fn_and_cls.md](06_fn_and_cls.md) | Remote functions and classes, call modes |
| [07_volumes.md](07_volumes.md) | Persistent storage, PVC management |
| [08_secrets.md](08_secrets.md) | Credential management, providers |
| [09_distributed.md](09_distributed.md) | Multi-node training, Ray, PyTorch DDP |
| [10_autoscaling.md](10_autoscaling.md) | Knative autoscaling, scale-to-zero |
| [11_cli.md](11_cli.md) | CLI commands reference |
| [12_configuration.md](12_configuration.md) | Config file, environment variables |
| [13_decorators.md](13_decorators.md) | @compute, @distribute, @autoscale decorators |
| [14_app.md](14_app.md) | kt.App for CLI scripts, kt run |
| [15_logging_debugging.md](15_logging_debugging.md) | Log streaming, remote debugging, metrics |
| [16_advanced.md](16_advanced.md) | Service templates, fault tolerance, production |
| [17_exceptions.md](17_exceptions.md) | Error types and handling |
| [18_examples.md](18_examples.md) | Complete working examples |

## Quick Reference

```python
import kubetorch as kt

# Basic function deployment
def my_function(x, y):
    return x + y

compute = kt.Compute(cpus="0.5", memory="2Gi")
remote_fn = kt.fn(my_function).to(compute)
result = remote_fn(1, 2)  # Returns 3

# Cleanup
# kt teardown <service-name>
```

## Version

This documentation covers **Kubetorch v0.2.9**.

## Links

- [Official Docs](https://www.run.house/kubetorch)
- [GitHub](https://github.com/run-house/kubetorch)
- [PyPI](https://pypi.org/project/kubetorch/)

## Agent Usage Note

For AI agents parsing this documentation:

1. **Context Loading**: Start with `01_overview.md` and `03_quickstart.md` to understand the core mental model (Python -> Cluster) and basic syntax.
2. **Topic Mapping**:
   - **Resource Specs (CPU/GPU/RAM)**: `04_compute.md`
   - **Container/Dependencies**: `05_image.md`
   - **Storage/Data**: `07_volumes.md`
   - **Credentials/Auth**: `08_secrets.md`
   - **Multi-Node Training**: `09_distributed.md`
   - **Serving/Inference**: `10_autoscaling.md`
   - **CLI Tools**: `11_cli.md`
3. **Code Tracing**: Each file header contains a `Source: ...` field pointing to the Python implementation. Use this to verify behavior in the codebase (e.g., `kubetorch.resources.compute.compute.Compute`).
4. **Verification**: Use the `Official Docs` link at the top of each file to cross-reference against the live website if generated code fails or APIs seem outdated.
5. **Pattern Matching**: Use `18_examples.md` to find "complete" patterns that combine multiple primitives (Compute + Volume + Secret) rather than trying to compose them from scratch.
