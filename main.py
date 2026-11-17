"""GTA VI Twitch CCU forecaster (make.fun bounty entry).

Python 3.13 standard library only, offline, deterministic, <=8s, <=1GB.
Forecasts hours 2..24 of release day as five quantiles of mean concurrent viewers,
using hour 1's viewer count adjusted by empirical median release day shape profiles
derived from comparable game launches.
"""

import json
import math
import os
import sys
from pathlib import Path

# The grader's -P leaves /bot off sys.path: put it back first.
sys.path.insert(0, str(Path(__file__).resolve().parent))

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [-1.645, -0.674, 0, 0.674, 1.645]
SIGMA = 0.20  # Optimized spread parameter

# Empirical median ratio y(h) / y(1) across comparable game launches (hours 2..24)
MEDIAN_RATIOS = {
    2: 0.876,
    3: 0.756,
    4: 0.735,
    5: 0.754,
    6: 0.812,
    7: 0.798,
    8: 0.857,
    9: 0.871,
    10: 0.880,
    11: 0.906,
    12: 0.973,
    13: 1.053,
    14: 1.158,
    15: 1.457,
    16: 1.621,
    17: 1.682,
    18: 1.831,
    19: 2.225,
    20: 2.308,
    21: 2.292,
    22: 2.237,
    23: 2.140,
    24: 1.970,
}


def round2(x: float) -> float | int:
    """x rounded to 2 decimals, half up, as JavaScript's Math.round(x * 100) / 100 rounds it."""
    scaled = x * 100
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    value = whole / 100
    return int(value) if value.is_integer() else value


def hour_quantiles(p1: float, h: int) -> list[float | int]:
    ratio = MEDIAN_RATIOS.get(h, 1.0)
    p50 = p1 * ratio
    qs = []
    for z in Z:
        val = max(1.0, min(1e9, p50 * math.exp(z * SIGMA * math.sqrt(h - 1))))
        qs.append(round2(val))
    # Ensure strict non-decreasing order
    for i in range(1, len(qs)):
        if qs[i] < qs[i - 1]:
            qs[i] = qs[i - 1]
    return qs


def forecast_case(case: dict, name: str) -> dict:
    if case["levels"] != LEVELS:
        raise ValueError(f"{name} asks for levels {case['levels']}, not {LEVELS}")
    first = next((k for k in case["known"] if k["hour"] == 1), None)
    if first is None:
        raise ValueError(f"{name} has no hour-1 print")
    p1 = max(1.0, float(first["viewers"]))
    hours_out = []
    for row in case["forecast"]:
        h = row["hour"]
        hours_out.append({"hour": h, "q": hour_quantiles(p1, h)})
    return {"hours": hours_out}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        forecast = forecast_case(case, path.name)
        (OUTPUT_DIR / f"{path.stem}.out").write_text(
            json.dumps(forecast, separators=(",", ":")) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
