import pandas as pd
import os

# 🟢 Define file paths & sheet names
excel1_path = 'path_to_excel1.xlsx'  # 🔹 Path to Excel1
excel2_path = 'path_to_excel2.xlsx'  # 🔹 Path to Excel2
output_path = 'updated_excel1.xlsx'  # 🔹 Output file name

sheet1_name = 'Sheet1'  # 🔹 Sheet name in Excel1
sheet2_name = 'Sheet2'  # 🔹 Sheet name in Excel2
output_sheet_name = 'Updated_Status'  # 🔹 Sheet name for the output

# 🟢 Column mappings (Change as needed)
id_col1 = 'ID'              # 🔹 ID column in Excel1
status_col1 = 'Status'      # 🔹 Status column in Excel1
status_col2 = 'Status'      # 🔹 Status column in Excel2
new_status_col = 'Status_excel2'  # 🔹 New column for updated status

# 🟢 Columns to concatenate in Excel2 for generating 'ID'
id_parts = ['TransactionID', 'Name', 'Submitter']

try:
    # 🟢 Validate file existence
    if not os.path.exists(excel1_path):
        raise FileNotFoundError(f"❌ File not found: {excel1_path}")
    if not os.path.exists(excel2_path):
        raise FileNotFoundError(f"❌ File not found: {excel2_path}")

    # 🟢 Load Excel files
    excel1 = pd.read_excel(excel1_path, sheet_name=sheet1_name)
    excel2 = pd.read_excel(excel2_path, sheet_name=sheet2_name)

    # 🟢 Validate required columns
    missing_cols1 = [col for col in [id_col1, status_col1] if col not in excel1.columns]
    missing_cols2 = [col for col in id_parts + [status_col2] if col not in excel2.columns]

    if missing_cols1:
        raise KeyError(f"❌ Missing columns in Excel1: {missing_cols1}")
    if missing_cols2:
        raise KeyError(f"❌ Missing columns in Excel2: {missing_cols2}")

    # 🟢 Trim whitespace and convert ID to string in Excel1
    excel1[id_col1] = excel1[id_col1].astype(str).str.strip()

    # 🟢 Create ID column in Excel2 by combining three columns, handling NaN values
    excel2[id_col1] = excel2[id_parts].fillna("").astype(str).agg('-'.join, axis=1).str.strip()

    # 🟢 Handle duplicate statuses in Excel2 (Add 'Duplicate-' prefix for second occurrence)
    excel2.loc[:, status_col2] = excel2.groupby(id_col1)[status_col2].transform(lambda x: x.mask(x.duplicated(keep='first'), 'Duplicate-' + x))

    # 🟢 Merge Excel1 with Excel2 based on ID (Retain all original Excel1 columns)
    merged = pd.merge(excel1, excel2[[id_col1, status_col2]], on=id_col1, how='left')

    # 🟢 Add new status column to Excel1's structure
    merged[new_status_col] = merged[status_col2].fillna('Missing')

    # 🟢 Drop the temporary column from Excel2
    merged.drop(columns=[status_col2], inplace=True)

    # 🟢 Identify IDs from Excel2 that are **not in Excel1** (Additional Records)
    additional_records = excel2[~excel2[id_col1].isin(excel1[id_col1])].copy()

    if not additional_records.empty:
        additional_records[new_status_col] = additional_records[status_col2] + ' - Additional'  # Mark them as additional
        additional_records.drop(columns=[status_col2], inplace=True)  # Remove original status column

        # 🟢 Add missing columns to match Excel1 structure
        for col in excel1.columns:
            if col not in additional_records:
                additional_records[col] = None  # Fill missing columns with NaN

        # 🟢 Arrange columns in the same order as Excel1 + new status column
        additional_records = additional_records[excel1.columns.tolist() + [new_status_col]]

        # 🟢 Append additional records to the final dataset
        merged = pd.concat([merged, additional_records], ignore_index=True)

    # 🟢 Save the final data to a new Excel file with the same structure as Excel1
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        merged.to_excel(writer, sheet_name=output_sheet_name, index=False)

    print(f"✅ Excel file '{output_path}' updated successfully with new column '{new_status_col}'!")

except FileNotFoundError as e:
    print(e)
except KeyError as e:
    print(f"❌ Column Error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
