# PXS GPU Docker Image

Pre-built Docker image for running PXS (PhysicsX) workloads on B200 GPUs via Kubetorch.

## Image Details

- **Registry**: `ghcr.io/physicsxltd/pxs-gpu:latest`
- **Base**: `ghcr.io/coreweave/nccl-tests:13.0.1-devel-ubuntu22.04-nccl2.28.7-1-6b47463`
- **CUDA**: 13.0 (B200/Blackwell support)
- **Python**: 3.11 (via uv)
- **PyTorch**: 2.7.1+cu126
- **PXS**: Latest with Opora and CUDA 12 extras
- **Kubetorch**: Server dependencies included

## Building the Image

### Prerequisites

1. Docker with BuildKit support
2. Artifactory credentials for PXS packages
3. GitHub PAT for pushing to ghcr.io

### Build Steps

```bash
cd /Users/hayden/workspaces/coreweave_poc

# 1. Load Artifactory credentials
source .env.secrets

# 2. Create temporary credentials file for BuildKit secret
echo "$ARTIFACTORY_USER:$ARTIFACTORY_TOKEN" > /tmp/artifactory_creds

# 3. Build the image (use --no-cache to force full rebuild)
DOCKER_BUILDKIT=1 docker build \
  --platform linux/amd64 \
  --secret id=artifactory_creds,src=/tmp/artifactory_creds \
  -f demos/sunk/Dockerfile.pxs \
  -t pxs-gpu:latest \
  demos/sunk/

# 4. Clean up credentials
rm /tmp/artifactory_creds
```

### Testing Locally

```bash
# Verify all dependencies are installed
docker run --rm --platform linux/amd64 pxs-gpu:latest \
  python3 -c "from pythonjsonlogger import jsonlogger; import kubetorch; import pxs; print('All deps OK')"
```

## Pushing to Registry

### Prerequisites

1. Login to ghcr.io:
   ```bash
   source gh_pat  # or export GH_PAT=...
   echo $GH_PAT | docker login ghcr.io -u <github-username> --password-stdin
   ```

### Push Steps

```bash
# 1. Tag the local image for the registry
docker tag pxs-gpu:latest ghcr.io/physicsxltd/pxs-gpu:latest

# 2. Push to registry
docker push ghcr.io/physicsxltd/pxs-gpu:latest
```

**Important**: Always run `docker tag` before `docker push` to ensure the newly built image is pushed, not a cached old version.

## Using in Kubetorch

**Recommendation**: Use the image digest (SHA) to ensure the cluster pulls the exact image version and avoids caching issues.

1. Get the latest digest:
   ```bash
   docker images --digests ghcr.io/physicsxltd/pxs-gpu:latest
   ```

2. Use it in your script:
   ```python
   import kubetorch as kt

   # Use the pre-built image with specific digest
   image = kt.Image().from_docker(
       "ghcr.io/physicsxltd/pxs-gpu@sha256:<YOUR_DIGEST_HERE>"
   )

   # For private registry, add imagePullSecrets via service_template
   service_template = {
       "spec": {
           "template": {
               "spec": {
                   "imagePullSecrets": [{"name": "ghcr-secret"}],
               }
           }
       }
   }

compute = kt.Compute(
    cpus="16",
    memory="128Gi",
    gpus="1",
    image=image,
    service_template=service_template,
    # ... other config
)
```

### Creating the imagePullSecret

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<github-user> \
  --docker-password=<PAT> \
  -n <namespace>
```

## Dockerfile Explained

The Dockerfile uses BuildKit secrets to securely install PXS without baking credentials into the image:

1. **Base image**: CoreWeave NCCL image with CUDA 13.0
2. **uv**: Fast Python package manager
3. **Python 3.11**: Installed via uv for PXS compatibility
4. **PXS**: Installed with `[opora,cuda-12]` extras using BuildKit secret mount
5. **kubetorch[server]**: Server dependencies for Kubetorch runtime

## Troubleshooting

### Image pull fails with 401 Unauthorized
- Ensure `ghcr-secret` exists in the namespace
- Check that the PAT has `read:packages` scope

### Container crashes with "No module named X"
- The image may be outdated; rebuild with `--no-cache`
- Ensure you tagged and pushed the newly built image

### Cluster uses cached old image
- **Option 1 (Best)**: Use digest instead of `:latest` tag (see above)
- **Option 2**: Force fresh pull via `imagePullPolicy: Always` in `service_template`:
  ```python
  service_template = {
      "spec": {
          "template": {
              "spec": {
                  "containers": [{"name": "kubetorch", "imagePullPolicy": "Always"}],
                  # ...
              }
          }
      }
  }
  ```
- **Option 3**: Delete the deployment and let it re-pull

