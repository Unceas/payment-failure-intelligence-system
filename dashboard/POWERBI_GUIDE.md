# Power BI Dashboard Setup Guide

## Step 1 — Import Data

1. Open **Power BI Desktop**
2. Click **Get Data → Text/CSV**
3. Import these files from `outputs/`:
   - `engineered_data.csv` (main fact table)
   - `data_quality_report.csv`
   - `insights_summary.csv`
   - `monthly_revenue_loss.csv`

---

## Step 2 — Data Model

In the **Model view**, ensure `engineered_data` is your primary table. No relationships needed for this single-table model.

---

## Step 3 — DAX Measures

Create these measures in the `engineered_data` table:

```dax
Total Transactions = COUNTROWS(engineered_data)

Total Failed = CALCULATE(COUNTROWS(engineered_data), engineered_data[status] = "Failed")

Total Success = CALCULATE(COUNTROWS(engineered_data), engineered_data[status] = "Success")

Success Rate = DIVIDE([Total Success], [Total Transactions], 0) * 100

Failure Rate = DIVIDE([Total Failed], [Total Transactions], 0) * 100

Total Revenue Processed = SUM(engineered_data[amount])

Revenue Lost = CALCULATE(SUM(engineered_data[amount]), engineered_data[status] = "Failed")

Revenue Loss % = DIVIDE([Revenue Lost], [Total Revenue Processed], 0) * 100

Avg Failed Txn Value = CALCULATE(AVERAGE(engineered_data[amount]), engineered_data[status] = "Failed")

Night Failure Rate = 
DIVIDE(
    CALCULATE([Total Failed], engineered_data[is_night] = 1),
    CALCULATE([Total Transactions], engineered_data[is_night] = 1),
    0
) * 100
```

---

## Step 4 — Dashboard Pages

### 🟦 Page 1: Executive Summary

| Visual | Field Config |
|--------|-------------|
| Card | Total Transactions |
| Card | Success Rate |
| Card | Failure Rate |
| Card | Total Revenue Processed |
| Card | Revenue Lost |
| Donut Chart | Legend: status, Values: Total Transactions |

### 🟨 Page 2: Failure Intelligence

| Visual | X-Axis | Y-Axis |
|--------|--------|--------|
| Line Chart | hour | Failure Rate measure |
| Bar Chart | category | Failure Rate measure |
| Bar Chart | device_type | Failure Rate measure |
| Bar Chart | region | Failure Rate measure |
| Bar Chart | payment_method | Failure Rate measure |

### 🟩 Page 3: Trends

| Visual | X-Axis | Y-Axis |
|--------|--------|--------|
| Line/Bar Combo | timestamp (Month) | Total Transactions, Total Failed |
| Line Chart | timestamp (Month) | Failure Rate |
| Bar Chart | month | Revenue Lost (from monthly_revenue_loss.csv) |

### 🟥 Page 4: Segmentation

| Visual | X-Axis | Y-Axis |
|--------|--------|--------|
| Bar Chart | user_type | Failure Rate |
| Bar Chart | amount_bucket | Failure Rate |

### 🟪 Page 5: Drilldown (with Slicers)

Add **Slicer** visuals for:
- `category`
- `device_type`
- `region`
- `timestamp` (date range)

Then add any chart from Page 2 — it will auto-filter based on slicers.

---

## Step 5 — Formatting Tips

- Set **canvas background** to dark (`#07071a`) via View → Canvas Settings
- Use **Segoe UI** font throughout
- Set card **accent bar** colors: green for success, red for failure
- Enable **cross-filtering** between all visuals

---

## Step 6 — Publish

1. File → **Publish to Power BI Service**
2. Share the workspace link in your resume/portfolio
