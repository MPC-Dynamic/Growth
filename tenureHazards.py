import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
import math

# ---------------------------
# 1. Data Preparation
# ---------------------------

# Load data from csv file
df = pd.read_csv('ee.csv')

# Convert Entrance_Date and Exit_Date to datetime (invalid dates become NaT)
df['Entrance_Date'] = pd.to_datetime(df['Entrance_Date'], errors='coerce')
df['Exit_Date'] = pd.to_datetime(df['Exit_Date'], errors='coerce')

# Calculate Tenure_Days:
#   - For those missing an Exit_Date, use the latest Entrance_Date as a proxy end date.
latest_entry_date = df['Entrance_Date'].max()
df['Tenure_Days'] = (df['Exit_Date'].fillna(latest_entry_date) - df['Entrance_Date']).dt.days

# Create an Event indicator: 1 if an Exit_Date is recorded, 0 otherwise.
df['Event'] = df['Exit_Date'].notnull().astype(int)

# ---------------------------
# 2. Kaplan-Meier Survival Analysis (for context)
# ---------------------------

kmf = KaplanMeierFitter()
kmf.fit(df['Tenure_Days'], event_observed=df['Event'])

plt.figure(figsize=(10, 6))
kmf.plot()
plt.xlabel("Tenure (Days)")
plt.ylabel("Survival Probability")
plt.title("Kaplan-Meier Estimate of Survival Probability")
plt.grid(True)
plt.show()

# ---------------------------
# 3. Compute Daily Hazard Rate
# ---------------------------

# Determine the maximum tenure (in days)
max_time = df['Tenure_Days'].max()
days = np.arange(0, max_time + 1)

# Count events on each day. Reindex over the full range of days.
event_counts = df.groupby('Tenure_Days')['Event'].sum().reindex(days, fill_value=0)

# For each day, count how many individuals are still "at risk"
risk_counts = np.array([ (df['Tenure_Days'] >= t).sum() for t in days ])

# Compute the daily hazard rate as: hazard = events / risk (for each day)
hazard_rate = event_counts / risk_counts

# ---------------------------
# 4. Aggregate to Yearly Hazard Rates
# ---------------------------
# Here we group the daily hazard information into yearly bins (each covering 365 days).
# We calculate the total events and total "person-days at risk" for each year,
# and then compute the average hazard for that year.
n_years = math.ceil((max_time + 1) / 365)
yearly_hazard = []  # This will hold the average daily hazard in each year

for y in range(n_years):
    start_day = y * 365
    end_day = min((y + 1) * 365, max_time + 1)
    # Sum the events in this year
    events_year = event_counts[start_day:end_day].sum()
    # Sum the risk counts (i.e. the total number of person-days at risk)
    risk_year = risk_counts[start_day:end_day].sum()
    # Compute the average daily hazard for the year
    hazard_year = events_year / risk_year if risk_year != 0 else np.nan
    yearly_hazard.append(hazard_year)

# Convert the yearly hazard list into a Pandas Series with the year as the index.
yearly_hazard_series = pd.Series(yearly_hazard, index=np.arange(n_years))

# For an annualized rate (which approximates the number of events per year),
# multiply the average daily hazard by 365.
yearly_hazard_annualized = yearly_hazard_series * 365

# ---------------------------
# 5. Plot the Yearly Hazard Rates
# ---------------------------

plt.figure(figsize=(10, 6))
plt.plot(yearly_hazard_series.index, yearly_hazard_series, marker='o', linestyle='-', label='Average Daily Hazard (Yearly)')
plt.plot(yearly_hazard_series.index, yearly_hazard_annualized, marker='s', linestyle='--', label='Annualized Hazard Rate')
plt.xlabel("Years since entry")
plt.ylabel("Hazard Rate")
plt.title("Yearly Smoothed Hazard Rates")
plt.legend()
plt.grid(True)
plt.show()

# Optionally, print the yearly hazard rates for inspection:
print("Yearly Average Daily Hazard Rates:")
print(yearly_hazard_series)
print("\nYearly Annualized Hazard Rates:")
print(yearly_hazard_annualized)
