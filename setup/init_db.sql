-- Vita Markets Database Initialization Script
-- This script creates all necessary tables and loads sample data

-- Create schema if needed
CREATE SCHEMA IF NOT EXISTS public;

-- Drop existing tables (for clean re-runs)
DROP TABLE IF EXISTS public.vitamarkets_raw CASCADE;
DROP TABLE IF EXISTS public.mart_sales_summary CASCADE;
DROP TABLE IF EXISTS public.simple_prophet_forecast CASCADE;
DROP TABLE IF EXISTS public.forecast_error_metrics CASCADE;

-- Create raw data table
CREATE TABLE public.vitamarkets_raw (
    date DATE NOT NULL,
    sku TEXT NOT NULL,
    category TEXT,
    units_sold NUMERIC,
    order_value NUMERIC,
    channel TEXT,
    country TEXT,
    customer_segment TEXT,
    cost_per_unit NUMERIC,
    margin_pct NUMERIC,
    promo_flag INTEGER,
    event TEXT,
    ad_spend NUMERIC,
    web_traffic NUMERIC,
    review_score NUMERIC,
    discontinued_flag INTEGER,
    launch_date DATE,
    discontinue_date DATE,
    archetype TEXT,
    PRIMARY KEY (date, sku, channel, country, customer_segment)
);

-- Create index for better query performance
CREATE INDEX idx_vitamarkets_raw_date ON public.vitamarkets_raw(date);
CREATE INDEX idx_vitamarkets_raw_sku ON public.vitamarkets_raw(sku);

-- Load sample data from CSV
-- Note: Adjust the path to your CSV file location
\echo 'Loading sample data from CSV...'
\COPY public.vitamarkets_raw FROM 'vitamarkets_ultrarealistic_sampledataset.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Verify data loaded
\echo 'Data loaded successfully!'
SELECT 
    COUNT(*) as total_rows,
    MIN(date) as earliest_date,
    MAX(date) as latest_date,
    COUNT(DISTINCT sku) as unique_skus
FROM public.vitamarkets_raw;

\echo ''
\echo 'Database initialization complete!'
\echo 'Next steps:'
\echo '  1. Run dbt models: cd vitamarkets_dbt/vitamarkets && dbt run'
\echo '  2. Generate forecasts: python prophet_improved.py'
\echo '  3. View dashboard: Open MainDash.pbix in Power BI'
