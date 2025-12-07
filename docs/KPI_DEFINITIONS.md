# KPI Definitions

## Overview

This document defines all key performance indicators (KPIs) used in the Vita Markets analytics pipeline and Power BI dashboards. Each KPI includes its business purpose, calculation logic, and interpretation guidelines.

---

## Sales Performance KPIs

### 1. Total Units Sold

**Definition:** Total number of product units sold across all SKUs and channels.

**Calculation:**
```sql
SELECT SUM(total_units_sold) 
FROM mart_sales_summary
WHERE date BETWEEN '2024-01-01' AND '2024-12-31'
```

**Business Purpose:** Primary volume metric for inventory planning and production forecasting.

**Interpretation:**
- Increasing trend → Strong demand, may need to increase inventory
- Decreasing trend → Weak demand, risk of overstock
- Sudden spike → Promotional success or seasonal effect

**Target:** 10% YoY growth

**Dashboard Location:** Executive KPI View (top card)

---

### 2. Total Revenue (Total Order Value)

**Definition:** Sum of all order values in USD.

**Calculation:**
```sql
SELECT SUM(total_order_value) 
FROM mart_sales_summary
WHERE date BETWEEN '2024-01-01' AND '2024-12-31'
```

**Business Purpose:** Primary financial metric for revenue tracking and business health.

**Interpretation:**
- Revenue can grow while units decline (price increase or mix shift to premium products)
- Revenue declining faster than units → Discount pressure or shift to lower-margin products

**Target:** 15% YoY growth

**Dashboard Location:** Executive KPI View (top card)

---

### 3. Year-over-Year (YoY) Growth

**Definition:** Percentage change in revenue or units compared to same period last year.

**Calculation:**
```sql
WITH this_year AS (
    SELECT SUM(total_order_value) AS revenue
    FROM mart_sales_summary
    WHERE date >= '2024-01-01' AND date <= '2024-12-31'
),
last_year AS (
    SELECT SUM(total_order_value) AS revenue
    FROM mart_sales_summary
    WHERE date >= '2023-01-01' AND date <= '2023-12-31'
)
SELECT 
    ((t.revenue - l.revenue) / l.revenue * 100) AS yoy_growth_pct
FROM this_year t, last_year l
```

**Business Purpose:** Measures business momentum and market share gains/losses.

**Interpretation:**
- Positive YoY: Company is growing
- Negative YoY: Company is shrinking (may be market-wide or company-specific)
- >20% YoY: High-growth phase (typical for new products or aggressive expansion)

**Target:** 
- New Launch SKUs: >100% YoY (first 2 years)
- Mature SKUs: 5-10% YoY
- Portfolio Average: 15% YoY

**Dashboard Location:** Executive KPI View (gauge/card per SKU)

---

### 4. Average Order Value (AOV)

**Definition:** Average revenue per transaction.

**Calculation:**
```sql
SELECT 
    SUM(total_order_value) / SUM(transaction_count) AS aov
FROM mart_sales_summary
WHERE date BETWEEN '2024-01-01' AND '2024-12-31'
```

**Business Purpose:** Indicates pricing power and customer basket size.

**Interpretation:**
- Increasing AOV → Customers buying more per order (upsell/cross-sell success)
- Decreasing AOV → Discount pressure or shift to single-item purchases

**Target:** $120 (varies by channel: website > mobile > amazon)

**Dashboard Location:** Executive KPI View (trend chart)

---

## Forecasting KPIs

### 5. Mean Absolute Error (MAE)

**Definition:** Average absolute difference between forecasted and actual units sold.

**Calculation:**
```python
MAE = mean(abs(actual - forecast))
```

**Units:** Same as target variable (units sold)

**Business Purpose:** Primary accuracy metric for forecast reliability. Lower is better.

**Interpretation:**
- MAE = 5 → On average, forecast is off by ±5 units
- MAE should be < 10% of average daily sales

**Target:** 
- High-volume SKUs (>50 units/day): MAE < 8 units
- Medium-volume SKUs (20-50 units/day): MAE < 5 units
- Low-volume SKUs (<20 units/day): MAE < 3 units

**Dashboard Location:** Forecasting Dashboard (accuracy gauge per SKU)

**Table:** `forecast_error_metrics.MAE`

---

### 6. Mean Absolute Percentage Error (MAPE)

**Definition:** Average absolute percentage difference between forecasted and actual values.

**Calculation:**
```python
MAPE = mean(abs((actual - forecast) / actual)) * 100
```

**Units:** Percentage (%)

**Business Purpose:** Normalized accuracy metric that allows comparison across SKUs of different scales.

**Interpretation:**
- MAPE < 10%: Excellent forecast
- MAPE 10-20%: Good forecast
- MAPE 20-50%: Acceptable forecast (for volatile products)
- MAPE > 50%: Poor forecast (needs model improvement)

**Target:** 
- Portfolio Median: <15%
- Individual SKU: <20%

**Dashboard Location:** Forecasting Dashboard (accuracy table)

**Note:** Currently not calculated; see upgrade plan to add MAPE calculation.

---

### 7. Root Mean Squared Error (RMSE)

**Definition:** Square root of average squared differences between forecasted and actual values.

**Calculation:**
```python
RMSE = sqrt(mean((actual - forecast)^2))
```

**Units:** Same as target variable (units sold)

**Business Purpose:** Penalizes large errors more than MAE. Useful for understanding worst-case misses.

**Interpretation:**
- RMSE > MAE → Forecast has some large outlier errors
- RMSE ≈ MAE → Errors are consistent (no major outliers)

**Target:** RMSE < 1.5 × MAE

**Dashboard Location:** Forecasting Dashboard (advanced metrics table)

**Note:** Currently not calculated; see upgrade plan to add RMSE calculation.

---

### 8. Forecast Bias

**Definition:** Average signed difference between forecasted and actual values.

**Calculation:**
```python
Bias = mean(forecast - actual)
```

**Units:** Same as target variable (units sold)

**Business Purpose:** Detects systematic over-forecasting or under-forecasting.

**Interpretation:**
- Bias > 0: Consistently over-forecasting (overstock risk)
- Bias < 0: Consistently under-forecasting (stockout risk)
- Bias ≈ 0: Unbiased forecast (ideal)

**Target:** Bias within ±2 units (or ±5% of average daily sales)

**Dashboard Location:** Forecasting Dashboard (bias chart per SKU)

**Note:** Currently not calculated; see upgrade plan to add bias tracking.

---

### 9. Prediction Interval Coverage

**Definition:** Percentage of actual values that fall within the 80% prediction interval.

**Calculation:**
```python
Coverage = (count(yhat_lower <= actual <= yhat_upper) / count(actual)) * 100
```

**Units:** Percentage (%)

**Business Purpose:** Validates that uncertainty intervals are calibrated correctly.

**Interpretation:**
- Coverage ≈ 80%: Well-calibrated intervals
- Coverage < 80%: Intervals too narrow (under-estimating uncertainty)
- Coverage > 80%: Intervals too wide (over-estimating uncertainty)

**Target:** 75-85% (should match prediction interval level)

**Dashboard Location:** Forecasting Dashboard (coverage gauge)

**Note:** Currently not calculated; see upgrade plan to add coverage validation.

---

## Product Lifecycle KPIs

### 10. SKU Lifecycle Stage

**Definition:** Classification of SKU based on sales trend and launch date.

**Categories:**
- **Growth:** <2 years old, YoY growth >20%
- **Mature:** 2-5 years old, YoY growth 0-20%
- **Decline:** >5 years old or YoY growth <0%
- **Discontinued:** `discontinued_flag = 1`

**Calculation:**
```sql
SELECT 
    sku,
    CASE 
        WHEN discontinued_flag = 1 THEN 'Discontinued'
        WHEN CURRENT_DATE - launch_date < INTERVAL '2 years' 
             AND yoy_growth_pct > 20 THEN 'Growth'
        WHEN CURRENT_DATE - launch_date BETWEEN INTERVAL '2 years' AND INTERVAL '5 years' 
             AND yoy_growth_pct BETWEEN 0 AND 20 THEN 'Mature'
        ELSE 'Decline'
    END AS lifecycle_stage
FROM (
    -- Subquery to calculate YoY growth per SKU
    ...
) AS sku_metrics
```

**Business Purpose:** Informs product portfolio management decisions.

**Interpretation:**
- **Growth SKUs:** Invest in marketing, ensure supply chain can scale
- **Mature SKUs:** Optimize margins, consider line extensions
- **Decline SKUs:** Plan phase-out, allocate resources to growth SKUs
- **Discontinued SKUs:** Monitor clearance sales, avoid reordering

**Dashboard Location:** Executive KPI View (SKU matrix/scatter plot)

---

### 11. New Product Penetration

**Definition:** Percentage of total revenue from SKUs launched in the last 12 months.

**Calculation:**
```sql
WITH new_skus AS (
    SELECT SUM(total_order_value) AS new_revenue
    FROM mart_sales_summary
    WHERE launch_date >= CURRENT_DATE - INTERVAL '12 months'
),
total AS (
    SELECT SUM(total_order_value) AS total_revenue
    FROM mart_sales_summary
)
SELECT (n.new_revenue / t.total_revenue * 100) AS new_product_penetration_pct
FROM new_skus n, total t
```

**Business Purpose:** Measures innovation velocity and portfolio refresh rate.

**Interpretation:**
- >20%: High innovation rate (good for growth stage)
- 10-20%: Moderate innovation (typical for mature companies)
- <10%: Low innovation (risk of stagnation)

**Target:** 15-20%

**Dashboard Location:** Executive KPI View (pie chart)

---

## Operational KPIs

### 12. Inventory Turnover (Implied)

**Definition:** How quickly inventory is sold and replaced.

**Note:** Not directly calculated in current pipeline (requires inventory data), but can be inferred from forecast vs. actual.

**Calculation (if inventory data available):**
```
Inventory Turnover = COGS / Average Inventory Value
```

**Business Purpose:** Measures efficiency of inventory management.

**Target:** 6-12x per year (higher = less capital tied up in inventory)

---

### 13. Stockout Risk

**Definition:** Probability that demand exceeds forecast upper bound.

**Calculation:**
```sql
SELECT 
    sku,
    COUNT(*) FILTER (WHERE actual > yhat_upper) AS stockout_days,
    COUNT(*) AS total_days,
    (COUNT(*) FILTER (WHERE actual > yhat_upper)::FLOAT / COUNT(*)) * 100 AS stockout_risk_pct
FROM (
    SELECT 
        f.sku,
        f.yhat_upper,
        m.total_units_sold AS actual
    FROM simple_prophet_forecast f
    INNER JOIN mart_sales_summary m ON f.ds::DATE = m.date AND f.sku = m.sku
    WHERE f.type = 'forecast'
) AS comparison
GROUP BY sku
```

**Business Purpose:** Identifies SKUs at risk of running out of stock.

**Interpretation:**
- <5%: Low risk
- 5-10%: Moderate risk (increase safety stock)
- >10%: High risk (urgent action needed)

**Target:** <5% stockout rate

**Dashboard Location:** Operations Dashboard (alert table)

**Note:** Not currently tracked; recommended addition.

---

## Channel & Segment KPIs

### 14. Channel Mix

**Definition:** Percentage of revenue by sales channel.

**Calculation:**
```sql
SELECT 
    channel,
    SUM(total_order_value) AS revenue,
    (SUM(total_order_value) / (SELECT SUM(total_order_value) FROM mart_sales_summary) * 100) AS revenue_pct
FROM mart_sales_summary
GROUP BY channel
ORDER BY revenue DESC
```

**Channels:**
- Website (direct)
- Amazon (marketplace)
- Mobile app

**Business Purpose:** Tracks channel diversification and identifies channel-specific trends.

**Interpretation:**
- High Amazon %: Dependency risk (platform fees, policy changes)
- High website %: Better margins but requires marketing investment
- Balanced mix: Resilience to channel disruptions

**Target:** 
- Website: 40-50%
- Amazon: 30-40%
- Mobile: 20-30%

**Dashboard Location:** Executive KPI View (pie chart)

---

### 15. Customer Segment Performance

**Definition:** Revenue and growth by customer demographic.

**Segments:**
- Young Pro (25-35 years)
- Family (35-50 years with children)
- Older Adult (50+ years)

**Calculation:**
```sql
SELECT 
    customer_segment,
    SUM(total_order_value) AS revenue,
    SUM(total_units_sold) AS units
FROM mart_sales_summary
WHERE date >= '2024-01-01'
GROUP BY customer_segment
ORDER BY revenue DESC
```

**Business Purpose:** Informs marketing targeting and product development.

**Dashboard Location:** Executive KPI View (bar chart)

---

## Data Quality KPIs

### 16. Data Completeness

**Definition:** Percentage of expected data points that are non-null.

**Calculation:**
```sql
SELECT 
    (COUNT(total_units_sold) / COUNT(*) * 100) AS completeness_pct
FROM mart_sales_summary
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
```

**Target:** >99%

**Dashboard Location:** Internal data quality dashboard (not customer-facing)

---

### 17. Data Freshness

**Definition:** Time elapsed since last data update.

**Calculation:**
```sql
SELECT 
    MAX(date) AS latest_data_date,
    CURRENT_DATE - MAX(date) AS days_since_update
FROM mart_sales_summary
```

**Target:** <1 day (daily refresh)

**Dashboard Location:** Internal data quality dashboard

---

## Summary Table

| KPI | Type | Target | Priority | Dashboard Page |
|-----|------|--------|----------|----------------|
| Total Revenue | Sales | 15% YoY | High | Executive |
| Total Units Sold | Sales | 10% YoY | High | Executive |
| YoY Growth | Sales | 15% | High | Executive |
| AOV | Sales | $120 | Medium | Executive |
| MAE | Forecast | <8 units | High | Forecasting |
| MAPE | Forecast | <15% | High | Forecasting |
| RMSE | Forecast | <12 units | Medium | Forecasting |
| Forecast Bias | Forecast | ±2 units | Medium | Forecasting |
| Coverage | Forecast | 75-85% | Medium | Forecasting |
| New Product Penetration | Product | 15-20% | Medium | Executive |
| Channel Mix | Operational | 40/30/30 | Low | Executive |
| Stockout Risk | Operational | <5% | Medium | Operations |

---

## Calculation Schedule

| KPI | Update Frequency | Source |
|-----|------------------|--------|
| Sales KPIs | Daily | `mart_sales_summary` |
| Forecasting KPIs | Daily | `forecast_error_metrics` |
| Product Lifecycle | Weekly | Calculated in Power BI |
| Channel Mix | Daily | `mart_sales_summary` |

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-12-07 | Initial KPI definitions | System |

---

**Related Documents:**
- Data Dictionary: `docs/DATA_DICTIONARY.md`
- Business Decisions: `docs/BUSINESS_DECISIONS.md`
- Architecture: `docs/ARCHITECTURE.md`
