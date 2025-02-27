import pandas as pd
import os

# Define file paths (update as needed)
excel1_path = "excel1.xlsx"
excel2_path = "excel2.xlsx"
output_path = "updated_excel1.xlsx"
sheet_name = "sheet1"  # Update if needed

# Define columns to compare
columns_to_compare = ["Transactionid", "number", "name", "type", "country"]

try:
    # Check if files exist
    if not os.path.exists(excel1_path) or not os.path.exists(excel2_path):
        raise FileNotFoundError("One or both Excel files are missing!")

    # Load Excel files
    df1 = pd.read_excel(excel1_path, sheet_name=sheet_name)
    df2 = pd.read_excel(excel2_path, sheet_name=sheet_name)

    # Check if required columns exist
    required_columns = set(columns_to_compare + ["status"])
    if not required_columns.issubset(df1.columns) or not required_columns.issubset(df2.columns):
        raise ValueError(f"Missing required columns in one of the Excel files: {required_columns}")

    # Convert columns to string to prevent type mismatches
    for col in columns_to_compare + ["status"]:
        df1[col] = df1[col].astype(str)
        df2[col] = df2[col].astype(str)

    # Extract Transaction ID before "_"
    df1["Transactionid"] = df1["Transactionid"].apply(lambda x: x.split("_")[0] if "_" in x else x)
    df2["Transactionid"] = df2["Transactionid"].apply(lambda x: x.split("_")[0] if "_" in x else x)

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
    df1.to_excel(output_path, index=False)
    print(f"✅ Updated Excel saved as: {output_path}")

except FileNotFoundError as e:
    print(f"❌ Error: {e}")

except ValueError as e:
    print(f"❌ Error: {e}")

except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
