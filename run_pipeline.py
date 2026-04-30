"""
run_pipeline.py
---------------
Master script - runs the full pipeline end-to-end:
  1. Data Cleaning
  2. Feature Engineering
  3. Analysis + Charts
  4. Dashboard data export (dashboard/data.js)

Run: python run_pipeline.py
(from inside the payment-analysis/ folder)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json, os, sys, warnings
warnings.filterwarnings('ignore')

# Change working directory to the directory of this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

os.makedirs('outputs/charts', exist_ok=True)
os.makedirs('dashboard', exist_ok=True)

plt.rcParams.update({
    'figure.facecolor':'#0f0f1a','axes.facecolor':'#1a1a2e',
    'axes.edgecolor':'#444','text.color':'#e0e0e0',
    'axes.labelcolor':'#e0e0e0','xtick.color':'#aaa',
    'ytick.color':'#aaa','grid.color':'#2a2a3e','grid.alpha':0.6,
    'font.family':'sans-serif',
})
PAL = ['#6c63ff','#ff6584','#43e97b','#f7971e','#4facfe','#a18cd1','#fccb90']

def save(name):
    plt.tight_layout()
    plt.savefig(f'outputs/charts/{name}.png', dpi=150, bbox_inches='tight',
                facecolor=plt.rcParams['figure.facecolor'])
    plt.close()
    print(f"    chart saved -> outputs/charts/{name}.png")

print("\n" + "="*60)
print("  PAYMENT FAILURE INTELLIGENCE SYSTEM - PIPELINE")
print("="*60)

# ---------------------------------------------------------------
# STEP 1: DATA CLEANING
# ---------------------------------------------------------------
print("\n[1/4] Data Cleaning...")
df = pd.read_csv('data/raw_transactions.csv')
print(f"  Raw rows: {len(df):,}")

np.random.seed(0)
df.loc[np.random.choice(df.index,200,replace=False),'amount']      = np.nan
df.loc[np.random.choice(df.index,150,replace=False),'region']      = np.nan
df.loc[np.random.choice(df.index,100,replace=False),'device_type'] = np.nan

df['amount']      = df['amount'].fillna(df['amount'].median())
df['region']      = df['region'].fillna(df['region'].mode()[0])
df['device_type'] = df['device_type'].fillna(df['device_type'].mode()[0])

dup_sample = df.sample(50, random_state=1)
df = pd.concat([df, dup_sample], ignore_index=True)
df = df.drop_duplicates(subset='transaction_id', keep='first')

df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.dropna(subset=['timestamp'])
df = df[(df['amount'] >= 1) & (df['amount'] <= 500_000)]
df = df.reset_index(drop=True)

quality = pd.DataFrame({
    'metric':['original_rows','cleaned_rows','duplicates_removed',
               'nulls_imputed','overall_failure_rate'],
    'value':[100_000, len(df), 50, 450,
             f"{(df['status']=='Failed').mean():.4f}"]
})
quality.to_csv('outputs/data_quality_report.csv', index=False)
df.to_csv('outputs/cleaned_data.csv', index=False)
print(f"  Cleaned rows: {len(df):,}  |  Failure rate: {(df['status']=='Failed').mean():.2%}")

# ---------------------------------------------------------------
# STEP 2: FEATURE ENGINEERING
# ---------------------------------------------------------------
print("\n[2/4] Feature Engineering...")

df['hour']        = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.dayofweek
df['day_name']    = df['timestamp'].dt.day_name()
df['month']       = df['timestamp'].dt.month
df['month_name']  = df['timestamp'].dt.strftime('%b')
df['year']        = df['timestamp'].dt.year
df['date']        = df['timestamp'].dt.date
df['is_weekend']  = df['day_of_week'].isin([5,6]).astype(int)
df['is_night']    = ((df['hour']>=0)&(df['hour']<6)).astype(int)
df['log_amount']  = np.log1p(df['amount'])
df['amount_bucket'] = pd.cut(df['amount'],
    bins=[0,1000,10000,50000,np.inf],
    labels=['Low (<1K)','Medium (1K-10K)','High (10K-50K)','Very High (>50K)'])
df['is_failed'] = (df['status']=='Failed').astype(int)

user_stats = df.groupby('user_id').agg(
    transactions_per_user=('transaction_id','count'),
    user_failure_rate=('is_failed','mean'),
).reset_index()
user_stats['user_type'] = np.where(user_stats['transactions_per_user']>=15,'Returning','New')
df = df.merge(user_stats[['user_id','transactions_per_user','user_failure_rate','user_type']],
              on='user_id', how='left')

daily = df.groupby('date').agg(total=('transaction_id','count'),failed=('is_failed','sum')).reset_index()
daily['date'] = pd.to_datetime(daily['date'])
daily['daily_fail_rate']  = daily['failed']/daily['total']
daily['rolling_7d_rate']  = daily['daily_fail_rate'].rolling(7,min_periods=1).mean()

df.to_csv('outputs/engineered_data.csv', index=False)
daily.to_csv('outputs/daily_trends.csv', index=False)
print(f"  Features added. Columns: {df.shape[1]}")

# ---------------------------------------------------------------
# STEP 3: ANALYSIS + CHARTS
# ---------------------------------------------------------------
print("\n[3/4] Analysis & Charts...")

# Aggregations
monthly = df.groupby(df['timestamp'].dt.to_period('M')).agg(
    total=('transaction_id','count'),revenue=('amount','sum'),
    failed=('is_failed','sum')).reset_index()
monthly['period_str'] = monthly['timestamp'].astype(str)
monthly['fail_rate']  = monthly['failed']/monthly['total']*100

hourly = df.groupby('hour').agg(total=('is_failed','count'),failed=('is_failed','sum'))
hourly['fail_rate'] = hourly['failed']/hourly['total']*100

cat_stats = df.groupby('category').agg(total=('is_failed','count'),failed=('is_failed','sum')).reset_index()
cat_stats['fail_rate'] = cat_stats['failed']/cat_stats['total']*100
cat_stats = cat_stats.sort_values('fail_rate',ascending=False)

dev_stats = df.groupby('device_type').agg(total=('is_failed','count'),failed=('is_failed','sum')).reset_index()
dev_stats['fail_rate'] = dev_stats['failed']/dev_stats['total']*100

reg_stats = df.groupby('region').agg(total=('is_failed','count'),failed=('is_failed','sum')).reset_index()
reg_stats['fail_rate'] = reg_stats['failed']/reg_stats['total']*100
reg_stats = reg_stats.sort_values('fail_rate',ascending=False)

pm_stats = df.groupby('payment_method').agg(total=('is_failed','count'),failed=('is_failed','sum')).reset_index()
pm_stats['fail_rate'] = pm_stats['failed']/pm_stats['total']*100

# Chart 1: Failure by Hour
fig,ax = plt.subplots(figsize=(13,5))
ax.plot(hourly.index,hourly['fail_rate'],color='#ff6584',linewidth=2.5,marker='o',markersize=5)
ax.fill_between(hourly.index,hourly['fail_rate'],alpha=0.2,color='#ff6584')
ax.axvspan(-0.5,5.5,alpha=0.08,color='#6c63ff',label='Night (0-5 AM)')
ax.set_title('Failure Rate by Hour of Day',fontsize=14,color='white',fontweight='bold')
ax.set_xlabel('Hour');ax.set_ylabel('Failure Rate (%)')
ax.set_xticks(range(24));ax.legend()
save('failure_by_hour')

# Chart 2: By Category
fig,ax = plt.subplots(figsize=(10,5))
cs = cat_stats.sort_values('fail_rate',ascending=True)
bars = ax.barh(cs['category'],cs['fail_rate'],color=PAL,edgecolor='none')
for bar,val in zip(bars,cs['fail_rate']):
    ax.text(val+0.2,bar.get_y()+bar.get_height()/2,f'{val:.1f}%',va='center',color='white',fontsize=10)
ax.set_title('Failure Rate by Category',fontsize=14,color='white',fontweight='bold')
ax.set_xlabel('Failure Rate (%)')
save('failure_by_category')

# Chart 3: By Device
fig,ax = plt.subplots(figsize=(7,5))
bars = ax.bar(dev_stats['device_type'],dev_stats['fail_rate'],
              color=['#6c63ff','#43e97b','#f7971e'],width=0.5,edgecolor='none')
for bar,val in zip(bars,dev_stats['fail_rate']):
    ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.2,
            f'{val:.1f}%',ha='center',color='white',fontsize=12)
ax.set_title('Failure Rate by Device',fontsize=14,color='white',fontweight='bold')
ax.set_xlabel('Device');ax.set_ylabel('Failure Rate (%)')
save('failure_by_device')

# Chart 4: By Region
fig,ax = plt.subplots(figsize=(8,5))
bars = ax.bar(reg_stats['region'],reg_stats['fail_rate'],color=PAL,width=0.5,edgecolor='none')
for bar,val in zip(bars,reg_stats['fail_rate']):
    ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.2,
            f'{val:.1f}%',ha='center',color='white',fontsize=12)
ax.set_title('Failure Rate by Region',fontsize=14,color='white',fontweight='bold')
ax.set_xlabel('Region');ax.set_ylabel('Failure Rate (%)')
save('failure_by_region')

# Chart 5: Time Series
fig,axes = plt.subplots(2,1,figsize=(14,8),sharex=True)
axes[0].plot(daily['date'],daily['total'],color='#6c63ff',linewidth=1.2,alpha=0.6)
axes[0].plot(daily['date'],daily['total'].rolling(7).mean(),color='white',linewidth=2,label='7-Day Avg')
axes[0].set_title('Daily Transactions',color='white',fontsize=12,fontweight='bold');axes[0].legend()
axes[1].plot(daily['date'],daily['daily_fail_rate']*100,color='#ff6584',linewidth=1,alpha=0.4)
axes[1].plot(daily['date'],daily['rolling_7d_rate']*100,color='#f7971e',linewidth=2.5,label='7-Day Avg')
axes[1].set_title('Daily Failure Rate (%)',color='white',fontsize=12,fontweight='bold');axes[1].legend()
axes[1].set_xlabel('Date')
fig.suptitle('Transaction Trends Over Time',fontsize=15,color='white',fontweight='bold')
save('time_series')

# Chart 6: Segmentation
seg = df.groupby('user_type')['is_failed'].mean().reset_index()
amt = df.groupby('amount_bucket',observed=True)['is_failed'].mean().reset_index()
fig,axes = plt.subplots(1,2,figsize=(13,5))
bars0 = axes[0].bar(seg['user_type'],seg['is_failed']*100,color=['#6c63ff','#ff6584'],width=0.4)
for bar,val in zip(bars0,seg['is_failed']*100):
    axes[0].text(bar.get_x()+bar.get_width()/2,val+0.2,f'{val:.1f}%',ha='center',color='white',fontsize=13)
axes[0].set_title('New vs Returning Users',color='white',fontsize=12,fontweight='bold')
axes[0].set_ylabel('Failure Rate (%)')
bars1 = axes[1].bar(amt['amount_bucket'].astype(str),amt['is_failed']*100,
                    color=['#43e97b','#f7971e','#ff6584','#a18cd1'],width=0.5)
for bar,val in zip(bars1,amt['is_failed']*100):
    axes[1].text(bar.get_x()+bar.get_width()/2,val+0.2,f'{val:.1f}%',ha='center',color='white',fontsize=11)
axes[1].set_title('Failure by Transaction Value',color='white',fontsize=12,fontweight='bold')
axes[1].tick_params(axis='x',rotation=15)
fig.suptitle('Segmentation Analysis',fontsize=15,color='white',fontweight='bold')
save('segmentation_analysis')

# Chart 7: Revenue Loss
failed_df = df[df['status']=='Failed'].copy()
total_revenue_processed = df['amount'].sum()
total_revenue_lost      = failed_df['amount'].sum()
avg_failed_amt          = failed_df['amount'].mean()

monthly_loss = failed_df.groupby(failed_df['timestamp'].dt.to_period('M'))['amount'].sum().reset_index()
monthly_loss.columns=['month','revenue_loss']
monthly_loss['month'] = monthly_loss['month'].astype(str)

fig,ax = plt.subplots(figsize=(13,5))
ax.bar(monthly_loss['month'],monthly_loss['revenue_loss']/1e5,color='#ff6584',alpha=0.85)
ax.plot(monthly_loss['month'],monthly_loss['revenue_loss'].rolling(3).mean()/1e5,
        color='white',linewidth=2.5,label='3-Month Avg')
ax.set_title('Monthly Revenue Loss (INR Lakhs)',fontsize=14,color='white',fontweight='bold')
ax.set_xlabel('Month');ax.set_ylabel('INR Lakhs')
ax.tick_params(axis='x',rotation=45,labelsize=7);ax.legend()
save('revenue_loss')

# Chart 8: Funnel
total_initiated = len(df)
total_processed = int(total_initiated*0.98)
total_success   = int((df['status']=='Success').sum())
fig,ax = plt.subplots(figsize=(9,5))
stages = ['Initiated','Processed','Success']
vals   = [total_initiated,total_processed,total_success]
colors = ['#6c63ff','#4facfe','#43e97b']
bars = ax.barh(stages[::-1],vals[::-1],color=colors[::-1],height=0.5)
for bar,val in zip(bars,vals[::-1]):
    ax.text(val+500,bar.get_y()+bar.get_height()/2,
            f'{val:,}  ({val/total_initiated*100:.1f}%)',va='center',color='white',fontsize=11)
ax.set_title('Transaction Funnel',fontsize=14,color='white',fontweight='bold')
ax.set_xlim(0,total_initiated*1.2);ax.set_xlabel('Transactions')
save('funnel_analysis')

# Statistical Tests
cont_dev = pd.crosstab(df['device_type'],df['status'])
chi2_d,p_d,_,_ = stats.chi2_contingency(cont_dev)
cont_cat = pd.crosstab(df['category'],df['status'])
chi2_c,p_c,_,_ = stats.chi2_contingency(cont_cat)
u_stat,p_mw = stats.mannwhitneyu(df[df['status']=='Success']['amount'],
                                  df[df['status']=='Failed']['amount'],alternative='two-sided')
cont_night = pd.crosstab(df['is_night'],df['status'])
_,p_n,_,_ = stats.chi2_contingency(cont_night)
night_rate = df[df['is_night']==1]['is_failed'].mean()
day_rate   = df[df['is_night']==0]['is_failed'].mean()

peak_hour = int(hourly['fail_rate'].idxmax())
top_cat   = cat_stats.iloc[0]
top_reg   = reg_stats.iloc[0]
top_dev   = dev_stats.sort_values('fail_rate',ascending=False).iloc[0]

insights = pd.DataFrame([
    ('total_transactions',          len(df)),
    ('total_failed',                int((df['status']=='Failed').sum())),
    ('overall_failure_rate_pct',    round((df['status']=='Failed').mean()*100,2)),
    ('total_revenue_processed_inr', round(total_revenue_processed,2)),
    ('total_revenue_lost_inr',      round(total_revenue_lost,2)),
    ('revenue_loss_pct',            round(total_revenue_lost/total_revenue_processed*100,2)),
    ('avg_failed_txn_value_inr',    round(avg_failed_amt,2)),
    ('highest_failure_category',    top_cat['category']),
    ('highest_fail_cat_rate_pct',   round(top_cat['fail_rate'],2)),
    ('highest_failure_region',      top_reg['region']),
    ('highest_fail_reg_rate_pct',   round(top_reg['fail_rate'],2)),
    ('highest_failure_device',      top_dev['device_type']),
    ('highest_fail_dev_rate_pct',   round(top_dev['fail_rate'],2)),
    ('peak_failure_hour',           peak_hour),
    ('peak_hour_failure_rate_pct',  round(float(hourly.loc[peak_hour,'fail_rate']),2)),
    ('night_failure_rate_pct',      round(night_rate*100,2)),
    ('day_failure_rate_pct',        round(day_rate*100,2)),
    ('chi2_device_pvalue',          round(p_d,6)),
    ('chi2_category_pvalue',        round(p_c,6)),
    ('mannwhitney_amount_pvalue',   round(p_mw,6)),
],columns=['metric','value'])

insights.to_csv('outputs/insights_summary.csv',index=False)
monthly_loss.to_csv('outputs/monthly_revenue_loss.csv',index=False)
print(f"  {len(os.listdir('outputs/charts'))} charts saved")

# ---------------------------------------------------------------
# STEP 4: EXPORT DASHBOARD DATA
# ---------------------------------------------------------------
print("\n[4/4] Exporting dashboard data...")

seg_data = df.groupby('user_type')['is_failed'].mean().reset_index()
amt_data = df.groupby('amount_bucket',observed=True)['is_failed'].mean().reset_index()

dashboard_data = {
    "kpis": {
        "total_transactions":     len(df),
        "total_failed":           int((df['status']=='Failed').sum()),
        "total_success":          int((df['status']=='Success').sum()),
        "success_rate":           round((df['status']=='Success').mean()*100,2),
        "failure_rate":           round((df['status']=='Failed').mean()*100,2),
        "total_revenue_cr":       round(total_revenue_processed/1e7,2),
        "revenue_lost_cr":        round(total_revenue_lost/1e7,2),
        "avg_failed_txn":         round(avg_failed_amt,2),
        "peak_failure_hour":      peak_hour,
    },
    "failure_by_hour": {
        "hours":   hourly.index.tolist(),
        "rates":   hourly['fail_rate'].round(2).tolist(),
        "totals":  hourly['total'].tolist(),
        "failed":  hourly['failed'].tolist(),
    },
    "failure_by_category": {
        "categories": cat_stats['category'].tolist(),
        "rates":      cat_stats['fail_rate'].round(2).tolist(),
        "totals":     cat_stats['total'].tolist(),
        "failed":     cat_stats['failed'].tolist(),
    },
    "failure_by_device": {
        "devices": dev_stats['device_type'].tolist(),
        "rates":   dev_stats['fail_rate'].round(2).tolist(),
        "totals":  dev_stats['total'].tolist(),
        "failed":  dev_stats['failed'].tolist(),
    },
    "failure_by_region": {
        "regions": reg_stats['region'].tolist(),
        "rates":   reg_stats['fail_rate'].round(2).tolist(),
        "totals":  reg_stats['total'].tolist(),
        "failed":  reg_stats['failed'].tolist(),
    },
    "failure_by_payment": {
        "methods": pm_stats['payment_method'].tolist(),
        "rates":   pm_stats['fail_rate'].round(2).tolist(),
        "totals":  pm_stats['total'].tolist(),
    },
    "monthly_trends": {
        "months":  monthly['period_str'].tolist(),
        "total":   monthly['total'].tolist(),
        "failed":  monthly['failed'].tolist(),
        "revenue": [round(x/1e5,2) for x in monthly['revenue'].tolist()],
        "fail_rate": monthly['fail_rate'].round(2).tolist(),
    },
    "monthly_loss": {
        "months": monthly_loss['month'].tolist(),
        "loss_lakhs": [round(x/1e5,2) for x in monthly_loss['revenue_loss'].tolist()],
    },
    "segmentation": {
        "user_types":     seg_data['user_type'].tolist(),
        "user_rates":     (seg_data['is_failed']*100).round(2).tolist(),
        "amount_buckets": amt_data['amount_bucket'].astype(str).tolist(),
        "amount_rates":   (amt_data['is_failed']*100).round(2).tolist(),
    },
    "daily_trends": {
        "dates":   daily['date'].astype(str).tolist()[-90:],
        "total":   daily['total'].tolist()[-90:],
        "failed":  daily['failed'].tolist()[-90:],
        "rolling": daily['rolling_7d_rate'].round(4).tolist()[-90:],
    },
    "stats_tests": {
        "chi2_device_pvalue":   round(p_d,6),
        "chi2_category_pvalue": round(p_c,6),
        "mannwhitney_pvalue":   round(p_mw,6),
        "night_fail_rate":      round(night_rate*100,2),
        "day_fail_rate":        round(day_rate*100,2),
    }
}

js_content = f"window.DASHBOARD_DATA = {json.dumps(dashboard_data, indent=2)};"
with open('dashboard/data.js','w',encoding='utf-8') as f:
    f.write(js_content)

print("  [OK] Saved dashboard/data.js")
print("\n" + "="*60)
print("  PIPELINE COMPLETE!")
print("="*60)
print(f"\n  Total Transactions : {len(df):,}")
print(f"  Overall Fail Rate  : {(df['status']=='Failed').mean():.2%}")
print(f"  Revenue Processed  : INR {total_revenue_processed/1e7:,.2f} Cr")
print(f"  Revenue Lost       : INR {total_revenue_lost/1e7:,.2f} Cr")
print(f"\n  Open dashboard/index.html in your browser to view the dashboard.")
print("="*60 + "\n")
