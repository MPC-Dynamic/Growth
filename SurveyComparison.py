import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
from scipy import stats

# -----------------------------
# Load and prepare the data
# -----------------------------
df = pd.read_csv('generations_wtp.csv')

# ----------------------------
# Define a weighted average function that accepts a generation series and the willingness series.
# It filters out rows where the generation weight is 0 or missing.
# ----------------------------
def weighted_average(w, x):
    mask = (w != 0) & w.notnull() & x.notnull()
    if mask.sum() == 0:
        return np.nan
    return (w[mask] * x[mask]).sum() / w[mask].sum()

# ----------------------------
# Define the generation columns for both years.
# For 2021 we have: GenZ2021, Millennials2021, GenX&YoungestBoomers2021, Boomers2021, Silents2021.
# For 2018 we have: Millennials2018, Genx2018, Boomers2018, Silents2018.
# ----------------------------
generation_columns = [
    'GenZ2021', 'Millennials2021', 'GenX&YoungestBoomers2021', 'Boomers2021', 'Silents2021',
    'Millennials2018', 'Genx2018', 'Boomers2018', 'Silents2018'
]

# ----------------------------
# Create a helper to map each column name to a display-friendly generation and year.
# ----------------------------
def parse_generation(col):
    if col.endswith('2021'):
        year = '2021'
        if col == 'GenZ2021':
            gen = 'Gen Z'
        elif col == 'Millennials2021':
            gen = 'Millennials'
        elif col == 'GenX&YoungestBoomers2021':
            gen = 'Gen X'
        elif col == 'Boomers2021':
            gen = 'Boomers'
        elif col == 'Silents2021':
            gen = 'Silent'
        else:
            gen = col
    elif col.endswith('2018'):
        year = '2018'
        if col == 'Millennials2018':
            gen = 'Millennials'
        elif col == 'Genx2018':
            gen = 'Gen X'
        elif col == 'Boomers2018':
            gen = 'Boomers'
        elif col == 'Silents2018':
            gen = 'Silent'
        else:
            gen = col
    else:
        year = ''
        gen = col
    return gen, year

# ----------------------------
# Build a DataFrame for plotting.
# Each row has: Generation (display name), Year, and the computed Weighted Average.
# ----------------------------
plot_data_list = []
for col in generation_columns:
    gen, year = parse_generation(col)
    wa = weighted_average(df[col], df['WillingnessPayHigherPOAdues'])
    plot_data_list.append({'Generation': gen, 'Year': year, 'Weighted_Average': wa})
plot_df = pd.DataFrame(plot_data_list)

# We want the generation order to have Gen Z first.
gen_order = ['Gen Z', 'Millennials', 'Gen X', 'Boomers', 'Silent']

# ----------------------------
# Choose a color palette.
# Choices: "deep", "muted", "bright", "pastel", "dark", "colorblind".
# ----------------------------
palette = sns.color_palette("bright")

# ----------------------------
# Create the bar plot.
# Set hue_order so that within each generation the 2018 bar is placed to the left of the 2021 bar.
# Note: For generations without 2018 data (like Gen Z), only the 2021 bar is shown.
# ----------------------------
plt.figure(figsize=(12, 6))
ax = sns.barplot(
    data=plot_df,
    x='Generation',
    y='Weighted_Average',
    hue='Year',
    order=gen_order,
    hue_order=['2018', '2021'],  # Ensures 2018 bars precede 2021 bars
    errorbar=None,
    palette=palette
)
plt.title('Weighted Average Willingness to Pay Higher POA Dues by Generation')
plt.xlabel('Generation')
plt.ylabel('Average Willingness to Pay')
plt.ylim(2.0, 3.1)  # 
plt.xticks(rotation=45)
plt.grid(True, axis='y', linestyle='--', alpha=0.7)

# Shift the legend to the left to prevent overlap with the last two columns.
# Adjust bbox_to_anchor values as needed.
plt.legend(title="Year", bbox_to_anchor=(0.02, 0.98), loc='upper left', borderaxespad=0)

plt.tight_layout()
plt.show()

# ----------------------------
# Now run the computations: weighted averages, normality tests, and pairwise comparisons.
# ----------------------------
alpha = 0.05  # significance level for tests

# Dictionaries to store results
weighted_avgs = {}
normality_results = {}   # will store the p-value for the Shapiro–Wilk test
group_willingness_data = {}  # to hold the WillingnessPayHigherPOAdues values for each generation group

print("=== Weighted Averages and Normality Tests ===")
for col in generation_columns:
    # Create a mask for rows where the generation value is nonzero and both the generation and willingness data exist.
    mask = (df[col] != 0) & df[col].notnull() & df['WillingnessPayHigherPOAdues'].notnull()
    
    # Get the subset of WillingnessPayHigherPOAdues values
    group_data = df.loc[mask, 'WillingnessPayHigherPOAdues']
    group_willingness_data[col] = group_data  # save for later pairwise tests
    
    # Compute weighted average for this generation column
    wa = weighted_average(df[col], df['WillingnessPayHigherPOAdues'])
    weighted_avgs[col] = wa
    print(f"Weighted average for {col}: {wa}")
    
    # Only run normality test if enough data points exist (Shapiro requires at least 3 values)
    if len(group_data) >= 3:
        stat, p = stats.shapiro(group_data)
        normality_results[col] = p
        normality_str = "normal" if p > alpha else "not normal"
        print(f"Normality test for {col}: statistic = {stat:.4f}, p-value = {p:.4f} ({normality_str})")
    else:
        normality_results[col] = None
        print(f"Not enough data for normality test for {col}")

print("\n=== Pairwise Comparisons ===")
pairwise_results = {}
# Compare each pair of generation groups using the WillingnessPayHigherPOAdues values
for col1, col2 in itertools.combinations(generation_columns, 2):
    # Get the willingness values (dropping any NaNs)
    group1 = group_willingness_data[col1].dropna()
    group2 = group_willingness_data[col2].dropna()
    
    # Skip pair if one group has too few values
    if len(group1) < 3 or len(group2) < 3:
        print(f"Not enough data for pairwise test between {col1} and {col2}")
        continue
    
    # Check normality for both groups (if available)
    normal1 = (normality_results[col1] is not None) and (normality_results[col1] > alpha)
    normal2 = (normality_results[col2] is not None) and (normality_results[col2] > alpha)
    
    if normal1 and normal2:
        # If both groups are normally distributed, use an independent t-test
        stat, p = stats.ttest_ind(group1, group2)
        test_used = "t-test"
    else:
        # If one (or both) group is not normal, use the Mann–Whitney U test
        stat, p = stats.mannwhitneyu(group1, group2, alternative='two-sided')
        test_used = "Mann-Whitney U"
    
    pairwise_results[(col1, col2)] = (test_used, stat, p)
    significance = "SIGNIFICANT" if p < alpha else "not significant"
    print(f"{col1} vs {col2}: {test_used}, statistic = {stat:.4f}, p-value = {p:.4f} ({significance})")
