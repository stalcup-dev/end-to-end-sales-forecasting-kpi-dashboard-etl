Vita Markets – Automated Sales Forecasting & Power BI Dashboard

This project showcases my ability to design and deploy a complete, production-ready analytics solution—from raw data ingestion and cleaning, to 
statistical forecasting, KPI visualization, and automated delivery. It demonstrates advanced skills in Python, SQL, Power BI, data modeling, and automation, 
combined with business-focused analysis that translates complex datasets into actionable insights. The workflow is fully automated via scheduled scripts, 
writes results to a relational database, and produces executive-ready dashboards—reflecting the same end-to-end problem-solving and delivery expected of 
a Data Analyst in a live business environment.

📌 Project Overview
Vita Markets is a full-stack analytics project designed to replicate the challenges a real-world Direct-to-Consumer (DTC) e-commerce analyst would solve.
It demonstrates my ability to:
•	Acquire, clean, and model data
•	Automate forecasting at the SKU level
•	Validate outputs with statistical error metrics
•	Visualize results for both executives and operational teams
•	Deploy a repeatable, production-grade analytics pipeline
The result is a hands-free forecasting and KPI monitoring system that updates daily, ready for immediate business decision-making.
________________________________________
🎯 Analyst Skills Demonstrated
•	Business Requirement Translation – Designed pipeline to answer realistic commercial questions:
o	What are next quarter’s sales by SKU?
o	Which new products are offsetting discontinued SKUs?
o	How accurate are our forecasts over time?
•	Data Engineering – Built ETL scripts to ingest, clean, and store time series data in a relational database.
•	Statistical Forecasting – Implemented and tuned Prophet models using cmdstanpy for better performance.
•	Data Validation & Quality Control – Automated checks for missing values, unexpected trends, and accuracy scores (MAPE, RMSE).
•	Data Storytelling – Designed Power BI dashboards for multiple stakeholder groups:
o	Executive KPI view for high-level decision-making
o	Forecast vs. Actual overlays for operational planning
•	Automation & Scheduling – Packaged workflow into a Windows batch script with Task Scheduler for daily unattended runs.
•	Database Integration – Wrote forecast and error metrics directly to PostgreSQL for downstream analytics.
•	Version Control & Documentation – Maintained clear Git repo structure, .gitignore, and comprehensive project README.
________________________________________
🚀 Key Features
•	Automated ETL + Forecasting Pipeline
o	Cleans and transforms daily actual sales data.
o	Generates 90-day forecasts per SKU with uncertainty intervals.
o	Writes outputs and error metrics to Postgres.
•	Executive-Ready Dashboards
o	KPI tracking across all SKUs.
o	Year-over-year growth analysis, seasonal spikes, and product lifecycle visibility.
•	Hands-Free Operation
o	run_daily.cmd handles:
1.	Environment activation
2.	ETL process
3.	Forecast generation
4.	QC checks
5.	Logging with timestamps
•	Production-Ready Structure
o	Reusable folder and script organization.
o	Clear separation between raw data, processing, and outputs.
________________________________________
🛠️ Tech Stack
Languages & Libraries:
Python (Pandas, Prophet, cmdstanpy, SQLAlchemy, psycopg2, sci-kit,)
Database:
PostgreSQL (forecast & error metrics tables)
Visualization:
Power BI (MainDash.pbix)
Automation:
Windows Batch (run_daily.cmd), Task Scheduler
Version Control:
GitHub with .gitignore for venv/logs
________________________________________
📂 Project Structure
bash
CopyEdit
Vita Markets/
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
├── MainDash.pbix                   # Power BI report
├── ForecastingDash.png             # Forecast dashboard screenshot
├── KPIDashboard.png                # KPI dashboard screenshot
├── database.png                    # Database schema
├── run_daily.cmd                   # Automation script
├── .env                            # Environment variables
└── README.md                       # Documentation
________________________________________
⚙️ How to Run
Manual Run
powershell
CopyEdit
cd "C:\Users\<YourUser>\Desktop\Python\Vita Markets"
.\run_daily.cmd
Nightly Automation
1.	Create a Task in Windows Task Scheduler
2.	Trigger: Daily at preferred time
3.	Action:
vbnet
CopyEdit
Program: cmd.exe
Args: /c "C:\Users\<YourUser>\Desktop\Python\Vita Markets\run_daily.cmd"
Start in: C:\Users\<YourUser>\Desktop\Python\Vita Markets
4.	Logs output to /logs for review.
________________________________________
📊 Dashboards
KPI Dashboard	Forecasting Dashboard
	
________________________________________
📈 Example Outputs
Forecast Results Table (simple_prophet_forecast)
SKU	Date	Forecast	Lower Bound	Upper Bound
Flagship Growth	2025-08-09	325	290	360
New Launch	2025-08-09	115	98	132
Error Metrics Table (forecast_error_metrics)
SKU	MAPE	RMSE
Flagship Growth	7.8%	45.2
New Launch	9.1%	12.4
________________________________________
💡 Key Takeaways
This project demonstrates full life-cycle analytics skills:
1.	Translating ambiguous business needs into technical solutions.
2.	Structuring a clean, scalable, and automated analytics workflow.
3.	Using statistical forecasting methods in a business context.
4.	Building dashboards that tell a story and drive decisions.
5.	Deploying and maintaining a system that runs without human intervention.

