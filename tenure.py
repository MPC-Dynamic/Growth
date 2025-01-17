import pandas as pd

def process_sales_data(csv_file, specified_date):
    # Load the CSV file
    df = pd.read_csv(csv_file)
    
    # Convert the date columns to datetime format
    df['purchase_date'] = pd.to_datetime(df['purchase_date'])
    df['sale_date'] = pd.to_datetime(df['sale_date'], errors='coerce')
    
    # Filter the data based on the specified date
    filtered_df = df[(df['purchase_date'] <= specified_date) & ((df['sale_date'] >= specified_date) | (df['sale_date'].isnull()))]
    
    # Replace 'none' with the specified date
    filtered_df['sale_date'] = filtered_df['sale_date'].fillna(pd.to_datetime(specified_date))
    
    # Calculate the holding time in years
    filtered_df['holding_time'] = (filtered_df['sale_date'] - filtered_df['purchase_date']).dt.days / 365
    
    # Round the holding time to the nearest whole number
    filtered_df['holding_time'] = filtered_df['holding_time'].apply(lambda x: round(x))
    
    # Count the number of items held for each year
    holding_time_counts = filtered_df['holding_time'].value_counts().sort_index()
    
    return holding_time_counts

# Example usage
csv_file = 'Sales.csv'
specified_date = '2021-01-01'
holding_time_counts = process_sales_data(csv_file, specified_date)
print(holding_time_counts)
