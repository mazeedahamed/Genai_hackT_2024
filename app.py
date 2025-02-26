SELECT r.transaction_id, rdi.request_id, rdi.document_name
FROM results res
JOIN req_document_info rdi ON res.document_info = rdi.document_info
JOIN request r ON rdi.request_id = r.request_id
WHERE res.processing_status = 'failed'
  AND res.operation = 'L'
  AND rdi.document_name LIKE '2%';
