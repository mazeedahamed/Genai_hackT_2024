import pandas as pd

# Define file paths (update as needed)
excel1_path = "excel1.xlsx"
excel2_path = "excel2.xlsx"
sheet_name = "sheet1"  # Update if needed

# Define columns to compare
columns_to_compare = ["Transactionid", "number", "name", "type", "country"]

# Load Excel files
df1 = pd.read_excel(excel1_path, sheet_name=sheet_name)
df2 = pd.read_excel(excel2_path, sheet_name=sheet_name)

# Extract Transaction ID before "_"
df1["Transactionid"] = df1["Transactionid"].astype(str).apply(lambda x: x.split("_")[0])
df2["Transactionid"] = df2["Transactionid"].astype(str).apply(lambda x: x.split("_")[0])

# Count occurrences in both DataFrames
df1["count"] = df1.groupby(columns_to_compare)["Transactionid"].transform("count")
df2["count"] = df2.groupby(columns_to_compare)["Transactionid"].transform("count")

# Create a dictionary of (key: status) mapping from Excel1
df1_dict = df1.set_index(columns_to_compare)["status"].to_dict()

# Initialize new_status column
df1["new_status"] = ""

# Process each row in df1
for index, row in df1.iterrows():
    key = tuple(row[col] for col in columns_to_compare)
    
    if key in df1_dict:
        status = df1_dict[key]
        occurrences_in_1 = df1[df1[columns_to_compare].apply(tuple, axis=1) == key].shape[0]
        occurrences_in_2 = df2[df2[columns_to_compare].apply(tuple, axis=1) == key].shape[0]

        if occurrences_in_1 > occurrences_in_2:
            # More occurrences in Excel1
            if index < occurrences_in_2:
                df1.at[index, "new_status"] = status
            else:
                df1.at[index, "new_status"] = "Missing" if status in ["Correct and complete", "Incomplete"] else "Valid Drop"
        else:
            df1.at[index, "new_status"] = status

# Identify new entries in Excel2 that are not in Excel1
new_entries = df2[~df2.set_index(columns_to_compare).index.isin(df1.set_index(columns_to_compare).index)].copy()
new_entries["new_status"] = "New Party Incorrect"

# Append new rows to df1
df1 = pd.concat([df1, new_entries], ignore_index=True)

# Drop helper column
df1.drop(columns=["count"], inplace=True)

# Save the updated file
output_path = "updated_excel1.xlsx"
df1.to_excel(output_path, index=False)

print(f"Updated Excel saved as: {output_path}")
