### using Gaussian Filtering, local maxima & contour line to find peaks and throughs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.ndimage import gaussian_filter1d
import os

def analyze_housing_data(file_path, is_monthly=True):
    # Load the data
    df = pd.read_csv(file_path)
    
    # Identify date and value columns
    date_col = df.columns[0]  # Assuming the first column is always the date
    value_col = df.columns[1]  # Assuming the second column is always the value
    
    # Convert date to datetime
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Set date as index
    df.set_index(date_col, inplace=True)
    
    # Rename the value column for consistency
    df = df.rename(columns={value_col: 'Value'})
    
    # Convert Value column to numeric, replacing non-numeric values with NaN
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    
    # Drop NaN values
    df = df.dropna()
    
    if is_monthly:
        # Apply centered rolling mean
        df['Smoothed'] = df['Value'].rolling(window=12, center=True).mean()
        
        # Apply non-centered rolling mean for the last 6 months
        last_6_months = df['Value'].rolling(window=12, min_periods=1).mean().iloc[-6:]
        df.loc[last_6_months.index, 'Smoothed'] = last_6_months
        
        # Pad the data for Gaussian filtering
        pad_width = 50  # Adjust as needed
        padded_data = np.pad(df['Smoothed'].dropna(), (pad_width, pad_width), mode='edge')
        
        # Apply Gaussian filter
        smoothed_padded = gaussian_filter1d(padded_data, sigma=6)
        
        # Remove padding and ensure the length matches the original data
        smoothed_data = smoothed_padded[pad_width:pad_width+len(df)]
        df['Smoothed'] = smoothed_data
    else:
        # For annual data, use Gaussian filter
        df['Smoothed'] = gaussian_filter1d(df['Value'], sigma=1)
    
    # Plot original and smoothed data
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Value'], label='Original Data')
    plt.plot(df.index, df['Smoothed'], label='Smoothed Data')
    plt.title('Housing Units Authorized - Original vs Smoothed')
    plt.legend()
    plt.show()
    
    # Find peaks and troughs
    if is_monthly:
        peak_distance = 24  # 2 years for monthly
        prominence = 0.05 * (df['Smoothed'].max() - df['Smoothed'].min())
    else:
        peak_distance = 2  # 2 data points for annual
        prominence = 0.1 * (df['Smoothed'].max() - df['Smoothed'].min())
    
    peaks, _ = signal.find_peaks(df['Smoothed'], distance=peak_distance, prominence=prominence)
    troughs, _ = signal.find_peaks(-df['Smoothed'], distance=peak_distance, prominence=prominence)
    
    # Plot peaks and troughs
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Smoothed'])
    plt.plot(df.index[peaks], df['Smoothed'].iloc[peaks], "x", label='Peaks')
    plt.plot(df.index[troughs], df['Smoothed'].iloc[troughs], "o", label='Troughs')
    plt.title('Identified Peaks and Troughs')
    plt.legend()
    plt.show()
    
    # Analyze booms and busts
    extrema = np.sort(np.concatenate((peaks, troughs)))
    
    for i in range(1, len(extrema)):
        start = extrema[i-1]
        end = extrema[i]
        change = (df['Smoothed'].iloc[end] - df['Smoothed'].iloc[start]) / df['Smoothed'].iloc[start] * 100
        
        if change > 0:
            print(f"Boom from {df.index[start].date()} to {df.index[end].date()}: {change:.2f}% increase")
        else:
            print(f"Bust from {df.index[start].date()} to {df.index[end].date()}: {-change:.2f}% decrease")
    
    # Create a column for peaks and troughs
    df['PeaksTroughs'] = 0
    df.loc[df.index[peaks], 'PeaksTroughs'] = 1  # Mark peaks
    df.loc[df.index[troughs], 'PeaksTroughs'] = -1  # Mark troughs
    
    # Export the data
    output_file = os.path.splitext(file_path)[0] + '_processed.csv'
    df.to_csv(output_file, columns=['Value', 'Smoothed', 'PeaksTroughs'])
    print(f"Processed data saved to {output_file}")

# Usage
#analyze_housing_data('MonthlyTV.csv', is_monthly=True)
analyze_housing_data('Monthly.csv', is_monthly=True)
# or
#analyze_housing_data('AnnualTV.csv', is_monthly=False)
# analyze_housing_data('Annual.csv', is_monthly=False)
