"""GTA VI Twitch CCU forecaster (make.fun bounty entry).

Python 3.13 standard library only, offline, deterministic, <=8s, <=1GB.
Forecasts hours 2..24 of release day as five quantiles of mean concurrent viewers,
using median ratios and robust per-horizon sigma from comparable game launches.
"""

import json
import math
import os
import statistics
import sys
from datetime import datetime
from pathlib import Path

# The grader's -P leaves /bot off sys.path: put it back first.
sys.path.insert(0, str(Path(__file__).resolve().parent))

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z_VALUES = (-1.6448536, -0.6744898, 0.0, 0.6744898, 1.6448536)


def round2(x: float) -> float | int:
    """x rounded to 2 decimals, half up, as JavaScript's Math.round(x * 100) / 100 rounds it."""
    scaled = x * 100
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    value = whole / 100
    return int(value) if value.is_integer() else value


def clamp(val: float, low: float, high: float) -> float:
    return max(low, min(high, val))


def forecast_case(case: dict, name: str) -> dict:
    if case["levels"] != LEVELS:
        raise ValueError(f"{name} asks for levels {case['levels']}, not {LEVELS}")
    first = next((k for k in case["known"] if k["hour"] == 1), None)
    if first is None:
        raise ValueError(f"{name} has no hour-1 print")
    p1 = max(1.0, float(first["viewers"]))

    comparables = case.get("comparables", [])
    kept_curves = []
    for comp in comparables:
        try:
            ds = datetime.fromisoformat(comp["day_start"].replace("Z", "+00:00"))
        except Exception:
            continue
        h_to_viewers = {}
        for pt in comp.get("hourly", []):
            if pt.get("viewers") is None:
                continue
            try:
                ft = datetime.fromisoformat(pt["from"].replace("Z", "+00:00"))
            except Exception:
                continue
            diff_secs = (ft - ds).total_seconds()
            if 0 <= diff_secs < 24 * 3600:
                h = int(diff_secs // 3600) + 1
                if 1 <= h <= 24:
                    h_to_viewers.setdefault(h, []).append(float(pt["viewers"]))
        
        curve = {h: sum(vs) / len(vs) for h, vs in h_to_viewers.items() if vs}
        h1 = curve.get(1, 0.0)
        kept_h2_24 = sum(1 for h in range(2, 25) if h in curve)
        if h1 > 0 and kept_h2_24 >= 20:
            kept_curves.append(curve)

    hours_out = []
    if len(kept_curves) < 5:
        # Fallback: persistence formula with sigma 0.22
        for row in case["forecast"]:
            h = row["hour"]
            q_list = []
            for z in Z_VALUES:
                val = max(1e-6, min(1e9, p1 * math.exp(z * 0.22 * math.sqrt(h - 1))))
                q_list.append(round2(val))
            for i in range(1, len(q_list)):
                if q_list[i] < q_list[i - 1]:
                    q_list[i] = q_list[i - 1]
            hours_out.append({"hour": h, "q": q_list})
    else:
        # ratio[h] for h = 2..24
        ratio = {}
        for h in range(2, 25):
            ratios_h = []
            for curve in kept_curves:
                if 1 in curve and h in curve and curve[1] > 0:
                    ratios_h.append(curve[h] / curve[1])
            if ratios_h:
                ratio[h] = statistics.median(ratios_h)
            else:
                ratio[h] = 1.0

        # smooth ratio over h-2 .. h+2 (values present)
        ratio_smooth = {}
        for h in range(2, 25):
            window_vals = []
            for wh in range(max(2, h - 2), min(24, h + 2) + 1):
                if wh in ratio:
                    window_vals.append(ratio[wh])
            if window_vals:
                ratio_smooth[h] = statistics.mean(window_vals)
            else:
                ratio_smooth[h] = ratio.get(h, 1.0)

        # sigma[h]
        sigma_raw = {}
        for h in range(2, 25):
            r_vals = []
            rh = ratio.get(h, 1.0)
            log_rh = math.log(rh) if rh > 0 else 0.0
            for curve in kept_curves:
                if 1 in curve and h in curve and curve[1] > 0:
                    ch = curve[h] / curve[1]
                    if ch > 0:
                        r = abs(math.log(ch) - log_rh)
                        r_vals.append(r)
            if r_vals:
                sigma_raw[h] = 1.35 * statistics.median(r_vals)
            else:
                sigma_raw[h] = 0.6

        # smooth sigma over h-2 .. h+2 (present values only)
        sigma_smooth = {}
        for h in range(2, 25):
            window_vals = []
            for wh in range(max(2, h - 2), min(24, h + 2) + 1):
                if wh in sigma_raw:
                    window_vals.append(sigma_raw[wh])
            if window_vals:
                sigma_smooth[h] = statistics.mean(window_vals)
            else:
                sigma_smooth[h] = sigma_raw.get(h, 0.6)

        sigma_final = {}
        for h in range(2, 25):
            s = sigma_smooth.get(h, 0.6)
            sigma_final[h] = clamp(s * 1.5, 0.05, 1.6)

        # Forecast
        for row in case["forecast"]:
            h = row["hour"]
            rs = ratio_smooth.get(h, 1.0)
            p50 = p1 * rs
            sig = sigma_final.get(h, 0.6)
            q_list = []
            for z in Z_VALUES:
                val = p50 * math.exp(z * sig)
                val_clamped = max(1e-6, min(1e9, val))
                q_list.append(round2(val_clamped))
            for i in range(1, len(q_list)):
                if q_list[i] < q_list[i - 1]:
                    q_list[i] = q_list[i - 1]
            hours_out.append({"hour": h, "q": q_list})

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
