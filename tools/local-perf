#!/bin/sh
# Run performance benchmarks locally.
# This forces the tests to run even outside of CI.
# Pass extra arguments (like -k specific_test) through to pytest without modifying the script.

FORCE_PERF=true uv run pytest tests/test_performance.py -s "$@" > /dev/null
