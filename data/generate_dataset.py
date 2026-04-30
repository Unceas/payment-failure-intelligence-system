"""
generate_dataset.py
--------------------
Generates a realistic synthetic payment transactions dataset (100,000 rows).
Mirrors the structure of the Kaggle Online Payments Fraud Detection dataset.
All amounts are in INR.

Run: python data/generate_dataset.py
"""

import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta
import os

np.random.seed(42)
random.seed(42)

N = 100_000

print("=" * 60)
print("  PAYMENT FAILURE INTELLIGENCE SYSTEM")
print("  Dataset Generator")
print("=" * 60)
print(f"\n  Generating {N:,} transactions...")

# ─────────────────────────────────────────────────────────────
# 1. TIMESTAMPS  (2023-01-01 to 2024-12-31)
# ─────────────────────────────────────────────────────────────
start_date = datetime(2023, 1, 1)
end_date   = datetime(2024, 12, 31, 23, 59, 59)
total_days = (end_date - start_date).days + 1

# More transactions during business hours, fewer at night
hour_weights = [
    0.018, 0.015, 0.013, 0.012, 0.013, 0.020,   # 00–05  (night)
    0.035, 0.050, 0.060, 0.065, 0.065, 0.065,   # 06–11  (morning)
    0.063, 0.062, 0.058, 0.055, 0.054, 0.055,   # 12–17  (afternoon)
    0.052, 0.048, 0.044, 0.040, 0.032, 0.025,   # 18–23  (evening)
]
hour_weights = np.array(hour_weights) / sum(hour_weights)

timestamps = []
for _ in range(N):
    day_offset = random.randint(0, total_days - 1)
    ts_date   = start_date + timedelta(days=day_offset)
    hour      = int(np.random.choice(range(24), p=hour_weights))
    ts        = ts_date.replace(hour=hour,
                                minute=random.randint(0, 59),
                                second=random.randint(0, 59))
    timestamps.append(ts)

timestamps = sorted(timestamps)

# ─────────────────────────────────────────────────────────────
# 2. CATEGORICAL SETUP
# ─────────────────────────────────────────────────────────────
categories   = ['Food & Dining', 'Electronics', 'Travel',
                 'Utilities', 'Retail', 'Healthcare', 'Entertainment']
cat_weights  = [0.25, 0.15, 0.12, 0.15, 0.18, 0.08, 0.07]
cat_failure  = {
    'Food & Dining':  0.10,
    'Electronics':    0.22,
    'Travel':         0.18,
    'Utilities':      0.08,
    'Retail':         0.12,
    'Healthcare':     0.07,
    'Entertainment':  0.14,
}

devices         = ['Mobile', 'Desktop', 'Tablet']
device_weights  = [0.60, 0.30, 0.10]
device_mod      = {'Mobile': 1.35, 'Desktop': 0.75, 'Tablet': 1.05}

regions         = ['North', 'South', 'East', 'West', 'Central']
region_weights  = [0.22, 0.25, 0.18, 0.20, 0.15]
region_mod      = {'North': 1.10, 'South': 0.88, 'East': 1.22, 'West': 0.90, 'Central': 1.05}

payment_methods = ['UPI', 'Credit Card', 'Debit Card', 'Net Banking', 'Wallet']
pm_weights      = [0.35, 0.25, 0.20, 0.12, 0.08]
pm_mod          = {'UPI': 0.88, 'Credit Card': 0.82, 'Debit Card': 0.95,
                   'Net Banking': 1.15, 'Wallet': 1.08}

# ─────────────────────────────────────────────────────────────
# 3. USERS
# ─────────────────────────────────────────────────────────────
N_USERS   = 10_000
user_ids  = [f'USR{str(i).zfill(5)}' for i in range(1, N_USERS + 1)]
user_bias = np.random.lognormal(mean=0.0, sigma=0.35, size=N_USERS)
user_bias = np.clip(user_bias, 0.4, 3.0)
bias_map  = dict(zip(user_ids, user_bias))

# ─────────────────────────────────────────────────────────────
# 4. AMOUNTS  (INR, log-normal, ₹50 – ₹2,00,000)
# ─────────────────────────────────────────────────────────────
amounts = np.random.lognormal(mean=7.5, sigma=1.2, size=N)
amounts = np.clip(amounts, 50, 200_000).round(2)

# ─────────────────────────────────────────────────────────────
# 5. BUILD ROWS
# ─────────────────────────────────────────────────────────────
rows = []
for i in range(N):
    ts       = timestamps[i]
    category = str(np.random.choice(categories, p=cat_weights))
    device   = str(np.random.choice(devices,    p=device_weights))
    region   = str(np.random.choice(regions,    p=region_weights))
    pm       = str(np.random.choice(payment_methods, p=pm_weights))
    user_id  = str(np.random.choice(user_ids))
    amount   = float(amounts[i])

    # Hour modifier
    h = ts.hour
    if   0  <= h <  6: hour_mod = 1.60
    elif 6  <= h <  9: hour_mod = 1.25
    elif 9  <= h < 17: hour_mod = 0.88
    elif 17 <= h < 21: hour_mod = 1.00
    else:              hour_mod = 1.15

    # Amount modifier
    if   amount > 50_000: amt_mod = 1.40
    elif amount > 10_000: amt_mod = 1.15
    else:                 amt_mod = 1.00

    failure_prob = min(
        cat_failure[category] * device_mod[device] * region_mod[region]
        * pm_mod[pm] * hour_mod * amt_mod * bias_map[user_id],
        0.80
    )

    status = 'Failed' if random.random() < failure_prob else 'Success'

    rows.append({
        'transaction_id': f'TXN{str(i + 1).zfill(7)}',
        'timestamp':      ts.strftime('%Y-%m-%d %H:%M:%S'),
        'amount':         amount,
        'status':         status,
        'category':       category,
        'device_type':    device,
        'region':         region,
        'payment_method': pm,
        'user_id':        user_id,
    })

# ─────────────────────────────────────────────────────────────
# 6. SAVE
# ─────────────────────────────────────────────────────────────
os.makedirs('data', exist_ok=True)
df = pd.DataFrame(rows)
df.to_csv('data/raw_transactions.csv', index=False)

total    = len(df)
failures = (df['status'] == 'Failed').sum()
print(f"\n  [OK] Saved {total:,} rows -> data/raw_transactions.csv")
print(f"  [OK] Overall failure rate : {failures/total:.2%}")
print(f"  [OK] Date range           : {df['timestamp'].min()} -> {df['timestamp'].max()}")
print(f"  [OK] Total amount (INR)   : {df['amount'].sum()/1e7:.2f} Cr")
print("\n  Done! Run 'python run_pipeline.py' next.\n")
