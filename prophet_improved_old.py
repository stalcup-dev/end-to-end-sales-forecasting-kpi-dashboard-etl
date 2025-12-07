import pandas as pd
from sqlalchemy import create_engine
from prophet import Prophet
from sklearn.metrics import mean_absolute_error
import os

# Import your secure DB connection function
from db import get_engine  

# --- CONFIG ---
FORECAST_DAYS = 90
OUTPUT_DIR = 'prophet_forecasts'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 1. DATA PULL ---
engine = get_engine()
query = """
SELECT date, sku, total_units_sold
FROM mart_sales_summary
ORDER BY sku, date
"""
df = pd.read_sql(query, engine)

# --- 2. CLEAN & PREP ---
df = df[df['total_units_sold'] >= 0].copy()          # Remove negatives
df = df.dropna(subset=['total_units_sold'])          # Remove missing
df = df.rename(columns={'date': 'ds', 'total_units_sold': 'y'})
df['ds'] = pd.to_datetime(df['ds'])                  # Ensure datetime

# --- 3. AUTO-FILTER ELIGIBLE SKUs (>2y data & >500 units sold) ---
sku_stats = df.groupby('sku').agg(
    n_obs=('ds', 'count'),
    first_date=('ds', 'min'),
    last_date=('ds', 'max'),
    total_units=('y', 'sum')
).reset_index()
sku_stats['span_days'] = (sku_stats['last_date'] - sku_stats['first_date']).dt.days
eligible_skus = sku_stats[
    (sku_stats['span_days'] >= 730) & (sku_stats['total_units'] > 500)
]['sku']
df = df[df['sku'].isin(eligible_skus)]

# --- 4. OUTLIER HANDLING (clip top 1% per SKU) ---
def clip_outliers(sub):
    clip_val = sub['y'].quantile(0.99)
    sub['y'] = sub['y'].clip(upper=clip_val)
    return sub
df = df.groupby('sku', group_keys=False).apply(clip_outliers)

# --- 5. FORECASTING LOOP ---
custom_holidays = pd.DataFrame({
    'holiday': ['Black Friday', 'Christmas'],
    'ds': pd.to_datetime(['2024-11-29', '2024-12-25'])
})
all_forecasts = []
error_metrics = []

for sku in df['sku'].unique():
    sub = df[df['sku'] == sku].sort_values('ds')

    m = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        holidays=custom_holidays
    )
    m.fit(sub[['ds', 'y']])

    # Forecast
    future = m.make_future_dataframe(periods=FORECAST_DAYS)
    forecast = m.predict(future)
    forecast['sku'] = sku
    forecast['type'] = 'forecast'
    out = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'sku', 'type']]

    # Actuals
    actuals = sub[['ds', 'y']].copy()
    actuals['sku'] = sku
    actuals['yhat'] = actuals['y']
    actuals['yhat_lower'] = actuals['y']
    actuals['yhat_upper'] = actuals['y']
    actuals['type'] = 'actual'
    actuals = actuals[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'sku', 'type']]

    # Combine for overlay
    combined = pd.concat([actuals, out], ignore_index=True)
    all_forecasts.append(combined)

    # --- 6. Model Backtest (in-sample MAE) ---
    y_true = sub['y']
    y_pred = forecast.set_index('ds').loc[sub['ds'], 'yhat']
    mae = mean_absolute_error(y_true, y_pred)
    error_metrics.append({'sku': sku, 'MAE': mae, 'n_obs': len(y_true)})

# --- 7. EXPORT ---
result = pd.concat(all_forecasts, ignore_index=True)
result.to_csv(os.path.join(OUTPUT_DIR, 'simple_prophet_forecast.csv'), index=False)
pd.DataFrame(error_metrics).to_csv(os.path.join(OUTPUT_DIR, 'forecast_error_metrics.csv'), index=False)
print("[SUCCESS] Forecasts, actuals, and error metrics exported for Power BI overlay and validation.")

result.to_sql('simple_prophet_forecast', engine, schema='public', if_exists='replace', index=False)
print("[SUCCESS] DataFrame written to Postgres as table 'simple_prophet_forecast'.")

pd.DataFrame(error_metrics).to_sql('forecast_error_metrics', engine, schema='public', if_exists='replace', index=False)
print("[SUCCESS] Error metrics written to Postgres as table 'forecast_error_metrics'.")