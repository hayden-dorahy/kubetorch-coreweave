import kubetorch as kt


def hello_world():
    import platform
    return f"Hello from Kubetorch! Running on {platform.node()}"


if __name__ == "__main__":
    # Define compute (CPU only for testing)
    compute = kt.Compute(cpus="0.1")

    # Send function to cluster
    remote_fn = kt.fn(hello_world).to(compute)

    # Run remotely
    result = remote_fn()
    print(result)

