import pandas as pd

# Path to your Excel file
file_path = 'Financial Calculations 2025-26.xlsx'

# Load all sheets into a dictionary
sheets = pd.read_excel(file_path, sheet_name=None)

# Access each sheet by name
take_home_df = sheets['1. Take home + deductions']
bills_df = sheets['2. Bills']
food_df = sheets['3. Food']
luxury_df = sheets['4. Luxury items']

# Print the first few rows of each sheet
print("Take Home + Deductions:")
print(take_home_df.head())
print("\nBills:")
print(bills_df.head())
print("\nFood:")
print(food_df.head())
print("\nLuxury Items:")
print(luxury_df.head())