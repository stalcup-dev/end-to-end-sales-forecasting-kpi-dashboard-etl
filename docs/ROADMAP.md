# Roadmap & Known Limitations

> **Last Updated:** 2025-01-16

This document tracks planned improvements, known limitations, and technical debt.

---

## ✅ Completed (v2)

| Feature | Status | Notes |
|---------|--------|-------|
| Train/test split evaluation | ✅ Done | 30-day holdout with MAE, RMSE, MAPE, bias, coverage |
| Versioned forecast tables | ✅ Done | `prophet_forecasts_YYYYMMDD_HHMM` pattern |
| Stable Power BI views | ✅ Done | `simple_prophet_forecast`, `forecast_error_metrics` |
| Parallel SKU training | ✅ Done | `joblib` for ~4x speedup |
| US holiday handling | ✅ Done | Black Friday, Christmas, etc. |
| CI/CD pipeline | ✅ Done | GitHub Actions: ruff lint + pytest |
| Forecast run tracking | ✅ Done | `forecast_run_id` column in all outputs |
| Comprehensive documentation | ✅ Done | DATA_CONTRACT, FORECASTING_POLICIES, etc. |

---

## 🔜 Planned Improvements

### High Priority (Next Sprint)

| Feature | Description | Impact |
|---------|-------------|--------|
| **Fix dashboard aggregations** | Ensure all error metrics use AVERAGE not SUM | Critical for accurate reporting |
| **Promo regressor** | Add `promo_flag` as Prophet regressor for promo-dependent SKUs | 10-20% MAPE improvement on promo SKUs |
| **Rolling backtests** | 3-5 rolling-origin backtests instead of single split | More robust evaluation |
| **Weighted MAPE** | Volume-weighted MAPE for portfolio-level accuracy | Better business alignment |

### Medium Priority (Q2)

| Feature | Description | Impact |
|---------|-------------|--------|
| **Stockout handling** | Exclude OOS periods from training | Reduce bias for supply-disrupted SKUs |
| **Discontinued SKU detection** | Auto-detect and hard-stop forecasts at 0 | Prevent phantom demand |
| **Interval calibration** | Widen intervals when coverage < 80% | Improve prediction honesty |
| **Baseline benchmarks** | Add seasonal-naive and Prophet-no-regressors baselines | Honest model comparison |
| **Automated contract validation** | CI check that views have expected columns | Catch schema drift before deploy |

### Lower Priority (Backlog)

| Feature | Description | Impact |
|---------|-------------|--------|
| **Hierarchical reconciliation** | MinT/bottom-up reconciliation across channel/country | Coherent aggregates |
| **MLflow integration** | Experiment tracking and model versioning | Better reproducibility |
| **Great Expectations** | Advanced data quality validation | Catch data issues early |
| **Incremental forecasting** | Only re-train SKUs with new data | Faster pipeline runs |
| **Alert system** | Email/Slack alerts when MAPE degrades or coverage drops | Proactive monitoring |

---

## 🐛 Known Limitations

### Forecasting

| Limitation | Impact | Workaround |
|------------|--------|------------|
| No promo regressors | Promo-dependent SKUs may have higher MAPE | Manual adjustment during promo periods |
| No stockout handling | Supply-disrupted SKUs show negative bias | Manually flag OOS periods |
| Single train/test split | Evaluation sensitive to cutoff date | Review multiple historical runs |
| Fixed 90-day horizon | May be too long for volatile SKUs | Reduce horizon in config |

### Data

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Daily grain only | Can't capture intraday patterns | Aggregate to weekly if too noisy |
| No price data | Can't model price elasticity | Future enhancement |
| No external regressors | Missing weather, competitor, macro factors | Manual adjustment |

### Dashboard

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Windows-only Power BI | Mac users can't view interactive dashboard | Use screenshots or export to PDF |
| Manual refresh required | Data may be stale | Schedule auto-refresh or use DirectQuery |
| No mobile optimization | Dashboard doesn't render well on phones | Use Power BI mobile app |

---

## 📊 Technical Debt

| Item | Description | Priority |
|------|-------------|----------|
| Consolidate pipeline scripts | `forecast_prophet_v2.py` vs `vitamarkets/pipeline.py` vs `scripts/run_daily.py` | Medium |
| Remove backup README | `README_backup.md` should be deleted after review | Low |
| Standardize column names | Canonical vs compatibility views add complexity | Low |
| Add type hints | Python code lacks comprehensive type annotations | Low |

---

## 🎯 Success Metrics

When all planned improvements are complete, we expect:

| Metric | Current | Target |
|--------|---------|--------|
| Average MAPE | ~15% | < 12% |
| Coverage accuracy | Variable | 78-82% consistently |
| Pipeline runtime | ~2 min | < 1 min (with incremental) |
| Test coverage | ~80% | > 90% |
| Documentation pages | 7 | 10+ |

---

## 📝 Changelog

### v2.0.0 (2025-01-16)
- Added versioned tables with stable views
- Implemented train/test split evaluation
- Added 5 metrics: MAE, RMSE, MAPE, bias, coverage
- Parallel SKU training with joblib
- US holiday handling
- CI/CD with GitHub Actions
- Comprehensive documentation restructure

### v1.0.0 (2024-12-01)
- Initial release
- Basic Prophet forecasting
- Single forecast table
- Power BI dashboard

---

## 🔗 Related Documentation

- [DATA_CONTRACT.md](DATA_CONTRACT.md) — View schemas and Power BI integration
- [FORECASTING_POLICIES.md](FORECASTING_POLICIES.md) — SKU eligibility and metric targets
- [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) — Power BI usage guide
