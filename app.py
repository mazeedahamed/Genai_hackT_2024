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
