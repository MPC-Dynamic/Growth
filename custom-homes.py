#  Plot custom vs all single-family homes time series
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Read the CSV file
df = pd.read_csv('percentcustom.csv', header=None, names=['Year', 'US', 'TV_lower', 'TV_avg', 'TV_upper'])

# Convert columns to numeric, replacing any non-numeric values with NaN
numeric_columns = ['Year', 'US', 'TV_lower', 'TV_avg', 'TV_upper']
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Drop any rows with NaN values
df = df.dropna()

# Compute 95% confidence interval for TV data
df['TV_ci'] = (df['TV_upper'] - df['TV_lower']) / 2

# Create the plot
plt.figure(figsize=(12, 6))

# Plot US data
plt.plot(df['Year'], df['US'], label='US data', color='green', marker='o')

# Plot TV data with confidence interval
plt.plot(df['Year'], df['TV_avg'], label='Tellico Village', color='blue', marker='o')
plt.fill_between(df['Year'], df['TV_avg'] - df['TV_ci'], df['TV_avg'] + df['TV_ci'], 
                 color='blue', alpha=0.2)

# Add labels, title, and legend
plt.xlabel('Year')
plt.ylabel('Percent Custom-built')
plt.title('Percent Custom-built: Tellico Village vs US with 95% Confidence Interval')
plt.legend()

# Set x-axis ticks to 5-year intervals
start_year = df['Year'].min() - (df['Year'].min() % 5)
end_year = df['Year'].max() + (5 - df['Year'].max() % 5)
plt.xticks(np.arange(start_year, end_year + 1, 5))

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Show the plot
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
