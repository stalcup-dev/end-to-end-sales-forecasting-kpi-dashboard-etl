-- Verification script for Power BI data contract
-- Run in psql or pgAdmin

-- 1) Ensure views exist
SELECT to_regclass('public.v_forecast_daily_latest')   AS view_forecast_latest,
       to_regclass('public.v_forecast_sku_metrics_latest') AS view_metrics_latest,
       to_regclass('public.simple_prophet_forecast')   AS view_simple_prophet,
       to_regclass('public.forecast_error_metrics')    AS view_error_metrics;

-- 2) Row counts and max date/run
SELECT COUNT(*) AS rows_forecast,
       MAX(ds) AS max_ds,
       MAX(forecast_run_id) AS max_run
FROM public.simple_prophet_forecast;

SELECT COUNT(*) AS rows_metrics,
       MAX(run_id) AS max_run
FROM public.forecast_error_metrics;

-- 3) Spot-check metrics coverage
SELECT sku, test_mape_pct, test_mae, test_rmse, test_bias, test_coverage_pct
FROM public.forecast_error_metrics
ORDER BY test_mape_pct ASC
LIMIT 5;
