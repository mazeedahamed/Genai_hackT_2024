import pandas as pd
import os

# === CONFIGURATION ===
excel1_path = "excel1.xlsx"  # Path to first Excel file
excel2_path = "excel2.xlsx"  # Path to second Excel file
output_path = "updated_excel1.xlsx"  # Output file path
sheet_name = "sheet1"  # Sheet name in both files

# Columns for comparison
columns_to_compare = ["Transactionid", "number", "name", "type", "country"]
status_column = "status"  # Column name for the existing status
new_status_column = "new_status"  # Column name for the newly assigned status

# Status labels
STATUS_CORRECT = "Correct and complete"
STATUS_INCOMPLETE = "Incomplete"
STATUS_INCORRECT = "Incorrect"
STATUS_NEW_PARTY = "New Party Incorrect"
STATUS_VALID_DROP = "Valid Drop"
STATUS_MISSING = "Missing"

try:
    # Check if files exist
    if not os.path.exists(excel1_path) or not os.path.exists(excel2_path):
        raise FileNotFoundError("One or both Excel files are missing!")

    # Load Excel files
    df1 = pd.read_excel(excel1_path, sheet_name=sheet_name)
    df2 = pd.read_excel(excel2_path, sheet_name=sheet_name)

    # Check if required columns exist
    required_columns = set(columns_to_compare + [status_column])
    if not required_columns.issubset(df1.columns) or not required_columns.issubset(df2.columns):
        raise ValueError(f"Missing required columns in one of the Excel files: {required_columns}")

    # Convert columns to string to prevent type mismatches
    for col in columns_to_compare + [status_column]:
        df1[col] = df1[col].astype(str)
        df2[col] = df2[col].astype(str)

    # Extract Transaction ID before "_"
    df1["Transactionid"] = df1["Transactionid"].apply(lambda x: x.split("_")[0] if "_" in x else x)
    df2["Transactionid"] = df2["Transactionid"].apply(lambda x: x.split("_")[0] if "_" in x else x)

    # Count occurrences in both DataFrames
    df1["occurrence_count"] = df1.groupby(columns_to_compare).cumcount() + 1
    df2["occurrence_count"] = df2.groupby(columns_to_compare).cumcount() + 1

    # Merge df1 and df2
    merged_df = df1.merge(df2, on=columns_to_compare, how="outer", suffixes=("_df1", "_df2"))

    # Function to determine new status
    def determine_new_status(row):
        if pd.isna(row["status_df1"]):  
            return STATUS_NEW_PARTY  # Exists in df2 but not in df1
        elif pd.isna(row["status_df2"]):  
            if row["status_df1"] in [STATUS_CORRECT, STATUS_INCOMPLETE]:
                return STATUS_MISSING
            elif row["status_df1"] == STATUS_INCORRECT:
                return STATUS_VALID_DROP
        return row["status_df1"]

    merged_df[new_status_column] = merged_df.apply(determine_new_status, axis=1)

    # Adjust duplicates based on occurrences
    def adjust_duplicates(group):
        excel1_count = len(group[group["status_df1"].notna()])
        excel2_count = len(group[group["status_df2"].notna()])
        
        group = group.sort_values(by="occurrence_count")

        if excel1_count > excel2_count:  
            for i in range(excel2_count, excel1_count):
                if group.iloc[i]["status_df1"] in [STATUS_CORRECT, STATUS_INCOMPLETE]:
                    group.iloc[i, group.columns.get_loc(new_status_column)] = STATUS_MISSING
                elif group.iloc[i]["status_df1"] == STATUS_INCORRECT:
                    group.iloc[i, group.columns.get_loc(new_status_column)] = STATUS_VALID_DROP

        elif excel2_count > excel1_count:  
            for i in range(excel1_count, excel2_count):
                group.iloc[i, group.columns.get_loc(new_status_column)] = STATUS_NEW_PARTY
        
        return group

    merged_df = merged_df.groupby(columns_to_compare, group_keys=False).apply(adjust_duplicates)

    # Drop unnecessary columns
    merged_df.drop(columns=["occurrence_count"], inplace=True)

    # Save the updated file
    merged_df.to_excel(output_path, index=False)
    print(f"✅ Updated Excel saved as: {output_path}")

except FileNotFoundError as e:
    print(f"❌ Error: {e}")

except ValueError as e:
    print(f"❌ Error: {e}")

except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
