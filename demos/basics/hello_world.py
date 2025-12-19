import kubetorch as kt


def hello_world():
    import platform

    return f"Hello from Kubetorch! Running on {platform.node()}"


if __name__ == "__main__":
    # Define compute (CPU only for testing)
    compute = kt.Compute(cpus="0.1", launch_timeout=60, inactivity_ttl="1m")

    # Send function to cluster (shared pod for basics demos)
    remote_fn = kt.fn(hello_world, name="basics").to(compute)

    # Run remotely
    result = remote_fn()
    print(result)
