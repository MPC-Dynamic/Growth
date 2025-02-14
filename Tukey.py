# Reads survey.csv where second column contains categorical variables and first has numerical (satisfaction) scores
# Generate a bar chart of Categorical column vs. First column
# Perform an ANOVA test to check for differences.
# Run the Tukey HSD test to find which categories differ.
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import f_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# Load the dataset from 'survey.csv'
df = pd.read_csv('survey.csv')

# Automatically get the header names for the first two columns
satisfaction_col = df.columns[0]
marketing_col = df.columns[1]

# Compute the mean satisfaction for each unique value in the marketing column
marketing_means = df.groupby(marketing_col)[satisfaction_col].mean()

# Visualization of average satisfaction by the marketing column
plt.figure(figsize=(12, 6))
sns.barplot(x=marketing_means.index, y=marketing_means.values, errorbar=None)
plt.xticks(rotation=45, ha='right')
plt.title(f"Average {satisfaction_col} by {marketing_col}")
plt.xlabel(marketing_col)
plt.ylabel(f"Average {satisfaction_col}")

# Set y-axis limits (using the overall maximum satisfaction value)
plt.ylim(3, df['HowSat'].max()-0.25)  # scale the differences
plt.show()

# ANOVA test for significant differences across marketing categories
df_clean = df.dropna(subset=[satisfaction_col, marketing_col])
groups = [df_clean[df_clean[marketing_col] == category][satisfaction_col] 
          for category in df_clean[marketing_col].unique() 
          if len(df_clean[df_clean[marketing_col] == category]) > 1]

if len(groups) > 1:
    f_stat, p_value = f_oneway(*groups)
    print(f"ANOVA test result: F-statistic = {f_stat:.4f}, p-value = {p_value:.4f}")
else:
    print("Not enough data for ANOVA test.")

# Tukey HSD test for pairwise comparisons (if more than 2 groups exist)
if len(df_clean[marketing_col].unique()) > 2:
    tukey_results = pairwise_tukeyhsd(df_clean[satisfaction_col], df_clean[marketing_col])
    print("\nTukey HSD Test Results:")
    print(tukey_results.summary())
else:
    print("\nNot enough groups for Tukey HSD test.")
