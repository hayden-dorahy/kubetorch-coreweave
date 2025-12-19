# Development Workflows

> **Source**: [Access SUNK](https://docs.coreweave.com/docs/products/sunk/access_sunk), [Tunnel VS Code](https://docs.coreweave.com/docs/products/sunk/access_sunk/tunnel-vs-code), [Use scrontab](https://docs.coreweave.com/docs/products/sunk/run_workloads/use-scrontab-to-schedule-recurring-batch-jobs), [Profile Python applications](https://docs.coreweave.com/docs/products/sunk/tutorials/profile-python-applications-on-sunk)

## Interactive Development (VS Code)

Developing directly on the cluster is a common requirement. SUNK supports this primarily via the **Login Nodes**.

### VS Code Remote - SSH

Since Login Nodes are exposed via standard SSH (typically on a LoadBalancer IP), you can use the VS Code "Remote - SSH" extension.

1.  **Get Login IP**:
    ```bash
    kubectl get svc -n sunk -l app=slurm-login
    # Or asking your admin for the "Login Node IP"
    ```
2.  **Configure SSH Config**:
    ```ssh
    Host sunk-login
        HostName <LOAD_BALANCER_IP>
        User <YOUR_USERNAME>
        IdentityFile ~/.ssh/id_rsa
    ```
3.  **Connect**: Open VS Code -> Remote Explorer -> Connect to Host -> `sunk-login`.

**Best Practice**: Do **not** run heavy compute on the login node. Use it only for editing, git operations, and submitting jobs.

### VS Code Tunnels (Alternative)

If direct SSH is restricted (e.g., behind a firewall requiring VPN), you can use [VS Code Tunnels](https://code.visualstudio.com/docs/remote/tunnels).

1.  SSH into the login node (via bastion/VPN).
2.  Run `code tunnel`.
3.  Connect via `vscode.dev` or the VS Code desktop client using the tunnel ID.

## Profiling Applications

Profiling high-performance applications on SUNK is done using standard NVIDIA tools, but you must ensure the container has the necessary privileges and tools installed.

### NVIDIA Nsight Systems (`nsys`)

1.  **Container Support**: Ensure your image has `nsys` installed (standard in CoreWeave base images).
2.  **Privileges**: Profiling often requires access to hardware counters.
    -   In `nodeDefinitions`, you might need to ensure `securityContext.privileged` is effectively allowed or specific capabilities (`SYS_ADMIN`) are granted, though standard user-space profiling usually works without root.
3.  **Job Submission**:
    ```bash
    #!/bin/bash
    #SBATCH --job-name=profile
    #SBATCH --gres=gpu:1

    # Run nsys outputting to the shared home directory
    srun nsys profile -o /home/myuser/profiles/my_profile_%p \
         python train.py
    ```
4.  **Analysis**: Copy the `.nsys-rep` file back to your local machine (via `scp` or `rsync` from the login node) and view it in the Nsight Systems GUI.

## Recurring Jobs (`scrontab`)

SUNK enables the Slurm `scrontab` command, allowing users to schedule recurring cron-like jobs managed by Slurm.

-   **Usage**:
    ```bash
    scrontab -e
    ```
-   **Format**: Standard cron format, but lines are Slurm job submissions.
    ```cron
    # Run a cleanup script every morning at 3 AM
    0 3 * * * sbatch /home/myuser/scripts/daily_cleanup.sh
    ```
-   **Backend**: These are tracked by the Slurm Controller and persist across controller restarts.

## Interactive Debugging

To debug a running job or a specific node environment:

1.  **Interactive Job**:
    ```bash
    srun --pty --gres=gpu:1 --image=my-image:latest /bin/bash
    ```
    This gives you a shell *inside* a compute pod with GPUs attached.

2.  **Attaching to a Pod (Admin/Advanced)**:
    If you have K8s access, you can `kubectl exec` into a running compute pod to inspect processes, though this bypasses Slurm's accounting and is purely for debugging.

