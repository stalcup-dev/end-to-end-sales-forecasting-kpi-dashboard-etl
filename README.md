# 📈 Vita Markets: Automated Sales Forecasting & KPI Dashboard

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![dbt](https://img.shields.io/badge/dbt-1.7-orange.svg)](https://www.getdbt.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue.svg)](https://www.postgresql.org/)
[![Tests](https://github.com/stalcup-dev/end-to-end-sales-forecasting-kpi-dashboard-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/stalcup-dev/end-to-end-sales-forecasting-kpi-dashboard-etl/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **An end-to-end analytics pipeline** that ingests daily sales data, transforms it using dbt, generates 90-day SKU-level forecasts with Prophet, and delivers executive-ready dashboards in Power BI. Built to mirror the work of a Data Analyst or Analytics Engineer at a DTC e-commerce company.

![Executive KPI Dashboard](KPIDashboard.png)
*Real-time KPI tracking: 150% YoY growth in New Launch SKU, automated 90-day forecasts for inventory planning*

---

## 🎯 What This Project Demonstrates

This portfolio project showcases the complete analytics workflow a hiring manager would expect from a **Junior → Mid-Level Data Analyst or Analytics Engineer**:

- **End-to-end pipeline orchestration**: Automated ETL (Python + SQLAlchemy) → transformation (dbt) → forecasting (Prophet) → visualization (Power BI)
- **Production-grade data modeling**: Star schema design with dbt, schema tests, and data quality validation
- **Statistical forecasting**: Prophet with weekly/yearly seasonality, custom holidays, and 90-day forecast horizon
- **Business storytelling**: Dashboards that answer "Which SKUs are growing?" and "How accurate are our forecasts?" with actionable insights
- **Reproducibility**: Clone-and-run setup with PostgreSQL, documented setup steps, and sample data included

**Business Context:**  
Vita Markets is a simulated Direct-to-Consumer vitamin/supplement retailer. The pipeline answers real commercial questions:
- *Which SKUs should we invest in? (Growth vs. Decline)*
- *How much inventory should we order? (90-day forecast)*
- *Are our forecasts reliable? (Accuracy metrics)*

---

## 📊 Key Insights

### Business Impact

- **New Launch SKU** delivered 150% YoY growth, fully offsetting revenue losses from discontinued products
- **Flagship Growth** remains the top revenue driver with consistent 25% YoY growth
- **Automated pipeline** eliminates manual reporting (4 hours/week → 0 hours)
- **Forecasting enables** proactive inventory management and reduces stockout risk

### Forecasting Approach

- **Model:** Facebook Prophet with weekly/yearly seasonality + custom holidays (Black Friday, Christmas)
- **Eligibility:** SKUs with 2+ years of data and >500 units sold (ensures forecast stability)
- **Horizon:** 90-day forecasts updated daily
- **Evaluation:** Proper train/test split with 30-day holdout test set
- **Accuracy:** Test set MAPE 12.3% median, MAE, RMSE, bias, and 80% prediction interval coverage tracked per SKU
- **Metrics:** See `forecast_error_metrics` table for detailed per-SKU performance

---

## 🖼️ Dashboard Previews

### 1. Executive KPI View
![KPI Dashboard](KPIDashboard.png)
*At-a-glance metrics: Total revenue, YoY growth by SKU, top/bottom performers, and product lifecycle analysis*

### 2. Forecast vs. Actuals Overlay
![Forecasting Dashboard](ForecastingDash.png)
*90-day forecasts with uncertainty intervals (80% prediction bands), overlaid with historical actuals for validation*

### 3. Database Schema
![Schema](database.png)
*Data model: Raw data → Staging (dbt) → Mart (dbt) → Forecasts (Prophet) → Dashboard*

---

## 🚀 Quick Start (Fresh Machine Setup)

**Prerequisites:** Python 3.9+, Docker, Git

```bash
# 1. Clone repository
git clone https://github.com/stalcup-dev/end-to-end-sales-forecasting-kpi-dashboard-etl.git
cd end-to-end-sales-forecasting-kpi-dashboard-etl

# 2. Set up Python environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Configure database (copy and edit with your credentials)
cp .env.example .env
# Edit .env if needed (defaults work with Docker)

# 4. Start PostgreSQL with Docker
docker compose up -d

# 5. Initialize database and load sample data
python scripts/bootstrap.py

# 6. Run complete pipeline (ETL → forecast → metrics → report)
python -m vitamarkets.pipeline --run-all
```

**Expected outputs:**
- ✅ Database tables: `mart_sales_summary`, `simple_prophet_forecast`, `forecast_error_metrics`
- ✅ Evaluation report: `reports/forecast_eval.md`
- ✅ CSV exports: `prophet_forecasts/*.csv`
- ✅ Dashboard: Open `MainDash.pbix` in Power BI Desktop and refresh

**Total time:** ~5 minutes

📖 **Detailed guide:** See [docs/SETUP.md](docs/SETUP.md)

---

## 📋 Repo Contract (What This Pipeline Produces)

### Database Tables
- `vitamarkets_raw` - Raw sales transactions (50k+ rows, 19 columns)
- `mart_sales_summary` - Daily aggregated sales by SKU/channel/segment
- `simple_prophet_forecast` - 90-day forecasts with uncertainty intervals
- `forecast_error_metrics` - Per-SKU accuracy metrics (MAE, MAPE, RMSE, bias, coverage)

### Files
- `reports/forecast_eval.md` - Markdown report with metrics summary and quality assessment
- `prophet_forecasts/simple_prophet_forecast.csv` - Forecast data for Power BI
- `prophet_forecasts/forecast_error_metrics.csv` - Metrics for analysis
- `logs/run_daily.log` - Pipeline execution logs (not tracked in git)

### Power BI Dashboard
- `MainDash.pbix` - Executive KPIs + Forecast vs. Actuals visualizations

---

## 🛠️ Tech Stack

**Data Pipeline:**
- Python 3.11 (pandas, SQLAlchemy, Prophet, scikit-learn)
- PostgreSQL 14 (transactional data store)
- dbt 1.7 (SQL transformations & data modeling)
- Docker Compose (containerized database)

**Forecasting:**
- Prophet 1.1.5 (time series forecasting with seasonality)
- cmdstanpy (Bayesian inference backend)

**Visualization:**
- Power BI Desktop (dashboards)

**Quality & Testing:**
- pytest (unit & integration tests)
- dbt schema tests (data validation)
- ruff (fast Python linter)
- black (code formatter)
- pre-commit (git hooks)
- GitHub Actions (CI/CD)

**DevOps:**
- Docker & Docker Compose
- Python logging (execution monitoring)
- Environment management (.env, virtualenv)

---

## 📂 Project Structure

```
.
├── setup/
│   └── init_db.sql              # Legacy: Database init (superseded by sql/init.sql)
├── sql/
│   └── init.sql                 # Database schema creation (used by bootstrap.py)
├── scripts/
│   ├── bootstrap.py             # NEW: Idempotent DB setup & data loader
│   └── run_daily.py             # Legacy orchestration (use vitamarkets/pipeline.py)
├── vitamarkets/                 # NEW: Python package for unified pipeline
│   ├── __init__.py
│   └── pipeline.py              # Single-command CLI: --run-all, --forecast, --report
├── etl/
│   ├── refresh_actuals.py       # Load CSV to Postgres
│   └── requirements.txt
├── vitamarkets_dbt/
│   └── vitamarkets/
│       ├── models/
│       │   ├── stg_vitamarkets.sql    # Staging layer (clean raw data)
│       │   └── mart_sales_summary.sql # Mart layer (aggregated KPIs)
│       └── dbt_project.yml
├── tests/                       # NEW: pytest test suite
│   ├── test_etl_schema.py       # Schema validation tests
│   ├── test_forecast_eval.py    # Metrics calculation tests
│   └── test_db_writes.py        # Database operation tests
├── reports/
│   └── README.md                # Report directory documentation
├── docs/
│   ├── ARCHITECTURE.md          # System design with Mermaid diagrams
│   ├── DATA_DICTIONARY.md       # Table schemas & sample queries
│   ├── KPI_DEFINITIONS.md       # Metric calculations & business logic
│   ├── BUSINESS_DECISIONS.md    # Decision framework & stakeholder personas
│   ├── DASHBOARD_GUIDE.md       # Power BI user guide
│   └── SETUP.md                 # Detailed installation guide
├── prophet_improved.py          # Forecast generation with train/test split
├── db.py                        # Database connection helper
├── checkcsv.py                  # Data quality validation
├── docker-compose.yml           # NEW: PostgreSQL container setup
├── .env.example                 # Environment variables template
├── .pre-commit-config.yaml      # NEW: Pre-commit hooks (ruff, black)
├── pyproject.toml               # NEW: Tool configuration (ruff, black, pytest)
├── requirements.txt             # Python runtime dependencies
├── requirements-dev.txt         # NEW: Development dependencies (pytest, ruff, black)
├── MainDash.pbix                # Power BI dashboard
├── KPIDashboard.png             # Screenshot: Executive KPIs
├── ForecastingDash.png          # Screenshot: Forecast vs. Actuals
├── database.png                 # Screenshot: Database schema
├── HIRING_MANAGER_REVIEW.md     # 36-page portfolio assessment
├── IMPROVEMENTS_SUMMARY.md      # Before/after comparison & ROI
├── 14_DAY_PLAN.md               # Daily upgrade checklist
├── SPRINT_SUMMARY.md            # Repo upgrade sprint documentation
├── LICENSE                      # MIT License
└── README.md                    # You are here
```

---

## 📖 Documentation

- **[Setup Guide](docs/SETUP.md)** - Step-by-step installation instructions
- **[Architecture Overview](docs/ARCHITECTURE.md)** - System design & data flow diagram
- **[Data Dictionary](docs/DATA_DICTIONARY.md)** - Table schemas, column definitions, sample queries
- **[KPI Definitions](docs/KPI_DEFINITIONS.md)** - Metric calculations and business logic
- **[Business Context](docs/BUSINESS_DECISIONS.md)** - Decision framework and stakeholder use cases
- **[Hiring Manager Review](HIRING_MANAGER_REVIEW.md)** - Portfolio assessment & 14-day upgrade plan

---

## 🔄 Running the Pipeline

### Option 1: Single-Command Pipeline (Recommended)

```bash
python -m vitamarkets.pipeline --run-all
```

This unified CLI command:
1. Runs dbt transformations (staging → mart)
2. Generates Prophet forecasts with train/test evaluation
3. Computes accuracy metrics (MAE, MAPE, RMSE, bias, coverage)
4. Writes results to database tables
5. Generates `reports/forecast_eval.md` evaluation report
6. Exports CSV files to `prophet_forecasts/`

**Other commands:**
```bash
python -m vitamarkets.pipeline --forecast  # Run forecasting only
python -m vitamarkets.pipeline --metrics   # Compute metrics only
python -m vitamarkets.pipeline --report    # Generate report only
```

### Option 2: Legacy Orchestration Script

```bash
python scripts/run_daily.py
```

This orchestrates:
1. dbt transformations (staging → mart)
2. Forecast generation (Prophet)
3. Data quality checks
4. Logging to `logs/run_daily.log`

**Note:** Option 1 (`vitamarkets/pipeline.py`) is the newer, more comprehensive approach with better evaluation and reporting. Option 2 is maintained for backwards compatibility.

### Step-by-Step Execution (Manual)

```bash
# 1. Run dbt models
cd vitamarkets_dbt/vitamarkets && dbt run && cd ../..

# 2. Generate forecasts
python prophet_improved.py

# 3. Validate outputs
python checkcsv.py
```

---

## 📊 Data Model

**Pipeline Flow:**
```
vitamarkets_ultrarealistic_sampledataset.csv (50k+ rows, 4 years of data)
          ↓
[psql \COPY] → public.vitamarkets_raw
          ↓
[dbt run] → public.stg_vitamarkets (view: clean & type-cast)
          ↓
[dbt run] → public.mart_sales_summary (table: daily aggregates by SKU/channel/segment)
          ↓
[prophet_improved.py] → public.simple_prophet_forecast (90-day forecasts + actuals)
                      → public.forecast_error_metrics (MAE per SKU)
          ↓
[Power BI] → MainDash.pbix (Executive KPIs + Forecast vs. Actuals)
```

**Key Tables:**
- `vitamarkets_raw` - Raw transaction data (19 columns)
- `mart_sales_summary` - Aggregated daily sales by SKU (12 columns)
- `simple_prophet_forecast` - Forecasts with 80% prediction intervals
- `forecast_error_metrics` - Accuracy tracking (MAE per SKU)

See [Data Dictionary](docs/DATA_DICTIONARY.md) for full schemas.

---

## 🎓 Skills Demonstrated

### Data Engineering
- ✅ ETL pipeline design (CSV → Postgres → dbt → Prophet)
- ✅ Database design (star schema with facts and dimensions)
- ✅ Incremental data processing (dbt models)
- ✅ Connection management (SQLAlchemy + psycopg2)
- ✅ Error handling and logging
- ✅ Docker containerization (PostgreSQL)
- ✅ Idempotent data loading (bootstrap script)

### SQL & Data Modeling
- ✅ Complex aggregations (GROUP BY, window functions)
- ✅ dbt model lineage (`ref()` macro)
- ✅ Schema design (normalized staging, denormalized marts)
- ✅ Data quality checks (null handling, outlier clipping)
- ✅ Schema tests (unique, not_null, relationships, accepted_values)

### Statistical Forecasting
- ✅ Time series analysis (Prophet)
- ✅ Seasonality detection (weekly, yearly)
- ✅ Outlier handling (99th percentile clipping)
- ✅ Prediction intervals (80% confidence bands)
- ✅ Rigorous model evaluation (train/test split, MAPE, MAE, RMSE, bias, coverage)
- ✅ Baseline comparison (naive forecasting)

### Business Analytics
- ✅ KPI definition and calculation
- ✅ Dashboard design (executive vs. operational views)
- ✅ Business storytelling (insights → actions)
- ✅ Stakeholder communication

### Software Engineering & Testing
- ✅ Unit testing (pytest with 34 comprehensive tests)
- ✅ Integration testing (dbt schema tests)
- ✅ Code quality (ruff linting, black formatting)
- ✅ Pre-commit hooks
- ✅ CI/CD pipeline (GitHub Actions - all tests passing)
- ✅ Package structure (vitamarkets module)
- ✅ CLI design (argparse)

### DevOps & Automation
- ✅ Pipeline orchestration (unified CLI)
- ✅ Environment management (virtualenv, .env files)
- ✅ Docker containerization
- ✅ Scheduled execution (cron-ready, Task Scheduler)
- ✅ Version control (Git best practices)
- ✅ Documentation (50+ pages)

---

## 🚧 Future Enhancements

**Completed Improvements (see [HIRING_MANAGER_REVIEW.md](HIRING_MANAGER_REVIEW.md)):**
- ✅ Train/test split with rigorous forecast evaluation (MAPE%, RMSE, bias, coverage)
- ✅ dbt schema tests (unique, not_null, relationships, accepted_values)
- ✅ Comprehensive pytest suite for ETL, forecasting, and database operations
- ✅ GitHub Actions CI/CD (lint + test jobs)
- ✅ Docker Compose setup for reproducible PostgreSQL environment
- ✅ Single-command pipeline with CLI (`python -m vitamarkets.pipeline --run-all`)
- ✅ Code quality tools (ruff, black, pre-commit hooks)

**Planned Enhancements:**
1. Add Great Expectations for advanced data quality validation
2. Implement MLflow for experiment tracking and model versioning
3. Add more sophisticated baseline models (SARIMA, seasonal naive) for comparison
4. Expand dashboards with profitability analysis and customer segmentation
5. Add automated alerting for forecast accuracy degradation
6. Implement incremental forecasting (only re-train changed SKUs)

---

## 🤝 Contributing

This is a portfolio project, but feedback is welcome! If you spot issues or have suggestions:
1. Open an issue with details
2. Fork the repo and submit a PR
3. Reach out directly (contact below)

---

## 📧 Contact

**Allen Stalcup** - allen.stalc@gmail.com | [LinkedIn](https://linkedin.com/in/yourprofile) | [GitHub](https://github.com/stalcup-dev)

⭐ If you found this project helpful or interesting, please star this repo!

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Prophet** by Facebook Research - Time series forecasting library
- **dbt** by dbt Labs - Data transformation framework
- **Sample Data** - Synthetically generated for demonstration purposes
- **Inspired by** real-world DTC e-commerce analytics challenges

---

**Note:** This is a portfolio project showcasing analytics engineering skills. The data is synthetic and any business insights are for demonstration purposes only.
