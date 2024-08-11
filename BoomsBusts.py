### using Gaussian Filtering, local maxima & contour line to find peaks and throughs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.ndimage import gaussian_filter1d

def analyze_housing_data(file_path, is_monthly=True):
    # Load the data
    df = pd.read_csv(file_path)
    
    # Convert DATE to datetime
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    # Set DATE as index
    df.set_index('DATE', inplace=True)
    
    # Rename the column in  for easier reference
    df = df.rename(columns={'PERMITNSA_20240724': 'Value'})
    
    # Convert Value column to numeric, replacing '.' with NaN
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    
    # Drop NaN values
    df = df.dropna()
    
    if is_monthly:
        # For monthly data, use a combination of rolling mean and Gaussian filter
        df['Smoothed'] = df['Value'].rolling(window=12, center=True).mean()
        df['Smoothed'] = gaussian_filter1d(df['Smoothed'], sigma=6)
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

# Usage
analyze_housing_data('Monthly.csv', is_monthly=True)
# or
# analyze_housing_data('Annual.csv', is_monthly=False)
