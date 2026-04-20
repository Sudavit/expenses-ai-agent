#! /usr/bin/env python3

import pandas as pd


def analyze_gap(file_path="benchmark_history.jsonl"):
    df = pd.read_json(file_path, lines=True)

    # Filter for the most recent runs with 10k samples
    stats = (
        df.groupby("environment")["duration"]
        .agg(["mean", "std", "count"])
        .reset_index()
    )

    # Calculate the 'Cloud Penalty'
    local_mean = stats.loc[stats["environment"] == "Local Laptop", "mean"].values[0]
    cloud_mean = stats.loc[stats["environment"] == "GitHub Runner", "mean"].values[0]
    penalty = cloud_mean / local_mean

    print("--- PermuStats Hardware Report ---")
    print(stats.to_string(index=False))
    print(f"\nCloud Penalty: {penalty:.2f}x slower than Local")


if __name__ == "__main__":
    analyze_gap()
