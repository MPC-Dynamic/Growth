import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import gamma, lognorm

# ----------------------------------------------------------------------
# Historical data: each row is one year of stats
# ----------------------------------------------------------------------
data = {
    'Year': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
    'Median': [10, 10, 11, 11, 9, 5, 6, 3, 3, 5],
    'Mean': [10.29288703, 10.24503311, 11.446875, 10.32911392, 10.78978979,
             9.104972376, 9.575835476, 8.317808219, 6.977839335, 8.551075269],
    'Mode': [1, 11, 1, 1, 1, 1, 1, 1, 1, 1],
    'StdDev': [6.890347013, 7.091211057, 7.583825569, 7.63778663, 8.733898315,
               8.682776764, 9.306495467, 9.076163421, 8.048778844, 9.199793384],
    'ShortTermSales': [40, 48, 53, 76, 80, 121, 137, 159, 161, 116],
    'TotalSales': [239, 302, 320, 316, 333, 362, 389, 365, 361, 372]
}

df = pd.DataFrame(data)

# ----------------------------------------------------------------------
# Helper function: generate durations for a single year
# using a mixture of two distributions.
# ----------------------------------------------------------------------
def simulate_durations_for_year(
    n_sales, 
    frac_short_term, 
    long_mean, 
    long_std, 
    short_shape=2.0, 
    short_scale=1.0, 
    long_lognorm_shape=None
):
    """
    n_sales        : total number of homes sold that year
    frac_short_term: fracti


    # Neighborhood-specific
    for nbhd, stats_list in neighborhood_stats.items():
        nbhd_results = pd.concat(stats_list, ignore_index=True)
        sheet_name = nbhd[:31]  # Excel sheet name limit
        nbhd_results.to_excel(writer, sheet_name=sheet_name, index=False)

print("All done! 'original_data_with_duration.csv' now has all columns for every date, and stats are in 'hold_duration_counts.xlsx'.")
