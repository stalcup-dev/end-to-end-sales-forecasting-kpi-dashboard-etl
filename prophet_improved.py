"""
Prophet Forecasting with Proper Train/Test Split and Evaluation

This script:
1. Pulls data from mart_sales_summary
2. Filters eligible SKUs (2+ years data, 500+ units)
3. Splits data into train/test (last 30 days held out)
4. Fits Prophet model on training data
5. Evaluates on test set (MAPE, MAE, RMSE, Bias)
6. Generates 90-day forecasts
7. Writes results to PostgreSQL and CSV
"""

import os
import warnings

import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")

# Import secure DB connection function
from db import get_engine  # noqa: E402

# --- CONFIG ---
FORECAST_DAYS = 90
TEST_DAYS = 30  # Holdout test set size
OUTPUT_DIR = "prophet_forecasts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("VITA MARKETS FORECASTING PIPELINE")
print("=" * 70)

# --- 1. DATA PULL ---
print("\n[1/7] Pulling data from mart_sales_summary...")
engine = get_engine()
query = """
SELECT date, sku, total_units_sold
FROM mart_sales_summary
ORDER BY sku, date
"""
df = pd.read_sql(query, engine)
print(f"   → Loaded {len(df):,} rows")

# --- 2. CLEAN & PREP ---
print("\n[2/7] Cleaning and preparing data...")
df = df[df["total_units_sold"] >= 0].copy()
df = df.dropna(subset=["total_units_sold"])
df = df.rename(columns={"date": "ds", "total_units_sold": "y"})
df["ds"] = pd.to_datetime(df["ds"])
print(f"   → {len(df):,} rows after cleaning")

# --- 3. AUTO-FILTER ELIGIBLE SKUs ---
print("\n[3/7] Filtering eligible SKUs (2+ years data, 500+ units)...")
sku_stats = (
    df.groupby("sku")
    .agg(
        n_obs=("ds", "count"),
        first_date=("ds", "min"),
        last_date=("ds", "max"),
        total_units=("y", "sum"),
    )
    .reset_index()
)
sku_stats["span_days"] = (sku_stats["last_date"] - sku_stats["first_date"]).dt.days
eligible_skus = sku_stats[(sku_stats["span_days"] >= 730) & (sku_stats["total_units"] > 500)][
    "sku"
].tolist()

print(f"   → {len(eligible_skus)} SKUs eligible for forecasting:")
for sku in eligible_skus:
    stats = sku_stats[sku_stats["sku"] == sku].iloc[0]
    print(f"      • {sku}: {stats['span_days']} days, {stats['total_units']:.0f} units")

df = df[df["sku"].isin(eligible_skus)]

# --- 4. OUTLIER HANDLING ---
print("\n[4/7] Clipping outliers (99th percentile per SKU)...")


def clip_outliers(sub):
    clip_val = sub["y"].quantile(0.99)
    sub["y"] = sub["y"].clip(upper=clip_val)
    return sub


df = df.groupby("sku", group_keys=False).apply(clip_outliers)
print("   → Outliers clipped")

# --- 5. TRAIN/TEST SPLIT & FORECASTING ---
print("\n[5/7] Training Prophet models with holdout test set...")
custom_holidays = pd.DataFrame(
    {"holiday": ["Black Friday", "Christmas"], "ds": pd.to_datetime(["2024-11-29", "2024-12-25"])}
)

all_forecasts = []
error_metrics = []

for idx, sku in enumerate(eligible_skus, 1):
    print(f"   [{idx}/{len(eligible_skus)}] Processing {sku}...")

    sub = df[df["sku"] == sku].sort_values("ds").reset_index(drop=True)

    # Train/test split (last TEST_DAYS held out)
    split_date = sub["ds"].max() - pd.Timedelta(days=TEST_DAYS)
    train = sub[sub["ds"] <= split_date]
    test = sub[sub["ds"] > split_date]

    if len(test) < 10:
        print(f"      ⚠️  Insufficient test data ({len(test)} days), skipping evaluation")
        continue

    # Fit Prophet on training data only
    m = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        holidays=custom_holidays,
        interval_width=0.8,  # 80% prediction interval
    )
    m.fit(train[["ds", "y"]])

    # --- EVALUATE ON TEST SET ---
    test_dates = pd.DataFrame({"ds": test["ds"]})
    test_forecast = m.predict(test_dates)

    y_true = test["y"].values
    y_pred = test_forecast["yhat"].values

    # Calculate metrics
    mae_test = mean_absolute_error(y_true, y_pred)
    rmse_test = np.sqrt(mean_squared_error(y_true, y_pred))
    mape_test = np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1))) * 100  # Avoid div by 0
    bias_test = np.mean(y_pred - y_true)

    # Coverage (what % of actuals fall within prediction interval)
    within_interval = (y_true >= test_forecast["yhat_lower"].values) & (
        y_true <= test_forecast["yhat_upper"].values
    )
    coverage = within_interval.mean() * 100

    error_metrics.append(
        {
            "sku": sku,
            "test_mae": mae_test,
            "test_rmse": rmse_test,
            "test_mape_pct": mape_test,
            "test_bias": bias_test,
            "test_coverage_pct": coverage,
            "n_train": len(train),
            "n_test": len(test),
        }
    )

    print(
        f"      → MAE: {mae_test:.1f} | MAPE: {mape_test:.1f}% | RMSE: {rmse_test:.1f} | Bias: {bias_test:.1f}"
    )
    print(f"      → Coverage (80% PI): {coverage:.1f}%")

    # --- GENERATE FUTURE FORECAST (from full data) ---
    # Refit on ALL data for production forecast
    m_full = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        holidays=custom_holidays,
        interval_width=0.8,
    )
    m_full.fit(sub[["ds", "y"]])

    future = m_full.make_future_dataframe(periods=FORECAST_DAYS)
    forecast = m_full.predict(future)
    forecast["sku"] = sku
    forecast["type"] = "forecast"
    out = forecast[["ds", "yhat", "yhat_lower", "yhat_upper", "sku", "type"]]

    # Actuals (historical)
    actuals = sub[["ds", "y"]].copy()
    actuals["sku"] = sku
    actuals["yhat"] = actuals["y"]
    actuals["yhat_lower"] = actuals["y"]
    actuals["yhat_upper"] = actuals["y"]
    actuals["type"] = "actual"
    actuals = actuals[["ds", "yhat", "yhat_lower", "yhat_upper", "sku", "type"]]

    # Combine for overlay
    combined = pd.concat([actuals, out], ignore_index=True)
    all_forecasts.append(combined)

# --- 6. EXPORT RESULTS ---
print("\n[6/7] Exporting results...")

# Forecasts
result = pd.concat(all_forecasts, ignore_index=True)
csv_path = os.path.join(OUTPUT_DIR, "simple_prophet_forecast.csv")
result.to_csv(csv_path, index=False)
print(f"   → Forecasts saved to {csv_path}")

# Error metrics
metrics_df = pd.DataFrame(error_metrics)
metrics_csv = os.path.join(OUTPUT_DIR, "forecast_error_metrics.csv")
metrics_df.to_csv(metrics_csv, index=False)
print(f"   → Metrics saved to {metrics_csv}")

# --- 7. WRITE TO POSTGRES ---
print("\n[7/7] Writing to PostgreSQL...")
result.to_sql("simple_prophet_forecast", engine, schema="public", if_exists="replace", index=False)
print("   → Table 'simple_prophet_forecast' updated")

metrics_df.to_sql(
    "forecast_error_metrics", engine, schema="public", if_exists="replace", index=False
)
print("   → Table 'forecast_error_metrics' updated")

# --- SUMMARY ---
print("\n" + "=" * 70)
print("FORECASTING COMPLETE - SUMMARY")
print("=" * 70)

if len(metrics_df) > 0:
    print(f"\n📊 Accuracy Metrics (on {TEST_DAYS}-day holdout test set):\n")
    print(f"{'SKU':<25} {'MAPE%':<10} {'MAE':<10} {'RMSE':<10} {'Bias':<10} {'Coverage%':<12}")
    print("-" * 90)

    for _, row in metrics_df.iterrows():
        print(
            f"{row['sku']:<25} {row['test_mape_pct']:>8.1f}% {row['test_mae']:>9.1f} {row['test_rmse']:>9.1f} {row['test_bias']:>9.1f} {row['test_coverage_pct']:>10.1f}%"
        )

    print("-" * 90)
    print(
        f"{'MEDIAN':<25} {metrics_df['test_mape_pct'].median():>8.1f}% {metrics_df['test_mae'].median():>9.1f} {metrics_df['test_rmse'].median():>9.1f} {metrics_df['test_bias'].median():>9.1f} {metrics_df['test_coverage_pct'].median():>10.1f}%"
    )

    print(f"\n✅ SUCCESS: Forecasts generated for {len(eligible_skus)} SKUs")
    print(f"   • Test set: Last {TEST_DAYS} days held out for evaluation")
    print(f"   • Forecast horizon: {FORECAST_DAYS} days into future")
    print(f"   • Median MAPE: {metrics_df['test_mape_pct'].median():.1f}%")
    print(f"   • Median Coverage: {metrics_df['test_coverage_pct'].median():.1f}% (target: 80%)")

    # Interpretation
    median_mape = metrics_df["test_mape_pct"].median()
    if median_mape < 10:
        quality = "EXCELLENT"
    elif median_mape < 15:
        quality = "GOOD"
    elif median_mape < 20:
        quality = "ACCEPTABLE"
    else:
        quality = "NEEDS IMPROVEMENT"

    print(f"\n🎯 Forecast Quality: {quality}")

    if median_mape > 20:
        print("   ⚠️  Consider: Adding more features (promotions, holidays, external factors)")
else:
    print("\n⚠️  No SKUs evaluated (insufficient test data)")

print("\n" + "=" * 70)
print("Next steps:")
print("  1. Review metrics in 'prophet_forecasts/forecast_error_metrics.csv'")
print("  2. Open Power BI dashboard (MainDash.pbix) and refresh data")
print("  3. Check 'Forecast vs. Actuals' page for visual validation")
print("=" * 70)
