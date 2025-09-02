1. Language Detection
"Let me walk you through our evaluation techniques for different use cases, starting with language detection. We've curated a ground truth of 141 language documents. These will be uploaded to an API, which will automatically trigger the language detection process. Once detection is complete, we’ll extract the results and store them in a database. We’ll then compare these results against our ground truth to calculate metrics such as accuracy and completeness."

2. Language Translation

"Next, we have language translation. We've identified the top 25 most frequently used languages. For each, we’ll upload the manual translation and trigger the AI translation via the API. After the AI translation is done, we compare it to the manual version using the BLEU score. We have a predefined threshold—like 98% for Arabic—and if the score falls below this, we run a deeper evaluation using our custom framework to analyze any issues. This helps us fine-tune the model and ensure high accuracy."

3. Document Classification

"Our third use case is document classification. We have a ground truth set for different environments, such as production and QA, based on user feedback. We’ll reprocess the finalized documents for each environment, triggering the classification API again. The AI-generated classifications will be compared against the ground truth to measure accuracy at different tiers, ensuring we have a clear picture of the model’s performance."

4. Party Identification

"Moving on to party identification, we deal with two data sources: EDT questionnaire data and SOW documents. We have ground truths for both production and QA environments. When we re-trigger this use case, the system fetches the latest data and performs AI-based extraction. We then apply a rapid grouping logic to cluster similar parties, reducing duplicates. We compare the results to the ground truth and measure accuracy, while also identifying any extra or missing parties. For any missing parties, we categorize them into different buckets, providing a detailed report."

5. Party Disposition

"Lastly, for party disposition, we work with three vendors: Sealing, DTAQ, and RDC. Each vendor provides three attributes: name, address, and country. If all three match, it’s a true match; if not, we classify it accordingly. We have separate ground truths for each vendor and environment. When re-processing, we extract the results and update the database. We then generate a confusion matrix to show the accuracy, false positives, and false negatives for each vendor."

6. Final Points

"All these reports are ready to be shared with the LRC and MRM for review and approval. The entire process is fully automated, and once triggered, the reports are instantly generated and ready for sharing. We can run these use cases in any environment, as long as the ground truth is updated. This framework helps us

