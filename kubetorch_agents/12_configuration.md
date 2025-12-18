# Configuration

> **Source:** `kubetorch.config.KubetorchConfig`, `kubetorch.globals`

Kubetorch uses a hierarchical configuration system:
1. Method Arguments (e.g. `kt.Compute(namespace=...)`)
2. Environment Variables
3. Config File (`~/.kt/config.yaml`)
4. Defaults

## Config File: `~/.kt/config.yaml`

Created automatically. Manage with `kt config` CLI.

```yaml
username: hayden
license_key: xyz...
namespace: default
queue: research-queue
stream_logs: true
stream_metrics: true
install_namespace: kubetorch
```

## Environment Variables

All variables are prefixed with `KT_`.

| Variable | Config Key | Description |
|----------|------------|-------------|
| `KT_USERNAME` | `username` | User identifier for service naming |
| `KT_LICENSE_KEY` | `license_key` | License key |
| `KT_NAMESPACE` | `namespace` | Target K8s namespace |
| `KT_QUEUE` | `queue` | Default KAI scheduler queue |
| `KT_STREAM_LOGS` | `stream_logs` | Enable/disable log streaming (true/false) |
| `KT_STREAM_METRICS` | `stream_metrics` | Enable/disable metrics (true/false) |
| `KT_INSTALL_NAMESPACE` | `install_namespace` | Where operator is installed |
| `KT_API_URL` | `api_url` | External ingress URL (if using ingress) |
| `KT_CLUSTER_CONFIG` | `cluster_config` | JSON dict of cluster-specific settings |
| `KUBECONFIG` | - | Path to Kubeconfig file |

## Other Environment Variables

These affect runtime behavior but aren't in the config file:

- `KT_LAUNCH_TIMEOUT`: Seconds to wait for pod startup (default 900)
- `KT_LOG_LEVEL`: Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `KT_GPU_ANTI_AFFINITY`: Prevent scheduling on GPU nodes if no GPU requested (`true`/`false`)
- `KT_DEBUG_MODE`: Enable debug logging/features

## Cluster Config (`cluster_config`)

A JSON dictionary stored in config or env var for advanced cluster settings:

```json
{
  "otel_enabled": true,
  "ingress_host": "kubetorch.mycompany.com"
}
```

## Resolution Logic

When you call `kt.Compute(namespace=None)`:
1. Checks `namespace` arg (None)
2. Checks `KT_NAMESPACE` env var
3. Checks `namespace` in `~/.kt/config.yaml`
4. Checks current context in `~/.kube/config`
5. Defaults to `"default"`

