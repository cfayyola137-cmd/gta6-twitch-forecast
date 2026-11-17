[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/cfayyola137-cmd/gta6-twitch-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/cfayyola137-cmd/gta6-twitch-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/reward?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

# GTA VI Twitch Viewership Forecaster

This program generates hourly probabilistic forecasts of concurrent viewership (CCU) for the Grand Theft Auto VI category on Twitch during its launch day.

## How the Model Works

The forecasting pipeline utilizes historical launch datasets and comparable game launches to project hourly trajectories:
- **Shape Ratios:** Extracts normalized hourly profile curves from comparable major game launches.
- **Median Per Horizon:** Computes the median relative trajectory across historical launches for each forecast horizon.
- **Robust Per-Horizon Sigma:** Estimates robust dispersion and volatility parameters for each horizon.
- **Log-Space Quantiles:** Projects probabilistic bounds by combining scale adjustments with log-normal quantiles (5%, 25%, 50%, 75%, 95%).

## Run It

```bash
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

*Note: This entry was submitted for make.fun's gta6-twitch-ccu-forecast-01 bounty.*
