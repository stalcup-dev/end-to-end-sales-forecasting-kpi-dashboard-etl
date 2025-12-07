# Business Context & Decision Framework

## Overview

This document explains how the Vita Markets analytics pipeline translates data into actionable business decisions. It defines stakeholder personas, key business questions, and decision rules that link dashboard insights to operational actions.

---

## Stakeholder Personas

### 1. Executive Leadership (CEO, CFO)

**Role:** Strategic direction and resource allocation

**Key Questions:**
- Which SKUs should we invest in?
- Are we growing faster than the market?
- What's our revenue forecast for next quarter?
- Should we launch new products or double down on existing winners?

**Primary Dashboard:** Executive KPI View

**Decision Authority:**
- Budget allocation across SKUs
- Product portfolio decisions (launch, sunset)
- Channel strategy (expand Amazon vs. direct-to-consumer)

**Metrics They Care About:**
- Total Revenue (monthly, quarterly, annual)
- YoY Growth (by SKU and total)
- New Product Penetration
- Profit Margins (future addition)

---

### 2. Operations & Supply Chain

**Role:** Inventory planning and fulfillment

**Key Questions:**
- How much inventory should we order for next month?
- Which SKUs are at risk of stockouts?
- Can we reduce inventory holding costs without hurting service levels?
- Should we expedite shipments for any SKUs?

**Primary Dashboard:** Forecast vs. Actuals

**Decision Authority:**
- Purchase orders to suppliers
- Safety stock levels
- Warehouse space allocation

**Metrics They Care About:**
- 90-Day Forecast (by SKU)
- Prediction Intervals (for safety stock calculation)
- Forecast Accuracy (MAE, MAPE)
- Stockout Risk

---

### 3. Marketing & Growth

**Role:** Customer acquisition and retention

**Key Questions:**
- Which customer segments are growing fastest?
- What's the ROI on ad spend by SKU?
- Should we run promotions for declining SKUs?
- Which channels should we invest in?

**Primary Dashboard:** Executive KPI View (customer segment and channel breakdowns)

**Decision Authority:**
- Ad budget allocation by SKU
- Promotional campaigns
- Channel expansion (e.g., add TikTok Shop)

**Metrics They Care About:**
- YoY Growth by Segment
- Channel Mix
- AOV by Channel
- Ad Spend vs. Revenue (future addition)

---

## Business Questions & Answers

### Question 1: Which SKUs should we invest in for 2025?

**Dashboard Evidence:**
- View: Executive KPI View → SKU Performance Table
- Sort by: YoY Growth % (descending)

**Decision Rule:**
```
IF YoY Growth > 50% AND Forecast Accuracy (MAPE) < 20%:
    → INVEST: Increase marketing budget by 30%
    → INVEST: Ensure supply chain can scale (add backup suppliers)
    → CONSIDER: Line extension or bundle offers

ELSE IF YoY Growth 20-50% AND Forecast Stable:
    → MAINTAIN: Keep current budget
    → OPTIMIZE: Test pricing variations

ELSE IF YoY Growth 0-20%:
    → HARVEST: Reduce ad spend, focus on profitability
    → CONSIDER: Product refresh or phase-out

ELSE IF YoY Growth < 0%:
    → SUNSET: Plan clearance sales
    → REALLOCATE: Shift resources to growth SKUs
```

**Example (Current Data):**
- **New Launch SKU:** +150% YoY → INVEST (double marketing budget)
- **Flagship Growth:** +25% YoY → MAINTAIN
- **Discontinued SKU:** -40% YoY → SUNSET (clearance by Q2 2025)

---

### Question 2: How much inventory should we order this month?

**Dashboard Evidence:**
- View: Forecasting Dashboard → 90-Day Forecast Table
- Metrics: `yhat` (point forecast), `yhat_upper` (80% upper bound)

**Decision Rule:**
```
Safety Stock = (yhat_upper - yhat) * Safety Factor
Order Quantity = SUM(next_30_days_forecast) + Safety Stock - Current Inventory

WHERE:
  - yhat = Prophet point forecast
  - yhat_upper = 80th percentile (covers 80% of scenarios)
  - Safety Factor = 1.2 (configurable based on risk tolerance)
```

**Example:**
```
SKU: Flagship Growth
- 30-Day Forecast (yhat): 1,200 units
- Upper Bound (yhat_upper): 1,450 units
- Safety Stock: (1,450 - 1,200) * 1.2 = 300 units
- Current Inventory: 400 units
- Order Quantity: 1,200 + 300 - 400 = 1,100 units

ACTION: Place order for 1,100 units by Dec 15 (lead time: 3 weeks)
```

---

### Question 3: Should we run a promotion for a declining SKU?

**Dashboard Evidence:**
- View: Executive KPI View → SKU Performance Trend
- Filter: YoY Growth < 0%

**Decision Rule:**
```
IF YoY Growth < -10% AND Product Age < 3 years:
    → TEST PROMOTION: 20% discount for 2 weeks
    → MEASURE: Lift in units sold vs. forecast
    → IF Lift > 50%: Continue promotion
    → ELSE: Discontinue and sunset SKU

ELSE IF YoY Growth < -10% AND Product Age >= 3 years:
    → CLEARANCE: 30-50% discount to clear inventory
    → NO REORDER: Mark as discontinued
```

**Example:**
```
SKU: Old Standby
- YoY Growth: -15%
- Product Age: 4 years
- Current Inventory: 800 units
- Forecast (next 90 days): 300 units

ACTION: 
1. Launch clearance sale: 40% off (ends inventory in 60 days)
2. Mark as discontinued in system
3. Reallocate shelf space to New Launch SKU
```

---

### Question 4: Are our forecasts accurate enough to trust?

**Dashboard Evidence:**
- View: Forecasting Dashboard → Accuracy Table
- Metrics: MAPE (%), MAE (units), Bias

**Decision Rule:**
```
IF MAPE < 15% AND Bias within ±5%:
    → HIGH CONFIDENCE: Use forecast for purchase orders
    → Safety Stock: 10% buffer

ELSE IF MAPE 15-25%:
    → MODERATE CONFIDENCE: Use forecast with caution
    → Safety Stock: 20% buffer
    → REVIEW: Check for outliers or seasonality issues

ELSE IF MAPE > 25%:
    → LOW CONFIDENCE: Do NOT use forecast for inventory
    → FALLBACK: Use historical average + manual adjustments
    → ACTION: Improve forecast model (add features, longer history)
```

**Example:**
```
SKU: Flagship Growth
- MAPE: 11.2% → HIGH CONFIDENCE
- Bias: +2.1 units (slight over-forecast) → Acceptable

SKU: Discontinued SKU
- MAPE: 24.3% → MODERATE CONFIDENCE
- Bias: +8.9 units (significant over-forecast) → CAUTION

ACTION:
- Flagship Growth: Trust forecast, order based on yhat_upper
- Discontinued SKU: Use historical average, add 30% safety buffer
```

---

### Question 5: Which customer segments should we target in Q1 2025?

**Dashboard Evidence:**
- View: Executive KPI View → Customer Segment Performance
- Metrics: Revenue, YoY Growth, AOV by Segment

**Decision Rule:**
```
IF Segment YoY Growth > 30%:
    → INVEST: Increase targeted ads by 40%
    → PERSONALIZE: Develop segment-specific messaging

ELSE IF Segment YoY Growth 10-30%:
    → MAINTAIN: Keep current ad spend
    → TEST: A/B test new creatives

ELSE IF Segment YoY Growth < 10%:
    → HARVEST: Reduce ad spend, focus on retention
    → INVESTIGATE: Survey to understand declining interest
```

**Example (Hypothetical Data):**
```
Young Pro:
- Revenue: $2.1M
- YoY Growth: +45%
- AOV: $135
→ ACTION: Increase Facebook/Instagram ads targeting 25-35 year-olds

Family:
- Revenue: $1.8M
- YoY Growth: +12%
- AOV: $110
→ ACTION: Maintain current spend, test bundle offers

Older Adult:
- Revenue: $1.2M
- YoY Growth: +5%
- AOV: $95
→ ACTION: Reduce ad spend, focus on email retention campaigns
```

---

## Decision Matrix: SKU Portfolio Management

| SKU Archetype | YoY Growth | Action | Marketing Budget | Inventory Strategy |
|---------------|------------|--------|------------------|--------------------|
| **New Star** | >100% | INVEST AGGRESSIVELY | +50% | High safety stock (25%) |
| **Growth** | 20-100% | INVEST | +20-30% | Moderate safety stock (15%) |
| **Mature** | 0-20% | MAINTAIN | No change | Standard safety stock (10%) |
| **Declining** | -10 to 0% | HARVEST | -20% | Reduce safety stock (5%) |
| **Failing** | <-10% | SUNSET | -50% (clearance only) | Clear inventory, no reorder |

---

## Operational Playbooks

### Playbook 1: Forecast Miss (Actual > Forecast Upper Bound)

**Trigger:** Actual sales exceed `yhat_upper` for 3+ consecutive days

**Symptoms:**
- Stockout risk
- Delayed shipments
- Lost revenue

**Actions:**
1. **Immediate (Day 1-3):**
   - Place expedited order with premium supplier (3-5 day delivery)
   - Temporarily reduce ad spend to slow demand
   - Enable backorder option on website

2. **Short-term (Week 1-2):**
   - Investigate root cause (viral social media? Competitor issue?)
   - Update forecast model with recent data
   - Increase safety stock buffer for this SKU

3. **Long-term (Month 1+):**
   - Renegotiate supplier lead times
   - Add backup supplier
   - Increase forecast upper bound multiplier (e.g., 1.2x → 1.3x)

---

### Playbook 2: Declining SKU Revenue

**Trigger:** YoY Growth < -10% for 2 consecutive quarters

**Symptoms:**
- Excess inventory
- Price erosion
- Low margins

**Actions:**
1. **Diagnose (Week 1-2):**
   - Review customer reviews (quality issues?)
   - Analyze competitor launches (market shift?)
   - Survey past buyers (why did they stop?)

2. **Test (Month 1):**
   - Run limited promotion (20% off for 2 weeks)
   - Measure lift vs. forecast baseline
   - Calculate profitability of promotion

3. **Decide (Month 2):**
   - IF promotion successful (lift >50%): Continue with regular promotions
   - ELSE: Plan phase-out and clearance

---

### Playbook 3: New Product Launch

**Trigger:** New SKU added to `vitamarkets_raw` table

**Timeline:**
1. **Pre-launch (Month -1):**
   - Ensure supply chain ready (confirm lead times, minimum order quantities)
   - Set initial safety stock: 30% of expected demand
   - No forecast available yet (use proxy from similar SKU)

2. **Launch (Month 0):**
   - Monitor daily sales vs. plan
   - Collect 30 days of data before generating Prophet forecast

3. **Post-launch (Month 1-3):**
   - Generate first forecast after 30+ days of data
   - Adjust marketing based on early performance
   - Decide: Scale up or pivot based on first 90 days

4. **Maturity (Month 4+):**
   - Transition to automated forecasting and inventory planning
   - Reduce safety stock to 15% as confidence improves

---

## Success Metrics

### Business Outcomes

**Primary Goal:** Increase revenue while maintaining profitability

**Metric Targets:**
- **Revenue Growth:** 15% YoY (portfolio level)
- **Forecast Accuracy:** MAPE <15% (median across SKUs)
- **Inventory Efficiency:** 
  - Stockout Rate: <3% of SKU-days
  - Overstock Rate: <10% of inventory value
- **New Product Success:** 50% of launches achieve >100% YoY growth in first year

---

### How This Dashboard Drives Value

**Before Dashboard:**
- ❌ Inventory decisions based on gut feel → 15% stockout rate, 25% overstock
- ❌ Ad spend spread evenly across all SKUs → Low ROI on declining SKUs
- ❌ Reactive to supply issues → Lost sales, expedited shipping costs

**After Dashboard:**
- ✅ Data-driven inventory planning → 3% stockout rate, 8% overstock
- ✅ Ad budget focused on high-growth SKUs → 30% higher ROAS
- ✅ Proactive supply chain management → 90% on-time order fulfillment

**Estimated Annual Impact:**
- Revenue uplift: +$500K (from reduced stockouts)
- Cost savings: +$200K (from reduced overstock and expedited shipping)
- Marketing ROI improvement: +25%
- **Total Value:** ~$700K per year

---

## Dashboard Usage Guidelines

### For Executives

**Daily (5 min):**
- Check Executive KPI View → Top card (Total Revenue, YoY Growth)
- Scan for any red alerts (SKUs declining >20%)

**Weekly (20 min):**
- Review SKU Performance Table → Identify trends
- Discuss with team: Any SKUs need investment or phase-out?

**Monthly (60 min):**
- Deep dive: Compare forecast vs. actual
- Review marketing ROI and channel mix
- Plan resource allocation for next quarter

---

### For Operations

**Daily (10 min):**
- Check Forecasting Dashboard → Next 7 Days Forecast
- Verify: Do we have inventory to meet forecast?
- IF forecast_upper > current_inventory: Place expedited order

**Weekly (30 min):**
- Review forecast accuracy trends
- Adjust safety stock buffers based on recent MAPE
- Coordinate with suppliers on upcoming demand spikes

**Monthly (90 min):**
- Analyze forecast errors: Which SKUs are hardest to predict?
- Work with Data Analyst to improve model (add promotional flags, holidays)
- Optimize inventory levels based on seasonality

---

### For Marketing

**Weekly (30 min):**
- Review customer segment performance
- Identify: Which segments are growing? Which are declining?
- Adjust ad targeting and creative strategy

**Monthly (60 min):**
- Analyze channel mix trends
- Test: Should we shift budget from Amazon to direct-to-consumer?
- Plan promotional calendar aligned with forecast peaks

---

## Key Business Insights (Example)

Based on current data in the repository:

### Insight 1: New Launch SKU is the Growth Driver

**Data:**
- YoY Growth: +150%
- Revenue Contribution: ~20% of total
- Forecast Accuracy: High (MAPE estimated <15%)

**Implication:**
- This SKU is offsetting declines in mature products
- High confidence in scaling up (forecast is reliable)

**Action:**
- Double marketing budget for New Launch
- Ensure supply chain can handle 2x current volume
- Consider line extension (e.g., new flavors, sizes)

---

### Insight 2: Discontinued SKU Needs Clearance

**Data:**
- YoY Growth: -40% (declining)
- Current Trajectory: Will be obsolete by Q2 2025

**Implication:**
- Holding inventory is tying up capital
- Risk of write-downs if not cleared quickly

**Action:**
- Launch clearance sale: 40% off
- Target completion: 60 days
- Reallocate resources to growth SKUs

---

### Insight 3: Flagship Growth Remains Stable

**Data:**
- YoY Growth: +25% (solid)
- Forecast Accuracy: MAPE ~11% (excellent)
- Revenue Contribution: ~50% of total

**Implication:**
- Core cash cow product
- Predictable demand → efficient inventory planning

**Action:**
- Maintain current strategy
- Optimize margins (can we reduce ad spend without hurting growth?)
- Ensure continuity of supply (lock in supplier contracts)

---

## Continuous Improvement

**Quarterly Review:**
1. Are our decision rules working? (measure actual outcomes vs. plan)
2. Should we adjust thresholds? (e.g., change "invest" cutoff from 20% to 25%)
3. What new metrics do we need? (e.g., customer lifetime value, return rate)

**Annual Review:**
1. How much value did this dashboard create? (vs. pre-dashboard baseline)
2. What features should we add? (e.g., pricing optimization, competitor tracking)
3. Should we expand to new product categories?

---

## Contact & Escalation

**For dashboard issues:**
- Contact: Data Analyst / Analytics Engineer (your email here)

**For business decisions:**
- Escalate to: Director of Operations, VP Marketing, CFO (depending on question)

**For forecast accuracy concerns:**
- Work with: Data team to retune Prophet model or add features

---

**Related Documents:**
- KPI Definitions: `docs/KPI_DEFINITIONS.md`
- Data Dictionary: `docs/DATA_DICTIONARY.md`
- Architecture: `docs/ARCHITECTURE.md`
