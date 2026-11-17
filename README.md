# gta6-twitch-forecast

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/cfayyola137-cmd/gta6-twitch-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/cfayyola137-cmd/gta6-twitch-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Hour-by-hour probabilistic forecast of Twitch's "Grand Theft Auto VI" category viewers on
release day, 2026-11-19 (UTC). One hour into the launch day, the program reads the case it is
given — the category's 14-day history, the hour-1 viewer count, and ~40 comparable game launches'
release-day curves — and writes five quantiles (5%, 25%, 50%, 75%, 95%) of the mean concurrent
viewers for each of hours 2 to 24.

## Model

1. Every comparable launch's release day is reduced to an hourly curve; each curve is divided by
   its own hour-1 count, so the curves become shape ratios relative to the launch's opening hour.
2. Per horizon, the median ratio across comparables is the forecast's center (a robust estimate:
   a launch day's shape is far more stable than its absolute size), smoothed over a five-hour
   window.
3. Per horizon, the spread is the median absolute log residual of those curves around the median
   ratio, scaled by 1.35 and a widening factor (capped), so the quantiles widen with the horizon.
4. Quantiles are `p50 * exp(z_tau * sigma_h)` in log space; they are rounded half-up, clamped and
   forced non-decreasing. With fewer than five usable comparables the program falls back to the
   house persistence formula (hour 1 held flat, random-walk spread).

Python 3.13, standard library only, offline, deterministic, well under the 8-second budget.

## Run it

```sh
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
