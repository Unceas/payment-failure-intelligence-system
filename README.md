# 💳 Payment Failure Intelligence & Revenue Optimization System

> **End-to-end Data Analytics portfolio project** demonstrating data cleaning, feature engineering, statistical analysis, visualization, and business intelligence.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=flat&logo=pandas)
![Seaborn](https://img.shields.io/badge/Seaborn-0.12+-4EAE4E?style=flat)
![SciPy](https://img.shields.io/badge/SciPy-Stats-8CAAE6?style=flat)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=flat&logo=powerbi)

---

## 📌 Problem Statement

Digital payment platforms lose significant revenue due to transaction failures. Without clear visibility into **when**, **why**, and **which segments** experience failures, businesses cannot take targeted corrective action.

This project builds a complete analytics system that:
- Diagnoses failure patterns across time, category, device, and region
- Quantifies exact revenue loss due to failed transactions
- Validates findings with statistical hypothesis testing
- Delivers actionable recommendations through an interactive dashboard

---

## 🎯 Objectives

| # | Objective |
|---|-----------|
| 1 | Identify failure patterns across time, category, and user segments |
| 2 | Detect high-risk scenarios using statistical testing |
| 3 | Quantify revenue loss due to transaction failures |
| 4 | Provide data-driven business recommendations |
| 5 | Build an interactive dashboard for decision-makers |

---

## 📦 Dataset

**Synthetic dataset** — 100,000 transactions generated to mirror the [Kaggle Online Payments Fraud Detection Dataset](https://www.kaggle.com/datasets/jainilcoder/online-payment-fraud-detection).

| Field | Description |
|-------|-------------|
| `transaction_id` | Unique transaction identifier |
| `timestamp` | Date & time (2023–2024) |
| `amount` | Transaction amount in INR (₹50 – ₹2,00,000) |
| `status` | Success / Failed |
| `category` | Food & Dining, Electronics, Travel, Utilities, Retail, Healthcare, Entertainment |
| `device_type` | Mobile, Desktop, Tablet |
| `region` | North, South, East, West, Central |
| `payment_method` | UPI, Credit Card, Debit Card, Net Banking, Wallet |
| `user_id` | 10,000 unique users |

---

## ⚙️ Tech Stack

| Layer | Tool |
|-------|------|
| Data Processing | Python — Pandas, NumPy |
| Statistical Analysis | SciPy (Chi-Square, Mann-Whitney U) |
| Visualization | Matplotlib, Seaborn |
| Dashboard | Interactive HTML/JS (Chart.js) + Power BI |
| Environment | Python 3.8+ |

---

## 🏗️ Project Structure

```
payment-analysis/
├── data/
│   ├── generate_dataset.py       ← Synthetic data generator
│   └── raw_transactions.csv      ← Raw data (100K rows)
│
├── notebooks/
│   ├── 01_cleaning.py            ← Data cleaning pipeline
│   ├── 02_feature_engineering.py ← Feature creation
│   └── 03_analysis.py            ← Full analysis + charts
│
├── outputs/
│   ├── cleaned_data.csv
│   ├── data_quality_report.csv
│   ├── engineered_data.csv
│   ├── insights_summary.csv
│   ├── monthly_revenue_loss.csv
│   └── charts/                   ← 8 analysis charts
│
├── dashboard/
│   ├── index.html                ← Interactive web dashboard
│   ├── data.js                   ← Auto-generated dashboard data
│   └── POWERBI_GUIDE.md          ← Step-by-step Power BI setup
│
├── run_pipeline.py               ← Master script (runs everything)
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate the dataset
python data/generate_dataset.py

# 3. Run the full pipeline
python run_pipeline.py

# 4. Open the dashboard
# Open dashboard/index.html in your browser
```

---

## 📊 Analysis Framework

### A. Data Cleaning
- Handled 450+ missing values (median/mode imputation)
- Removed 50 duplicate transactions
- Validated timestamp formats and categorical fields
- Enforced amount bounds (₹1 – ₹5,00,000)

### B. Feature Engineering
- **Time features**: hour, day_of_week, is_weekend, is_night
- **Transaction features**: log_amount, amount_bucket (Low/Medium/High/Very High)
- **User features**: transactions_per_user, user_failure_rate, user_type (New/Returning)
- **Rolling features**: 7-day rolling failure rate

### C. Statistical Testing

| Test | Variables | Result |
|------|-----------|--------|
| Chi-Square | Device Type vs Failure Status | **Significant** (p < 0.05) |
| Chi-Square | Category vs Failure Status | **Significant** (p < 0.05) |
| Mann-Whitney U | Amount: Success vs Failure | **Not Significant** (p > 0.05) |
| Chi-Square | Night vs Daytime Failure | **Significant** (p < 0.05) |

---

## 💡 Key Insights

> **"Failure rate increases by ~60% between 12–5 AM compared to business hours"**

> **"Electronics category has the highest failure rate — ~30% above platform average"**

> **"Mobile users experience statistically significantly higher failure rates (p < 0.05)"**

> **"East region shows the highest regional failure rate, indicating infrastructure issues"**

> **"High-value transactions (>₹50K) fail at a disproportionately higher rate"**

---

## 💼 Business Recommendations

| Priority | Recommendation |
|----------|---------------|
| 🔴 High | Implement automatic retry mechanism during night window (12–5 AM) |
| 🔴 High | Investigate payment gateway performance for Electronics category |
| 🟡 Medium | Optimize mobile payment SDK — reduce timeout thresholds |
| 🟡 Medium | Partner with regional banks in East region to improve success rates |
| 🟢 Low | Adjust fraud detection thresholds for high-value transactions to reduce false failures |
| 🟢 Low | Build real-time alerting when hourly failure rate exceeds 20% |

---

## 📈 Dashboard

The interactive dashboard has 5 pages:

| Page | Content |
|------|---------|
| 🟦 Executive Summary | KPIs, donut chart, key insights |
| 🟨 Failure Intelligence | Failure rate by hour, category, device, region, payment method |
| 🟩 Trends | Monthly volume, failure rate trend, revenue loss timeline |
| 🟥 Segmentation | New vs Returning users, High vs Low value analysis |
| 🟪 Drilldown | Interactive filters: Category, Device, Region |

---

## 👤 Author

Built as a **Data Analyst portfolio project** demonstrating end-to-end analytical thinking, Python data engineering, statistical validation, and business insight communication.
