# CLI Reference

> **Official Docs:** [CLI API Reference](https://www.run.house/kubetorch/api-reference/cli)
> **Source:** `kubetorch.cli`

Kubetorch includes a powerful CLI tool `kt` (provided by `kubetorch[client]`).

## General Commands

### `kt list`
List all active Kubetorch services.

```bash
kt list
# Shows: Name | Namespace | Type | URL | Status
```

### `kt check <name>`
Run health checks on a service.

```bash
kt check my-service
# Checks: Pod status, Rsync status, HTTP endpoint, GPU config
```

### `kt describe <name>`
Show detailed information about a service.

```bash
kt describe my-service
# Shows: Resources, Image, Endpoints, Events
```

### `kt logs <name>`
Stream logs from a service.

```bash
kt logs my-service
kt logs my-service --tail 100 --follow
```

### `kt teardown`
Delete services.

```bash
kt teardown my-service           # Delete specific
kt teardown --all                # Delete all YOUR services
kt teardown --prefix experiment- # Delete matching prefix
```

## Access Commands

### `kt ssh <name>`
Open an interactive shell in the service pod.

```bash
kt ssh my-service
```

### `kt port-forward <name>`
Forward a local port to the service.

```bash
kt port-forward my-service 8080:80
```

## Configuration Commands

### `kt config`
Manage `~/.kt/config.yaml`.

```bash
kt config list                   # Show all config
kt config get username           # Get value
kt config set username alice     # Set value
kt config unset queue            # Unset value
```

## Running Code

### `kt run`
Run a script or command on the cluster.

```bash
# Run python script
kt run python train.py --epochs 10

# Run with specific resources
kt run python train.py --gpus 1 --cpus 4 --name my-run

# Run any command
kt run "ls -la /data"
```

Requires `kt.app()` defined in the script or default configuration.

### `kt deploy`
Deploy functions/classes decorated with `@kt.compute` in a file.

```bash
kt deploy my_app.py
```

This deploys the services but doesn't run them immediately (services wait for HTTP requests).

## Internal Commands (Debug)

### `kt server`
Starts the Kubetorch HTTP server (runs inside the pod).

### `kt rsync`
Starts the rsync server (runs inside the rsync pod).

