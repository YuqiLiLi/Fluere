import pandas as pd

# Read the CSV files into DataFrames
data_original = pd.read_csv('traffic_data_without.csv')
data_modified = pd.read_csv('traffic_data.csv')

# Ensure both DataFrames have the same columns
if not data_original.columns.equals(data_modified.columns):
    raise ValueError("Column names differ between the two CSV files.")

# Calculate average speed and average occupancy for both datasets
avg_speed_original = data_original['Speed'].mean()
avg_occupancy_original = data_original['Occupancy'].mean()

avg_speed_modified = data_modified['Speed'].mean()
avg_occupancy_modified = data_modified['Occupancy'].mean()

# Calculate percentage increase in average speed and average occupancy
speed_increase_percent = ((avg_speed_modified - avg_speed_original) / avg_speed_original) * 100
occupancy_increase_percent = ((avg_occupancy_modified - avg_occupancy_original) / avg_occupancy_original) * 100

# Print the results
print("Comparison between 'traffic_data_without.csv' (original) and 'traffic_data.csv' (modified):")
print("\nAverage Speed:")
print("Original:", avg_speed_original)
print("Modified:", avg_speed_modified)
print("Percentage increase:", speed_increase_percent, "%")

print("\nAverage Occupancy:")
print("Original:", avg_occupancy_original)
print("Modified:", avg_occupancy_modified)
print("Percentage increase:", occupancy_increase_percent, "%")
