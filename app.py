import pandas as pd
from datetime import datetime

# Load Excel files
excel1_path = "excel1.xlsx"  # Update with actual path
excel2_path = "excel2.xlsx"  # Update with actual path

df1 = pd.read_excel(excel1_path)
df2 = pd.read_excel(excel2_path)

# Define columns to group by
group_by_columns = ['account no', 'party name']

# Count occurrences for proper mapping
df1['occurrence'] = df1.groupby(group_by_columns).cumcount()
df2['occurrence'] = df2.groupby(group_by_columns).cumcount()

# Rename 'party name' in df2 to 'party name_ai' to differentiate it after merging
df2 = df2.rename(columns={'party name': 'party name_ai'})

# Merge based on account number, party name, and occurrence
merged = df1.merge(df2, on=['account no', 'party name', 'occurrence'], how='left')

# Find unmatched records in df2 (entries that don’t exist in df1)
unmatched_records = df2[~df2.set_index(['account no', 'party name_ai', 'occurrence']).index.isin(
    df1.set_index(['account no', 'party name', 'occurrence']).index)]

# Append unmatched records **only under 'party name_ai'** while keeping 'party name' empty
new_rows = []
for account, group in unmatched_records.groupby('account no'):
    # Add empty separator row for clarity
    new_rows.append(pd.DataFrame([[account] + [''] * (len(df1.columns) - 1)], columns=df1.columns))
    
    # Append only to 'party name_ai'
    new_group = group[['account no', 'party name_ai']]
    new_group.insert(1, 'party name', '')  # Keep 'party name' empty
    new_group = new_group.reindex(columns=df1.columns, fill_value='')  # Ensure column alignment
    new_rows.append(new_group)

# Concatenate unmatched records
new_rows_df = pd.concat(new_rows, ignore_index=True) if new_rows else pd.DataFrame(columns=df1.columns)

# Combine merged data with newly formatted unmatched records
final_df = pd.concat([merged, new_rows_df], ignore_index=True).drop(columns=['occurrence'])

# Save output with a timestamped filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"merged_output_{timestamp}.xlsx"
final_df.to_excel(output_filename, index=False)

print(f"File saved as: {output_filename}")
