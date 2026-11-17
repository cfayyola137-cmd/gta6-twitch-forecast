"""Verification script for GTA VI Twitch CCU forecaster (not shipped logic).
Runs main.py over the practice cases and validates output correctness,
determinism, bounds, and ordering.
"""

import os
import sys
import json
import math
import subprocess
from pathlib import Path

KIT_INPUT = "/root/makefun/gta6-twitch-ccu-forecast-01-kit/input"
TMP_OUT1 = "/root/makefun/gta6-entry/tmp_out1"
TMP_OUT2 = "/root/makefun/gta6-entry/tmp_out2"


def run_main(input_dir: str, output_dir: str) -> None:
    env = os.environ.copy()
    env["MAKEFUN_INPUT_DIR"] = str(input_dir)
    env["MAKEFUN_OUTPUT_DIR"] = str(output_dir)
    res = subprocess.run(
        [sys.executable, "main.py"],
        env=env,
        capture_output=True,
        text=True
    )
    if res.returncode != 0:
        print(f"main.py failed with return code {res.returncode}")
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
        sys.exit(1)


def verify() -> None:
    print("Running verification across practice cases...")
    run_main(KIT_INPUT, TMP_OUT1)
    run_main(KIT_INPUT, TMP_OUT2)

    out1_files = sorted(Path(TMP_OUT1).glob("*.out"))
    out2_files = sorted(Path(TMP_OUT2).glob("*.out"))

    assert len(out1_files) > 0, "No output files generated"
    assert len(out1_files) == len(out2_files), "Output file counts differ between runs"

    for f1, f2 in zip(out1_files, out2_files):
        assert f1.name == f2.name
        content1 = f1.read_bytes()
        content2 = f2.read_bytes()
        assert content1 == content2, f"Outputs for {f1.name} are non-deterministic (differ between runs)"

        data = json.loads(content1.decode("utf-8"))
        assert list(data.keys()) == ["hours"], f"Invalid keys in {f1.name}: {list(data.keys())}"
        hours = data["hours"]
        assert len(hours) == 23, f"Expected 23 hours, got {len(hours)} in {f1.name}"

        expected_hours = list(range(2, 25))
        actual_hours = [row["hour"] for row in hours]
        assert actual_hours == expected_hours, f"Hours mismatch: {actual_hours}"

        for row in hours:
            h = row["hour"]
            q = row["q"]
            assert isinstance(q, list) and len(q) == 5, f"Hour {h}: q must be a list of 5 elements"
            for val in q:
                assert math.isfinite(val), f"Hour {h}: quantile {val} is not finite"
                assert 0 < val <= 1e9, f"Hour {h}: quantile {val} out of range (0, 1e9]"
            for i in range(1, len(q)):
                assert q[i] >= q[i - 1], f"Hour {h}: quantiles not non-decreasing: {q}"

    print("Verification PASSED: All outputs valid, bounded, ordered, and deterministic.")


if __name__ == "__main__":
    verify()
