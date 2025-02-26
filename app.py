SELECT r.transaction_id
FROM request r
JOIN req_document_info d ON r.request_id = d.request_id
JOIN results res ON d.document_info = res.document_info
WHERE res.processing_status = 'failed'
  AND res.operation = 'L'
  AND d.document_name LIKE '2%';
