"""Demo: Knative autoscaling with concurrent ML inference requests.

This shows how Knative scales pods based on request concurrency:
- Starts with 0 pods
- Scales up when concurrent requests arrive
- Scales back to 0 when idle

Example:
    python demos/advanced/autoscale_demo.py
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import kubetorch as kt


def predict(input_data: dict) -> dict:
    """Simulate ML inference (e.g., image classification).

    Takes 5 seconds per request to simulate GPU model inference time.
    This is slow enough that Knative will scale up for concurrent requests.
    """
    import socket
    import time

    # Simulate inference time (5 seconds like a real GPU model)
    time.sleep(5)

    return {
        "input_id": input_data.get("id", 0),
        "prediction": f"class_{input_data.get('id', 0) % 10}",
        "confidence": 0.95,
        "pod": socket.gethostname(),
    }


def run_autoscale_demo():
    """Run the autoscaling demo."""

    # Configure autoscaling:
    # - min_scale=0: Can scale to zero when idle
    # - max_scale=3: Up to 3 pods for concurrent requests
    # - concurrency=1: ONLY 1 request per pod at a time (forces scale-up!)
    #   This is typical for GPU inference where you can't share the GPU
    # - Fast scale-to-zero for demo purposes
    compute = kt.Compute(
        cpus="0.5",
        memory="1Gi",
        launch_timeout=180,
    ).autoscale(
        min_scale=0,
        max_scale=3,
        concurrency=1,  # Key! Forces 1 request per pod - triggers scale-up
        scale_to_zero_pod_retention_period="30s",
        scale_down_delay="0s",
    )

    remote_predict = kt.fn(predict, name="ml_autoscale").to(compute)

    print("\n" + "=" * 60)
    print("AUTOSCALE DEMO: ML Inference with Concurrent Requests")
    print("=" * 60)

    # Phase 1: Single request (cold start)
    print("\n📍 Phase 1: Single request (cold start from 0 pods)")
    print("-" * 40)
    start = time.time()
    result = remote_predict({"id": 1})
    print(f"   Result: {result}")
    print(f"   Time: {time.time() - start:.1f}s (includes cold start)")

    # Phase 2: Concurrent requests (should scale up)
    print("\n📍 Phase 2: 3 concurrent requests (should scale to 3 pods)")
    print("-" * 40)
    print("   With concurrency=1, each pod handles only 1 request at a time.")
    print("   Knative MUST scale up to handle concurrent requests.\n")

    inputs = [{"id": i} for i in range(3)]
    start = time.time()

    # Send 3 requests concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(remote_predict, inp) for inp in inputs]
        results = []
        for future in as_completed(futures):
            results.append(future.result())

    # Show which pods handled requests
    pods_used = set(r["pod"] for r in results)
    elapsed = time.time() - start
    print(f"   Results: {len(results)} predictions completed")
    print(f"   Pods used: {len(pods_used)} unique pods")
    for pod in pods_used:
        count = sum(1 for r in results if r["pod"] == pod)
        print(f"     - {pod} ({count} requests)")
    print(f"   Total time: {elapsed:.1f}s")
    print("\n   Analysis:")
    print("   - Sequential (1 pod): would take ~15s (3 × 5s)")
    print("   - Parallel (3 pods): ~5-8s (all run simultaneously)")
    print(f"   - We took: {elapsed:.1f}s")

    # Phase 3: Wait for scale-down
    print("\n📍 Phase 3: Waiting for scale-to-zero (~45s)")
    print("-" * 40)
    print("   Pods will terminate after 30s idle + graceful shutdown...")
    print("   (Check with: kubectl get pods | grep autoscale)")

    print("\n" + "=" * 60)
    print("Demo complete! Use 'kt teardown hayden-mlautoscale' to clean up.")
    print("=" * 60)


if __name__ == "__main__":
    run_autoscale_demo()
