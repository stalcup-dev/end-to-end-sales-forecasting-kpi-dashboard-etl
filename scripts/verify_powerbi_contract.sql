-- Verification script for Power BI data contract
-- Run in psql or pgAdmin. Fails loudly if required columns are missing.

-- 1) Ensure views exist
SELECT to_regclass('public.v_forecast_daily_latest')       AS view_forecast_latest,
       to_regclass('public.v_forecast_sku_metrics_latest') AS view_metrics_latest,
       to_regclass('public.simple_prophet_forecast')       AS view_simple_prophet,
       to_regclass('public.forecast_error_metrics')        AS view_error_metrics;

-- 2) Row counts + freshness
SELECT 'simple_prophet_forecast' AS object,
       COUNT(*) AS rows,
       MAX(ds) AS max_ds,
       MAX(forecast_run_id) AS max_run
FROM public.simple_prophet_forecast
UNION ALL
SELECT 'forecast_error_metrics' AS object,
       COUNT(*) AS rows,
       NULL::date AS max_ds,
       MAX(run_id) AS max_run
FROM public.forecast_error_metrics;

-- 3) Column presence checks (fail if missing)
DO $$
DECLARE
    missing_forecast text;
    missing_metrics  text;
    missing_forecast_view text;
    missing_metrics_view  text;
BEGIN
    SELECT string_agg(req.column_name, ', ') INTO missing_forecast
    FROM (VALUES ('ds'), ('sku'), ('yhat'), ('yhat_lower'), ('yhat_upper'), ('data_type'), ('forecast_run_id')) AS req(column_name)
    LEFT JOIN information_schema.columns c
           ON c.table_schema = 'public' AND c.table_name = 'simple_prophet_forecast' AND c.column_name = req.column_name
    WHERE c.column_name IS NULL;

    IF missing_forecast IS NOT NULL THEN
        RAISE EXCEPTION 'Missing columns in simple_prophet_forecast: %', missing_forecast;
    ELSE
        RAISE NOTICE 'simple_prophet_forecast columns OK';
    END IF;

    SELECT string_agg(req.column_name, ', ') INTO missing_metrics
    FROM (VALUES ('sku'), ('test_mae'), ('test_rmse'), ('test_mape_pct'), ('test_bias'), ('test_coverage_pct'), ('n_train'), ('n_test'), ('run_id')) AS req(column_name)
    LEFT JOIN information_schema.columns c
           ON c.table_schema = 'public' AND c.table_name = 'forecast_error_metrics' AND c.column_name = req.column_name
    WHERE c.column_name IS NULL;

    IF missing_metrics IS NOT NULL THEN
        RAISE EXCEPTION 'Missing columns in forecast_error_metrics: %', missing_metrics;
    ELSE
        RAISE NOTICE 'forecast_error_metrics columns OK';
    END IF;

    SELECT string_agg(req.column_name, ', ') INTO missing_forecast_view
    FROM (VALUES ('forecast_date'), ('sku'), ('predicted_units'), ('lower_bound_80pct'), ('upper_bound_80pct'), ('data_type'), ('forecast_run_id')) AS req(column_name)
    LEFT JOIN information_schema.columns c
           ON c.table_schema = 'public' AND c.table_name = 'v_forecast_daily_latest' AND c.column_name = req.column_name
    WHERE c.column_name IS NULL;

    IF missing_forecast_view IS NOT NULL THEN
        RAISE EXCEPTION 'Missing columns in v_forecast_daily_latest: %', missing_forecast_view;
    ELSE
        RAISE NOTICE 'v_forecast_daily_latest columns OK';
    END IF;

    SELECT string_agg(req.column_name, ', ') INTO missing_metrics_view
    FROM (VALUES ('sku'), ('mean_absolute_error'), ('root_mean_squared_error'), ('mean_absolute_pct_error'), ('forecast_bias'), ('prediction_interval_coverage_pct'), ('training_days'), ('test_days'), ('forecast_run_id')) AS req(column_name)
    LEFT JOIN information_schema.columns c
           ON c.table_schema = 'public' AND c.table_name = 'v_forecast_sku_metrics_latest' AND c.column_name = req.column_name
    WHERE c.column_name IS NULL;

    IF missing_metrics_view IS NOT NULL THEN
        RAISE EXCEPTION 'Missing columns in v_forecast_sku_metrics_latest: %', missing_metrics_view;
    ELSE
        RAISE NOTICE 'v_forecast_sku_metrics_latest columns OK';
    END IF;
END $$;

-- 4) Spot-check metrics coverage
SELECT sku, test_mape_pct, test_mae, test_rmse, test_bias, test_coverage_pct
FROM public.forecast_error_metrics
ORDER BY test_mape_pct ASC
LIMIT 5;
