# Power BI Data Contract

> **Last Updated:** 2025-01-16  
> **Contract Version:** 2.0

This document defines the authoritative schemas for all database objects that Power BI (and other downstream tools) must use. Breaking these contracts will cause dashboard failures.

---

## 🚨 Critical Rules

1. **Always query views, never versioned tables.**
2. **Use AVERAGE for metrics, never SUM.**
3. **Add slicers by `data_type` (actual vs forecast).**
4. **Show `forecast_run_id` on dashboards to prove freshness.**

---

## Object Hierarchy

```
Pipeline Output
├── prophet_forecasts_YYYYMMDD_HHMM (versioned table - DO NOT QUERY)
├── prophet_forecast_metrics_YYYYMMDD_HHMM (versioned table - DO NOT QUERY)
│
├── v_forecast_daily_latest (stable view - canonical column names)
├── v_forecast_sku_metrics_latest (stable view - canonical column names)
│
├── simple_prophet_forecast (compatibility view - legacy column names) ← POWER BI USES THIS
└── forecast_error_metrics (compatibility view - legacy column names) ← POWER BI USES THIS
```

---

## Compatibility Views (Use These in Power BI)

### `public.simple_prophet_forecast`

Daily forecast and actuals data with legacy column names for backward compatibility.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `ds` | date | Calendar date | `2024-03-15` |
| `sku` | text | Product SKU identifier | `Flagship Growth` |
| `yhat` | double precision | Point forecast (or actual if `data_type='actual'`) | `125.7` |
| `yhat_lower` | double precision | 80% prediction interval lower bound | `98.2` |
| `yhat_upper` | double precision | 80% prediction interval upper bound | `153.2` |
| `data_type` | text | Row type: `actual` or `forecast` | `forecast` |
| `forecast_run_id` | text | Run timestamp (YYYYMMDD_HHMM) | `20250116_1430` |

**Sample Query:**
```sql
SELECT ds, sku, yhat, yhat_lower, yhat_upper, data_type
FROM public.simple_prophet_forecast
WHERE sku = 'Flagship Growth'
  AND ds >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY ds;
```

### `public.forecast_error_metrics`

Per-SKU accuracy metrics computed on 30-day holdout test set.

| Column | Type | Description | Target |
|--------|------|-------------|--------|
| `sku` | text | Product SKU identifier | — |
| `test_mae` | double precision | Mean Absolute Error (units) | Lower is better |
| `test_rmse` | double precision | Root Mean Squared Error (units) | Lower is better |
| `test_mape_pct` | double precision | Mean Absolute Percentage Error (%) | < 20% good |
| `test_bias` | double precision | Forecast bias: mean(yhat - actual) | Near 0 |
| `test_coverage_pct` | double precision | % of actuals within 80% PI | ≈ 80% |
| `n_train` | integer | Training window size (days) | > 730 |
| `n_test` | integer | Test window size (days) | 30 |
| `run_id` | text | Run timestamp (YYYYMMDD_HHMM) | — |

**Sample Query:**
```sql
SELECT sku, 
       ROUND(test_mape_pct::numeric, 1) AS mape_pct,
       ROUND(test_coverage_pct::numeric, 1) AS coverage_pct,
       test_bias
FROM public.forecast_error_metrics
ORDER BY test_mape_pct;
```

---

## Canonical Views (Modern Column Names)

Use these if building new integrations. Power BI currently uses compatibility views above.

### `public.v_forecast_daily_latest`

| Column | Type | Description |
|--------|------|-------------|
| `forecast_date` | date | Calendar date |
| `sku` | text | Product SKU |
| `predicted_units` | double precision | Point forecast or actual |
| `lower_bound_80pct` | double precision | 80% PI lower |
| `upper_bound_80pct` | double precision | 80% PI upper |
| `data_type` | text | `actual` or `forecast` |
| `forecast_run_id` | text | Run timestamp |

### `public.v_forecast_sku_metrics_latest`

| Column | Type | Description |
|--------|------|-------------|
| `sku` | text | Product SKU |
| `mean_absolute_error` | double precision | MAE |
| `root_mean_squared_error` | double precision | RMSE |
| `mean_absolute_pct_error` | double precision | MAPE (%) |
| `forecast_bias` | double precision | Bias |
| `prediction_interval_coverage_pct` | double precision | Coverage (%) |
| `training_days` | integer | Train window |
| `test_days` | integer | Test window |
| `forecast_run_id` | text | Run timestamp |

---

## Power Query Integration

### Recommended Pattern (Pinned to View)

Use `Value.NativeQuery` to ensure Power BI always hits the view, not cached navigation:

```m
let
   Source = PostgreSQL.Database("localhost", "vitamarkets"),
   Forecast = Value.NativeQuery(
       Source, 
       "SELECT * FROM public.simple_prophet_forecast", 
       null, 
       [EnableFolding=true]
   )
in
   Forecast
```

```m
let
   Source = PostgreSQL.Database("localhost", "vitamarkets"),
   Metrics = Value.NativeQuery(
       Source, 
       "SELECT * FROM public.forecast_error_metrics", 
       null, 
       [EnableFolding=true]
   )
in
   Metrics
```

### Verifying Connection in Power BI

1. Open **Power Query Editor** → **Advanced Editor**
2. Confirm `Schema = "public"` and table name matches view exactly
3. If using Navigation step, ensure `Item = "simple_prophet_forecast"` (not a versioned table)

---

## ⚠️ Aggregation Rules

**CRITICAL: Error metrics must use AVERAGE, never SUM.**

| Metric | ❌ Wrong DAX | ✅ Correct DAX |
|--------|-------------|----------------|
| MAE | `SUM(test_mae)` | `AVERAGE(test_mae)` |
| MAPE | `SUM(test_mape_pct)` | `AVERAGE(test_mape_pct)` |
| RMSE | `SUM(test_rmse)` | `AVERAGE(test_rmse)` |
| Bias | `SUM(test_bias)` | `AVERAGE(test_bias)` |
| Coverage | `SUM(test_coverage_pct)` | `AVERAGE(test_coverage_pct)` |

**Why?** Summing error metrics produces meaningless inflated values. A sum of MAE across 8 SKUs doesn't represent any real error measurement.

### Recommended DAX Measures

```dax
MAE Avg = AVERAGE(forecast_error_metrics[test_mae])
MAPE Avg % = AVERAGE(forecast_error_metrics[test_mape_pct])
Coverage Avg % = AVERAGE(forecast_error_metrics[test_coverage_pct])
Bias Avg = AVERAGE(forecast_error_metrics[test_bias])
Max Forecast Date = MAX(simple_prophet_forecast[ds])
Latest Run ID = MAX(simple_prophet_forecast[forecast_run_id])
```

---

## Verification SQL

Run these after each pipeline execution to verify contracts are intact:

```sql
-- 1. Forecast view has data
SELECT 
    COUNT(*) AS total_rows,
    COUNT(DISTINCT sku) AS sku_count,
    MAX(ds) AS max_date,
    MAX(forecast_run_id) AS latest_run
FROM public.simple_prophet_forecast;

-- 2. Metrics view has all SKUs
SELECT 
    COUNT(*) AS sku_count,
    ROUND(AVG(test_mape_pct)::numeric, 1) AS avg_mape,
    ROUND(AVG(test_coverage_pct)::numeric, 1) AS avg_coverage
FROM public.forecast_error_metrics;

-- 3. Columns exist as expected
SELECT column_name, data_type 
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'simple_prophet_forecast'
ORDER BY ordinal_position;

-- Expected output:
-- ds              | date
-- sku             | text  
-- yhat            | double precision
-- yhat_lower      | double precision
-- yhat_upper      | double precision
-- data_type       | text
-- forecast_run_id | text
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Power BI shows "relation does not exist" | View was dropped but not recreated | Run `python forecast_prophet_v2.py` |
| `forecast_run_id` is stale | Pipeline didn't complete | Check logs, re-run pipeline |
| Metrics show unrealistic values | Using SUM instead of AVERAGE | Update DAX to use AVERAGE |
| View has wrong columns | Querying versioned table | Update Power Query to use view name |
| Coverage far from 80% | Model miscalibrated | See [FORECASTING_POLICIES.md](FORECASTING_POLICIES.md) |
