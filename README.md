# Vita Markets: End-to-End Sales Forecasting & KPI Dashboard

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL 14](https://img.shields.io/badge/PostgreSQL-14-316192?logo=postgresql)](https://www.postgresql.org/)
[![dbt 1.7](https://img.shields.io/badge/dbt-1.7-FF694B?logo=dbt)](https://www.getdbt.com/)
[![Prophet 1.1.5](https://img.shields.io/badge/Prophet-1.1.5-blue?logo=meta)](https://facebook.github.io/prophet/)
[![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi)](https://powerbi.microsoft.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/stalcup-dev/end-to-end-sales-forecasting-kpi-dashboard-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/stalcup-dev/end-to-end-sales-forecasting-kpi-dashboard-etl/actions)

> **An end-to-end analytics pipeline** that ingests daily sales data, transforms it using dbt, generates 90-day SKU-level forecasts with Prophet, and delivers executive-ready dashboards in Power BI. Built to mirror the work of a **Data Analyst** at a DTC e-commerce company.

![Executive KPI Dashboard](KPIDashboard.png)
*Real-time KPI tracking: 150% YoY growth in New Launch SKU, automated 90-day forecasts for inventory planning*

---

## 🎯 What This Project Demonstrates

A complete analytics workflow from raw data to executive dashboards:

| Skill Area | What I Built |
|------------|-------------|
| **SQL & Data Modeling** | Star schema design with dbt, staging/mart layers, complex aggregations, window functions |
| **Statistical Analysis** | Time series forecasting with Prophet, train/test evaluation, 5 accuracy metrics |
| **Data Visualization** | Executive dashboards in Power BI with KPIs, forecast vs. actuals, accuracy gauges |
| **ETL/Data Pipelines** | Automated CSV → PostgreSQL → dbt → Prophet → Power BI pipeline |
| **Business Storytelling** | Dashboards that answer "Which SKUs are growing?" and "How accurate are our forecasts?" |
| **Data Quality** | dbt schema tests, pytest suite (34+ tests), CI/CD with GitHub Actions |

**Business Context:**  
Vita Markets is a simulated Direct-to-Consumer vitamin/supplement retailer. The pipeline answers real commercial questions:
- *Which SKUs should we invest in? (Growth vs. Decline)*
- *How much inventory should we order? (90-day forecast)*
- *Are our forecasts reliable? (Accuracy metrics)*

---

## 📊 Key Business Insights

### Results Delivered

- **New Launch SKU** delivered **150% YoY growth**, fully offsetting revenue losses from discontinued products
- **Flagship Growth** remains the top revenue driver with consistent **25% YoY growth**
- **Automated pipeline** eliminates manual reporting (**4 hours/week → 0 hours**)
- **Forecasting** enables proactive inventory management and reduces stockout risk

### Forecasting Performance

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Median MAPE | 12.3% | Point forecasts are ~88% accurate on average |
| Coverage | ~80% | 80% of actuals fall within prediction intervals |
| Bias | ~0 | Forecasts are neither systematically high nor low |

---

## 🖼️ Dashboard Previews

### Executive KPI View
![KPI Dashboard](KPIDashboard.png)
*At-a-glance metrics: Total revenue, YoY growth by SKU, top/bottom performers, and product lifecycle analysis*

### Forecast vs. Actuals Overlay
![Forecasting Dashboard](ForecastingDash.png)
*90-day forecasts with uncertainty intervals (80% prediction bands), overlaid with historical actuals for validation*

---

## ⚡ Quick Start (10 minutes)

```powershell
# 1. Clone & setup
git clone https://github.com/stalcup-dev/end-to-end-sales-forecasting-kpi-dashboard-etl.git
cd end-to-end-sales-forecasting-kpi-dashboard-etl
python -m venv .venv; .venv\Scripts\activate        # Windows
pip install -r requirements.txt

# 2. Start Postgres (requires Docker)
docker compose up -d

# 3. Bootstrap database + seed data
cp .env.example .env   # Edit credentials if needed
python scripts/bootstrap.py

# 4. Run full pipeline (dbt → Prophet → metrics → report)
python forecast_prophet_v2.py
```

**Verify it worked:** see [Verification Checklist](#-verification-checklist) below.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  vitamarkets_ultrarealistic_sampledataset.csv (50k rows, 4 years)          │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PostgreSQL   public.vitamarkets_raw                                        │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  ▼  dbt run
┌─────────────────────────────────────────────────────────────────────────────┐
│  dbt Models   stg_vitamarkets (view) → mart_sales_summary (table)           │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  ▼  forecast_prophet_v2.py
┌─────────────────────────────────────────────────────────────────────────────┐
│  Prophet      prophet_forecasts_YYYYMMDD_HHMM (versioned table)             │
│  Forecasts    prophet_forecast_metrics_YYYYMMDD_HHMM (versioned table)      │
│               ↓ stable views                                                │
│               simple_prophet_forecast, forecast_error_metrics               │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Power BI     MainDash.pbix (Executive KPIs + Forecast vs. Actuals)         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎓 Skills Demonstrated

### SQL & Data Modeling
- ✅ Complex aggregations (GROUP BY, window functions, CTEs)
- ✅ dbt model lineage with `ref()` macro
- ✅ Star schema design (normalized staging, denormalized marts)
- ✅ Data quality checks (null handling, outlier clipping)
- ✅ Schema tests (unique, not_null, relationships, accepted_values)

### Statistical Forecasting & Analysis
- ✅ Time series analysis with Facebook Prophet
- ✅ Seasonality detection (weekly, yearly patterns)
- ✅ Outlier handling (99th percentile clipping)
- ✅ Prediction intervals (80% confidence bands)
- ✅ Rigorous model evaluation (train/test split)
- ✅ 5 accuracy metrics: MAE, RMSE, MAPE, bias, coverage

### Data Visualization & Business Intelligence
- ✅ Executive KPI dashboard design
- ✅ Forecast vs. actuals visualization with uncertainty bands
- ✅ DAX measures for aggregations
- ✅ Slicers and filters for self-service analytics
- ✅ Business storytelling (insights → actions)

### Data Engineering & ETL
- ✅ ETL pipeline design (CSV → Postgres → dbt → Prophet)
- ✅ Database design with PostgreSQL
- ✅ Connection management (SQLAlchemy + psycopg2)
- ✅ Error handling and logging
- ✅ Docker containerization
- ✅ Idempotent data loading

### Software Engineering Best Practices
- ✅ Unit testing (pytest with 34+ tests)
- ✅ Code quality (ruff linting, black formatting)
- ✅ CI/CD pipeline (GitHub Actions)
- ✅ Version control (Git best practices)
- ✅ Documentation (50+ pages)

---

## 📊 Power BI Data Contract

> **⚠️ CRITICAL:** Power BI must query **views**, not versioned tables. See [docs/DATA_CONTRACT.md](docs/DATA_CONTRACT.md) for full schema.

| View | Purpose |
|------|---------|
| `public.simple_prophet_forecast` | Daily forecasts + actuals (columns: `ds`, `yhat`, `yhat_lower`, `yhat_upper`) |
| `public.forecast_error_metrics` | Per-SKU accuracy (columns: `test_mae`, `test_mape_pct`, `test_coverage_pct`, etc.) |

### ⚠️ Metrics Aggregation Warning

| ❌ WRONG | ✅ CORRECT |
|----------|-----------|
| `SUM(test_mae)` | `AVERAGE(test_mae)` |
| `SUM(test_mape_pct)` | `AVERAGE(test_mape_pct)` |

**Error metrics must use AVERAGE (or median), never SUM.** Summing errors produces meaningless inflated values.

---

## ✅ Verification Checklist

Run after pipeline completes to confirm everything worked:

```sql
-- 1. Forecast data exists with recent run
SELECT COUNT(*) AS rows, MAX(ds) AS max_date, MAX(forecast_run_id) AS run
FROM public.simple_prophet_forecast;
-- Expected: rows > 20000, max_date ~ today + 90 days

-- 2. Metrics exist for all SKUs
SELECT COUNT(*) AS sku_count, ROUND(AVG(test_mape_pct)::numeric, 1) AS avg_mape
FROM public.forecast_error_metrics;
-- Expected: sku_count = 8, avg_mape < 30

-- 3. Views have expected columns
SELECT column_name FROM information_schema.columns
WHERE table_name = 'simple_prophet_forecast' AND table_schema = 'public'
ORDER BY ordinal_position;
-- Expected: ds, sku, yhat, yhat_lower, yhat_upper, data_type, forecast_run_id
```

---

## 📂 Project Structure

```
.
├── forecast_prophet_v2.py       # Main forecasting pipeline (recommended)
├── scripts/
│   ├── bootstrap.py             # Idempotent DB setup + data loader
│   └── run_daily.py             # Legacy orchestration
├── vitamarkets_dbt/vitamarkets/
│   └── models/
│       ├── stg_vitamarkets.sql  # Staging (clean raw data)
│       └── mart_sales_summary.sql # Mart (daily aggregates)
├── tests/                       # pytest suite (34+ tests)
├── docs/                        # Comprehensive documentation
├── MainDash.pbix                # Power BI dashboard
└── docker-compose.yml           # PostgreSQL container
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| **[SETUP.md](docs/SETUP.md)** | Full installation & environment setup |
| **[DATA_CONTRACT.md](docs/DATA_CONTRACT.md)** | View schemas, column definitions, Power BI integration |
| **[FORECASTING_POLICIES.md](docs/FORECASTING_POLICIES.md)** | SKU eligibility, outlier handling, metric targets |
| **[DASHBOARD_GUIDE.md](docs/DASHBOARD_GUIDE.md)** | Power BI usage, DAX formulas, metric interpretation |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, Mermaid diagrams |
| [DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) | All table schemas with sample queries |
| [KPI_DEFINITIONS.md](docs/KPI_DEFINITIONS.md) | Metric calculations & business logic |
| [ROADMAP.md](docs/ROADMAP.md) | Planned improvements, known limitations |

---

## 🛠️ Tech Stack

- **Python 3.11** — pandas, SQLAlchemy, Prophet, scikit-learn, joblib
- **PostgreSQL 14** — transactional database (Docker Compose)
- **dbt 1.7** — SQL transformations & schema tests
- **Prophet 1.1.5** — time series forecasting with seasonality
- **Power BI Desktop** — dashboards
- **pytest + ruff + GitHub Actions** — testing & CI/CD

---

## 🚀 v1 → v2 Upgrade Highlights

| Aspect | v1 | v2 |
|--------|----|----|
| Evaluation | None | 30-day holdout → MAE, RMSE, MAPE, bias, coverage |
| Parallel training | Sequential | `joblib` parallelism (~4x faster) |
| Holiday handling | Prophet defaults | Explicit US holidays |
| Pipeline | Scattered scripts | Unified `forecast_prophet_v2.py` |
| Contract | None | Stable views + versioned tables |
| CI | None | `ruff` lint + `pytest` on every push |

---

## 📧 Contact

**Allen Stalcup** — [allen.stalc@gmail.com](mailto:allen.stalc@gmail.com) | [LinkedIn](https://linkedin.com/in/) | [GitHub](https://github.com/stalcup-dev)

⭐ Star this repo if you found it useful!

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

**Note:** This is a portfolio project showcasing analytics and data engineering skills. The data is synthetic and any business insights are for demonstration purposes only.
