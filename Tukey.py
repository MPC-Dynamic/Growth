import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import f_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# Load the dataset from 'survey.csv'
df = pd.read_csv('survey.csv')

# Compute the mean HowSat for each unique value in 'Marketing'
marketing_means = df.groupby('Marketing')['HowSat'].mean()

# Visualization of average HowSat by 'Marketing'
plt.figure(figsize=(12, 6))
sns.barplot(x=marketing_means.index, y=marketing_means.values, ci=None)
plt.xticks(rotation=45, ha='right')
plt.title("Average HowSat by Marketing Category")
plt.xlabel("Marketing Categories")
plt.ylabel("Average HowSat")
plt.show()

# ANOVA test for significant differences across Marketing categories
df_clean = df.dropna(subset=['HowSat', 'Marketing'])
groups = [df_clean[df_clean['Marketing'] == category]['HowSat'] 
          for category in df_clean['Marketing'].unique() 
          if len(df_clean[df_clean['Marketing'] == category]) > 1]

if len(groups) > 1:
    f_stat, p_value = f_oneway(*groups)
    print(f"ANOVA test result: F-statistic = {f_stat:.4f}, p-value = {p_value:.4f}")
else:
    print("Not enough data for ANOVA test.")

# Tukey HSD test for pairwise comparisons
if len(df_clean['Marketing'].unique()) > 2:
    tukey_results = pairwise_tukeyhsd(df_clean['HowSat'], df_clean['Marketing'])
    print("\nTukey HSD Test Results:")
    print(tukey_results.summary())
else:
    print("\nNot enough groups for Tukey HSD test.")
