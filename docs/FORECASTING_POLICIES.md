# Forecasting Policies

> **Last Updated:** 2025-01-16

This document defines the business rules and technical policies governing SKU eligibility, data preparation, model parameters, and metric interpretation.

---

## SKU Eligibility Rules

Not all SKUs are forecastable. The pipeline applies filters to ensure only SKUs with sufficient history are modeled.

| Rule | Threshold | Rationale |
|------|-----------|-----------|
| **Minimum history** | ≥ 730 days (2 years) | Captures at least one full annual cycle |
| **Minimum volume** | > 500 total units sold | Avoids noise-dominated low-volume SKUs |

**What happens to ineligible SKUs?**
- They are logged as "skipped" in pipeline output
- No forecast rows are generated
- No metrics row is created
- They do NOT appear in `simple_prophet_forecast` or `forecast_error_metrics`

---

## SKU Types (Behavioral Categories)

SKUs fall into distinct behavioral patterns. Understanding these helps interpret metrics and set expectations.

| Type | Description | Forecasting Strategy | Metric Targets |
|------|-------------|---------------------|----------------|
| **Classic Seasonal** | Strong weekly/yearly seasonality, mild trend | Prophet with yearly+weekly seasonality; holidays enabled | MAPE < 15%, coverage ≈ 80% |
| **Flagship Growth** | Trend-dominated, consistent growth | Flexible changepoints; monitor for saturation | Bias ≈ 0, MAPE trending down |
| **Promo Dependent** | Sales spike on promotions | Add `promo_flag` regressor (future work) | Lower RMSE on spikes, better coverage |
| **Viral Spike** | Rare unpredictable surges | Widen intervals, focus on honest uncertainty | Coverage ≈ 80%, accept higher MAPE |
| **Supply Disrupted** | Constrained by stockouts | Exclude/flag OOS periods (future work) | Reduce negative bias |
| **Discontinued** | Demand trends to zero | Hard-stop forecast at 0 after discontinue date | No phantom demand |
| **Cannibalized** | Demand shifted to other SKUs | Treat as structural break; use recent window | Reduce post-break bias |
| **Slow Decliner** | Gentle downtrend | Constrain trend flexibility | Low bias, stable MAE |

---

## Data Preparation

### Outlier Handling

**Policy:** Clip values above the 99th percentile per SKU.

| Step | Description |
|------|-------------|
| 1. Compute 99th percentile | Per-SKU, based on historical `total_units_sold` |
| 2. Clip outliers | Values > 99th percentile → set to 99th percentile |
| 3. Preserve data | Outliers are capped, not removed |

**Rationale:** Prevents extreme values (e.g., data entry errors, one-time bulk orders) from distorting model fit while preserving the overall signal.

### Aggregation Grain

| Level | Value |
|-------|-------|
| Time grain | Daily |
| Primary key | `date + sku` (after collapsing channel/segment) |
| Aggregation | `SUM(total_units_sold)` across channel/country/segment |

---

## Model Parameters

### Prophet Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `yearly_seasonality` | True | E-commerce has strong annual patterns |
| `weekly_seasonality` | True | Weekday vs. weekend effects |
| `daily_seasonality` | False | Too noisy at daily grain |
| `holidays` | US federal holidays | Captures Black Friday, Christmas, etc. |
| `interval_width` | 0.80 | 80% prediction interval |
| `changepoint_prior_scale` | Prophet default (0.05) | Balanced flexibility |

### Train/Test Split

| Component | Value |
|-----------|-------|
| Test (holdout) window | 30 days |
| Training window | All data before holdout |
| Forecast horizon | 90 days beyond last actual |

---

## Metrics Reference

### Definitions

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **MAE** | `mean(abs(actual - predicted))` | Average error in units; lower is better |
| **RMSE** | `sqrt(mean((actual - predicted)²))` | Penalizes large errors; lower is better |
| **MAPE** | `mean(abs((actual - predicted) / actual)) × 100` | Percentage error; < 20% is good |
| **Bias** | `mean(predicted - actual)` | Positive = over-forecasting, negative = under |
| **Coverage** | `% of actuals within [yhat_lower, yhat_upper]` | Should be ≈ 80% for 80% PI |

### Target Thresholds

| Metric | 🟢 Good | 🟡 Acceptable | 🔴 Needs Work |
|--------|---------|---------------|---------------|
| MAPE | < 10% | 10–20% | > 20% |
| Coverage | 75–85% | 65–75% or 85–95% | < 65% or > 95% |
| Bias | -5 to +5 | -15 to +15 | > ±15 |

### How to Read Coverage

- **Coverage ≈ 80%:** Model is well-calibrated; intervals are honest.
- **Coverage < 70%:** Intervals too narrow; widen by increasing uncertainty or retraining.
- **Coverage > 90%:** Intervals too wide; model may be underconfident or overfit to noise.

---

## Metric Aggregation Rules

**CRITICAL: When aggregating metrics across SKUs, use AVERAGE (or median), never SUM.**

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| Sum of MAE across SKUs | Average MAE across SKUs |
| Sum of MAPE across SKUs | Average (or median) MAPE |

**Why?** Summing errors across SKUs produces a meaningless number. If SKU A has MAE=10 and SKU B has MAE=20, the "sum" of 30 doesn't represent any real forecast error.

### Recommended Dashboard Measures

```dax
-- Portfolio-level accuracy (average across SKUs)
Avg MAPE % = AVERAGE(forecast_error_metrics[test_mape_pct])
Avg MAE = AVERAGE(forecast_error_metrics[test_mae])
Avg Coverage % = AVERAGE(forecast_error_metrics[test_coverage_pct])

-- For volume-weighted MAPE (future enhancement):
-- Weighted MAPE = SUMX(sku, mape * volume) / SUM(volume)
```

---

## Pipeline Versioning

### How It Works

1. Each pipeline run creates **versioned tables**:
   - `prophet_forecasts_YYYYMMDD_HHMM`
   - `prophet_forecast_metrics_YYYYMMDD_HHMM`

2. Pipeline creates/updates **stable views** pointing to latest tables:
   - `v_forecast_daily_latest` (canonical column names)
   - `v_forecast_sku_metrics_latest` (canonical column names)

3. Pipeline creates/updates **compatibility views** for Power BI:
   - `simple_prophet_forecast` (legacy column names)
   - `forecast_error_metrics` (legacy column names)

### Why Versioning?

- **Audit trail:** Previous runs are preserved for comparison
- **Safe rollback:** If new run has issues, old data still exists
- **No dashboard breakage:** Views always exist, just point to latest tables

---

## Known Limitations

| Limitation | Impact | Planned Fix |
|------------|--------|-------------|
| No promo regressors | Promo-dependent SKUs may have higher MAPE | Add `promo_flag` as regressor |
| No stockout handling | Supply-disrupted SKUs show negative bias | Filter OOS periods |
| Single train/test split | Evaluation may be sensitive to cutoff date | Implement rolling backtests |
| No hierarchical reconciliation | SKU forecasts may not sum to channel totals | Add MinT/bottom-up reconciliation |

---

## References

- [Prophet Documentation](https://facebook.github.io/prophet/)
- [DATA_CONTRACT.md](DATA_CONTRACT.md) — View schemas and Power BI integration
- [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) — How to interpret metrics in Power BI
