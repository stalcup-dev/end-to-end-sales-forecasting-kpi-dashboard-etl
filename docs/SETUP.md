# Getting Started

Complete setup instructions for running the Vita Markets analytics pipeline locally.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher** (tested on Python 3.11)
  - Check version: `python --version`
  - Download: https://www.python.org/downloads/

- **PostgreSQL 14 or higher**
  - Check version: `psql --version`
  - Download: https://www.postgresql.org/download/
  - **OR** use Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=mysecretpassword postgres:14`

- **Git**
  - Check version: `git --version`
  - Download: https://git-scm.com/downloads

- **Power BI Desktop** (optional, for viewing dashboard)
  - Download: https://powerbi.microsoft.com/desktop/
  - Note: Windows only; Mac users can view screenshots in repo

---

## Setup (5-10 minutes)

### Step 1: Clone Repository

```bash
git clone https://github.com/stalcup-dev/end-to-end-sales-forecasting-kpi-dashboard-etl.git
cd end-to-end-sales-forecasting-kpi-dashboard-etl
```

### Step 2: Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

You should see `(.venv)` prefix in your terminal prompt.

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r etl/requirements.txt
```

**Expected packages:**
- pandas==2.2.2
- SQLAlchemy==2.0.32
- psycopg2-binary==2.9.9
- prophet==1.1.5
- python-dotenv==1.0.1
- scikit-learn==1.5.1

**Troubleshooting:**
- If Prophet installation fails, you may need to install `pystan` first:
  ```bash
  pip install pystan==2.19.1.1
  pip install prophet==1.1.5
  ```

### Step 4: Set Up PostgreSQL Database

#### Option A: Local PostgreSQL Installation

1. **Create database:**
   ```bash
   psql -U postgres -h localhost
   ```
   ```sql
   CREATE DATABASE vitamarkets;
   \q
   ```

2. **Load initial tables and sample data:**
   ```bash
   psql -U postgres -h localhost -d vitamarkets -f setup/init_db.sql
   ```

#### Option B: Docker PostgreSQL

1. **Start PostgreSQL container:**
   ```bash
   docker run -d \
     --name vitamarkets-db \
     -p 5432:5432 \
     -e POSTGRES_PASSWORD=mysecretpassword \
     -e POSTGRES_DB=vitamarkets \
     postgres:14
   ```

2. **Wait 5 seconds for startup, then load data:**
   ```bash
   docker cp vitamarkets_ultrarealistic_sampledataset.csv vitamarkets-db:/tmp/data.csv
   docker exec -i vitamarkets-db psql -U postgres -d vitamarkets < setup/init_db.sql
   ```

### Step 5: Configure Environment Variables

1. **Copy template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your credentials:
   ```bash
   # Option 1: Full URI (recommended)
   DB_URI=postgresql://postgres:mysecretpassword@localhost:5432/vitamarkets

   # Option 2: Individual parameters
   PG_USER=postgres
   PG_PASS=mysecretpassword
   PG_HOST=localhost
   PG_PORT=5432
   PG_DB=vitamarkets
   ```

3. **Test connection:**
   ```bash
   python -c "from db import get_engine; engine = get_engine(); print('✅ Connection successful!')"
   ```

### Step 6: Install dbt Dependencies (if using dbt)

```bash
cd vitamarkets_dbt/vitamarkets
pip install dbt-postgres
dbt deps
cd ../..
```

### Step 7: Verify Setup

Run a quick test to ensure everything is working:

```bash
python -c "
from db import get_engine
import pandas as pd

engine = get_engine()
df = pd.read_sql('SELECT COUNT(*) FROM vitamarkets_raw', engine)
print(f'✅ Setup verified! Found {df.iloc[0,0]} rows in vitamarkets_raw')
"
```

**Expected output:**
```
✅ Setup verified! Found 50000+ rows in vitamarkets_raw
```

---

## Running the Pipeline

### Option A: Full Pipeline (Recommended)

Run the complete end-to-end pipeline:

```bash
python scripts/run_daily.py
```

**What this does:**
1. Runs `dbt deps` (install dbt packages)
2. Runs `dbt run` (execute staging and mart models)
3. Runs `etl/refresh_actuals.py` (refresh actuals table)
4. Runs `prophet_improved.py` (generate 90-day forecasts)
5. Runs `checkcsv.py` (data quality checks)
6. Writes logs to `logs/run_daily.log`

**Duration:** ~2-5 minutes depending on hardware

### Option B: Step-by-Step Execution

Run each component individually for debugging:

#### 1. Run dbt Transformations

```bash
cd vitamarkets_dbt/vitamarkets
dbt run
cd ../..
```

**Expected output:**
```
Running with dbt=1.7.0
Found 2 models, 0 tests, 0 snapshots, ...
Completed successfully
Done. PASS=2 WARN=0 ERROR=0 SKIP=0 TOTAL=2
```

**Tables created:**
- `public.stg_vitamarkets` (view)
- `public.mart_sales_summary` (table)

#### 2. Generate Forecasts

```bash
python prophet_improved.py
```

**Expected output:**
```
[SUCCESS] Forecasts, actuals, and error metrics exported for Power BI overlay and validation.
[SUCCESS] DataFrame written to Postgres as table 'simple_prophet_forecast'.
[SUCCESS] Error metrics written to Postgres as table 'forecast_error_metrics'.
```

**Tables created:**
- `public.simple_prophet_forecast`
- `public.forecast_error_metrics`

**CSV files created:**
- `prophet_forecasts/simple_prophet_forecast.csv`
- `prophet_forecasts/forecast_error_metrics.csv`

#### 3. Run Data Quality Checks

```bash
python checkcsv.py
```

**Expected output:**
```
CSV row count: 50000+
         sku  total_units_sold  total_order_value
0  Flagship Growth          15234          1823456.78
...
```

---

## Expected Outputs

After running the pipeline, you should have:

### Database Tables

Check tables exist:
```bash
psql -U postgres -h localhost -d vitamarkets -c "\dt"
```

**Expected tables:**
- `vitamarkets_raw` (raw data)
- `mart_sales_summary` (aggregated KPIs)
- `simple_prophet_forecast` (forecasts + actuals)
- `forecast_error_metrics` (accuracy metrics)

### CSV Files

```
prophet_forecasts/
├── simple_prophet_forecast.csv
└── forecast_error_metrics.csv
```

### Log Files

```
logs/
└── run_daily.log
```

---

## Viewing the Dashboard

### Power BI Desktop (Windows)

1. Open Power BI Desktop
2. File → Open → Select `MainDash.pbix`
3. If prompted for data source credentials:
   - Server: `localhost:5432`
   - Database: `vitamarkets`
   - Username/Password: (your PostgreSQL credentials)
4. Click "Home" → "Refresh" to load latest data

### Alternative: View Screenshots

If you don't have Power BI Desktop:
- **Executive KPI View:** See `KPIDashboard.png`
- **Forecast vs. Actuals:** See `ForecastingDash.png`
- **Database Schema:** See `database.png`

---

## Scheduling (Optional)

### Linux/Mac: Cron

Add to crontab (`crontab -e`):
```bash
# Run daily at 6 AM
0 6 * * * cd /path/to/repo && /path/to/repo/.venv/bin/python scripts/run_daily.py >> logs/cron.log 2>&1
```

### Windows: Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 6:00 AM
4. Action: Start a program
   - Program: `cmd.exe`
   - Arguments: `/c "C:\path\to\repo\run_daily.cmd"`
   - Start in: `C:\path\to\repo`

### Cloud: GitHub Actions (Future)

See `.github/workflows/daily-pipeline.yml` (to be added)

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'prophet'`

**Solution:**
```bash
pip install pystan==2.19.1.1
pip install prophet==1.1.5
```

Prophet requires the Stan probabilistic programming language backend.

---

### Issue: `psycopg2.OperationalError: could not connect to server`

**Possible causes:**
1. PostgreSQL is not running
   - Check: `pg_ctl status` (native) or `docker ps` (Docker)
   - Start: `pg_ctl start` or `docker start vitamarkets-db`

2. Wrong credentials in `.env`
   - Verify username/password with: `psql -U postgres -h localhost`

3. Firewall blocking port 5432
   - Check: `telnet localhost 5432`

---

### Issue: `dbt run` fails with "Relation 'vitamarkets_raw' does not exist"

**Solution:**
Run the database initialization script first:
```bash
psql -U postgres -h localhost -d vitamarkets -f setup/init_db.sql
```

---

### Issue: Prophet forecasting is very slow

**Possible causes:**
1. Large dataset (>100k rows per SKU)
2. Not using cmdstan backend

**Solution:**
Prophet uses cmdstan for Bayesian inference, which can be slow on first run. Subsequent runs are cached and faster.

To speed up:
- Reduce `FORECAST_DAYS` in `prophet_improved.py` (e.g., 30 instead of 90)
- Filter to fewer SKUs in the eligibility check

---

### Issue: Power BI can't connect to PostgreSQL

**Solution:**
1. Install PostgreSQL ODBC driver (if not already installed)
2. In Power BI: Get Data → PostgreSQL Database
   - Server: `localhost`
   - Database: `vitamarkets`
   - Data Connectivity mode: DirectQuery (or Import)

---

## Uninstall / Cleanup

To remove all components:

```bash
# 1. Drop database
psql -U postgres -h localhost -c "DROP DATABASE vitamarkets;"

# 2. Remove virtual environment
rm -rf .venv

# 3. Remove generated files
rm -rf logs/ prophet_forecasts/ .env

# 4. (Optional) Delete repo
cd .. && rm -rf end-to-end-sales-forecasting-kpi-dashboard-etl
```

---

## Next Steps

- **Explore the data:** See `docs/DATA_DICTIONARY.md` for table schemas
- **Understand the architecture:** See `docs/ARCHITECTURE.md` for system design
- **Learn about KPIs:** See `docs/KPI_DEFINITIONS.md` for metric definitions
- **Customize forecasts:** Edit `prophet_improved.py` to add features or tune hyperparameters
- **Add tests:** See upgrade plan in `HIRING_MANAGER_REVIEW.md`

---

## Getting Help

**Documentation:**
- Architecture: `docs/ARCHITECTURE.md`
- Data Dictionary: `docs/DATA_DICTIONARY.md`
- KPI Definitions: `docs/KPI_DEFINITIONS.md`
- Hiring Manager Review: `HIRING_MANAGER_REVIEW.md`

**Common Issues:**
- Check `logs/run_daily.log` for error messages
- Ensure PostgreSQL is running: `pg_isready -h localhost`
- Verify Python version: `python --version` (should be 3.9+)

**Contact:**
- GitHub Issues: https://github.com/stalcup-dev/end-to-end-sales-forecasting-kpi-dashboard-etl/issues
- Email: (your email here)
