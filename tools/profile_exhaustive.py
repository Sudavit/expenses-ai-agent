import pyinstrument

# replace AI.main by the directory containing main.py
from expenses_ai_agent.main import main

# for example, if it's src/foo/main.py,
# this becomes "from foo.main import main"

# use whatever test args you need to get an exhaustive pofile.


def profile_exhaustive():
    # list args you want to call main with here, like this:
    #   test_args = ["-n", "9", "--stat", "cycle-counts"]
    test_args = None

    profiler = pyinstrument.Profiler()

    print("🚀 Starting Profiling Expedition '{test_args}' ...")

    profiler.start()
    try:
        main(test_args)
    finally:
        profiler.stop()

    # Output the results to the console
    print("\n--- 📊 Profiling Results ---")
    profiler.print()


if __name__ == "__main__":
    profile_exhaustive()
