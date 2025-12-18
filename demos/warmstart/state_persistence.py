"""Demo: State persists between function calls.

Global variables on the pod survive between calls - useful for caching,
loaded models, or accumulating results.
"""
# This cache lives on the pod and persists between calls
CACHE = {}
CALL_COUNT = 0


def cache_operation(action: str, key: str = None, value: str = None):
    """Interact with the persistent cache on the pod."""
    global CACHE, CALL_COUNT
    CALL_COUNT += 1
    
    if action == "set" and key and value:
        CACHE[key] = value
        return f"[Call #{CALL_COUNT}] Set {key}={value}. Cache now: {CACHE}"
    
    elif action == "get" and key:
        val = CACHE.get(key, "NOT FOUND")
        return f"[Call #{CALL_COUNT}] Get {key}={val}. Cache: {CACHE}"
    
    elif action == "list":
        return f"[Call #{CALL_COUNT}] Cache contents: {CACHE}"
    
    elif action == "clear":
        CACHE.clear()
        return f"[Call #{CALL_COUNT}] Cache cleared!"
    
    return f"[Call #{CALL_COUNT}] Unknown action: {action}"


if __name__ == "__main__":
    import kubetorch as kt
    import sys

    compute = kt.Compute(cpus="0.1", labels={"demo": "state-persistence"})
    remote_fn = kt.fn(cache_operation, name="warmstart_state").to(compute)  # separate - needs isolated state
    
    # Parse command line args
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python state_persistence.py set <key> <value>")
        print("  python state_persistence.py get <key>")
        print("  python state_persistence.py list")
        print("  python state_persistence.py clear")
        print("\nExample:")
        print("  python state_persistence.py set name Alice")
        print("  python state_persistence.py set color blue")
        print("  python state_persistence.py list")
        print("  python state_persistence.py get name")
        sys.exit(0)
    
    action = sys.argv[1]
    key = sys.argv[2] if len(sys.argv) > 2 else None
    value = sys.argv[3] if len(sys.argv) > 3 else None
    
    result = remote_fn(action, key, value)
    print(result)

