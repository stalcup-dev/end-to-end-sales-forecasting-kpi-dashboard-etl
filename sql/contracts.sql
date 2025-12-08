-- ====================================================================
-- POWER BI DATA CONTRACT (REBUILD VIEWS FROM LATEST VERSIONED TABLES)
-- Run this script after a forecast run to re-point stable +
-- compatibility views at the most recent prophet_* tables.
-- ====================================================================

DO $$
DECLARE
    latest_forecast_table text;
    latest_metrics_table  text;
BEGIN
    SELECT relname INTO latest_forecast_table
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public'
      AND relkind = 'r'
      AND relname LIKE 'prophet_forecasts_%'
    ORDER BY relname DESC
    LIMIT 1;

    SELECT relname INTO latest_metrics_table
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public'
      AND relkind = 'r'
      AND relname LIKE 'prophet_forecast_metrics_%'
    ORDER BY relname DESC
    LIMIT 1;

    IF latest_forecast_table IS NULL OR latest_metrics_table IS NULL THEN
        RAISE EXCEPTION 'No prophet forecast tables found. Run the forecast pipeline first.';
    END IF;

    -- Drop then recreate to enforce schema
    EXECUTE 'DROP VIEW IF EXISTS public.simple_prophet_forecast';
    EXECUTE 'DROP VIEW IF EXISTS public.forecast_error_metrics';
    EXECUTE 'DROP VIEW IF EXISTS public.v_forecast_daily_latest';
    EXECUTE 'DROP VIEW IF EXISTS public.v_forecast_sku_metrics_latest';

    -- Canonical daily forecast view
    EXECUTE format($f$
        CREATE OR REPLACE VIEW public.v_forecast_daily_latest AS
        SELECT
            CAST(ds AS date) AS forecast_date,
            sku,
            yhat AS predicted_units,
            yhat_lower AS lower_bound_80pct,
            yhat_upper AS upper_bound_80pct,
            type AS data_type,
            run_id AS forecast_run_id
        FROM public.%I
        ORDER BY sku, ds
    $f$, latest_forecast_table);

    -- Canonical metrics view
    EXECUTE format($f$
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
        FROM public.%I
        ORDER BY test_mape_pct ASC
    $f$, latest_metrics_table);

    -- Compatibility: legacy forecast view
    EXECUTE $$
        CREATE OR REPLACE VIEW public.simple_prophet_forecast AS
        SELECT
            forecast_date AS ds,
            sku,
            predicted_units AS yhat,
            lower_bound_80pct AS yhat_lower,
            upper_bound_80pct AS yhat_upper,
            data_type,
            forecast_run_id
        FROM public.v_forecast_daily_latest
    $$;

    -- Compatibility: legacy metrics view
    EXECUTE $$
        CREATE OR REPLACE VIEW public.forecast_error_metrics AS
        SELECT
            sku,
            mean_absolute_error AS test_mae,
            root_mean_squared_error AS test_rmse,
            mean_absolute_pct_error AS test_mape_pct,
            forecast_bias AS test_bias,
            prediction_interval_coverage_pct AS test_coverage_pct,
            training_days AS n_train,
            test_days AS n_test,
            forecast_run_id AS run_id
        FROM public.v_forecast_sku_metrics_latest
    $$;
END $$;

COMMENT ON VIEW public.v_forecast_daily_latest IS 'Latest forecast run (actuals + predictions).';
COMMENT ON VIEW public.v_forecast_sku_metrics_latest IS 'Latest per-SKU forecast accuracy metrics.';
COMMENT ON VIEW public.simple_prophet_forecast IS 'Compatibility view for legacy Power BI queries (ds/yhat naming).';
COMMENT ON VIEW public.forecast_error_metrics IS 'Compatibility metrics view for legacy Power BI queries.';
