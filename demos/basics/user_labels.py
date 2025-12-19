"""Test labels in Kubetorch."""

import kubetorch as kt


def hello_with_labels():
    return "hello with labels!"


if __name__ == "__main__":
    compute = kt.Compute(
        cpus="0.1",
        launch_timeout=60,
        labels={"user": "hayden", "team": "research"},
    )

    remote = kt.fn(hello_with_labels, name="basics_labels").to(compute)
    print(remote())
