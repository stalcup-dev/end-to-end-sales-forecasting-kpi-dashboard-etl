Vita Markets – Automated Sales Forecasting & Power BI Dashboard
<img src="docs/images/KPIDashboard.png" width="850">

A full-stack analytics system that simulates the workflow of a real Direct-to-Consumer (DTC) e-commerce analyst. This project showcases end-to-end capability across data engineering, forecasting, automation, and BI reporting—delivering an entirely hands-free, production-ready forecasting and KPI monitoring pipeline.

It demonstrates expertise in Python, SQL, Prophet forecasting, Power BI, PostgreSQL, and real-world business analysis.

📌 Project Overview

Vita Markets is a complete analytics environment designed to solve real commercial challenges:

Cleaning and modeling raw time-series sales data

Automated SKU-level forecasting

Statistical validation of model performance

Executive dashboards for performance monitoring

Reliable daily automation with logging and QC checks

Database-ready outputs for downstream analytics

The system updates automatically, generating 90-day forecasts, storing results in PostgreSQL, and refreshing dashboards for decision-makers.

🎯 Analyst Skills Demonstrated
Business Analytics & Requirements Gathering

Next-quarter forecast by SKU

SKU lifecycle trends → growth, decline, replacement

Forecast accuracy tracking (MAPE, RMSE)

Operational readiness: forecast vs. actual deltas

Data Engineering & ETL

Automated ingestion and cleaning of daily sales data

Structured ETL pipeline with reusable modules

Consistent handling of missing values and anomalies

Statistical Forecasting

Prophet models tuned via cmdstanpy

Confidence intervals and trend component analysis

Error scoring logged for continuous validation

Data Storytelling & Visualization

Executive KPI dashboard (Power BI)

Forecast vs. Actual operational view

Seasonal patterns, YOY trends, SKU performance

Automation & Productionization

Fully unattended daily pipeline via run_daily.cmd

Environment activation, ETL, forecasting, QC, and logging

Error-resistant structure suitable for production migration

Database Integration

Writes forecasts + error metrics to Postgres tables

Enables downstream BI, reporting, or dbt transformation

🚀 Key Features
Automated ETL + Forecasting Pipeline

Cleans raw daily sales data

Generates rolling 90-day forecast per SKU

Logs QC checks and error metrics

Writes all outputs to PostgreSQL

Executive-Ready Dashboards

Full KPI suite

YOY change, seasonal spikes, demand cycles

Product lifecycle and revenue concentration

Hands-Free Operation

run_daily.cmd handles:

Environment activation

ETL workflow

Forecast generation

QC checks + accuracy metrics

Timestamped logging

Production-Grade Project Layout

Clear separation of raw data, scripts, outputs

Modular code for reusability

Ready for cloud scheduling (Airflow/Cloud Run)

🛠️ Tech Stack

Languages & Libraries
Python (Pandas, Prophet, cmdstanpy, SQLAlchemy, psycopg2, scikit-learn)

Database
PostgreSQL (forecast + error metrics tables)

Visualization
Power BI (MainDash.pbix)

Automation
Windows Batch (run_daily.cmd) + Task Scheduler

Version Control
GitHub with .gitignore (venv, logs, environment files)

---

📂 Project Structure

VitaMarkets/
├── .venv/                         # Virtual environment
├── data/                          # Raw & cleaned datasets
├── etl/                           # ETL pipeline
├── improved prophet forecasts/    # Experimental modeling
├── logs/                          # Execution logs
├── prophet_forecasts/             # Forecast outputs
├── scripts/                       # Helper modules
├── vitamarkets_dbt/               # Optional dbt models
├── checkcsv.py                    # Data validation
├── prophet_improved.py            # Forecast pipeline
├── vitamarkets_ultra_realistic_sampledataset.csv
├── MainDash.pbix                  # Power BI dashboard
├── ForecastingDash.png            # Forecast screenshot
├── KPIDashboard.png               # KPI screenshot
├── database.png                   # Database schema
├── run_daily.cmd                  # Automation script
├── .env                           # Environment variables
└── README.md

⚙️ How to Run the Pipeline
Manual Run

cd "C:\Users\<YourUser>\Desktop\Python\Vita Markets"
.\run_daily.cmd

Nightly Automation (Windows Task Scheduler)

Create a new Task

Trigger → Daily at chosen time

Action →

Program: cmd.exe  
Args: /c "C:\Users\<YourUser>\Desktop\Python\Vita Markets\run_daily.cmd"
Start in: C:\Users\<YourUser>\Desktop\Python\Vita Markets

4. Review logs in /logs each morning

📊 Dashboards
KPI Dashboard
<img src="KPIDashboard.png" width="750">
Forecasting Dashboard
<img src="ForecastingDash.png" width="750">
📈 Example Outputs
Forecast Results (simple_prophet_forecast)
SKU	Date	Forecast	Lower Bound	Upper Bound
Flagship Growth	2025-08-09	325	290	360
New Launch	2025-08-09	115	98	132
Error Metrics (forecast_error_metrics)
SKU	MAPE	RMSE
Flagship Growth	7.8%	45.2
New Launch	9.1%	12.4
💡 Key Takeaways

This project demonstrates mastery of real-world analytics workflow:

Turning business ambiguity into clear technical logic

Building scalable, automated forecasting systems

Applying statistical modeling to real commercial problems

Creating dashboards that support strategic decisions

Deploying a pipeline that runs autonomously and reliably

