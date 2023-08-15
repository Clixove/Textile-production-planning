-- Some ground truth of allocating orders to spinning batches violate train/test split.
-- The selected orders are in the training set, but they're allocated to batches where records appear only in
--  spinning table's testing set.
SELECT d.*, o.parts
FROM orders o
JOIN DEA d ON o.order_id = d.order_id
LEFT JOIN (
    SELECT DISTINCT batch_id
    FROM spinning
    WHERE date > '2020-09-06'
) AS after_date ON o.batch_id = after_date.batch_id
LEFT JOIN (
    SELECT DISTINCT batch_id
    FROM spinning
    WHERE date <= '2020-09-06'
) AS before_date ON o.batch_id = before_date.batch_id
WHERE date(o.created_time) <= '2020-09-06'
AND after_date.batch_id IS NOT NULL
AND before_date.batch_id IS NULL;
