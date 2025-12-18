import kubetorch as kt


def list_data():
    """List contents of the mounted PVC"""
    import os
    import subprocess
    
    mount_path = "/mnt/data"
    
    # Check if mounted
    if not os.path.exists(mount_path):
        return f"Mount path {mount_path} does not exist!"
    
    # List contents
    # List top-level
    result = subprocess.run(["ls", "-la", mount_path], capture_output=True, text=True)
    output = f"Contents of {mount_path}:\n{result.stdout}\n"
    
    # Check datasets folder
    datasets_path = os.path.join(mount_path, "datasets")
    if os.path.exists(datasets_path):
        result2 = subprocess.run(["ls", "-la", datasets_path], capture_output=True, text=True)
        output += f"\nContents of {datasets_path}:\n{result2.stdout}"
    
    return output


if __name__ == "__main__":
    # Load existing slurm-data PVC
    vol = kt.Volume.from_name(
        name="slurm-data",
        namespace="tenant-slurm",
        mount_path="/mnt/data"
    )

    # Deploy to tenant-slurm namespace (where PVC lives)
    compute = kt.Compute(
        cpus="0.1",
        namespace="tenant-slurm",
        volumes=[vol]
    )

    print("Deploying to tenant-slurm with slurm-data PVC mounted...")
    remote_fn = kt.fn(list_data).to(compute)
    result = remote_fn()
    print(result)

