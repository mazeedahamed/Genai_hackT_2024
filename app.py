import pandas as pd
from datetime import datetime

# Load Excel files
excel1_path = "excel1.xlsx"  # Update with actual path
excel2_path = "excel2.xlsx"  # Update with actual path

df1 = pd.read_excel(excel1_path)
df2 = pd.read_excel(excel2_path)

# Define columns to group by (externalized for flexibility)
group_by_columns = ['account no', 'party name']  # Modify as needed

# Count occurrences for proper mapping
df1['occurrence'] = df1.groupby(group_by_columns).cumcount()
df2['occurrence'] = df2.groupby(group_by_columns).cumcount()

# Merge based on account number, party name, and occurrence
merged = df1.merge(df2, on=group_by_columns + ['occurrence'], how='left', suffixes=('', '_ai'))

# Add ai_response_parties column
merged['ai_response_parties'] = merged['party name_ai'].fillna('')

# Find unmatched records in df2 per account
unmatched_records = df2[~df2.set_index(group_by_columns + ['occurrence']).index.isin(df1.set_index(group_by_columns + ['occurrence']).index)]

# Group unmatched records by account and append them under the respective account
new_rows = []

for account, group in unmatched_records.groupby('account no'):
    new_rows.append(pd.DataFrame([[account] + [''] * (len(df1.columns) - 1)], columns=df1.columns))  # Empty separator row
    new_group = group.rename(columns={'party name': 'ai_response_parties'})[['account no', 'ai_response_parties']]
    new_group = new_group.reindex(columns=df1.columns, fill_value='')
    new_rows.append(new_group)

new_rows_df = pd.concat(new_rows, ignore_index=True) if new_rows else pd.DataFrame(columns=df1.columns)

# Combine merged data with newly formatted unmatched records
final_df = pd.concat([merged, new_rows_df], ignore_index=True).drop(columns=['occurrence'])

# Save output with a timestamped filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"merged_output_{timestamp}.xlsx"
final_df.to_excel(output_filename, index=False)

print(f"File saved as: {output_filename}")
