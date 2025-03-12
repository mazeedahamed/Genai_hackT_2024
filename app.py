import pandas as pd

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

# Merge based on group_by_columns and occurrence
merged = df1.merge(df2, on=group_by_columns + ['occurrence'], how='left', suffixes=('', '_ai'))

# Add ai_response_parties column
merged['ai_response_parties'] = merged['party name']
merged.loc[merged['party name_ai'].isna(), 'ai_response_parties'] = ''

# Find unmatched records in df2
df2_unmatched = df2[~df2.set_index(group_by_columns + ['occurrence']).index.isin(df1.set_index(group_by_columns + ['occurrence']).index)]

# Append unmatched records
new_rows = pd.DataFrame(columns=df1.columns)
new_rows = new_rows.append(df2_unmatched.rename(columns={'party name': 'ai_response_parties'}), ignore_index=True)

final_df = pd.concat([merged, new_rows], ignore_index=True)
final_df.drop(columns=['occurrence'], inplace=True)

# Save output to Excel
final_df.to_excel("merged_output.xlsx", index=False)

