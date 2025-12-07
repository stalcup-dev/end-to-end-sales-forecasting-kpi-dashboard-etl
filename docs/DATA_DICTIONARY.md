# Data Dictionary

## Table of Contents
1. [Overview](#overview)
2. [Table: vitamarkets_raw](#table-vitamarkets_raw)
3. [Table: stg_vitamarkets](#table-stg_vitamarkets)
4. [Table: mart_sales_summary](#table-mart_sales_summary)
5. [Table: simple_prophet_forecast](#table-simple_prophet_forecast)
6. [Table: forecast_error_metrics](#table-forecast_error_metrics)
7. [Data Lineage](#data-lineage)
8. [Sample Queries](#sample-queries)

---

## Overview

This document provides detailed schema definitions for all tables in the Vita Markets analytics pipeline. Each table includes column names, data types, descriptions, nullability, and business logic.

**Database:** PostgreSQL 14+  
**Schema:** `public`

---

## Table: vitamarkets_raw

**Purpose:** Landing zone for raw sales data from CSV source.

**Materialization:** Table  
**Refresh:** Full replace (can be changed to incremental)  
**Primary Key:** (date, sku, channel, country, customer_segment)

### Schema

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `date` | DATE | NO | Transaction date (YYYY-MM-DD format) |
| `sku` | TEXT | NO | Stock Keeping Unit identifier (e.g., "Flagship Growth", "New Launch") |
| `category` | TEXT | YES | Product category (e.g., "Tech", "Health") |
| `units_sold` | NUMERIC | YES | Number of units sold in this transaction |
| `order_value` | NUMERIC | YES | Total revenue for this transaction (USD) |
| `channel` | TEXT | YES | Sales channel: "website", "amazon", "mobile" |
| `country` | TEXT | YES | Country code: "US", "CA" |
| `customer_segment` | TEXT | YES | Customer demographic: "Young Pro", "Family", "Older Adult" |
| `cost_per_unit` | NUMERIC | YES | Cost of goods per unit (USD) |
| `margin_pct` | NUMERIC | YES | Profit margin percentage (0.32 = 32%) |
| `promo_flag` | INTEGER | YES | 1 if promotional pricing applied, 0 otherwise |
| `event` | TEXT | YES | Special event (e.g., "Black Friday", "New Year") |
| `ad_spend` | NUMERIC | YES | Advertising spend for this SKU on this date (USD) |
| `web_traffic` | NUMERIC | YES | Website visits attributed to this SKU |
| `review_score` | NUMERIC | YES | Customer review score (1.0 to 5.0) |
| `discontinued_flag` | INTEGER | YES | 1 if SKU is discontinued, 0 otherwise |
| `launch_date` | DATE | YES | Date SKU was launched |
| `discontinue_date` | DATE | YES | Date SKU was discontinued (NULL if active) |
| `archetype` | TEXT | YES | Product lifecycle stage: "growth", "mature", "decline" |

### Indexes
- Primary Key: `(date, sku, channel, country, customer_segment)`
- Index: `idx_vitamarkets_raw_date` on `date`
- Index: `idx_vitamarkets_raw_sku` on `sku`

### Sample Row
```sql
date           | 2024-11-01
sku            | Flagship Growth
category       | Tech
units_sold     | 45
order_value    | 5234.67
channel        | website
country        | US
customer_segment | Young Pro
cost_per_unit  | 80.00
margin_pct     | 0.32
promo_flag     | 0
event          | NULL
ad_spend       | 320.50
web_traffic    | 1250
review_score   | 4.2
discontinued_flag | 0
launch_date    | 2021-01-01
discontinue_date | NULL
archetype      | growth
```

---

## Table: stg_vitamarkets

**Purpose:** Staging layer that cleans and type-casts raw data.

**Materialization:** View (dbt default)  
**Source:** `public.vitamarkets_raw`  
**dbt Model:** `models/stg_vitamarkets.sql`

### Schema

| Column | Type | Nullable | Description | Transformation |
|--------|------|----------|-------------|----------------|
| `date` | DATE | NO | Transaction date | No change |
| `sku` | TEXT | NO | Stock Keeping Unit identifier | No change |
| `category` | TEXT | YES | Product category | No change |
| `units_sold` | INTEGER | NO | Number of units sold | `ROUND(units_sold)::INT` |
| `order_value` | NUMERIC(10,2) | NO | Total revenue (USD) | `ROUND(order_value::NUMERIC, 2)` |
| `channel` | TEXT | YES | Sales channel | No change |
| `country` | TEXT | YES | Country code | No change |
| `customer_segment` | TEXT | YES | Customer demographic | No change |
| `cost_per_unit` | NUMERIC(10,2) | YES | Cost of goods per unit | `ROUND(cost_per_unit::NUMERIC, 2)` |
| `margin_pct` | NUMERIC(5,2) | YES | Profit margin percentage | `ROUND(margin_pct::NUMERIC, 2)` |
| `promo_flag` | INTEGER | YES | Promotional flag | No change |
| `event` | TEXT | YES | Special event | No change |
| `ad_spend` | NUMERIC(10,2) | YES | Advertising spend | `ROUND(ad_spend::NUMERIC, 2)` |
| `web_traffic` | INTEGER | YES | Website visits | `ROUND(web_traffic)::INT` |
| `review_score` | NUMERIC(3,2) | YES | Customer review score | `ROUND(review_score::NUMERIC, 2)` |
| `discontinued_flag` | INTEGER | YES | Discontinued flag | No change |
| `launch_date` | DATE | YES | SKU launch date | No change |
| `discontinue_date` | DATE | YES | SKU discontinuation date | No change |
| `archetype` | TEXT | YES | Product lifecycle stage | No change |

### Filters
- `WHERE units_sold IS NOT NULL AND order_value IS NOT NULL`

---

## Table: mart_sales_summary

**Purpose:** Aggregated KPI table for forecasting and dashboards.

**Materialization:** Table  
**Source:** `public.stg_vitamarkets`  
**dbt Model:** `models/mart_sales_summary.sql`  
**Grain:** One row per (date, sku, category, channel, country, customer_segment)

### Schema

| Column | Type | Nullable | Description | Calculation |
|--------|------|----------|-------------|-------------|
| `date` | DATE | NO | Transaction date | From stg_vitamarkets |
| `sku` | TEXT | NO | Stock Keeping Unit identifier | From stg_vitamarkets |
| `category` | TEXT | YES | Product category | From stg_vitamarkets |
| `channel` | TEXT | YES | Sales channel | From stg_vitamarkets |
| `country` | TEXT | YES | Country code | From stg_vitamarkets |
| `customer_segment` | TEXT | YES | Customer demographic | From stg_vitamarkets |
| `total_units_sold` | INTEGER | NO | Total units sold | `SUM(units_sold)` |
| `total_order_value` | NUMERIC(12,2) | NO | Total revenue (USD) | `SUM(order_value)` |
| `transaction_count` | INTEGER | NO | Number of transactions | `COUNT(*)` |
| `main_event` | TEXT | YES | Primary event for this date/SKU | `MAX(event)` |
| `promo_flag` | INTEGER | YES | Promotional flag | `MAX(promo_flag)` |
| `discontinued_flag` | INTEGER | YES | Discontinued flag | `MAX(discontinued_flag)` |

### Business Logic
- **Aggregation Level:** Daily totals per unique combination of dimensions
- **Used By:** Prophet forecasting engine, Power BI dashboards
- **Refresh Frequency:** Daily (via `dbt run`)

### Sample Row
```sql
date                | 2024-11-01
sku                 | Flagship Growth
category            | Tech
channel             | website
country             | US
customer_segment    | Young Pro
total_units_sold    | 145
total_order_value   | 18234.67
transaction_count   | 12
main_event          | NULL
promo_flag          | 0
discontinued_flag   | 0
```

---

## Table: simple_prophet_forecast

**Purpose:** Stores 90-day forecasts and historical actuals for overlay visualization.

**Materialization:** Table  
**Source:** Output from `prophet_improved.py`  
**Refresh:** Full replace after each forecast run

### Schema

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `ds` | TIMESTAMP | NO | Date (Prophet naming convention) |
| `yhat` | NUMERIC | NO | Predicted value (or actual if type='actual') |
| `yhat_lower` | NUMERIC | NO | Lower bound of 80% prediction interval |
| `yhat_upper` | NUMERIC | NO | Upper bound of 80% prediction interval |
| `sku` | TEXT | NO | Stock Keeping Unit identifier |
| `type` | TEXT | NO | "actual" or "forecast" |

### Business Logic
- **Actuals:** Historical data from `mart_sales_summary` where `yhat = actual_units_sold`
- **Forecasts:** Prophet predictions for next 90 days
- **Prediction Intervals:** 80% confidence bands (can be changed to 95%)
- **Used By:** Power BI "Forecast vs. Actuals" dashboard

### Sample Rows
```sql
-- Historical actual
ds           | 2024-10-15 00:00:00
yhat         | 45.0
yhat_lower   | 45.0
yhat_upper   | 45.0
sku          | Flagship Growth
type         | actual

-- Future forecast
ds           | 2024-12-15 00:00:00
yhat         | 48.3
yhat_lower   | 35.2
yhat_upper   | 61.4
sku          | Flagship Growth
type         | forecast
```

---

## Table: forecast_error_metrics

**Purpose:** Tracks forecasting accuracy per SKU.

**Materialization:** Table  
**Source:** Output from `prophet_improved.py`  
**Refresh:** Full replace after each forecast run

### Schema

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `sku` | TEXT | NO | Stock Keeping Unit identifier |
| `MAE` | NUMERIC | NO | Mean Absolute Error (in units) |
| `n_obs` | INTEGER | NO | Number of observations used for training |

### Business Logic
- **MAE Calculation:** `mean(abs(actual - predicted))`
- **⚠️ Current Limitation:** Calculated on **in-sample data** (training set), not holdout test set
- **Recommended Fix:** Calculate on last 30 days of held-out data

### Sample Row
```sql
sku    | Flagship Growth
MAE    | 6.8
n_obs  | 1095
```

---

## Data Lineage

```
vitamarkets_ultrarealistic_sampledataset.csv
  ↓ (psql \COPY)
vitamarkets_raw
  ↓ (dbt: stg_vitamarkets.sql)
stg_vitamarkets
  ↓ (dbt: mart_sales_summary.sql)
mart_sales_summary
  ↓ (Python: prophet_improved.py)
simple_prophet_forecast + forecast_error_metrics
  ↓ (Power BI Direct Query)
Dashboard
```

---

## Sample Queries

### 1. Total Revenue by SKU (Last 30 Days)
```sql
SELECT 
    sku,
    SUM(total_order_value) AS revenue,
    SUM(total_units_sold) AS units
FROM mart_sales_summary
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY sku
ORDER BY revenue DESC;
```

### 2. Year-over-Year Growth by SKU
```sql
WITH this_year AS (
    SELECT sku, SUM(total_order_value) AS revenue_ty
    FROM mart_sales_summary
    WHERE date >= DATE_TRUNC('year', CURRENT_DATE)
    GROUP BY sku
),
last_year AS (
    SELECT sku, SUM(total_order_value) AS revenue_ly
    FROM mart_sales_summary
    WHERE date >= DATE_TRUNC('year', CURRENT_DATE) - INTERVAL '1 year'
      AND date < DATE_TRUNC('year', CURRENT_DATE)
    GROUP BY sku
)
SELECT 
    t.sku,
    t.revenue_ty,
    l.revenue_ly,
    ROUND(((t.revenue_ty - l.revenue_ly) / l.revenue_ly * 100)::NUMERIC, 1) AS yoy_growth_pct
FROM this_year t
LEFT JOIN last_year l ON t.sku = l.sku
ORDER BY yoy_growth_pct DESC NULLS LAST;
```

### 3. Forecast Accuracy by SKU
```sql
SELECT 
    sku,
    MAE,
    n_obs,
    ROUND((MAE / (SELECT AVG(total_units_sold) FROM mart_sales_summary WHERE mart_sales_summary.sku = forecast_error_metrics.sku) * 100)::NUMERIC, 1) AS mape_pct
FROM forecast_error_metrics
ORDER BY MAE ASC;
```

### 4. Next 7 Days Forecast (Top 3 SKUs)
```sql
WITH top_skus AS (
    SELECT sku
    FROM mart_sales_summary
    WHERE date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY sku
    ORDER BY SUM(total_order_value) DESC
    LIMIT 3
)
SELECT 
    f.ds::DATE AS forecast_date,
    f.sku,
    ROUND(f.yhat::NUMERIC, 1) AS predicted_units,
    ROUND(f.yhat_lower::NUMERIC, 1) AS lower_bound,
    ROUND(f.yhat_upper::NUMERIC, 1) AS upper_bound
FROM simple_prophet_forecast f
INNER JOIN top_skus t ON f.sku = t.sku
WHERE f.type = 'forecast'
  AND f.ds >= CURRENT_DATE
  AND f.ds <= CURRENT_DATE + INTERVAL '7 days'
ORDER BY f.sku, f.ds;
```

### 5. SKUs with Declining Trends (Last 90 Days)
```sql
WITH recent AS (
    SELECT sku, SUM(total_units_sold) AS units_recent
    FROM mart_sales_summary
    WHERE date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY sku
),
prior AS (
    SELECT sku, SUM(total_units_sold) AS units_prior
    FROM mart_sales_summary
    WHERE date >= CURRENT_DATE - INTERVAL '180 days'
      AND date < CURRENT_DATE - INTERVAL '90 days'
    GROUP BY sku
)
SELECT 
    r.sku,
    r.units_recent,
    p.units_prior,
    ROUND(((r.units_recent - p.units_prior) / p.units_prior * 100)::NUMERIC, 1) AS change_pct
FROM recent r
INNER JOIN prior p ON r.sku = p.sku
WHERE r.units_recent < p.units_prior
ORDER BY change_pct ASC;
```

---

## Column Naming Conventions

- **`_flag`**: Binary indicator (0 or 1)
- **`_pct`**: Percentage (stored as decimal: 0.32 = 32%)
- **`_date`**: Date column (DATE type)
- **`total_*`**: Aggregated sum
- **`main_*`**: Derived/representative value (e.g., MAX of a group)
- **`n_*`**: Count or number of items

---

## Data Quality Rules

### Required Validations (Recommended)
1. **Referential Integrity:** All SKUs in `mart_sales_summary` should exist in `vitamarkets_raw`
2. **Non-Negative Values:** `units_sold`, `order_value`, `ad_spend` should be >= 0
3. **Valid Date Range:** `date` should be between 2021-01-01 and CURRENT_DATE + 90 days
4. **Channel Values:** `channel` should be in ('website', 'amazon', 'mobile', NULL)
5. **Country Values:** `country` should be in ('US', 'CA', NULL)

### Implemented Checks (dbt)
- None currently (see upgrade plan for adding dbt tests)

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-12-07 | Initial data dictionary created | System |

---

**For more information:**
- Architecture: See `docs/ARCHITECTURE.md`
- Setup: See `docs/SETUP.md`
- Business Context: See `docs/BUSINESS_DECISIONS.md`
