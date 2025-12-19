import kubetorch as kt


def hello_world():
    import platform

    return f"Hello from Kubetorch! Running on {platform.node()}"


if __name__ == "__main__":
    # Define compute (CPU only for testing)
    compute = kt.Compute(cpus="0.1", launch_timeout=60).autoscale(
        min_scale=0,  # Scale to zero when idle
        max_scale=1,  # Max pods for concurrent requests
        concurrency=1,  # 1 request per pod (critical for GPU inference)
        scale_to_zero_pod_retention_period="30s",  # Fast for dev (default 10m)
    )

    # Send function to cluster (shared pod for basics demos)
    remote_fn = kt.fn(hello_world, name="basics").to(compute)

    # Run remotely
    result = remote_fn()
    print(result)
