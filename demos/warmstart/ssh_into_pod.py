"""Demo: SSH into a running Kubetorch pod.

This script creates a pod and then opens an interactive SSH session
so you can explore the pod's filesystem, check GPU status, etc.
"""


def setup_pod():
    """Just a placeholder to ensure the pod is running."""
    import socket

    return f"Pod ready on {socket.gethostname()}"


if __name__ == "__main__":
    import kubetorch as kt

    print("Creating/connecting to pod...")

    compute = kt.Compute(cpus="0.1", labels={"demo": "ssh"})
    remote_fn = kt.fn(setup_pod, name="warmstart_ssh").to(compute)

    # Ensure pod is ready
    result = remote_fn()
    print(f"✓ {result}")

    print("\n" + "=" * 60)
    print("OPENING SSH SESSION")
    print("=" * 60)
    print("You're now inside the pod. Try:")
    print("  ls /              # See filesystem")
    print("  nvidia-smi        # Check GPU (if available)")
    print("  pip list          # See installed packages")
    print("  cat /proc/cpuinfo # CPU info")
    print("  exit              # Leave SSH session")
    print("=" * 60 + "\n")

    # Open interactive SSH session
    compute.ssh()
