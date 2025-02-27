import pandas as pd
import os

# === CONFIGURATION ===
excel1_path = "excel1.xlsx"
excel2_path = "excel2.xlsx"
output_path = "updated_excel1.xlsx"
sheet_name = "sheet1"

# Columns for comparison
columns_to_compare = ["Transactionid", "number", "name", "type", "country"]
status_column = "status"
new_status_column = "new_status"

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

    # Convert columns to string to prevent type mismatches
    for col in columns_to_compare + [status_column]:
        df1[col] = df1[col].astype(str)
        df2[col] = df2[col].astype(str)

    # Extract Transaction ID before "_"
    df1["Transactionid"] = df1["Transactionid"].apply(lambda x: x.split("_")[0] if "_" in x else x)
    df2["Transactionid"] = df2["Transactionid"].apply(lambda x: x.split("_")[0] if "_" in x else x)

    # Count occurrences of each unique record in both DataFrames
    df1["count_df1"] = df1.groupby(columns_to_compare)["Transactionid"].transform("count")
    df2["count_df2"] = df2.groupby(columns_to_compare)["Transactionid"].transform("count")

    # Merge both DataFrames on key columns
    merged_df = df1.merge(df2, on=columns_to_compare, how="outer", suffixes=("_df1", "_df2"), indicator=True)

    # Initialize new_status column
    merged_df[new_status_column] = merged_df[status_column].copy()

    # Process each row
    for index, row in merged_df.iterrows():
        count_df1 = row.get("count_df1", 0) if not pd.isna(row.get("count_df1", 0)) else 0
        count_df2 = row.get("count_df2", 0) if not pd.isna(row.get("count_df2", 0)) else 0
        status_df1 = row.get("status_df1")

        if count_df2 > count_df1:
            # If df2 has more occurrences than df1, mark the extra ones as "New Party Incorrect"
            if count_df1 > 0:
                merged_df.at[index, new_status_column] = status_df1  # Keep original status for occurrences in df1
            else:
                merged_df.at[index, new_status_column] = STATUS_NEW_PARTY  # Extra occurrences in df2

        elif count_df1 > count_df2:
            # If df1 has more occurrences than df2, handle the extra ones
            if count_df2 > 0:
                merged_df.at[index, new_status_column] = status_df1  # Keep original status for occurrences in df2
            else:
                if status_df1 in [STATUS_CORRECT, STATUS_INCOMPLETE]:
                    merged_df.at[index, new_status_column] = STATUS_MISSING
                elif status_df1 == STATUS_INCORRECT:
                    merged_df.at[index, new_status_column] = STATUS_VALID_DROP

    # Drop helper columns
    merged_df.drop(columns=["count_df1", "count_df2"], inplace=True, errors="ignore")

    # Save the updated file
    merged_df.to_excel(output_path, index=False)
    print(f"✅ Updated Excel saved as: {output_path}")

except FileNotFoundError as e:
    print(f"❌ Error: {e}")

except ValueError as e:
    print(f"❌ Error: {e}")

except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
