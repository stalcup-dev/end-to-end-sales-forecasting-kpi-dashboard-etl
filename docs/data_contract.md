# Power BI Data Contract (Canonical Views)

Authoritative schemas for the four objects Power BI and downstream tools must use. Canonical views have modern names; compatibility views keep legacy column names for existing Power BI queries.

## Canonical: `public.v_forecast_daily_latest`

| Column | Type | Description | Required for Power BI |
| --- | --- | --- | --- |
| forecast_date | date | Calendar date for the row (actuals + forecasts) | Yes |
| sku | text | Product SKU | Yes |
| predicted_units | double precision | Point forecast or actual units | Yes |
| lower_bound_80pct | double precision | 80% PI lower bound | Yes |
| upper_bound_80pct | double precision | 80% PI upper bound | Yes |
| data_type | text | `actual` or `forecast` flag | Yes (slicer) |
| forecast_run_id | text | Run identifier (YYYYMMDD_HHMM) | Yes (refresh proof) |

## Canonical: `public.v_forecast_sku_metrics_latest`

| Column | Type | Description | Required for Power BI |
| --- | --- | --- | --- |
| sku | text | Product SKU | Yes |
| mean_absolute_error | double precision | MAE on 30-day holdout | Yes |
| root_mean_squared_error | double precision | RMSE on 30-day holdout | Yes |
| mean_absolute_pct_error | double precision | MAPE (%) on 30-day holdout | Yes |
| forecast_bias | double precision | Mean(yhat - y) on holdout | Yes |
| prediction_interval_coverage_pct | double precision | Coverage (%) of 80% PI on holdout | Yes |
| training_days | integer | Training window days | Yes |
| test_days | integer | Holdout window days | Yes |
| forecast_run_id | text | Run identifier (YYYYMMDD_HHMM) | Yes (refresh proof) |

## Compatibility: `public.simple_prophet_forecast`

| Column | Type | Description | Required for Power BI |
| --- | --- | --- | --- |
| ds | date | Calendar date | Yes |
| sku | text | Product SKU | Yes |
| yhat | double precision | Point forecast or actual units | Yes |
| yhat_lower | double precision | 80% PI lower bound | Yes |
| yhat_upper | double precision | 80% PI upper bound | Yes |
| data_type | text | `actual` or `forecast` flag | Yes (slicer) |
| forecast_run_id | text | Run identifier (YYYYMMDD_HHMM) | Yes (refresh proof) |

## Compatibility: `public.forecast_error_metrics`

| Column | Type | Description | Required for Power BI |
| --- | --- | --- | --- |
| sku | text | Product SKU | Yes |
| test_mae | double precision | MAE on 30-day holdout | Yes |
| test_rmse | double precision | RMSE on 30-day holdout | Yes |
| test_mape_pct | double precision | MAPE (%) on 30-day holdout | Yes |
| test_bias | double precision | Mean(yhat - y) on holdout | Yes |
| test_coverage_pct | double precision | Coverage (%) of 80% PI on holdout | Yes |
| n_train | integer | Training window days | Yes |
| n_test | integer | Holdout window days | Yes |
| run_id | text | Run identifier (YYYYMMDD_HHMM) | Yes (refresh proof) |

## Rules
- Always query the compatibility views from Power BI (`simple_prophet_forecast`, `forecast_error_metrics`).
- Do not query versioned tables (`prophet_forecasts_*`, `prophet_forecast_metrics_*`) directly.
- Views must be recreated every pipeline run so they always point at the latest forecast tables.
- Aggregations for metrics must use averages/medians (never sums). Add slicers by `data_type` and show refresh-proof fields (`max(ds)`, `max(forecast_run_id)`).
