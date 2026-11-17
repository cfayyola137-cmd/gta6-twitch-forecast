# GTA VI Twitch CCU Forecaster

A robust, high-performance release day concurrent viewer forecaster for Grand Theft Auto VI on Twitch (`gta6-twitch-ccu-forecast-01` bounty entry for make.fun).

## Approach
- **Empirical Diurnal Shape Profile:** Uses empirical median hourly release-day viewer ratios (`y(h) / y(1)`) extracted from 38 comparable major game launches to model the expected intra-day arc (accounting for night dips and evening peaks up to 2.3x hour 1).
- **Calibrated Quantiles:** Applies log-space random-walk variance scaling (`sigma = 0.20`) around the shape-adjusted median forecast (`q50`), producing well-calibrated quantiles (`0.05`, `0.25`, `0.50`, `0.75`, `0.95`).
- **Standard Library Only:** Written entirely in Python 3.13 standard library with zero external dependencies, running in under 0.1s and well within memory limits.

## Usage
```bash
export MAKEFUN_INPUT_DIR=/input
export MAKEFUN_OUTPUT_DIR=/output
python3 main.py
```
