"""Demo: Advanced Resource Requests.

Request specific memory, disk, and shared memory sizes.
"""

import kubetorch as kt


def check_resources():
    import os
    import shutil

    # Check Memory (cgroup limit might be tricky to read, checking /proc/meminfo)
    # Note: /proc/meminfo shows node memory, not container limit, unless lxcfs is used.
    # But we can check /dev/shm size

    total, used, free = shutil.disk_usage("/dev/shm")
    shm_size_gb = total / (1024**3)

    total_disk, _, _ = shutil.disk_usage("/")
    disk_size_gb = total_disk / (1024**3)

    return {
        "shm_size_gb": f"{shm_size_gb:.2f} GB",
        "disk_size_gb": f"{disk_size_gb:.2f} GB (approx node/overlay size)",
        "cpu_count": os.cpu_count(),
    }


if __name__ == "__main__":
    compute = kt.Compute(
        cpus="1",
        memory="2Gi",
        disk_size="5Gi",  # Ephemeral storage request
        shared_memory_limit="1Gi",  # /dev/shm size (important for PyTorch loaders)
        launch_timeout=60,
        inactivity_ttl="10m",
    )

    print("Deploying with custom resources (1GB /dev/shm)...")
    remote_fn = kt.fn(check_resources, name="advanced_resources").to(compute)

    result = remote_fn()
    print(result)
