# fitting 2 Weibulls
import numpy as np
from scipy.optimize import curve_fit
import pandas as pd

def combined_weibull(x, amp1, k1, lam1, amp2, k2, lam2):
    weibull1 = amp1 * (k1 / lam1) * ((x / lam1) ** (k1 - 1)) * np.exp(-(x / lam1) ** k1)
    weibull2 = amp2 * (k2 / lam2) * ((x / lam2) ** (k2 - 1)) * np.exp(-(x / lam2) ** k2)
    return weibull1 + weibull2

# Read input data
data = pd.read_csv('input_data.csv', header=None, names=['Years', 'Residents'])

# Convert both 'Years' and 'Residents' columns to numeric, replacing any non-numeric values with NaN
data['Years'] = pd.to_numeric(data['Years'], errors='coerce')
data['Residents'] = pd.to_numeric(data['Residents'], errors='coerce')

# Remove any rows with NaN values
data = data.dropna()

# Extract x and y values
x = data['Years'].values
y = data['Residents'].values

# Initial guesses for the parameters of the two Weibull curves
initial_guesses = [max(y), 1.5, 5, max(y) / 2, 1.5, 15]

# Fit the combined distribution
popt, _ = curve_fit(combined_weibull, x, y, p0=initial_guesses, bounds=(0, np.inf))

# Extract optimized parameters
amp1, k1, lam1, amp2, k2, lam2 = popt

# Calculate individual distributions
weibull1 = amp1 * (k1 / lam1) * ((x / lam1) ** (k1 - 1)) * np.exp(-(x / lam1) ** k1)
weibull2 = amp2 * (k2 / lam2) * ((x / lam2) ** (k2 - 1)) * np.exp(-(x / lam2) ** k2)

# Round the results to nearest integer
weibull1_rounded = np.round(weibull1).astype(int)
weibull2_rounded = np.round(weibull2).astype(int)

# Adjust rounding errors to ensure sum matches original data
total_rounded = weibull1_rounded + weibull2_rounded
diff = y.astype(int) - total_rounded

for i in range(len(diff)):
    if diff[i] > 0:
        if weibull1_rounded[i] > weibull2_rounded[i]:
            weibull1_rounded[i] += diff[i]
        else:
            weibull2_rounded[i] += diff[i]
    elif diff[i] < 0:
        if weibull1_rounded[i] > abs(diff[i]):
            weibull1_rounded[i] += diff[i]
        else:
            weibull2_rounded[i] += diff[i]

# Create output dataframe
output_Wdata = pd.DataFrame({
    'Years': x,
    'Weibull comp1': weibull1,
    'Weibull comp2': weibull2,
    'Weibull1': weibull1_rounded,
    'Weibull2': weibull2_rounded
})

# Save output to CSV
output_Wdata.to_csv('output_Wdata.csv', index=False)

print("Separation in two Weibulls complete. Output saved to 'output_Wdata.csv'.")
