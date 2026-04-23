import json
import os
import time
from datetime import UTC, datetime

import pytest

from expenses_ai_agent.main import main as benchmark  # change AI to name of project.

# Change the skip logic and the environment tag
is_ci = os.getenv("GITHUB_ACTIONS") == "true"
is_forced = os.getenv("FORCE_PERF") == "true"


@pytest.mark.skipif(not (is_ci or is_forced), reason="Performance test")
def test_performance_heavy_sampling():
    env_name = "GitHub Runner" if is_ci else "Local Laptop"
    start = time.perf_counter()
    samples = 10_000  # run 10_000 times
    arg_string = None  # or a list of strings, if you want it to have arguments
    for i in range(samples):  # run it 1000 times
        benchmark(arg_string)
    end = time.perf_counter()
    print(f"Benchmark took {end - start:.4f}s")
    duration = end - start
    # Create a results dictionary
    results = {
        "timestamp": datetime.now(UTC).isoformat(),  # Forced UTC
        "duration": duration,
        "n": 10,
        "samples": samples,
        "environment": env_name,
    }

    # Append to a local file
    with open("benchmark_history.jsonl", "a") as f:
        f.write(json.dumps(results) + "\n")
