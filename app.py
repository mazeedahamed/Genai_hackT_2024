comment_groups = {
    "Clients of Client": ["client-1", "client-2"],
    "Direct Part": ["direct-1", "direct-2"],
    "Manager": ["manager-1", "manager-2"],
    "Supervisor": ["sup-1", "sup-2", "sup-3"],
    "Team Lead": ["lead-1", "lead-2"]
}

def generate_summary(df, comment_groups):
    """
    Generate a summary report based on new_status and grouped comment categories.
    """
    # Group by 'number' and count occurrences of different statuses
    summary = df.groupby("number")[new_status_column].value_counts().unstack().fillna(0)

    # Rename columns for readability
    summary = summary.rename(columns={
        STATUS_CORRECT: "Correct and Complete",
        STATUS_INCOMPLETE: "Incomplete",
        STATUS_INCORRECT: "Incorrect",
        STATUS_NEW_PARTY: "New Party Incorrect",
        STATUS_VALID_DROP: "Valid Drop",
        STATUS_MISSING: "Missing"
    })

    # Add missing status columns (if not present)
    for status in ["Correct and Complete", "Incomplete", "Incorrect", "New Party Incorrect", "Valid Drop", "Missing"]:
        if status not in summary.columns:
            summary[status] = 0

    # Initialize grouped comment-based counts
    for category in comment_groups.keys():
        summary[category] = 0

    # Count occurrences based on comment groups
    for category, keywords in comment_groups.items():
        regex_pattern = "|".join(keywords)  # Combine all keywords into a regex OR pattern
        filtered_df = df[(df[new_status_column] == STATUS_INCORRECT) & (df[comments_column].str.contains(regex_pattern, na=False, case=False))]
        comment_counts = filtered_df.groupby("number")[comments_column].count()
        summary[category] = summary.index.map(comment_counts).fillna(0).astype(int)

    return summary.reset_index()


====================

    # Drop unnecessary columns
    merged_df.drop(columns=["_merge"], inplace=True, errors="ignore")

    # Generate summary using externalized comment groups
    summary_df = generate_summary(merged_df, comment_groups)

    # Save the updated file with normal data first, followed by the summary
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_sheet_name = f"Summary_{timestamp}"

    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        merged_df.to_excel(writer, sheet_name="Updated Data", index=False)
        summary_df.to_excel(writer, sheet_name=summary_sheet_name, index=False)






===================


import pandas as pd

def update_manual_status(excel1_path, excel2_path, sheet_name="manually_added"):
    """
    Reads the 'manually_added' sheet from excel1, compares rows with excel2,
    and adds a 'new_status' column based on presence in excel2.
    
    Parameters:
    - excel1_path (str): Path to the first Excel file (with manually added sheet)
    - excel2_path (str): Path to the second Excel file (comparison file)
    - sheet_name (str): Name of the sheet in excel1 that contains manually added data

    Returns:
    - pd.DataFrame: Updated DataFrame with all original columns + 'new_status'
    """
    # Load manually added sheet
    manually_df = pd.read_excel(excel1_path, sheet_name=sheet_name, dtype=str)

    # Load excel2 data for comparison
    excel2_df = pd.read_excel(excel2_path, dtype=str)

    # Define comparison columns
    compare_cols = ["Transactionid", "number", "name", "type", "country"]

    # Perform comparison and set new_status
    manually_df["new_status"] = manually_df[compare_cols].apply(
        lambda row: "correctly identified" if row.tolist() in excel2_df[compare_cols].values.tolist() else "missing",
        axis=1
    )

    return manually_df  # Returning the updated DataFrame



manually_df = update_manual_status(excel1_path, excel2_path)

# Save all sheets, including the updated manually added data
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
summary_sheet_name = f"Summary_{timestamp}"

with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
    merged_df.to_excel(writer, sheet_name="Updated Data", index=False)
    summary_df.to_excel(writer, sheet_name=summary_sheet_name, index=False)
    
    # Write updated 'manually_added' sheet
    manually_df.to_excel(writer, sheet_name="manually_added", index=False)



=================


import pandas as pd

def generate_manual_summary(manually_df, category_filters=None, source_filters=None):
    """
    Generates a summary report from the manually added DataFrame.
    
    Parameters:
    - manually_df (pd.DataFrame): Data from 'manually_added' sheet.
    - category_filters (dict): Dictionary of category names and their headers. 
                               Example: {"direct party": "Direct Party", "another category": "Another Header"}
    - source_filters (dict): Dictionary of source names and their headers.
                             Example: {"[Sow Document]": "Sow Doc", "[Edd Questionier]": "EDDQ"}

    Returns:
    - pd.DataFrame: Summary DataFrame aggregated at the 'account id' level.
    """
    # Default category filters if none provided
    if category_filters is None:
        category_filters = {"direct party": "Direct Party"}  # Add more as needed

    # Default source filters if none provided
    if source_filters is None:
        source_filters = {"[Sow Document]": "Sow Doc", "[Edd Questionier]": "EDDQ"}

    # Group by 'account id' to count total parties
    summary_df = manually_df.groupby("account id").size().reset_index(name="Total Parties")

    # Add source-based counts
    for source_value, header_name in source_filters.items():
        source_count = manually_df[manually_df["source"] == source_value].groupby("account id").size().reset_index(name=header_name)
        summary_df = summary_df.merge(source_count, on="account id", how="left")

    # Add category-based counts
    for category_value, header_name in category_filters.items():
        category_count = manually_df[manually_df["category"] == category_value].groupby("account id").size().reset_index(name=header_name)
        summary_df = summary_df.merge(category_count, on="account id", how="left")

    # Fill NaN values with 0 since merge might result in NaNs for missing categories/sources
    summary_df.fillna(0, inplace=True)

    return summary_df  # Returning the summary DataFrame


=====


# Generate manual summary
manual_summary_df = generate_manual_summary(manually_df)

# Save all sheets, including the manual summary
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
summary_sheet_name = f"Summary_{timestamp}"
manual_summary_sheet = f"manual_summary_{timestamp}"

with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
    merged_df.to_excel(writer, sheet_name="Updated Data", index=False)
    summary_df.to_excel(writer, sheet_name=summary_sheet_name, index=False)
    manually_df.to_excel(writer, sheet_name="manually_added", index=False)
    manual_summary_df.to_excel(writer, sheet_name=manual_summary_sheet, index=False)

print("✅ Excel updated successfully with all sheets!")

