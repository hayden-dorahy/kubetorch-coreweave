# Secrets

> **Official Docs:** [Supporting Primitives](https://www.run.house/kubetorch/concepts/supporting-primitives)
> **Source:** `kubetorch.resources.secrets.secret.Secret`

Kubetorch `Secret` manages sensitive data like API keys, credentials, and tokens. It wraps Kubernetes Secrets and provides convenient providers for common services.

## Constructor

```python
kt.Secret(
    name: str = None,           # Secret name
    provider: str = None,       # Provider name (e.g. "aws", "gcp")
    values: Dict = None,        # Key-value pairs
    path: str = None,           # Path to secret file/directory
    env_vars: Dict = None,      # Env var mapping
    override: bool = False,     # Overwrite existing K8s secret
    namespace: str = None,      # K8s namespace
)
```

## Creating Secrets

### 1. From Built-in Providers

Kubetorch has built-in providers that know where to look for credentials (e.g., `~/.aws/credentials`).

```python
# AWS credentials (~/.aws/credentials)
aws_secret = kt.Secret.from_provider("aws")

# HuggingFace token (~/.cache/huggingface/token)
hf_secret = kt.Secret.from_provider("huggingface")

# GitHub token (GH_TOKEN env var or gh CLI config)
gh_secret = kt.Secret.from_provider("github")
```

**Supported Providers:**
- `anthropic`
- `aws`
- `azure`
- `cohere`
- `gcp`
- `github`
- `huggingface`
- `lambda`
- `langchain`
- `openai`
- `pinecone`
- `ssh`
- `wandb`
- `kubeconfig`

### 2. From Environment Variables

```python
# Map local env vars to secret keys
secret = kt.Secret.from_env(
    name="my-api-keys",
    env_vars={
        "API_KEY": "MY_LOCAL_API_KEY_VAR",  # Key in secret -> Local env var
        "DB_PASS": "DB_PASSWORD"
    }
)
```

### 3. From Local Path

```python
# Create secret from file contents
secret = kt.Secret.from_path(
    path="~/.my-app/config.json",
    name="app-config"
)
```

### 4. From Values (Dict)

```python
# Direct values (be careful not to commit secrets!)
secret = kt.Secret(
    name="manual-secret",
    values={"password": "super-secret-value"}
)
```

### 5. From Existing K8s Secret

```python
secret = kt.Secret.from_name("existing-k8s-secret")
```

---

## Using Secrets with Compute

Pass the `Secret` object or its name (string) to `kt.Compute`.

```python
compute = kt.Compute(
    cpus="1",
    secrets=[
        kt.Secret.from_provider("aws"),     # Automatically mounts credentials
        "existing-k8s-secret",              # Existing secret
    ]
)
```

### How Secrets are Mounted

#### Provider Secrets
Each provider has a default behavior:
- **AWS**: Mounts to `~/.aws/credentials`
- **HuggingFace**: Sets `HF_TOKEN` env var
- **OpenAI**: Sets `OPENAI_API_KEY` env var
- **SSH**: Mounts keys to `~/.ssh/`

#### Generic Secrets
- **Env Vars**: If created via `from_env` or with specific keys, values are injected as environment variables.
- **Files**: If created via `from_path`, files are mounted at `/secrets/<secret-name>/`.

---

## Examples

### AWS + HuggingFace Training

```python
aws_secret = kt.Secret.from_provider("aws")
hf_secret = kt.Secret.from_provider("huggingface")

compute = kt.Compute(
    gpus=1,
    secrets=[aws_secret, hf_secret],
    env_vars={"HF_HOME": "/cache/huggingface"}  # Use with volume for caching
)

def train():
    # Can now access S3 and private HF models
    import boto3
    from transformers import AutoModel
    
    s3 = boto3.client("s3")
    model = AutoModel.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
    return "Success"
```

### SSH Key for Git Access

```python
# Mounts ~/.ssh/id_rsa (or similar) to remote pod
ssh_secret = kt.Secret.from_provider("ssh")

image = (
    kt.images.Debian()
    .run_bash("apt-get update && apt-get install -y git")
    .run_bash("mkdir -p ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts")
)

compute = kt.Compute(
    cpus="1",
    image=image,
    secrets=[ssh_secret]
)

def git_clone():
    import subprocess
    # Can clone private repos
    subprocess.run(["git", "clone", "git@github.com:my-org/private-repo.git"])
```

### Custom API Key

```python
import os

# Create secret from local env var
api_key_secret = kt.Secret.from_env(
    name="my-api-key",
    env_vars={"API_KEY": "LOCAL_API_KEY_VAR"}
)

compute = kt.Compute(
    cpus="1",
    secrets=[api_key_secret]
)

def call_api():
    key = os.environ["API_KEY"]
    # ... use key
```

---

## Provider Details

### `aws`
- **Source**: `~/.aws/credentials`, `~/.aws/config`, or `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` env vars
- **Target**: Mounted to `~/.aws/` in container
- **Env Vars**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (if available)

### `gcp`
- **Source**: `gcloud` CLI application default credentials
- **Target**: Mounted JSON key file + `GOOGLE_APPLICATION_CREDENTIALS` env var

### `huggingface`
- **Source**: `~/.cache/huggingface/token` or `HF_TOKEN` env var
- **Target**: `HF_TOKEN` env var in container

### `wandb`
- **Source**: `~/.netrc` or `WANDB_API_KEY` env var
- **Target**: `WANDB_API_KEY` env var in container

### `ssh`
- **Source**: `~/.ssh/id_rsa`, `~/.ssh/id_ed25519`
- **Target**: `~/.ssh/` in container

---

## Best Practices

1. **Never commit secrets** to code. Use providers or env vars.
2. **Use overrides** carefully. `override=True` will update the K8s secret.
3. **Namespace isolation**. Secrets are namespaced. Ensure your Compute namespace matches.
4. **Least privilege**. Only mount necessary secrets.

