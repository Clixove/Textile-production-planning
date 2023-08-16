SELECT '''' || a.batch_id || '''' as batch_id, count(*) as count
FROM texturing AS a
JOIN texturing AS b
ON a.batch_id = b.batch_id AND a.start_time < b.end_time AND a.end_time > b.start_time
       AND a.rowid != b.rowid
GROUP BY a.batch_id
HAVING count >= 2
ORDER BY count DESC