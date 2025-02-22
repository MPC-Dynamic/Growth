import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# -----------------------------
# Load and prepare the data
# -----------------------------
df = pd.read_csv('generations_wtp.csv')

# Convert key columns to numeric to avoid type errors
columns_to_convert = [
    'GenZ2021', 'Millennials2021', 'GenX&YoungestBoomers2021', 
    'Boomers2021', 'Silents2021', 'Millennials2018', 
    'Genx2018', 'Boomers2018', 'Silents2018', 
    'WillingnessPayHigherPOAdues'
]
for col in columns_to_convert:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# -----------------------------
# Define weighted average and std functions
# -----------------------------
def weighted_average(gen_col):
    """
    For the given generation column, select only rows where the value is nonzero.
    Multiply each corresponding WillingnessPayHigherPOAdues value by the generation value,
    sum these products, and divide by the sum of the generation values.
    """
    nonzero = df[gen_col] != 0
    return (df.loc[nonzero, 'WillingnessPayHigherPOAdues'] * df.loc[nonzero, gen_col]).sum() / df.loc[nonzero, gen_col].sum()

def weighted_std(gen_col):
    """
    Compute the weighted standard deviation for WillingnessPayHigherPOAdues,
    using the generation value as the weight.
    """
    nonzero = df[gen_col] != 0
    x = df.loc[nonzero, 'WillingnessPayHigherPOAdues']
    w = df.loc[nonzero, gen_col]
    avg = weighted_average(gen_col)
    variance = (w * (x - avg)**2).sum() / w.sum()
    return np.sqrt(variance)

# -----------------------------
# Define generation mapping
# -----------------------------
# This mapping allows us to refer to the generation names in a consistent order.
# For Gen Z, only 2021 exists.
generation_mapping = {
    'Gen Z':      {'2021': 'GenZ2021',                '2018': None},
    'Millennials':{'2021': 'Millennials2021',         '2018': 'Millennials2018'},
    'Gen X':      {'2021': 'GenX&YoungestBoomers2021','2018': 'Genx2018'},
    'Boomers':    {'2021': 'Boomers2021',             '2018': 'Boomers2018'},
    'Silent':     {'2021': 'Silents2021',             '2018': 'Silents2018'}
}

# -----------------------------
# Compute weighted averages and standard deviations
# -----------------------------
weighted_avgs = {'2021': {}, '2018': {}}
weighted_stds = {'2021': {}, '2018': {}}

for gen, cols in generation_mapping.items():
    # For 2021 values (exists for every generation)
    if cols['2021'] is not None:
        weighted_avgs['2021'][gen] = weighted_average(cols['2021'])
        weighted_stds['2021'][gen] = weighted_std(cols['2021'])
    # For 2018 values (Gen Z is missing)
    if cols['2018'] is not None:
        weighted_avgs['2018'][gen] = weighted_average(cols['2018'])
        weighted_stds['2018'][gen] = weighted_std(cols['2018'])

# -----------------------------
# Prepare data for plotting
# -----------------------------
# We want the following order: Gen Z, Millennials, Gen X, Boomers, Silent.
plot_df = pd.DataFrame({
    'Generation': ['Gen Z', 'Millennials', 'Gen X', 'Boomers', 'Silent'],
    # For 2018, Gen Z will be NaN since no data exists
    '2018_Value': [
        weighted_avgs['2018'].get('Gen Z', np.nan),
        weighted_avgs['2018'].get('Millennials', np.nan),
        weighted_avgs['2018'].get('Gen X', np.nan),
        weighted_avgs['2018'].get('Boomers', np.nan),
        weighted_avgs['2018'].get('Silent', np.nan)
    ],
    '2018_Std': [
        weighted_stds['2018'].get('Gen Z', np.nan),
        weighted_stds['2018'].get('Millennials', np.nan),
        weighted_stds['2018'].get('Gen X', np.nan),
        weighted_stds['2018'].get('Boomers', np.nan),
        weighted_stds['2018'].get('Silent', np.nan)
    ],
    '2021_Value': [
        weighted_avgs['2021'].get('Gen Z', np.nan),
        weighted_avgs['2021'].get('Millennials', np.nan),
        weighted_avgs['2021'].get('Gen X', np.nan),
        weighted_avgs['2021'].get('Boomers', np.nan),
        weighted_avgs['2021'].get('Silent', np.nan)
    ],
    '2021_Std': [
        weighted_stds['2021'].get('Gen Z', np.nan),
        weighted_stds['2021'].get('Millennials', np.nan),
        weighted_stds['2021'].get('Gen X', np.nan),
        weighted_stds['2021'].get('Boomers', np.nan),
        weighted_stds['2021'].get('Silent', np.nan)
    ]
})

# -----------------------------
# Plotting the grouped bar chart
# -----------------------------
# In each group the bar for 2018 (if available) is plotted to the left and 2021 to the right.
generations = plot_df['Generation']
indices = np.arange(len(generations))
bar_width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
# Plot 2018 bars at left position; note Gen Z will show as NaN (no bar drawn)
bars_2018 = ax.bar(indices - bar_width/2, plot_df['2018_Value'], bar_width, 
                   yerr=plot_df['2018_Std'], capsize=5, label='2018', color='lightgreen')
# Plot 2021 bars at right position
bars_2021 = ax.bar(indices + bar_width/2, plot_df['2021_Value'], bar_width, 
                   yerr=plot_df['2021_Std'], capsize=5, label='2021', color='skyblue')

ax.set_xticks(indices)
ax.set_xticklabels(generations)
ax.set_xlabel('Generation')
ax.set_ylabel('Weighted Average Willingness to Pay\n(Excluding Zero Values)')
ax.set_title('Willingness to Pay Higher POA Dues by Generation\nComparison between 2018 and 2021')
ax.legend()
ax.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# -----------------------------
# Statistical Analysis: Normality & Pairwise Comparisons
# -----------------------------
print("\nStatistical Analysis (Excluding Zero Values):")
print("-" * 50)

# For each generation that has both 2018 and 2021 data, compare the raw willingness values.
# (Gen Z is skipped because 2018 does not exist.)
for gen, cols in generation_mapping.items():
    if cols['2018'] is None:
        print(f"\n{gen}: Only 2021 data available; skipping pairwise comparison.")
        continue
    
    # Extract nonzero data from the raw generation columns
    col_2021 = cols['2021']
    col_2018 = cols['2018']
    data_2021 = df[col_2021][df[col_2021] != 0].dropna()
    data_2018 = df[col_2018][df[col_2018] != 0].dropna()
    
    if len(data_2021) < 3 or len(data_2018) < 3:
        print(f"\n{gen}: Not enough data for statistical comparison (n2021={len(data_2021)}, n2018={len(data_2018)})")
        continue
    
    # Perform Shapiro–Wilk normality tests
    stat1, p1 = stats.shapiro(data_2021)
    stat2, p2 = stats.shapiro(data_2018)
    normal1 = p1 > 0.05
    normal2 = p2 > 0.05
    print(f"\n{gen} - Normality tests:")
    print(f"2021: Shapiro stat = {stat1:.4f}, p-value = {p1:.4f} ({'normal' if normal1 else 'not normal'})")
    print(f"2018: Shapiro stat = {stat2:.4f}, p-value = {p2:.4f} ({'normal' if normal2 else 'not normal'})")
    
    # Choose the appropriate test based on normality
    if normal1 and normal2:
        t_stat, p_val = stats.ttest_ind(data_2021, data_2018, equal_var=False)
        test_used = "t-test"
    else:
        t_stat, p_val = stats.mannwhitneyu(data_2021, data_2018, alternative='two-sided')
        test_used = "Mann-Whitney U"
    
    print(f"\n{gen} - {test_used} between 2021 and 2018:")
    print(f"Statistic: {t_stat:.4f}, p-value: {p_val:.4f}")
    print(f"Mean 2021 (n={len(data_2021)}): {data_2021.mean():.4f}")
    print(f"Mean 2018 (n={len(data_2018)}): {data_2018.mean():.4f}")
