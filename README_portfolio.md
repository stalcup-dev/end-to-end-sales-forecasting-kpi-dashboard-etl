# Vita Markets — End-to-End Sales Forecasting & KPI Analytics

A production-grade analytics workflow that mirrors the work of a **Data Analyst** at a DTC e-commerce company. The pipeline ingests raw sales data, models it in PostgreSQL via dbt, generates 90-day SKU-level forecasts with Prophet, and serves executive dashboards in Power BI.

![Vita Markets Dashboard](./images/vitamarkets-dashboard.png) <!-- replace path if needed -->

---

## 🔍 Business Problem

Vita Markets—a simulated vitamin/supplement retailer—needed a reliable, automated way to:

- Track sales performance (daily granularity) across SKUs, channels, and customer segments.
- Forecast demand 90 days out for inventory planning.
- Monitor forecast quality with actionable accuracy metrics.
- Deliver executive-ready dashboards that stakeholders can trust.

---

## 🎯 My Role & Responsibilities

As the analytics lead on this project, I owned the full lifecycle:

- **Data sourcing & cleaning** from CSV to PostgreSQL (`vitamarkets_raw`, `mart_sales_summary`).
- **Data modeling** with dbt (staging + mart models, schema tests).
- **Forecasting & validation** using Prophet with 30-day holdout evaluation.
- **Dashboard design** in Power BI (KPIs, forecast vs actuals, accuracy gauges).
- **Automation & reproducibility** via Python CLI, documented workflows, and CI tests.

---

## 🧠 Skills Demonstrated

| Skill                        | Implementation Highlights |
|------------------------------|----------------------------|
| **SQL & Data Modeling**      | dbt models, star schema, complex aggregations, window functions |
| **Forecasting & Analytics**  | Prophet with seasonality, holiday effects, 99th percentile outlier clipping |
| **Business Intelligence**    | Power BI dashboards, DAX measures, data-type slicers, refresh-proof metrics |
| **Data Quality & Testing**   | dbt schema tests, pytest suite (34+ tests), CI via GitHub Actions |
| **Storytelling & UX**        | Executive KPI views, forecast overlays, business context documentation |
| **Automation & Tooling**     | Python pipelines (`forecast_prophet_v2.py`), joblib parallelism, Dockerized Postgres |

---

## 🗺️ Architecture Overview

```
CSV Source (50k rows, daily grain, 4 years)
          ↓
PostgreSQL (vitamarkets_raw)
          ↓ dbt run
Staging View (`stg_vitamarkets`)
          ↓
Mart Table (`mart_sales_summary`)
          ↓ forecast_prophet_v2.py
Prophet Forecasts + Metrics (versioned tables)
          ↓ stable views (Power BI contract)
`simple_prophet_forecast`, `forecast_error_metrics`
          ↓
Power BI (Executive KPIs + Forecast vs Actuals)
```

---

## 📈 Key Outcomes

- **New Launch SKU** surged by **150% YoY**, fully offsetting discontinued products.
- **Flagship Growth SKU** maintained **25% YoY growth** with predictable demand.
- **Automation** eliminated ~**4 hours/week** of manual reporting.
- **Forecast Accuracy**: median MAPE ~**12%**, prediction interval coverage ~**80%** (target hit).

---

## 📊 Power BI Highlights

- **Executive KPI View**: Revenue totals, YoY growth, SKU lifecycle analysis, channel mix.
- **Forecasting Dashboard**: Actual vs forecast overlays, 80% confidence bands, per-SKU accuracy table.
- **DAX Measures** enforce best practices—e.g., metrics like MAE/MAPE use `AVERAGE(...)`, never sums.

> ⚠️ Helpful Tip: All downstream tools must query the stable views (`simple_prophet_forecast`, `forecast_error_metrics`) to avoid schema drift.

---

## 🔧 Tech Stack

- **Languages**: Python 3.11, SQL (PostgreSQL), DAX
- **Libraries**: pandas, Prophet, SQLAlchemy, joblib, dbt
- **Data Warehouse**: PostgreSQL 14 (Dockerized)
- **BI Tool**: Power BI Desktop
- **Testing / Quality**: pytest, dbt tests, ruff, GitHub Actions
- **Documentation**: Extensive Markdown (architecture, setup, policies, roadmap)

---

## ⚡ Quick Demo Commands

```bash
# Clone & set up environment
git clone https://github.com/stalcup-dev/end-to-end-sales-forecasting-kpi-dashboard-etl.git
cd end-to-end-sales-forecasting-kpi-dashboard-etl
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# Launch Postgres (Docker) and seed data
docker compose up -d
cp .env.example .env    # update credentials if needed
python scripts/bootstrap.py

# Run end-to-end pipeline (dbt → Prophet → metrics → CSVs → report)
python forecast_prophet_v2.py
```

**Verification SQL:**

```sql
-- Forecast view should have ≥ 20,000 rows and current run ID
SELECT COUNT(*) AS rows, MAX(ds) AS max_date, MAX(forecast_run_id) AS latest_run
FROM public.simple_prophet_forecast;

-- Metrics view should hold all SKUs with healthy MAPE
SELECT COUNT(*) AS sku_count, ROUND(AVG(test_mape_pct)::numeric, 1) AS avg_mape
FROM public.forecast_error_metrics;
```

---

## 📚 Further Reading

- `docs/SETUP.md`: Environment setup and pipeline walkthrough
- `docs/DATA_CONTRACT.md`: Schema contracts for Power BI
- `docs/FORECASTING_POLICIES.md`: SKU eligibility, outlier handling, metric targets
- `docs/DASHBOARD_GUIDE.md`: Power BI usage and DAX best practices
- `docs/ROADMAP.md`: Planned enhancements and known limitations

---

## 💡 Lessons & Next Steps

- Introduce promo regressors to handle promotion-driven SKUs.
- Implement rolling-origin backtests for more robust evaluation.
- Add automated alerts if coverage deviates from the 80% target.
- Explore hierarchical reconciliation to align SKU forecasts with totals.

---

## 🙋 About Me

**Allen Stalcup**  
Email: [allen.stalc@gmail.com](mailto:allen.stalc@gmail.com)  
LinkedIn: [linkedin.com/in/](https://linkedin.com/in/)  
GitHub: [stalcup-dev](https://github.com/stalcup-dev)

*Passionate about creating analytics solutions that combine data engineering rigor with compelling business insights.*
