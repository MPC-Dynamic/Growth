import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
from scipy.stats import f_oneway, ttest_ind

# -------------------------------
# 1. Data Loading and Preparation
# -------------------------------

# Load the CSV file.
df = pd.read_csv("generations.csv")

# Assume the first column is the satisfaction (or proxy for satisfaction)
# Rename it to 'Satisfaction' (this ensures that later plotting commands work correctly)
satisfaction_col = df.columns[0]
df.rename(columns={satisfaction_col: 'Satisfaction'}, inplace=True)

# The remaining columns are assumed to represent counts for different generations.
generation_cols = df.columns[1:]

# Create a household identifier (if one does not already exist).
df['HouseholdID'] = df.index

# Calculate Family Size (total number of individuals in the household)
df['FamilySize'] = df[generation_cols].sum(axis=1)

# Melt the data so that each row corresponds to a household and a generation type.
# The 'Count' column indicates how many individuals of that generation are in the household.
df_melted = df.melt(
    id_vars=['HouseholdID', 'Satisfaction', 'FamilySize'],
    value_vars=generation_cols,
    var_name='Generation',
    value_name='Count'
)

# Expand the melted DataFrame: repeat each row as many times as the count.
df_expanded = df_melted.loc[df_melted.index.repeat(df_melted['Count'])].copy()
df_expanded.drop(columns='Count', inplace=True)
df_expanded.reset_index(drop=True, inplace=True)

# -------------------------------
# 2. Visualization
# -------------------------------


# (A) Bar Plot: Mean Satisfaction by Generation using errorbar='sd'
mean_satisfaction = df_expanded.groupby('Generation')['Satisfaction'].mean().reset_index()
plt.figure(figsize=(10, 6))

#sns.barplot(x='Generation', y='Satisfaction', data=mean_satisfaction, errorbar='sd')



sns.barplot(
    x='Generation',
    y='Satisfaction',
    data=mean_satisfaction,
    order=generation_cols,   # Explicitly set the order here
    errorbar='sd'
)




#plt.title("Mean Household Satisfaction by Generation")
#plt.title("Mean  - Woud You Still Choose this Community -  by Generation")
plt.title(" Willingness to pay higher POA fees -  by Generation")
#plt.title(" Average Years Lived in the Community by Generation")
plt.xlabel("Generation")
plt.ylabel("Mean Satisfaction")
### Set the y-axis limits from 4 to the maximum satisfaction value
#plt.ylim(3.9, mean_satisfaction['Satisfaction'].max() + 0.1)  # Set y-axis limits from 4 to max + buffer
#plt.ylim(0.7, mean_satisfaction['Satisfaction'].max() + 0.01)  # for binary responses like Would Still Choose
plt.ylim(0.2, mean_satisfaction['Satisfaction'].max() + 0.05)  # for Willingness to Pay
#plt.ylim(0, mean_satisfaction['Satisfaction'].max() + 1)  # for years lived in TV
#plt.ylim(10, mean_satisfaction['Satisfaction'].max() + 0.5)  # for time spent on survey

plt.tight_layout()
plt.show()




# (B) Boxplot: Satisfaction by Family Size using the original household-level data (df)
plt.figure(figsize=(8, 5))
sns.boxplot(x='FamilySize', y='Satisfaction', data=df)
plt.title("Household Satisfaction by Family Size")
plt.xlabel("Family Size")
plt.ylabel("Satisfaction Score")
plt.tight_layout()
plt.show()

# -------------------------------
# 3. Simple Estimation (ANOVA and Pairwise t-tests)
# -------------------------------

# --- Generation Differences ---

# Get the unique generation levels from the expanded data.
gen_levels = df_expanded['Generation'].unique()

# Group satisfaction by generation.
gen_groups = [df_expanded[df_expanded['Generation'] == gen]['Satisfaction'] for gen in gen_levels]

# Perform one-way ANOVA across generations.
anova_gen_result = f_oneway(*gen_groups)
print("ANOVA for Generation Differences in Satisfaction:")
print(anova_gen_result)
print()

# Perform pairwise t-tests between generations.
gen_pairs = list(itertools.combinations(gen_levels, 2))
t_test_gen_results = {}
print("Pairwise t-test results (Generation comparisons):")
for pair in gen_pairs:
    group1 = df_expanded[df_expanded['Generation'] == pair[0]]['Satisfaction']
    group2 = df_expanded[df_expanded['Generation'] == pair[1]]['Satisfaction']
    t_stat, p_val = ttest_ind(group1, group2, equal_var=False)
    t_test_gen_results[pair] = (t_stat, p_val)
    print(f"{pair}: t = {t_stat:.3f}, p = {p_val:.3f}")
print()

# --- Family Size Differences ---

# Get the unique family sizes from the original DataFrame.
family_sizes = sorted(df['FamilySize'].unique())
family_groups = [df[df['FamilySize'] == size]['Satisfaction'] for size in family_sizes]

# Perform one-way ANOVA across family sizes.
anova_family_result = f_oneway(*family_groups)
print("ANOVA for Family Size Differences in Satisfaction:")
print(anova_family_result)
print()

# Perform pairwise t-tests between family sizes.
family_pairs = list(itertools.combinations(family_sizes, 2))
t_test_family_results = {}
print("Pairwise t-test results (Family Size comparisons):")
for pair in family_pairs:
    group1 = df[df['FamilySize'] == pair[0]]['Satisfaction']
    group2 = df[df['FamilySize'] == pair[1]]['Satisfaction']
    t_stat, p_val = ttest_ind(group1, group2, equal_var=False)
    t_test_family_results[pair] = (t_stat, p_val)
    print(f"Family Size {pair[0]} vs {pair[1]}: t = {t_stat:.3f}, p = {p_val:.3f}")

