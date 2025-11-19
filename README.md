# Vita Markets – Automated Sales Forecasting & Power BI Dashboard

https://github.com/stalcup-dev/end-to-end-sales-forecasting-kpi-dashboard-etl/blob/main/KPIDashboard.png?raw=true
[![Dashboard](KPIDashboard.png)]([https://github.com/stalcup-dev/your-repo](https://github.com/stalcup-dev/end-to-end-sales-forecasting-kpi-dashboard-etl/blob/main/KPIDashboard.png?raw=true))


This project showcases a complete, production-style analytics solution: from raw data ingestion and cleaning, to statistical forecasting, KPI visualization, and automated delivery.

It demonstrates skills in Python, SQL, Power BI, data modeling, and automation, with a focus on turning complex time-series sales data into actionable business insights. The workflow is automated via scheduled scripts, writes results to a relational database, and produces executive-ready dashboards—mirroring the end-to-end work of a Data Analyst in a live business environment.

---

## Project Overview

Vita Markets is a full-stack analytics project designed to mirror the challenges a real-world Direct-to-Consumer (DTC) e-commerce analyst would solve.

This project demonstrates the ability to:

- Acquire, clean, and model sales data
- Automate SKU-level forecasting
- Validate outputs with statistical error metrics
- Visualize results for executives and operational teams
- Deploy a repeatable, production-grade analytics pipeline

The result is a hands-free forecasting and KPI monitoring system that can update daily and support immediate business decision-making.

---

## Analyst Skills Demonstrated

### Business Requirement Translation

The pipeline is designed to answer realistic commercial questions:

- What are next quarter’s sales by SKU?
- Which new products are offsetting discontinued SKUs?
- How accurate are our forecasts over time?
- How do actuals track against forecasts at the SKU level?

### Data Engineering

- ETL scripts to ingest, clean, and transform time-series sales data
- Structured handling of missing values and outliers
- Storage of forecast outputs and error metrics in a relational database

### Statistical Forecasting

- Forecasting models built using Prophet, tuned via `cmdstanpy`
- SKU-level 90-day forecasts with uncertainty intervals
- Evaluation using metrics such as MAPE and RMSE

### Data Validation & Quality Control

- Automated checks for:
  - Missing or malformed data
  - Unexpected trends or breaks in the series
  - Forecast accuracy and drift over time

### Data Storytelling & Visualization

- Power BI dashboards tailored to different stakeholder groups:
  - Executive KPI view for high-level performance
  - Forecast vs. Actual overlays for operational planning
  - Seasonality and product lifecycle visibility

### Automation & Scheduling

- Windows batch script (`run_daily.cmd`) orchestrates:
  - Environment activation
  - ETL pipeline
  - Forecast generation
  - Quality control checks
  - Logging with timestamps for monitoring

### Database Integration

- Forecast results and error metrics are written to PostgreSQL
- Tables are ready for downstream analytics, reporting, or dbt models

---

## Key Features

### Automated ETL + Forecasting Pipeline

- Cleans and transforms daily actual sales data
- Generates 90-day forecasts per SKU
- Calculates accuracy metrics (e.g., MAPE, RMSE)
- Writes forecasts and metrics to PostgreSQL

### Executive-Ready Dashboards

- KPI tracking across all SKUs
- Year-over-year growth analysis
- Identification of seasonal spikes and product lifecycle stages
- Clear views for both executives and operations

### Hands-Free Operation

The `run_daily.cmd` script handles:

1. Activating the Python environment  
2. Running the ETL process  
3. Generating forecasts  
4. Running QC checks  
5. Writing logs with timestamps to `/logs`

### Production-Oriented Structure

- Reusable folder and script organization
- Separation of raw data, processing logic, and outputs
- Ready to be adapted to cloud scheduling (Airflow, Cron, etc.)

---

## Tech Stack

**Languages & Libraries**

- Python (pandas, Prophet, cmdstanpy, SQLAlchemy, psycopg2, scikit-learn)

**Database**

- PostgreSQL (forecast and error metrics tables)

**Visualization**

- Power BI (`MainDash.pbix`)

**Automation**

- Windows Batch (`run_daily.cmd`)
- Windows Task Scheduler

**Version Control**

- Git & GitHub
- `.gitignore` configured for virtual environment, logs, and environment files

---

## Project Structure

```text
VitaMarkets/
├── .venv/                         # Python virtual environment
├── data/                          # Raw and processed datasets
├── etl/                           # ETL scripts
├── improved prophet forecasts/    # Archived experiments
├── logs/                          # Execution logs
├── prophet_forecasts/             # Final forecasts
├── scripts/                       # Utility scripts
├── vitamarkets_dbt/               # (Optional) dbt models
├── checkcsv.py                    # Data validation script
├── prophet_improved.py            # Forecast generation
├── vitamarkets_ultra_realistic_sampledataset.csv  # Synthetic dataset
├── MainDash.pbix                  # Power BI report
├── ForecastingDash.png            # Forecast dashboard screenshot
├── KPIDashboard.png               # KPI dashboard screenshot
├── database.png                   # Database schema image
├── run_daily.cmd                  # Automation script
├── .env                           # Environment variables
└── README.md                      # Documentation

```
```
How to Run
Manual Run
cd "C:\Users\<YourUser>\Desktop\Python\Vita Markets"
.\run_daily.cmd

Nightly Automation (Windows Task Scheduler)

Open Task Scheduler and create a new task.

Trigger: Daily at your preferred time.

Action:

Program: cmd.exe
Arguments: /c "C:\Users\<YourUser>\Desktop\Python\Vita Markets\run_daily.cmd"
Start in: C:\Users\<YourUser>\Desktop\Python\Vita Markets


Logs are written to the logs/ directory for review.
```
