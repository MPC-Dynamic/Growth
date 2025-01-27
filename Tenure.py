import pandas as pd
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

# Load data from csv file
df = pd.read_csv('ee.csv')

# Convert Entrance_Date and Exit_Date to datetime, handling errors properly
df['Entrance_Date'] = pd.to_datetime(df['Entrance_Date'], errors='coerce')
df['Exit_Date'] = pd.to_datetime(df['Exit_Date'], errors='coerce')

# Calculate Tenure_Days, handling NaT in Exit_Date
latest_entry_date = df['Entrance_Date'].max()
df['Tenure_Days'] = (df['Exit_Date'].fillna(latest_entry_date) - df['Entrance_Date']).dt.days

# Create Event column
df['Event'] = df['Exit_Date'].notnull().astype(int)

# Group by 'Type' and perform survival analysis for each type
types = df['Type'].unique()

summary_data = []

# Initialize storage for statistical test results
stat_test_results = []

for type in types:
    # Filter data for the current type
    type_df = df[df['Type'] == type]
    
    # Create Kaplan-Meier estimator
    kmf = KaplanMeierFitter()
    
    # Fit the model
    kmf.fit(type_df['Tenure_Days'], event_observed=type_df['Event'], label=f'Type {type}')
    
    # Plot the survival curve
    plt.figure(figsize=(10, 6))
    kmf.plot()
    plt.xlabel("Tenure (Days)")
    plt.ylabel("Survival Probability")
    plt.title(f"Kaplan-Meier Estimate of Survival Probability for Type {type}")
    plt.grid(True)
    plt.show()
    
    # Analyze the survival curve for critical years
    print(f"\nSurvival Function for Type {type}:")
    print(kmf.survival_function_)
    
    # Calculate median survival time
    median_survival_time = kmf.median_survival_time_
    median_survival_time_years = median_survival_time / 365 if median_survival_time else None
    print(f"Median Survival Time for Type {type}:", median_survival_time, "days or in years:", median_survival_time_years)
    
    # Calculate survival probability at specific times
    specific_times = [30, 60, 90, 180, 365]  # days
    survival_probabilities = kmf.survival_function_at_times(specific_times)
    print(f"Survival Probabilities at Specific Times for Type {type}:")
    for time, probability in zip(specific_times, survival_probabilities.values):
        print(f"Day {time}: {probability:.4f}")

    # Add summary data for this type
    summary_data.append({
        "Type": type,
        "Median Survival Time (days)": median_survival_time,
        "Median Survival Time (years)": median_survival_time_years,
        "Survival Probabilities at 30 days": survival_probabilities.loc[30] if 30 in survival_probabilities.index else None,
        "Survival Probabilities at 365 days": survival_probabilities.loc[365] if 365 in survival_probabilities.index else None,
    })

# Perform pairwise statistical tests for differences in survival between types
for i, type1 in enumerate(types):
    for j, type2 in enumerate(types):
        if i < j:
            type1_df = df[df['Type'] == type1]
            type2_df = df[df['Type'] == type2]

            # Perform log-rank test
            results = logrank_test(
                type1_df['Tenure_Days'], type2_df['Tenure_Days'],
                event_observed_A=type1_df['Event'], event_observed_B=type2_df['Event']
            )

            stat_test_results.append({
                "Type1": type1,
                "Type2": type2,
                "p-value": results.p_value,
                "Test Statistic": results.test_statistic
            })

# If you want to plot all types in one graph for comparison
plt.figure(figsize=(12, 8))
for type in types:
    type_df = df[df['Type'] == type]
    kmf = KaplanMeierFitter()
    #kmf.fit(type_df['Tenure_Days'], event_observed=type_df['Event'], label=f'Type {type}')
    kmf.fit(type_df['Tenure_Days'], event_observed=type_df['Event'], label=f'{type}')
    kmf.plot()

plt.xlabel("Tenure (Days)")
plt.ylabel("Survival Probability")
#plt.title("Kaplan-Meier Estimates for All Types")
plt.title("Kaplan-Meier Estimates for All Neighborhoodss")
plt.legend()
plt.grid(True)
plt.show()

# Display summary table
summary_df = pd.DataFrame(summary_data)
print("\nSummary of Kaplan-Meier Analysis:")
print(summary_df)

# Display statistical test results
stat_test_df = pd.DataFrame(stat_test_results)
print("\nStatistical Test Results (Log-Rank Test):")
print(stat_test_df)
