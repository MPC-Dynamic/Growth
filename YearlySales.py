# compute nonzero transactions, histograms for time property held
import pandas as pd
import numpy as np

# Load the data, handling potential errors
try:
    df = pd.read_csv("u.csv")
except FileNotFoundError:
    print("Error: u.csv not found. Please ensure the file exists in the same directory.")
    exit()

# data cleaning and processing

# Data Cleaning:  Price column
def clean_price(price_str):
    try:
        price_str = price_str.replace('$', '').replace(',', '') #Remove '$' and ','
        return float(price_str)
    except (ValueError, AttributeError): #Handle cases where price is not a valid string
        return 0.0 # Or handle this differently based on your needs (e.g., NaN)

df['Price'] = df['Price'].apply(clean_price)

# Convert date columns to datetime objects, handling potential errors
df['Sale Date'] = pd.to_datetime(df['Sale Date'], errors='coerce')
df['YearPermitted'] = pd.to_datetime(df['YearPermitted'], format='%Y', errors='coerce')


# Function to determine Vacant/Improved status (lots vs houses)
def determine_vacant_improved(row):
    if row['Vacant/Improved'] in ['V - VACANT', 'I - IMPROVED']:
        return row['Vacant/Improved']
    elif pd.notna(row['Sale Date']) and pd.notna(row['YearPermitted']):
        if row['Sale Date'] > row['YearPermitted']:
            return 'V - VACANT'
        else:
            return 'I - IMPROVED'
    else:
        return 'Unknown' # Or handle missing data more appropriately

df['Vacant/Improved'] = df.apply(determine_vacant_improved, axis=1)


# Group by ID and sort by Sale Date (descending for TimeDiff/PriceDiff calculation)
df = df.sort_values(by=['ID', 'Sale Date'], ascending=[True, False]).reset_index(drop=True)


# Function to calculate price & time differences and assign labels (simplified and improved)
def calculate_diffs_and_labels(group):
    # Calculate PriceDiff (earlier - newer)
    group['PriceDiff'] = group['Price'].shift(-1) - group['Price']  # Calculate difference with the next row (which is older)
    group['PriceDiff'] = group['PriceDiff'].fillna(0) # Fill NaN with 0 for the last row

    #Calculate TimeDiff (earlier - newer) in days
    group['TimeDiff'] = (group['Sale Date'].shift(-1) - group['Sale Date']).dt.days
    group['TimeDiff'] = group['TimeDiff'].fillna(0)

    group['Label'] = ''
    for i in range(len(group) - 1):
        if group['Price'].iloc[i] != 0 and group['Price'].iloc[i+1] != 0:
            vi_prev = group['Vacant/Improved'].iloc[i+1]
            vi_curr = group['Vacant/Improved'].iloc[i]
            if 'V - VACANT' in vi_prev and 'V - VACANT' in vi_curr:
                group['Label'].iloc[i] = 'V2V'
            elif 'I - IMPROVED' in vi_prev and 'V - VACANT' in vi_curr:
                group['Label'].iloc[i] = 'I2V'
            elif 'I - IMPROVED' in vi_prev and 'I - IMPROVED' in vi_curr:
                group['Label'].iloc[i] = 'I2I'
            else:
                group['Label'].iloc[i] = 'Other'
        elif group['Price'].iloc[i] == 0 or group['Price'].iloc[i+1] == 0:
            group['Label'].iloc[i] = 'ZeroPrice'

    return group


df = df.groupby('ID').apply(calculate_diffs_and_labels).reset_index(drop=True)

#Filter to keep only relevant rows
df = df[((df['PriceDiff'] != 0) | (df.groupby('ID')['PriceDiff'].transform('count') == 1)) | (df['Label'] == 'ZeroPrice')]

# --- Modified code for generating output files with TimeDiff distribution ---

# Filter for V2V and other labels
df_v2v = df[df['Label'] == 'V2V'].copy()
df_other = df[df['Label'] != 'V2V'].copy()

# Function to create the summary data with TimeDiff distribution
def create_summary(df_label):
    # Extract the year from 'Sale Date'
    df_label['Year'] = df_label['Sale Date'].dt.year
    
    # Make TimeDiff positive
    df_label['TimeDiff'] = df_label['TimeDiff'].abs()

    # Calculate TimeDiff in years
    df_label['TimeDiffYears'] = df_label['TimeDiff'] / 365.0

    # Group by year and calculate the transaction count
    summary = df_label.groupby('Year').agg(
        TransactionCount=('ID', 'count')
    ).reset_index()

    # Function to count TimeDiff within specific ranges
    def count_time_diff_range(years, lower, upper):
        if upper is None:  # For the 10+ years case
            return years[years >= lower].count()
        else:
            return years[(years >= lower) & (years < upper)].count()

    # Add columns for TimeDiff distribution
    for i in range(1, 21):
        summary[str(i)] = summary['Year'].apply(
            lambda year: count_time_diff_range(df_label[df_label['Year'] == year]['TimeDiffYears'], i - 1, i)
        )
    summary['20plus'] = summary['Year'].apply(
        lambda year: count_time_diff_range(df_label[df_label['Year'] == year]['TimeDiffYears'], 20, None)
    )

    return summary

# Create summary for V2V
summary_v2v = create_summary(df_v2v)

# Create summary for other labels
summary_other = create_summary(df_other)

# Save the summaries to CSV files
summary_v2v.to_csv("v2v_summary.csv", index=False)
summary_other.to_csv("other_labels_summary.csv", index=False)

print("V2V summary saved to v2v_summary.csv")
print("Other labels summary saved to other_labels_summary.csv")
