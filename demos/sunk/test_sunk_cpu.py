"""Test SUNK scheduler with CPU only."""

import kubetorch as kt


def test_sunk():
    import socket

    return f"Running on {socket.gethostname()} via SUNK!"


if __name__ == "__main__":
    # SUNK scheduler with CPU only
    compute = kt.Compute(
        cpus="0.5",
        memory="1Gi",
        namespace="tenant-slurm",
        launch_timeout=30,
        inactivity_ttl="10m",
        service_template={
            "spec": {
                "template": {
                    "spec": {
                        "schedulerName": "tenant-slurm-slurm-scheduler",
                        "terminationGracePeriodSeconds": 5,  # SUNK requires < KillWait - 5s
                    }
                }
            }
        },
        annotations={
            "sunk.coreweave.com/account": "root",
            "sunk.coreweave.com/comment": "CPU test via SUNK",
        },
    )

    print("Testing SUNK scheduler with CPU...")
    remote = kt.fn(test_sunk, name="sunk_cpu").to(compute)
    print(remote())
