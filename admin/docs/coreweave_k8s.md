# CoreWeave


## Kubernetes

### 1. Get Kubeconfig

Create an API token on the [CoreWeave Dashboard](https://console.coreweave.com/tokens) → download the kubeconfig file → save to `~/.kube/config`.

### 2. Connect to Cluster

Set the kubeconfig environment variable:

```bash
# Not needed if using default ~/.kube/config location
# export KUBECONFIG=~/.kube/config
```

> **Fix TLS errors**: If you get certificate errors, add `insecure-skip-tls-verify: true` to the kubeconfig:
>
> ```yaml
> clusters:
>   - cluster:
>       insecure-skip-tls-verify: true  # ← add this line
>       server: https://...
> ```
>
> (Acceptable for POC, not ideal for production.)

Test connection:

```bash
kubectl cluster-info
```

### 3. Explore the Cluster

Check nodes and GPU types:

```bash
kubectl get nodes -o wide
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.labels.gpu\.nvidia\.com/model}{"\t"}{.status.capacity.nvidia\.com/gpu}{"\n"}{end}'
```


## CoreWeave SLURM access (SUNK)

### Create an SSH key (if you don't have one)
```bash
ssh-keygen -t ed25519 -f ~/.ssh/coreweave_usw9b -N ""
```

### Upload your public key to CoreWeave:
1. Copy your public key: `cat ~/.ssh/coreweave_usw9b.pub`
2. Go to [CoreWeave Dashboard](https://console.coreweave.com/)
  - Click on your user icon on the top right
  - **User Settings** → **Slurm Attributes** → **SSH Public Keys**
3. Paste your key and click **Save**

### Connect

> Your username is shown in the CoreWeave dashboard under Slurm Attributes.
```bash
ssh -o IdentitiesOnly=yes -i ~/.ssh/coreweave_usw9b <YOUR-USERNAME>@sunk.poc7aa-usw9b.coreweave.app
```
