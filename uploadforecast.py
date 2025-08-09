# uploadforecast.py
import pandas as pd
import os
from pathlib import Path
from db import get_engine  # <- secure central DB connector

# Directories
BASE_DIR = Path(__file__).resolve().parent
FORECASTS_DIR = BASE_DIR / "prophet_forecasts"

# Load CSVs
df_forecasts = pd.read_csv(FORECASTS_DIR / "all_forecasts.csv")
df_errors = pd.read_csv(FORECASTS_DIR / "forecast_error_metrics.csv")

# Write to Postgres tables
engine = get_engine()
df_forecasts.to_sql("prophet_forecasts", engine, if_exists="replace", index=False)
df_errors.to_sql("prophet_forecast_error_metrics", engine, if_exists="replace", index=False)

print("Upload complete!")
