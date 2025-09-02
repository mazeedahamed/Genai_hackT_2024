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


Now, I’ll walk you through some of the results we observed from our A/B trials and consistency checks. In the interest of time, I’ll just show a few representative reports — a mix of both.
Starting with Translation:
For the A/B trials, GPT-4o consistently outperformed GPT-4. Based on the BLEU score thresholds we set, GPT-4o had only 5 documents fall below the 3% threshold, compared to 6 for GPT-4. Looking at overall performance, GPT-4o produced higher BLEU scores in 17 documents, while only 8 documents scored lower than GPT-4.
For the consistency check, we ran 5 different iterations. The variation in results was negligible, indicating strong stability in GPT-4o’s translations compared to GPT-4."
"Moving on to Detection:
We tested across 140 documents. GPT-4 achieved an accuracy of 91%, while GPT-4o improved this to 96%. The number of mismatches dropped from 10 in GPT-4 down to 5 in GPT-4o.
One observation worth noting is that acceptable mismatches slightly increased, mainly due to dialectal variations. For example, GPT-4o sometimes identifies “Devanagari Hindi” simply as “Hindi”. While technically accurate, it gets bucketed as a variance in our evaluation.
So overall, GPT-4o shows higher accuracy, fewer mismatches, and more consistent performance compared to GPT-4, both for translation and detection.


Now, let’s talk about entity identification. We ran five iterations to check for consistency, and the results showed very minimal variation, which is great for reliability. One of the challenges we faced is that identifying and categorizing parties can be quite complex.
To give you a detailed picture, we found that out of the 45 parties that were dropped, 17 were genuinely missing, while the remaining 28 were not considered valid drops. We’ll provide a breakdown of these missing parties, categorizing them into different groups, such as board members, government entities, individual names, and legal firms.
This detailed analysis will help us pinpoint exactly where the gaps are and refine our rules further. Over time, we’ve updated these rules, so now we can more accurately filter out noise and focus on the truly relevant data.

  Moving on to document classification, the report will present accuracy at multiple levels. We’ll break it down into three tiers: Tier 1, Tier 2, and a combined accuracy. For Tier 1, we’ll provide a detailed breakdown for each classification category, showing the accuracy and the number of documents that may have dropped from one tier to another.
For Tier 2, we’ll do the same, giving you a clear picture of how the accuracy compares. Overall, you’ll see that GPT-4o outperforms GPT-4 across these tiers. Additionally, with the new model, we’ve introduced a few more tiers, giving us even more granularity in our analysis


Now, let’s move on to performance insights. For our performance testing, we trigger all use cases in parallel directly from our source systems using an API. This means that all 50 parallel processes run simultaneously, allowing us to achieve significant efficiency. For example, when processing 200 documents, we can complete the task in about 15 minutes. This means that identifying parties from all 50 parallel streams takes roughly 2 minutes, including the Kafka processing.
