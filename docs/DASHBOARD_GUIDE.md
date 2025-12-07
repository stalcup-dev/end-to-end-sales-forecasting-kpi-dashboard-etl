# Dashboard User Guide

## Overview

The Vita Markets Power BI dashboard (`MainDash.pbix`) provides two primary views for different stakeholder needs:

1. **Executive KPI View** - High-level business performance metrics
2. **Forecasting Dashboard** - Operational planning with 90-day forecasts

---

## Opening the Dashboard

### Prerequisites
- Power BI Desktop (Windows only)
- PostgreSQL running with `vitamarkets` database
- Pipeline has been run at least once (data tables populated)

### Steps
1. Open Power BI Desktop
2. File → Open → Select `MainDash.pbix`
3. If prompted for data source credentials:
   - Server: `localhost` (or your PostgreSQL host)
   - Database: `vitamarkets`
   - Authentication: Database (username/password)
4. Click "Home" → "Refresh" to load latest data

---

## Page 1: Executive KPI View

![KPI Dashboard](../KPIDashboard.png)

### Purpose
At-a-glance business performance tracking for executives and leadership team.

### Key Visuals

#### Top Cards (KPIs)
- **Total Revenue** - Sum of all order values (current period)
- **Total Units Sold** - Sum of all units sold
- **YoY Growth %** - Percentage change vs. same period last year

#### SKU Performance Table
Sortable table showing:
- SKU name
- Total revenue
- Total units sold
- YoY growth %
- Lifecycle stage (Growth/Mature/Decline)

**How to use:**
- Sort by YoY Growth (descending) to find winners
- Sort by Revenue (descending) to see top revenue drivers
- Filter by lifecycle stage to focus on specific SKU types

#### Channel Mix (Pie Chart)
Distribution of revenue by sales channel:
- Website (direct-to-consumer)
- Amazon (marketplace)
- Mobile app

**Insight:** Balanced mix indicates diversification; heavy Amazon % indicates platform dependency

#### Customer Segment Performance (Bar Chart)
Revenue by demographic:
- Young Pro (25-35 years)
- Family (35-50 years with children)
- Older Adult (50+ years)

**Insight:** Fastest-growing segment should receive increased marketing investment

#### Time Series Trend
Monthly or daily revenue trend with YoY comparison line

**Insight:** Look for seasonality patterns (Q4 spike for holidays)

### Stakeholder Use Cases

**CEO/CFO:**
- "What's our revenue growth this quarter?"
- "Which SKUs should we invest in?"
- "Are we diversified across channels?"

**VP of Operations:**
- "Which SKUs are declining? (Need to reduce inventory orders)"
- "What's our top revenue driver? (Ensure supply chain can support)"

**VP of Marketing:**
- "Which customer segments are growing fastest?"
- "Should we shift budget from Amazon to direct-to-consumer?"

---

## Page 2: Forecasting Dashboard

![Forecasting Dashboard](../ForecastingDash.png)

### Purpose
90-day demand forecasts for inventory planning and supply chain management.

### Key Visuals

#### Forecast vs. Actuals (Line Chart)
Time series showing:
- **Blue line** - Historical actuals
- **Orange line** - Prophet forecast (point estimate)
- **Shaded band** - 80% prediction interval (uncertainty range)

**How to read:**
- If actual (blue) stays within shaded band → Forecast is accurate
- If actual consistently exceeds upper band → Under-forecasting (stockout risk)
- If actual consistently below lower band → Over-forecasting (overstock risk)

**Interactive:**
- Select SKU from dropdown to view specific product
- Hover over points to see exact values and dates

#### Next 30 Days Forecast Table
Tabular view showing:
- Date
- SKU
- Predicted units (`yhat`)
- Lower bound (conservative estimate)
- Upper bound (optimistic estimate)

**How to use:**
- Sum next 30 days to calculate monthly demand
- Use upper bound for safety stock calculation
- Export to Excel for purchase order planning

#### Forecast Accuracy Gauge
Visual indicator showing:
- **MAPE%** (Mean Absolute Percentage Error)
- **Color coding:**
  - Green (MAPE <10%): Excellent
  - Yellow (10-20%): Good
  - Orange (20-30%): Acceptable
  - Red (>30%): Needs improvement

**Interpretation:**
- If MAPE >20%, consider manual adjustments or model retraining
- Track MAPE over time to monitor forecast degradation

#### Accuracy Metrics Table
Detailed metrics per SKU:
- MAE (Mean Absolute Error) - in units
- MAPE% (normalized error)
- RMSE (Root Mean Squared Error) - penalizes large errors
- Bias (over-forecasting vs. under-forecasting)
- Coverage (% of actuals within 80% interval)

### Stakeholder Use Cases

**Operations Manager:**
- "How much inventory should I order for next month?"
  - Answer: Sum next 30 days forecast + safety stock based on upper bound
- "Which SKUs are hardest to forecast?"
  - Answer: Look for high MAPE% in accuracy table

**Supply Chain Analyst:**
- "When will demand spike?"
  - Answer: Look for peaks in forecast line (seasonality, holidays)
- "Can I trust this forecast?"
  - Answer: Check coverage % (should be ~80%)

**Inventory Planner:**
- "What's my safety stock buffer?"
  - Answer: `Safety Stock = (Upper Bound - Forecast) × Risk Factor`
  - Example: If forecast = 100, upper = 120, use 20 units × 1.2 = 24 units safety stock

---

## Refreshing Data

**Frequency:** Daily (automated via `run_daily.py` or Windows Task Scheduler)

**Manual Refresh:**
1. Ensure pipeline has run: `python scripts/run_daily.py`
2. Open Power BI
3. Click "Home" → "Refresh"
4. Wait for data load (usually <30 seconds)

**What gets updated:**
- Historical actuals (if new data added to `mart_sales_summary`)
- Forecasts (last 90 days recalculated daily)
- Accuracy metrics (updated based on recent performance)

---

## Common Questions

### Q: Why does my forecast show a gap?
**A:** If a SKU has missing data or was discontinued, Prophet may not generate a forecast. Check `forecast_error_metrics` table for eligibility status.

### Q: Why is the MAPE% so high for some SKUs?
**A:** Low-volume or highly volatile SKUs are harder to forecast. Consider:
- Aggregating to weekly instead of daily
- Using a simpler baseline (moving average)
- Manual adjustments based on business context (e.g., upcoming promotion)

### Q: Can I change the forecast horizon?
**A:** Yes! Edit `prophet_improved.py`, change `FORECAST_DAYS = 90` to desired value, and re-run.

### Q: What if actuals deviate from forecast?
**A:** 
1. Check if a one-time event occurred (viral social media, competitor issue)
2. Update forecast model by re-running `python prophet_improved.py`
3. Adjust safety stock buffers in short-term
4. Consider adding more features to model (promotions, external factors)

---

## Decision Workflows

### Workflow 1: New Purchase Order

1. **Filter SKU** in Forecasting Dashboard
2. **Sum next 30 days** forecast (from table)
3. **Add safety stock:** `(Upper Bound - Forecast) × 1.2`
4. **Subtract current inventory** (from ERP system)
5. **Place order** with supplier

**Example:**
- SKU: Flagship Growth
- 30-day forecast: 1,200 units
- Upper bound: 1,450 units
- Safety stock: (1,450 - 1,200) × 1.2 = 300 units
- Current inventory: 400 units
- **Order:** 1,200 + 300 - 400 = **1,100 units**

### Workflow 2: Identify Growth Opportunities

1. Go to **Executive KPI View**
2. **Sort SKU table** by YoY Growth % (descending)
3. **Identify SKUs** with >50% growth
4. **Check forecast accuracy** (MAPE% <20% = reliable)
5. **Action:**
   - Increase marketing budget +30%
   - Ensure supply chain can scale
   - Consider product line extension

### Workflow 3: Phase Out Declining SKU

1. Go to **Executive KPI View**
2. **Filter** SKUs with YoY Growth <-10%
3. **Check** forecast trend (is it recovering or continuing decline?)
4. **If declining for 2+ quarters:**
   - Launch clearance sale (30-50% off)
   - Mark as discontinued in system
   - Reallocate resources to growth SKUs

---

## Troubleshooting

### Issue: Dashboard won't open
**Solution:**
- Ensure Power BI Desktop is installed (Windows only)
- Check file isn't corrupted: re-download from repo

### Issue: "Can't connect to data source"
**Solution:**
- Verify PostgreSQL is running: `pg_isready -h localhost`
- Check credentials in `.env` file
- Test connection: `psql -U postgres -h localhost -d vitamarkets`

### Issue: Data looks stale
**Solution:**
- Run pipeline: `python scripts/run_daily.py`
- Check logs: `logs/run_daily.log` for errors
- Manually refresh in Power BI: Home → Refresh

### Issue: Visuals are blank
**Solution:**
- Ensure tables exist: `psql -d vitamarkets -c "\dt"`
- Check row counts: `SELECT COUNT(*) FROM mart_sales_summary;`
- If no data, run: `python prophet_improved.py`

---

## Customization

### Adding New Visuals

1. Click "Home" → "Get Data" → "PostgreSQL"
2. Select table (e.g., `mart_sales_summary`)
3. Drag fields to canvas
4. Choose visual type (bar chart, line chart, table, etc.)
5. Format using "Visualizations" pane

### Adding Filters

1. Click "Filters" pane (right side)
2. Drag field to "Filters on this page" or "Filters on all pages"
3. Select filter type (basic, advanced, top N)
4. Configure filter logic

### Adding Calculated Columns

Example: Add "Margin $" column
```DAX
Margin $ = [Total Revenue] * 0.32
```

1. Click "Modeling" → "New Column"
2. Enter DAX formula
3. Use in visuals like any other field

---

## Related Documentation

- **Setup Guide:** [docs/SETUP.md](SETUP.md)
- **Architecture:** [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- **KPI Definitions:** [docs/KPI_DEFINITIONS.md](KPI_DEFINITIONS.md)
- **Business Decisions:** [docs/BUSINESS_DECISIONS.md](BUSINESS_DECISIONS.md)
- **Data Dictionary:** [docs/DATA_DICTIONARY.md](DATA_DICTIONARY.md)

---

**Last Updated:** 2025-12-07  
**Dashboard Version:** 1.0  
**Contact:** allen.stalc@gmail.com
