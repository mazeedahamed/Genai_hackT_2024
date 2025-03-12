import pandas as pd
from datetime import datetime

# Define sheet names and file paths
sheet_name_excel1 = "Consolidated_data"  # Update if needed
sheet_name_excel2 = "Sheet1"  # Update if needed
excel1_path = "resources/Ground_Truth.xlsx"  # Path to GT_Excel
excel2_path = "resources/Execution_Results.xlsx"

# Define columns to compare
columns_to_compare_1 = ["Account_ID", "Party_Name", "Type"]
columns_to_compare_2 = ["Account_ID", "Party_Name_AI", "Type"]
status_column = "Status"
new_status_column = "new_status"
comments_column = "Feedback"

# Status labels
STATUS_CORRECT = "correct and complete"
STATUS_INCOMPLETE = "incomplete"
STATUS_INCORRECT = "incorrect"
STATUS_NEW_PARTY = "New Party Incorrect"
STATUS_VALID_DROP = "Valid Drop"
STATUS_MISSING = "Missing"

# Function to trim and lowercase all string columns
def trim_all_string_columns(df):
    string_columns = df.select_dtypes(include=["object"]).columns
    df[string_columns] = df[string_columns].apply(lambda x: x.str.strip().str.lower())
    return df

try:
    # Load Excel files
    df1 = pd.read_excel(excel1_path, sheet_name=sheet_name_excel1, dtype=str)
    df1 = trim_all_string_columns(df1)

    df2 = pd.read_excel(excel2_path, sheet_name=sheet_name_excel2, dtype=str)
    df2 = trim_all_string_columns(df2)

    # Ensure required columns exist
    required_columns = set(columns_to_compare_1 + [status_column])
    missing_columns_df1 = required_columns - set(df1.columns)
    missing_columns_df2 = set(columns_to_compare_2) - set(df2.columns)

    if missing_columns_df1:
        raise ValueError(f"Missing columns in df1: {missing_columns_df1}")
    if missing_columns_df2:
        raise ValueError(f"Missing columns in df2: {missing_columns_df2}")

    # Fill missing values with "NA"
    df1.fillna("NA", inplace=True)
    df2.fillna("NA", inplace=True)

    # Priority mapping for sorting
    priority_order = {
        STATUS_CORRECT: 1,
        STATUS_INCOMPLETE: 2,
        STATUS_INCORRECT: 3
    }

    # Store original indexes
    df1["original_index"] = df1.index

    # Assign priority values
    df1["priority"] = df1["Status"].map(priority_order).fillna(float("inf"))
    df1 = df1.sort_values(by=columns_to_compare_1 + ["priority"])

    # Assign occurrence numbers
    df1["occurrence"] = df1.groupby(columns_to_compare_1).cumcount() + 1
    df2["occurrence"] = df2.groupby(columns_to_compare_2).cumcount() + 1

    # Restore original sorting
    df1 = df1.sort_values(by="original_index").drop(columns=["original_index"])

    # Rename 'Party_Name' in df2 to 'Party_Name_AI' for merging
    df2 = df2.rename(columns={"Party_Name": "Party_Name_AI"})

    # Merge based on Account_ID, Type, and occurrence
    merged_df = df1.merge(df2, on=["Account_ID", "Type", "occurrence"], how="left")

    # Find unmatched records in df2 (entries that don't exist in df1)
    unmatched_records = df2[
        ~df2.set_index(columns_to_compare_2 + ["occurrence"]).index.isin(
            df1.set_index(columns_to_compare_1 + ["occurrence"]).index
        )
    ]

    # Append unmatched records under 'Party_Name_AI' with empty 'Party_Name'
    new_rows = []
    for account, group in unmatched_records.groupby("Account_ID"):
        # Add an empty separator row for clarity
        new_rows.append(pd.DataFrame([[account] + [""] * (len(df1.columns) - 1)], columns=df1.columns))

        # Append only to 'Party_Name_AI'
        new_group = group[["Account_ID", "Party_Name_AI", "Type"]]
        new_group.insert(1, "Party_Name", "")  # Keep 'Party_Name' empty
        new_group = new_group.reindex(columns=df1.columns, fill_value="")  # Ensure column alignment
        new_rows.append(new_group)

    # Combine unmatched records
    new_rows_df = pd.concat(new_rows, ignore_index=True) if new_rows else pd.DataFrame(columns=df1.columns)

    # Combine merged data with newly formatted unmatched records
    final_df = pd.concat([merged_df, new_rows_df], ignore_index=True).drop(columns=["occurrence"])

    # Save output with a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"merged_output_{timestamp}.xlsx"
    final_df.to_excel(output_filename, index=False)

    print(f"File saved as: {output_filename}")

except FileNotFoundError as e:
    print(f"Error: {e}")
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
