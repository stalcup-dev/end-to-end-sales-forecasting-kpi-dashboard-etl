-- ================================================================
-- POWER BI DATA CONTRACT - STABLE VIEWS
-- ================================================================
-- These views provide stable endpoints for Power BI dashboards.
-- They always point to the latest forecast run, regardless of
-- underlying table names or versioning schemes.
--
-- Power BI should ONLY query these views, never the underlying tables.
-- ================================================================

-- View 1: Latest Daily Forecasts (Actuals + Predictions)
-- ================================================================
-- Purpose: Time series overlay of historical actuals and 90-day forecasts
-- Grain: One row per date-sku combination
-- Usage: Line charts, time series visualizations
-- ================================================================
CREATE OR REPLACE VIEW public.v_forecast_daily_latest AS
SELECT 
    ds AS forecast_date,
    sku,
    yhat AS predicted_units,
    yhat_lower AS lower_bound_80pct,
    yhat_upper AS upper_bound_80pct,
    type AS data_type,  -- 'actual' or 'forecast'
    run_id AS forecast_run_id
FROM public.simple_prophet_forecast  -- Default fallback table
ORDER BY sku, ds;

COMMENT ON VIEW public.v_forecast_daily_latest IS 
'Latest forecast run with actuals overlay. Auto-updates on each pipeline run.';


-- View 2: Latest SKU-Level Forecast Metrics
-- ================================================================
-- Purpose: Model accuracy and performance metrics per SKU
-- Grain: One row per SKU
-- Usage: Scorecards, accuracy tracking, model validation
-- ================================================================
CREATE OR REPLACE VIEW public.v_forecast_sku_metrics_latest AS
SELECT 
    sku,
    test_mae AS mean_absolute_error,
    test_rmse AS root_mean_squared_error,
    test_mape_pct AS mean_absolute_pct_error,
    test_bias AS forecast_bias,
    test_coverage_pct AS prediction_interval_coverage_pct,
    n_train AS training_days,
    n_test AS test_days,
    run_id AS forecast_run_id
FROM public.forecast_error_metrics  -- Default fallback table
ORDER BY test_mape_pct ASC;

COMMENT ON VIEW public.v_forecast_sku_metrics_latest IS 
'Per-SKU forecast accuracy metrics from latest run. Lower MAPE = better accuracy.';


-- ================================================================
-- POWER BI QUERY EXAMPLES
-- ================================================================

-- Example 1: Forecast vs Actuals Chart
-- ================================================================
-- SELECT 
--     forecast_date,
--     sku,
--     predicted_units,
--     lower_bound_80pct,
--     upper_bound_80pct,
--     data_type
-- FROM public.v_forecast_daily_latest
-- WHERE sku = 'Flagship Growth'
--   AND forecast_date >= CURRENT_DATE - INTERVAL '180 days'
-- ORDER BY forecast_date;

-- Example 2: Top 10 Most Accurate SKUs
-- ================================================================
-- SELECT 
--     sku,
--     mean_absolute_pct_error AS mape_pct,
--     mean_absolute_error AS mae,
--     prediction_interval_coverage_pct AS coverage_pct
-- FROM public.v_forecast_sku_metrics_latest
-- ORDER BY mean_absolute_pct_error ASC
-- LIMIT 10;

-- Example 3: Next 30 Days Forecast Summary
-- ================================================================
-- SELECT 
--     sku,
--     SUM(predicted_units) AS total_forecasted_units,
--     MIN(lower_bound_80pct) AS min_lower_bound,
--     MAX(upper_bound_80pct) AS max_upper_bound
-- FROM public.v_forecast_daily_latest
-- WHERE data_type = 'forecast'
--   AND forecast_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
-- GROUP BY sku
-- ORDER BY total_forecasted_units DESC;
