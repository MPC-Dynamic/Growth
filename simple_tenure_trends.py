import pandas as pd
import matplotlib.pyplot as plt

def read_and_filter_data(file_path):
    # Read the CSV file
    data = pd.read_csv(file_path)

    # Convert relevant columns to datetime and numeric types
    data['Exit_Date'] = pd.to_datetime(data['Exit_Date'], format='%m/%d/%Y', errors='coerce')
    data['Year'] = data['Exit_Date'].dt.year

    # Filter out durations less than one year
    filtered_data = data[data['Duration'] >= 1.0]
    return filtered_data

def analyze_and_plot_trends(data):
    neighborhoods = data['Type'].unique()

    for neighborhood in neighborhoods:
        # Filter data for the neighborhood
        neighborhood_data = data[data['Type'] == neighborhood].copy()
        if len(neighborhood_data) < 5:  # Skip if insufficient data for analysis
            continue

        # Ensure 'Year' is integer
        neighborhood_data['Year'] = neighborhood_data['Year'].astype(int)

        # Prepare the time series and handle duplicates
        series = neighborhood_data.groupby('Year')['Duration'].mean()  # Aggregate by mean for duplicates
        series = series.sort_index().reindex(range(series.index.min(), series.index.max() + 1), fill_value=None)
        series = series.interpolate(method='linear')  # Fill missing values

        # Calculate rolling average to smooth the data
        rolling_avg = series.rolling(window=3, center=True).mean()

        # Plot trend
        plt.figure(figsize=(10, 6))
        plt.plot(series.index, series.values, label='Original Data', marker='o')
        plt.plot(rolling_avg.index, rolling_avg.values, label='Rolling Average (3-Year)', linestyle='--', color='red')
        plt.title(f'Trend Analysis for {neighborhood}')
        plt.xlabel('Year')
        plt.ylabel('Median Duration')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    # File path to the input CSV
    file_path = "ee_neihborhoods.csv"  
    

    # Read and filter data
    filtered_data = read_and_filter_data(file_path)

    # Analyze and plot trends
    analyze_and_plot_trends(filtered_data)
