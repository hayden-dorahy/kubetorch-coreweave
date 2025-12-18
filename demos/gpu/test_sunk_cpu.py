"""Test SUNK scheduler with CPU only."""
import kubetorch as kt


def check_sunk():
    import socket
    return f"Running on {socket.gethostname()} via SUNK scheduler!"


if __name__ == "__main__":
    # SUNK scheduler config
    service_template = {
        "spec": {
            "template": {
                "spec": {
                    "schedulerName": "tenant-slurm-slurm-scheduler"
                }
            }
        }
    }

    sunk_annotations = {
        "sunk.coreweave.com/account": "root",
        "sunk.coreweave.com/comment": "Kubetorch CPU test via SUNK",
    }

    compute = kt.Compute(
        cpus="0.1",
        namespace="tenant-slurm",
        annotations=sunk_annotations,
        service_template=service_template,
    )

    print("Testing SUNK scheduler with CPU...")
    remote_fn = kt.fn(check_sunk, name="sunk_cpu").to(compute)
    result = remote_fn()
    print(result)

