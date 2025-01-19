import pandas as pd
from datetime import datetime

# --------------------------------------------------------------------
# Read original CSV ONCE and prepare data
# --------------------------------------------------------------------
csv_file = 'Sales.csv'
df = pd.read_csv(csv_file)

# Convert date columns to datetime
df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
df['sale_date']     = pd.to_datetime(df['sale_date'],     errors='coerce')
df['build_date']    = pd.to_datetime(df['build_date'],    errors='coerce')

# --------------------------------------------------------------------
# Main script that loops through yearly increments and does statistics
# --------------------------------------------------------------------
start_date = datetime(2020, 1, 1)
end_date   = datetime(2025, 1, 1)

all_results        = []
neighborhood_stats = {}

current_date = start_date
while current_date <= end_date:
    # ----------------------------------------------------------------
    # 1) Create sale_date_for_{yyyy-mm-dd} column
    # ----------------------------------------------------------------
    sale_date_col = f"sale_date_for_{current_date.strftime('%Y-%m-%d')}"

    # If original sale_date < current_date => 1980-01-01
    # Otherwise (if sale_date >= current_date or is NaT) => current_date
    df[sale_date_col] = df['sale_date'].apply(
        lambda s: datetime(1980, 1, 1) if (pd.notna(s) and s < current_date)
                  else current_date
    )

    # ----------------------------------------------------------------
    # 2) Create duration_for_{yyyy-mm-dd} column
    # ----------------------------------------------------------------
    duration_col = f"duration_for_{current_date.strftime('%Y-%m-%d')}"
    
    df[duration_col] = (
        (df[sale_date_col] - df[['purchase_date', 'build_date']].max(axis=1))
        .dt.days
        .div(365)
        .round()
        .astype('Int64')   # Allow integer while preserving missing data if any
    )

    # ----------------------------------------------------------------
    # 3) Calculate statistics (filter negative durations if needed)
    # ----------------------------------------------------------------
    filtered_data = df[df[duration_col] >= 0]

    # Overall stats
    overall_counts = (
        filtered_data[duration_col]
        .value_counts()
        .sort_index()
        .reset_index()
        .rename(columns={'index': 'Holding Years', duration_col: 'Count'})
    )
    overall_counts['Specified Date'] = current_date.strftime('%Y-%m-%d')
    all_results.append(overall_counts)

    # Neighborhood-specific stats
    for neighborhood in df['neighborhood'].unique():
        if neighborhood not in neighborhood_stats:
            neighborhood_stats[neighborhood] = []
        subset = filtered_data[filtered_data['neighborhood'] == neighborhood]
        
        neighborhood_counts = (
            subset[duration_col]
            .value_counts()
            .sort_index()
            .reset_index()
            .rename(columns={'index': 'Holding Years', duration_col: 'Count'})
        )
        neighborhood_counts['Specified Date'] = current_date.strftime('%Y-%m-%d')
        neighborhood_stats[neighborhood].append(neighborhood_counts)

    # Move to next year
    current_date = datetime(current_date.year + 1, current_date.month, current_date.day)

# --------------------------------------------------------------------
# After the loop: overwrite original_data_with_duration.csv once
# --------------------------------------------------------------------
df.to_csv('original_data_with_duration.csv', index=False)

# --------------------------------------------------------------------
# Combine and write out final statistics to Excel
# --------------------------------------------------------------------
final_results = pd.concat(all_results, ignore_index=True)

with pd.ExcelWriter('hold_duration_counts.xlsx') as writer:
    # Overall stats
    final_results.to_excel(writer, sheet_name='Overall Stats', index=False)

    # Neighborhood-specific
    for nbhd, stats_list in neighborhood_stats.items():
        nbhd_results = pd.concat(stats_list, ignore_index=True)
        sheet_name = nbhd[:31]  # Excel sheet name limit
        nbhd_results.to_excel(writer, sheet_name=sheet_name, index=False)

print("All done! 'original_data_with_duration.csv' now has all columns for every date, and stats are in 'hold_duration_counts.xlsx'.")
