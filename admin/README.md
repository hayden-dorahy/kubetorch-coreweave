# Admin / Infrastructure

Cluster administration files. Regular users shouldn't need to modify these.

## Contents

| File | Description |
|------|-------------|
| `helmfile.yaml` | Kubetorch Helm chart deployment |
| `docs/kubetorch_setup.md` | Full Kubetorch installation guide |
| `docs/coreweave_k8s.md` | CoreWeave cluster connection notes |

## Deploying/Updating Kubetorch

```bash
cd admin/
helmfile sync        # Deploy
helmfile diff        # Preview changes
helmfile destroy     # Remove
```

## Key Config

The `helmfile.yaml` sets:
- DNS resolver: `coredns.kube-system.svc.cluster.local`
- Allowed namespaces: `default`, `kubetorch`, `tenant-slurm`

